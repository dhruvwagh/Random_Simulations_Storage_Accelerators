#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif


static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x4b94a47f, "__blk_alloc_disk" },
	{ 0xe914e41e, "strcpy" },
	{ 0xfa2f8212, "blk_queue_logical_block_size" },
	{ 0x1ffc5043, "device_add_disk" },
	{ 0x37a0cba, "kfree" },
	{ 0xae04012c, "__vmalloc" },
	{ 0x6ca1144a, "kmem_cache_alloc_trace" },
	{ 0x6012fa85, "bio_end_io_acct_remapped" },
	{ 0xbdfb6dbb, "__fentry__" },
	{ 0x92997ed8, "_printk" },
	{ 0x260203b9, "put_disk" },
	{ 0xd0da656b, "__stack_chk_fail" },
	{ 0x4e12c836, "blk_queue_physical_block_size" },
	{ 0xb08cd2e9, "blk_queue_flag_set" },
	{ 0xaa5cf3cb, "bio_start_io_acct" },
	{ 0x7cd8d75e, "page_offset_base" },
	{ 0xb5a459dc, "unregister_blkdev" },
	{ 0x4fb9aa7a, "bio_endio" },
	{ 0x17c24698, "set_capacity" },
	{ 0x23d2c091, "del_gendisk" },
	{ 0x5c3c7387, "kstrtoull" },
	{ 0xe8450e8, "param_ops_charp" },
	{ 0x5b8239ca, "__x86_return_thunk" },
	{ 0x6b10bee1, "_copy_to_user" },
	{ 0x3c3ff9fd, "sprintf" },
	{ 0x97651e6c, "vmemmap_base" },
	{ 0x999e8297, "vfree" },
	{ 0x85df9b6c, "strsep" },
	{ 0x720a27a7, "__register_blkdev" },
	{ 0x837b7b09, "__dynamic_pr_debug" },
	{ 0xcf721eb, "blk_queue_max_hw_sectors" },
	{ 0x754d539c, "strlen" },
	{ 0xeb233a45, "__kmalloc" },
	{ 0xe2c17b5d, "__SCT__might_resched" },
	{ 0x324171a4, "kmalloc_caches" },
	{ 0x76b4c310, "module_layout" },
};

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "6CA64EA9D9EEA24A10B54B0");
