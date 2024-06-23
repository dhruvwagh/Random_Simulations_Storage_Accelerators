cmd_/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o := gcc -Wp,-MMD,/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/.simp_blkdev.o.d -nostdinc -I./arch/x86/include -I./arch/x86/include/generated  -I./include -I./arch/x86/include/uapi -I./arch/x86/include/generated/uapi -I./include/uapi -I./include/generated/uapi -include ./include/linux/compiler-version.h -include ./include/linux/kconfig.h -include ./include/linux/compiler_types.h -D__KERNEL__ -fmacro-prefix-map=./= -Wall -Wundef -Werror=strict-prototypes -Wno-trigraphs -fno-strict-aliasing -fno-common -fshort-wchar -fno-PIE -Werror=implicit-function-declaration -Werror=implicit-int -Werror=return-type -Wno-format-security -std=gnu11 -mno-sse -mno-mmx -mno-sse2 -mno-3dnow -mno-avx -fcf-protection=none -m64 -falign-jumps=1 -falign-loops=1 -mno-80387 -mno-fp-ret-in-387 -mpreferred-stack-boundary=3 -mskip-rax-setup -mtune=generic -mno-red-zone -mcmodel=kernel -Wno-sign-compare -fno-asynchronous-unwind-tables -mindirect-branch=thunk-extern -mindirect-branch-register -mindirect-branch-cs-prefix -mfunction-return=thunk-extern -fno-jump-tables -mharden-sls=all -fno-delete-null-pointer-checks -Wno-frame-address -Wno-format-truncation -Wno-format-overflow -Wno-address-of-packed-member -O2 -fno-allow-store-data-races -Wframe-larger-than=1024 -fstack-protector-strong -Wno-array-bounds -Wimplicit-fallthrough=5 -Wno-main -Wno-unused-but-set-variable -Wno-unused-const-variable -Wno-dangling-pointer -fno-omit-frame-pointer -fno-optimize-sibling-calls -ftrivial-auto-var-init=zero -fno-stack-clash-protection -fzero-call-used-regs=used-gpr -pg -mrecord-mcount -mfentry -DCC_USING_FENTRY -Wdeclaration-after-statement -Wvla -Wno-pointer-sign -Wcast-function-type -Wno-stringop-truncation -Wno-stringop-overflow -Wno-restrict -Wno-maybe-uninitialized -Wno-alloc-size-larger-than -fno-strict-overflow -fno-stack-check -fconserve-stack -Werror=date-time -Werror=incompatible-pointer-types -Werror=designated-init -Wno-packed-not-aligned -g -gdwarf-5  -fsanitize=bounds -fsanitize=shift -fsanitize=bool -fsanitize=enum  -DMODULE  -DKBUILD_BASENAME='"simp_blkdev"' -DKBUILD_MODNAME='"simp_blkdev"' -D__KBUILD_MODNAME=kmod_simp_blkdev -c -o /home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o /home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.c   ; ./tools/objtool/objtool  --hacks=jump_label  --hacks=noinstr     --retpoline  --rethunk  --sls  --stackval  --static-call  --uaccess   --module  /home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o

source_/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o := /home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.c

deps_/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o := \
  include/linux/compiler-version.h \
    $(wildcard include/config/CC_VERSION_TEXT) \
  include/linux/kconfig.h \
    $(wildcard include/config/CPU_BIG_ENDIAN) \
    $(wildcard include/config/BOOGER) \
    $(wildcard include/config/FOO) \
  include/linux/compiler_types.h \
    $(wildcard include/config/DEBUG_INFO_BTF) \
    $(wildcard include/config/PAHOLE_HAS_BTF_TAG) \
    $(wildcard include/config/HAVE_ARCH_COMPILER_H) \
    $(wildcard include/config/CC_HAS_ASM_INLINE) \
  include/linux/compiler_attributes.h \
  include/linux/compiler-gcc.h \
    $(wildcard include/config/RETPOLINE) \
    $(wildcard include/config/ARCH_USE_BUILTIN_BSWAP) \
    $(wildcard include/config/SHADOW_CALL_STACK) \
    $(wildcard include/config/KCOV) \

/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o: $(deps_/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o)

$(deps_/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o):

/home/dhruv/Documents/WORK/Random_Simulations_Storage_Accelerators/simp_blkdev/simp_blkdev.o: $(wildcard ./tools/objtool/objtool)
