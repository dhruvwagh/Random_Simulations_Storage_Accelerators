#ifndef MURMURHASH3_H
#define MURMURHASH3_H

#include <cstdint>
#include <string>

uint32_t MurmurHash3(const std::string& key, uint32_t seed = 42);

#endif // MURMURHASH3_H
