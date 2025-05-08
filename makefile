# Compiler
CXX := g++
CXXFLAGS := -O3 -std=c++11 -pthread

# Source file
SRC := cas_benchmark.cpp

# Targets
all: cas_benchmark_lse cas_benchmark_llsc

cas_benchmark_lse: $(SRC)
	$(CXX) $(CXXFLAGS) -o $@ $<

cas_benchmark_llsc: $(SRC)
	$(CXX) $(CXXFLAGS) -mno-outline-atomics -o $@ $<

clean:
	rm -f cas_benchmark_lse cas_benchmark_llsc
