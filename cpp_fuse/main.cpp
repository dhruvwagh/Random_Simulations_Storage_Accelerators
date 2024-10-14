#define FUSE_USE_VERSION 35

#include <fuse3/fuse.h>
#include <cstring>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <mutex>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <thread>
#include <condition_variable>
#include <memory>

using namespace std;

// MurmurHash3 Implementation
uint32_t MurmurHash3(const string& key, uint32_t seed = 42) {
    const uint8_t* data = (const uint8_t*)key.data();
    int len = key.length();

    const int nblocks = len / 4;
    uint32_t h1 = seed;

    const uint32_t c1 = 0xcc9e2d51;
    const uint32_t c2 = 0x1b873593;

    // Body
    const uint32_t* blocks = (const uint32_t*)(data);
    for (int i = 0; i < nblocks; i++) {
        uint32_t k1 = blocks[i];

        k1 *= c1;
        k1 = (k1 << 15) | (k1 >> 17);
        k1 *= c2;

        h1 ^= k1;
        h1 = (h1 << 13) | (h1 >> 19);
        h1 = h1 * 5 + 0xe6546b64;
    }

    // Tail
    const uint8_t* tail = (const uint8_t*)(data + nblocks * 4);
    uint32_t k1 = 0;

    switch (len & 3) {
        case 3:
            k1 ^= tail[2] << 16;
            [[fallthrough]];
        case 2:
            k1 ^= tail[1] << 8;
            [[fallthrough]];
        case 1:
            k1 ^= tail[0];
            k1 *= c1;
            k1 = (k1 << 15) | (k1 >> 17);
            k1 *= c2;
            h1 ^= k1;
            break;
    }

    // Finalization
    h1 ^= len;
    h1 ^= (h1 >> 16);
    h1 *= 0x85ebca6b;
    h1 ^= (h1 >> 13);
    h1 *= 0xc2b2ae35;
    h1 ^= (h1 >> 16);

    return h1;
}

// SSD Simulation Classes
class Page {
public:
    bool valid;          // Is the data valid
    bool dirty;          // Has the page been written to
    uint8_t data[4096];  // 4 KB page

    Page() : valid(false), dirty(false) {
        memset(data, 0xFF, sizeof(data)); // Initialize to all 1s (typical for NAND flash)
    }
};

class Block {
public:
    static const uint32_t PAGES_PER_BLOCK = 64; // Reduced from 256
    vector<unique_ptr<Page>> pages;
    uint32_t erase_count;

    Block() : erase_count(0) {
        pages.reserve(PAGES_PER_BLOCK); // Reserve space, but do not allocate pages initially
    }

    void allocate_page(uint32_t page_index) {
        if (pages.size() <= page_index) {
            pages.resize(page_index + 1);
        }
        if (!pages[page_index]) {
            pages[page_index] = make_unique<Page>();
        }
    }

    bool is_full() const {
        for (const auto& page : pages) {
            if (!page || !page->valid) return false;
        }
        return true;
    }

    bool is_empty() const {
        for (const auto& page : pages) {
            if (page && page->valid) return false;
        }
        return true;
    }

    void erase() {
        for (auto& page : pages) {
            if (page) {
                page->valid = false;
                page->dirty = false;
                memset(page->data, 0xFF, sizeof(page->data)); // Erase to all 1s
            }
        }
        erase_count++;
    }
};

class SSD {
public:
    static const uint32_t TOTAL_BLOCKS = 256; // Reduced from 1024
    vector<unique_ptr<Block>> blocks;

    // Logical to physical mapping (LBA to physical address)
    map<uint32_t, pair<uint32_t, uint32_t>> lba_to_pba;
    map<uint32_t, uint32_t> wear_leveling_info;

    uint32_t next_free_block;
    mutex ssd_mutex;

    SSD() : next_free_block(0) {
        blocks.reserve(TOTAL_BLOCKS); // Reserve space for blocks, but do not allocate initially
    }

    void allocate_block(uint32_t block_index) {
        if (blocks.size() <= block_index) {
            blocks.resize(block_index + 1);
        }
        if (!blocks[block_index]) {
            blocks[block_index] = make_unique<Block>();
        }
    }

