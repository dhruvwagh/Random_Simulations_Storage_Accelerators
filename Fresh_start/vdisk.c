#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/errno.h>
#include <linux/types.h>
#include <linux/vmalloc.h>
#include <linux/genhd.h>
#include <linux/blkdev.h>
#include <linux/hdreg.h>
#include <linux/blk-mq.h>

#define DEVICE_NAME "vdisk"
#define VDISK_MINORS 16
#define KERNEL_SECTOR_SIZE 512

static int major_num = 0;
module_param(major_num, int, 0);
static int logical_block_size = 512;
module_param(logical_block_size, int, 0);
static int nsectors = 1024; /* How big the drive is */
module_param(nsectors, int, 0);

static struct vdisk_dev {
    int size;
    u8 *data;
    struct blk_mq_tag_set tag_set;
    struct request_queue *queue;
    struct gendisk *gd;
} device;

static void vdisk_transfer(struct vdisk_dev *dev, sector_t sector,
                           unsigned long nsect, char *buffer, int write) {
    unsigned long offset = sector * logical_block_size;
    unsigned long nbytes = nsect * logical_block_size;

    if ((offset + nbytes) > dev->size) {
        printk(KERN_NOTICE "Beyond-end write (%ld %ld)\n", offset, nbytes);
        return;
    }

    if (write)
        memcpy(dev->data + offset, buffer, nbytes);
    else
        memcpy(buffer, dev->data + offset, nbytes);
}

static int vdisk_open(struct block_device *bdev, fmode_t mode) {
    return 0;
}

static int vdisk_ioctl(struct block_device *bdev, fmode_t mode,
                       unsigned int cmd, unsigned long arg) {
    return -ENOTTY;
}

static int vdisk_getgeo(struct block_device *bdev, struct hd_geometry *geo) {
    long size;

    size = device.size * (logical_block_size / KERNEL_SECTOR_SIZE);
    geo->cylinders = (size & ~0x3f) >> 6;
    geo->heads = 4;
    geo->sectors = 16;  // Changed from 256 to 16
    geo->start = 0;
    return 0;
}

static struct block_device_operations vdisk_ops = {
    .owner           = THIS_MODULE,
    .open            = vdisk_open,
    .release         = NULL,
    .ioctl           = vdisk_ioctl,
    .getgeo          = vdisk_getgeo,
};

static blk_status_t vdisk_queue_rq(struct blk_mq_hw_ctx *hctx,
                                   const struct blk_mq_queue_data *bd) {
    struct request *rq = bd->rq;
    struct vdisk_dev *dev = rq->q->queuedata;
    struct bio_vec bvec;
    struct req_iterator iter;
    sector_t pos = blk_rq_pos(rq);
    void *buffer;
    blk_status_t ret = BLK_STS_OK;

    blk_mq_start_request(rq);

    rq_for_each_segment(bvec, rq, iter) {
        unsigned long b_len = bvec.bv_len;

        buffer = page_address(bvec.bv_page) + bvec.bv_offset;

        if (rq_data_dir(rq) == WRITE)
            vdisk_transfer(dev, pos, b_len / KERNEL_SECTOR_SIZE, buffer, 1);
        else
            vdisk_transfer(dev, pos, b_len / KERNEL_SECTOR_SIZE, buffer, 0);

        pos += b_len / KERNEL_SECTOR_SIZE;
    }

    blk_mq_end_request(rq, ret);
    return ret;
}

static struct blk_mq_ops vdisk_mq_ops = {
    .queue_rq = vdisk_queue_rq,
};

static int __init vdisk_init(void) {
    device.size = nsectors * logical_block_size;
    device.data = vmalloc(device.size);
    if (device.data == NULL)
        return -ENOMEM;

    major_num = register_blkdev(major_num, DEVICE_NAME);
    if (major_num < 0) {
        printk(KERN_WARNING "vdisk: unable to get major number\n");
        vfree(device.data);
        return -EBUSY;
    }

    device.tag_set.ops = &vdisk_mq_ops;
    device.tag_set.nr_hw_queues = 1;
    device.tag_set.queue_depth = 128;
    device.tag_set.numa_node = NUMA_NO_NODE;
    device.tag_set.cmd_size = 0;
    device.tag_set.flags = BLK_MQ_F_SHOULD_MERGE;
    device.tag_set.driver_data = &device;

    if (blk_mq_alloc_tag_set(&device.tag_set) != 0) {
        unregister_blkdev(major_num, DEVICE_NAME);
        vfree(device.data);
        return -ENOMEM;
    }

    device.queue = blk_mq_init_queue(&device.tag_set);
    if (IS_ERR(device.queue)) {
        blk_mq_free_tag_set(&device.tag_set);
        unregister_blkdev(major_num, DEVICE_NAME);
        vfree(device.data);
        return -ENOMEM;
    }

    device.queue->queuedata = &device;

    device.gd = blk_alloc_disk(NUMA_NO_NODE);  // Changed from alloc_disk to blk_alloc_disk
    if (!device.gd) {
        blk_cleanup_queue(device.queue);
        blk_mq_free_tag_set(&device.tag_set);
        unregister_blkdev(major_num, DEVICE_NAME);
        vfree(device.data);
        return -ENOMEM;
    }

    device.gd->major = major_num;
    device.gd->first_minor = 0;
    device.gd->fops = &vdisk_ops;
    device.gd->private_data = &device;
    strcpy(device.gd->disk_name, DEVICE_NAME);
    set_capacity(device.gd, nsectors * (logical_block_size / KERNEL_SECTOR_SIZE));
    device.gd->queue = device.queue;

    add_disk(device.gd);

    printk(KERN_INFO "vdisk: module loaded\n");
    return 0;
}

static void __exit vdisk_exit(void) {
    del_gendisk(device.gd);
    put_disk(device.gd);
    blk_cleanup_queue(device.queue);
    blk_mq_free_tag_set(&device.tag_set);
    unregister_blkdev(major_num, DEVICE_NAME);
    vfree(device.data);
    printk(KERN_INFO "vdisk: module unloaded\n");
}

module_init(vdisk_init);
module_exit(vdisk_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple virtual disk driver");