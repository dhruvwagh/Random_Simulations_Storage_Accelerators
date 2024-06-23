#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/fs.h>
#include <linux/blkdev.h>
#include <linux/bio.h>

#define SIMP_BLKDEV_MAJOR 240       // Major number for your device
#define SIMP_BLKDEV_NAME "simp_blkdev"

static struct gendisk *simp_blkdev_disk;

// Function to open the block device
static int simp_blkdev_open(struct block_device *bdev, fmode_t mode) {
    printk(KERN_INFO "simp_blkdev: Device opened\n");
    return 0;
};

// Function to release the block device
static void simp_blkdev_release(struct gendisk *gdisk, fmode_t mode) {
    printk(KERN_INFO "simp_blkdev: Device released\n");
};

static struct block_device_operations simp_blkdev_ops = {
    .owner = THIS_MODULE,
    .open = simp_blkdev_open,
    .release = simp_blkdev_release,
};

// Function called at module load time
static int __init simp_blkdev_init(void) {
    int ret;

    // Register block device
    ret = register_blkdev(SIMP_BLKDEV_MAJOR, SIMP_BLKDEV_NAME);
    if (ret < 0) {
        printk(KERN_ERR "simp_blkdev: Unable to register block device\n");
        return ret;
    }

    // Allocate and setup gendisk structure for the block device
    simp_blkdev_disk = alloc_disk(1); // Allocating disk for one partition
    if (!simp_blkdev_disk) {
        unregister_blkdev(SIMP_BLKDEV_MAJOR, SIMP_BLKDEV_NAME);
        return -ENOMEM;
    }

    simp_blkdev_disk->major = SIMP_BLKDEV_MAJOR;
    simp_blkdev_disk->first_minor = 0;
    simp_blkdev_disk->fops = &simp_blkdev_ops;
    simp_blkdev_disk->private_data = NULL;
    sprintf(simp_blkdev_disk->disk_name, "simp0");
    set_capacity(simp_blkdev_disk, 1024); // Setting device size to 1024 sectors (512 bytes each)

    add_disk(simp_blkdev_disk);

    printk(KERN_INFO "simp_blkdev: Block device registered\n");

    return 0;
};

// Function called at module unload time
static void __exit simp_blkdev_exit(void) {
    del_gendisk(simp_blkdev_disk);
    put_disk(simp_blkdev_disk);
    unregister_blkdev(SIMP_BLKDEV_MAJOR, SIMP_BLKDEV_NAME);
    printk(KERN_INFO "simp_blkdev: Block device unregistered\n");
};

module_init(simp_blkdev_init);
module_exit(simp_blkdev_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("Simple Block Device");
