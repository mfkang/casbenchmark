import matplotlib.pyplot as plt
import numpy as np
import re
import sys
import os
import glob
import csv
from itertools import cycle
from collections import defaultdict, OrderedDict

def parse_output_file(filename):
    threads, times, avg_attempts = [], [], []
    pattern = r"Threads:\s+(\d+),\s+Time:\s+([\d\.eE\+\-]+)\s+s,\s+Avg attempts per op:\s+([\d\.eE\+\-]+)"

    with open(filename) as f:
        for line in f:
            match = re.search(pattern, line)
            if match:
                threads.append(int(match.group(1)))
                times.append(float(match.group(2)))
                avg_attempts.append(float(match.group(3)))

    return threads, times, avg_attempts

def collect_input_files(args):
    input_files = []
    for path in args:
        if os.path.isdir(path):
            input_files += glob.glob(os.path.join(path, "*"))
        elif os.path.isfile(path):
            input_files.append(path)
        else:
            print(f"Warning: {path} not found.")
    return sorted(input_files)

def get_base_name(filename):
    name = os.path.basename(filename)
    return os.path.splitext(name)[0] if '.' in name else name

def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_cas_scaling.py file1 [file2 ...] OR a directory")
        sys.exit(1)

    input_files = collect_input_files(sys.argv[1:])
    if not input_files:
        print("No valid input files found.")
        sys.exit(1)

    merged_data = defaultdict(OrderedDict)  # {thread: {label_time: x, label_attempts: y}}

    # Plot 1: Time
    plt.figure(figsize=(8, 6))
    colors = cycle(plt.cm.tab10.colors)
    markers = cycle(['o', 's', 'v', '^', '<', '>', 'D', 'p', '*', 'x'])
    all_threads_range = []

    for filename in input_files:
        label = get_base_name(filename)
        threads, times, attempts = parse_output_file(filename)
        color, marker = next(colors), next(markers)
        plt.loglog(threads, times, marker=marker, color=color, label=label)
        all_threads_range.extend(threads)

        # Fill merged data
        for t, time, att in zip(threads, times, attempts):
            merged_data[t][f"{label}_Time"] = time
            merged_data[t][f"{label}_Attempts"] = att

    base_threads = np.array([min(all_threads_range), max(all_threads_range)])
    plt.plot(base_threads, 0.01 * base_threads, '--', color='gray', label='y ∝ x')
    plt.plot(base_threads, 0.0001 * base_threads**2, '--', color='black', label='y ∝ x²')

    plt.xlabel('Number of Threads')
    plt.ylabel('Time per thread per increment (s)')
    plt.title('CAS Scaling: Time vs Threads')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig("cas_scaling_time_all.png")
    plt.show()

    # Plot 2: Attempts
    plt.figure(figsize=(8, 6))
    colors = cycle(plt.cm.tab10.colors)
    markers = cycle(['o', 's', 'v', '^', '<', '>', 'D', 'p', '*', 'x'])

    for filename in input_files:
        label = get_base_name(filename)
        threads, _, attempts = parse_output_file(filename)
        color, marker = next(colors), next(markers)
        plt.loglog(threads, attempts, marker=marker, color=color, label=label)

    plt.plot(base_threads, 0.5 * base_threads, '--', color='gray', label='y ∝ x')

    plt.xlabel('Number of Threads')
    plt.ylabel('Avg CAS attempts per increment')
    plt.title('CAS Scaling: Attempts vs Threads')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    plt.tight_layout()
    plt.savefig("cas_scaling_attempts_all.png")
    plt.show()

    # Write merged CSV
    output_csv = "all_result.csv"
    all_keys = sorted(merged_data.keys())
    all_columns = set()
    for d in merged_data.values():
        all_columns.update(d.keys())
    all_columns = sorted(all_columns)
    
    with open(output_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Threads"] + all_columns)
        for t in all_keys:
            row = [t]
            for col in all_columns:
                row.append(merged_data[t].get(col, ""))
            writer.writerow(row)

    print(f"[✓] Merged CSV saved to: {output_csv}")

if __name__ == "__main__":
    main()
