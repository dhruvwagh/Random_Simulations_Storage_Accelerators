#ifndef RAMDRV_INTERNAL_H
#define RAMDRV_INTERNAL_H

#define RAMDRV_MODULE_NAME "ramdrv"
#define RAMDRV_BLKDEV_NAME "ramdrv"
#define RAMDRV_CNTLDEV_NAME "ramctl"

#define KERNEL_SECTOR_SIZE 512

#define RAMDRV_MINORS	16

struct ramdrv_dev {
        int size; //device size in bytes (only KERNEL_SECTOR_SIZE)
        u8 *data; //pointer to vmalloc'ed data
        short users; //curent device users
        spinlock_t lock; //dev async lock
        struct request_queue *queue; //request queue
        struct gendisk *gd; //linked gendisk
};

#endif
