#include <iostream>
#include <queue>
#include <thread>
#include <chrono>
#include <vector>
#include <random>
#include </home/arch/Documents/Random_Simulations_Storage_Accelerators/cpp_files/smhasher/src/MurmurHash3.cpp>

const int number_of_ssds = 4;
const int msb_number = static_cast<int>(log2(number_of_ssds));

std::vector<uint8_t> generate_random_value() {
    std::vector<uint8_t> value(4096);
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint8_t> dis(0, 255);
    for (size_t i = 0; i < 4096; ++i) {
        value[i] = dis(gen);
    }
    return value;
}

class key_value_pair {
public:
    uint32_t key;
    std::vector<uint8_t> value;

    key_value_pair(uint32_t k, const std::vector<uint8_t>& v) : key(k), value(v) {}
};

std::vector<std::queue<std::pair<uint64_t, std::vector<uint8_t>>>> hashed_buffers;
std::queue<std::pair<uint32_t, std::vector<uint8_t>>> arrival_buffer;

uint64_t hash_function(uint32_t key) {
    uint64_t hash[2];
    MurmurHash3_x64_128(&key, sizeof(key), 0, hash);
    return hash[0];
}

uint32_t extract_msbs(uint64_t value, int num_bits) {
    uint32_t mask = (1 << num_bits) - 1;
    uint32_t msbs = (value >> (64 - num_bits)) & mask;
    return msbs;
}

void input_func(std::queue<key_value_pair>& arrival_buffer) {
    for (int i = 0; i < 10000; ++i) {
        uint32_t address = rand() % (1UL << 32);
        std::vector<uint8_t> value = generate_random_value();
        key_value_pair kv_pair(address, value); // Create a key_value_pair object
        arrival_buffer.push(kv_pair);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}



void output(const std::pair<uint64_t, std::vector<uint8_t>>& kv_pair) {
    std::cout << "address sending to ssd: " << kv_pair.first << std::endl;
}

void bucket_sort(int msbs, const key_value_pair& kv_pair, uint64_t hashed_key) {
    int i = msbs;
    std::cout << "Bucket sorting into: " << i << std::endl;
    std::pair<uint64_t, std::vector<uint8_t>> hkv_pair(hashed_key, kv_pair.value);
    hashed_buffers[i].push(hkv_pair);
    std::cout << "buffer size: " << hashed_buffers[i].size() << std::endl;
}

void kv_process(std::queue<key_value_pair>& arrival_buffer) {
    std::cout << "kv_process thread started." << std::endl;
    while (true) {
        if (arrival_buffer.empty()) {
            std::cout << "kv_process: Waiting for input..." << std::endl;
            std::this_thread::sleep_for(std::chrono::seconds(5));
        } else {
            key_value_pair kv_p = arrival_buffer.front();
            arrival_buffer.pop();
            std::cout << "kv_process: Processing " << kv_p.key << std::endl;
            uint64_t hashed_key = hash_function(kv_p.key);
            int msbs = extract_msbs(hashed_key, msb_number);
            bucket_sort(msbs, kv_p, hashed_key);
            std::cout << "finished processing hash key: " << hashed_key << std::endl;
            std::cout << "arrival buffer after processing: " << arrival_buffer.size() << std::endl;
        }
    }
}



void switch_function(std::vector<std::queue<std::pair<uint64_t, std::vector<uint8_t>>>>& hashed_buffers) {
    std::cout << "switch thread started." << std::endl;
    while (true) {
        for (int i = 0; i < number_of_ssds; ++i) {
            std::cout << "Switching for bucket " << i << std::endl;
            std::cout << "size of hashed bucket: " << hashed_buffers[i].size() << std::endl;
            if (!hashed_buffers[i].empty()) {
                std::pair<uint64_t, std::vector<uint8_t>> kv_pair = hashed_buffers[i].front();
                hashed_buffers[i].pop();
                output(kv_pair);
            }
        }
        std::this_thread::sleep_for(std::chrono::seconds(5));
    }
}

int main() {
    for (int i = 0; i < number_of_ssds; ++i) {
        std::queue<std::pair<uint64_t, std::vector<uint8_t>>> tq;
        hashed_buffers.push_back(tq);
    }

    std::thread input_thread([&]() { input_func(arrival_buffer); });
    std::thread sort_thread([&]() { kv_process(arrival_buffer); });
    std::thread spit_thread([&]() { switch_function(hashed_buffers); });



    input_thread.join();
    sort_thread.join();
    spit_thread.join();

    return 0;
}
