#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <sched.h>
#include <unistd.h>
#include <cstring>

#ifndef FL
using counter_t = uint64_t;
#else
using counter_t = double;
#endif

uint64_t kernel(uint64_t iters, counter_t* mem, bool weak, int memorder) {
    uint64_t attempts = 0;
    do {
        counter_t expected = *mem, desired;
        do {
            desired = expected + 1;
            attempts++;
        } while (!__atomic_compare_exchange(mem, &expected, &desired, weak, memorder, memorder));
    } while (--iters);
    return attempts;
}

void bind_thread_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    int rc = sched_setaffinity(0, sizeof(cpuset), &cpuset);
    if (rc != 0) {
        std::cerr << "Failed to bind to core " << core_id << ": " << std::strerror(errno) << "\n";
    }
}

int main() {
    const int num_threads_list[] = {1, 2, 4, 8, 16, 32, 48, 64, 80, 96, 112, 128};
    const uint64_t iterations = 100000;

    for (int num_threads : num_threads_list) {
        counter_t counter = 0;
        std::vector<uint64_t> attempt_counts(num_threads);
        std::vector<std::thread> threads;
        std::atomic<bool> start_flag{false};

        auto t1 = std::chrono::high_resolution_clock::now();

        for (int t = 0; t < num_threads; ++t) {
            threads.emplace_back([&, t]() {
                bind_thread_to_core(t);

                while (!start_flag.load(std::memory_order_acquire)) {
                    // busy wait
                }

                attempt_counts[t] = kernel(iterations, &counter, false, __ATOMIC_RELAXED);
            });
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        auto start = std::chrono::high_resolution_clock::now();
        start_flag.store(true, std::memory_order_release);

        for (auto& th : threads) th.join();
        auto end = std::chrono::high_resolution_clock::now();

        double total_time = std::chrono::duration<double>(end - start).count();
        uint64_t total_attempts = 0;
        for (auto a : attempt_counts) total_attempts += a;

        std::cout << "Threads: " << num_threads
                  << ", Time: " << total_time << " s"
                  << ", Avg attempts per op: " << (double)total_attempts / (num_threads * iterations)
                  << std::endl;
    }

    return 0;
}
