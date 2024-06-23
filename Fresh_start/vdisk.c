#include <linux/module.h>
#include <linux/blkdev.h>
#include <linux/blk-mq.h>
#include <linux/vmalloc.h>
#include <linux/hdreg.h>
#include <linux/bio.h>

#define VDISK_SIZE (1024 * 1024 * 50)  // 50 MB size
#define VDISK_NAME "vdisk"

struct vdisk_info {
    unsigned char *data;  // Disk data
    struct request_queue *queue;
    struct gendisk *gd;
    struct blk_mq_tag_set tag_set;
};

static struct vdisk_info vdisk;

// Function to handle opening the block device
static int vdisk_open(struct gendisk *gd, fmode_t mode) {
    printk(KERN_INFO "vdisk: Device opened\n");
    return 0;
}

// Function to handle closing the block device
static void vdisk_release(struct gendisk *gd, fmode_t mode) {
    printk(KERN_INFO "vdisk: Device closed\n");
}

// Function to get the geometry of the virtual disk
static int vdisk_getgeo(struct block_device *bdev, struct hd_geometry *geo) {
    geo->heads = 4;
    geo->cylinders = 1024;
    geo->sectors = 256;
    geo->start = 0;
    return 0;
}

// Define the block device operations
static struct block_device_operations vdisk_ops = {
    .owner = THIS_MODULE,
    .open = vdisk_open,
    .release = vdisk_release,
    .getgeo = vdisk_getgeo,
};

// Function to process the queue (reads and writes)
static blk_status_t vdisk_queue_rq(struct blk_mq_hw_ctx *hctx, const struct blk_mq_queue_data *bd) {
    struct request *req = bd->rq;
    struct bio_vec bvec;
    struct req_iterator iter;
    loff_t pos;
    blk_status_t status = BLK_STS_OK;

    blk_mq_start_request(req);

    rq_for_each_segment(bvec, req, iter) {
        pos = iter.bio->bi_iter.bi_sector << 9;  // Convert sector to bytes
        if (bio_data_dir(iter.bio) == WRITE)
            memcpy(vdisk.data + pos, page_address(bvec.bv_page) + bvec.bv_offset, bvec.bv_len);
        else
            memcpy(page_address(bvec.bv_page) + bvec.bv_offset, vdisk.data + pos, bvec.bv_len);
    }

    blk_mq_end_request(req, status);
    return BLK_STS_OK;
}

// blk_mq_ops structure initialization
static struct blk_mq_ops vdisk_mq_ops = {
    .queue_rq = vdisk_queue_rq,
};

// Module initialization function
static int __init vdisk_init(void) {
    vdisk.data = vmalloc(VDISK_SIZE);
    if (!vdisk.data)
        return -ENOMEM;

    vdisk.tag_set.ops = &vdisk_mq_ops;
    vdisk.tag_set.nr_hw_queues = 1;
    vdisk.tag_set.queue_depth = 128;
    vdisk.tag_set.numa_node = NUMA_NO_NODE;
    vdisk.tag_set.cmd_size = 0;
    vdisk.tag_set.flags = BLK_MQ_F_SHOULD_MERGE;

    if (blk_mq_alloc_tag_set(&vdisk.tag_set)) {
        vfree(vdisk.data);
        return -ENOMEM;
    }

    vdisk.queue = blk_mq_init_queue(&vdisk.tag_set);
    if (IS_ERR(vdisk.queue)) {
        blk_mq_free_tag_set(&vdisk.tag_set);
        vfree(vdisk.data);
        return PTR_ERR(vdisk.queue);
    }

    vdisk.gd = alloc_disk(1);
    if (!vdisk.gd) {
        blk_cleanup_queue(vdisk.queue);
        blk_mq_free_tag_set(&vdisk.tag_set);
        vfree(vdisk.data);
        return -ENOMEM;
    }

    vdisk.gd->major = 0;  // dynamic major
    vdisk.gd->first_minor = 0;
    vdisk.gd->fops = &vdisk_ops;
    vdisk.gd->private_data = &vdisk;
    strcpy(vdisk.gd->disk_name, VDISK_NAME);
    set_capacity(vdisk.gd, VDISK_SIZE / 512);  // Set the capacity in sectors
    vdisk.gd->queue = vdisk.queue;
    add_disk(vdisk.gd);

    printk(KERN_INFO "vdisk: Virtual disk initialized\n");
    return 0;
}

// Module cleanup function
static void __exit vdisk_exit(void) {
    del_gendisk(vdisk.gd);
    put_disk(vdisk.gd);
    blk_cleanup_queue(vdisk.queue);
    blk_mq_free_tag_set(&vdisk.tag_set);
    vfree(vdisk.data);
    printk(KERN_INFO "vdisk: Module unloaded\n");
}

module_init(vdisk_init);
module_exit(vdisk_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("Virtual Block Device using blk_mq");
