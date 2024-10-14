CXX = g++
CXXFLAGS = -Wall -O2 -std=c++11 `pkg-config fuse3 --cflags`
LDFLAGS = `pkg-config fuse3 --libs -pthread`
SOURCES = main.cpp MurmurHash3.cpp
TARGET = myfs

all: $(TARGET)

$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCES) $(LDFLAGS)

clean:
	rm -f $(TARGET)