    bool read(uint32_t lba, uint8_t* buffer);
    bool write(uint32_t lba, const uint8_t* buffer);
    void garbage_collect();
    void wear_leveling();
    uint32_t find_free_page();
};

bool SSD::read(uint32_t lba, uint8_t* buffer) {
    lock_guard<mutex> lock(ssd_mutex);

    auto it = lba_to_pba.find(lba);
    if (it == lba_to_pba.end()) {
        // LBA not mapped
        return false;
    }

    uint32_t block_index = it->second.first;
    uint32_t page_index = it->second.second;

    allocate_block(block_index);
    Block& block = *blocks[block_index];

    if (block_index >= TOTAL_BLOCKS || page_index >= Block::PAGES_PER_BLOCK) {
        // Invalid physical address
        return false;
    }

    block.allocate_page(page_index);
    Page& page = *block.pages[page_index];
    if (!page.valid) {
        // Page is invalid
        return false;
    }

    memcpy(buffer, page.data, sizeof(page.data));
    return true;
}

bool SSD::write(uint32_t lba, const uint8_t* buffer) {
    lock_guard<mutex> lock(ssd_mutex);

    // Check if LBA already mapped
    auto it = lba_to_pba.find(lba);
    if (it != lba_to_pba.end()) {
        // Mark old page as invalid (cannot overwrite without erase)
        uint32_t old_block_index = it->second.first;
        uint32_t old_page_index = it->second.second;
        allocate_block(old_block_index);
        Block& old_block = *blocks[old_block_index];
        old_block.allocate_page(old_page_index);
        old_block.pages[old_page_index]->valid = false;
        old_block.pages[old_page_index]->dirty = true;
    }

    // Find a free page
    uint32_t physical_address = find_free_page();
    if (physical_address == UINT32_MAX) {
        // No free pages, perform garbage collection
        garbage_collect();
        physical_address = find_free_page();
        if (physical_address == UINT32_MAX) {
            // Still no free pages
            return false;
        }
    }

    uint32_t block_index = physical_address / Block::PAGES_PER_BLOCK;
    uint32_t page_index = physical_address % Block::PAGES_PER_BLOCK;

    // Allocate block and page if not already allocated
    allocate_block(block_index);
    Block& block = *blocks[block_index];
    block.allocate_page(page_index);

    // Write data to the page
    Page& page = *block.pages[page_index];
    memcpy(page.data, buffer, sizeof(page.data));
    page.valid = true;
    page.dirty = false;

    // Update mapping
    lba_to_pba[lba] = make_pair(block_index, page_index);
    return true;
}

uint32_t SSD::find_free_page() {
    for (uint32_t block_idx = next_free_block; block_idx < TOTAL_BLOCKS; ++block_idx) {
        allocate_block(block_idx);
        Block& block = *blocks[block_idx];
        for (uint32_t page_idx = 0; page_idx < Block::PAGES_PER_BLOCK; ++page_idx) {
            block.allocate_page(page_idx);
            Page& page = *block.pages[page_idx];
            if (!page.valid && !page.dirty) {
                next_free_block = block_idx; // Update next free block hint
                return block_idx * Block::PAGES_PER_BLOCK + page_idx;
            }
        }
    }
    // No free page found
    return UINT32_MAX;
}

void SSD::garbage_collect() {
    // Simple garbage collection algorithm:
    // Find a block with the most invalid pages and erase it
    uint32_t target_block_idx = UINT32_MAX;
    uint32_t max_invalid_pages = 0;

    for (uint32_t block_idx = 0; block_idx < TOTAL_BLOCKS; ++block_idx) {
        allocate_block(block_idx);
        Block& block = *blocks[block_idx];
        uint32_t invalid_pages = 0;
        for (const auto& page : block.pages) {
            if (page && !page->valid && page->dirty) {
                invalid_pages++;
            }
        }
        if (invalid_pages > max_invalid_pages) {
            max_invalid_pages = invalid_pages;
            target_block_idx = block_idx;
        }
    }

    if (target_block_idx != UINT32_MAX) {
        // Move valid pages to new locations
        allocate_block(target_block_idx);
        Block& block = *blocks[target_block_idx];
        for (uint32_t page_idx = 0; page_idx < Block::PAGES_PER_BLOCK; ++page_idx) {
            if (block.pages[page_idx] && block.pages[page_idx]->valid) {
                // Read page data
                uint8_t buffer[4096];
                memcpy(buffer, block.pages[page_idx]->data, sizeof(block.pages[page_idx]->data));
                // Write to a new page
                uint32_t lba = 0; // Find LBA that maps to this PBA
                for (const auto& mapping : lba_to_pba) {
                    if (mapping.second.first == target_block_idx && mapping.second.second == page_idx) {
                        lba = mapping.first;
                        break;
                    }
                }
                write(lba, buffer); // This updates the mapping
            }
        }
        // Erase the block
        block.erase();
        next_free_block = target_block_idx;
    }
}

void SSD::wear_leveling() {
    // Basic wear leveling (not fully implemented)
    // Track erase counts and redistribute writes if necessary
    // This function can be expanded to implement wear leveling algorithms
}

///////////////////////////////////////////////////////////////////////////////

// Global Variables

const uint32_t NUM_SSDS = 4;
vector<SSD> ssds(NUM_SSDS);
mutex metadata_mutex;

// In-memory file metadata (file size, LBA list)
struct FileMetadata {
    uint32_t size;
    vector<uint32_t> lbas; // Logical Block Addresses
};

map<string, FileMetadata> file_metadata;

///////////////////////////////////////////////////////////////////////////////

// Helper Functions

uint32_t get_ssd_index(const string& file_path) {
    uint32_t hash_value = MurmurHash3(file_path);
    uint32_t ssd_index = hash_value % NUM_SSDS;
    return ssd_index;
}

uint32_t allocate_lba(FileMetadata& metadata) {
    uint32_t lba = metadata.lbas.size();
    metadata.lbas.push_back(lba);
    return lba;
}

///////////////////////////////////////////////////////////////////////////////

// FUSE Callbacks

static int myfs_getattr(const char* path, struct stat* stbuf, struct fuse_file_info* fi) {
    memset(stbuf, 0, sizeof(struct stat));

    if (strcmp(path, "/") == 0) {
        stbuf->st_mode = S_IFDIR | 0755;
        stbuf->st_nlink = 2;
        return 0;
    }

    lock_guard<mutex> lock(metadata_mutex);
    auto it = file_metadata.find(path);
    if (it != file_metadata.end()) {
        stbuf->st_mode = S_IFREG | 0666;
        stbuf->st_nlink = 1;
        stbuf->st_size = it->second.size;
        return 0;
    }

    return -ENOENT;
}

static int myfs_readdir(const char* path, void* buf, fuse_fill_dir_t filler, off_t offset, struct fuse_file_info* fi, enum fuse_readdir_flags flags) {
    if (strcmp(path, "/") != 0) {
        return -ENOENT;
    }

    filler(buf, ".", NULL, 0, static_cast<fuse_fill_dir_flags>(0));
    filler(buf, "..", NULL, 0, static_cast<fuse_fill_dir_flags>(0));

    lock_guard<mutex> lock(metadata_mutex);
    for (const auto& entry : file_metadata) {
        string filename = entry.first.substr(1); // Remove leading '/'
        filler(buf, filename.c_str(), NULL, 0, static_cast<fuse_fill_dir_flags>(0));
    }
    return 0;
}

static int myfs_open(const char* path, struct fuse_file_info* fi) {
    lock_guard<mutex> lock(metadata_mutex);
    if (file_metadata.find(path) == file_metadata.end()) {
        return -ENOENT;
    }
    return 0;
}

static int myfs_create(const char* path, mode_t mode, struct fuse_file_info* fi) {
    lock_guard<mutex> lock(metadata_mutex);
    if (file_metadata.find(path) != file_metadata.end()) {
        return -EEXIST;
    }

    FileMetadata metadata;
    metadata.size = 0;
    file_metadata[path] = metadata;
    return 0;
}