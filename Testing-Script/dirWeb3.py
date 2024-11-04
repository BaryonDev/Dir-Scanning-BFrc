import requests
from urllib.parse import urljoin
import concurrent.futures
import sys
import time


def check_directory(base_url, directory):
    url = urljoin(base_url, directory)
    response = requests.get(url)
    if response.status_code == 200:
        print(f"[+] Directory found: {url}")
        return url
    return None


done = 'false'


def animate():
    while done == 'false':
        sys.stdout.write('\rloading |')
        time.sleep(0.1)
        sys.stdout.write('\rloading /')
        time.sleep(0.1)
        sys.stdout.write('\rloading -')
        time.sleep(0.1)
        sys.stdout.write('\rloading \\')
        time.sleep(0.1)
        sys.stdout.write('\rloading |')
        time.sleep(0.1)
        sys.stdout.write('\rloading /')
        time.sleep(0.1)
        sys.stdout.write('\rloading -')
        time.sleep(0.1)
        sys.stdout.write('\rloading \\')
        time.sleep(0.1)
        sys.stdout.write('\rloading |')
        time.sleep(0.1)
        sys.stdout.write('\rloading /')
        time.sleep(0.1)
        sys.stdout.write('\rloading -')
        time.sleep(0.1)
        sys.stdout.write('\rloading \\')
        time.sleep(0.1)
        sys.stdout.write('\rloading |')
        time.sleep(0.1)
        sys.stdout.write('\rloading /')
        time.sleep(0.1)
        sys.stdout.write('\rloading -')
        time.sleep(0.1)
        sys.stdout.write('\rloading \\')
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


def update_progress(current, total):
    percentage = (current / total) * 100
    print(f"\rDir scanned {current}/{total} at {percentage:.1f}%", end='')


def scan_directories(base_url, directories, max_threads=20):
    found_directories = []
    total_directories = len(directories)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_dir = {executor.submit(
            check_directory, base_url, directory): directory for directory in directories}

        for index, future in enumerate(concurrent.futures.as_completed(future_to_dir)):
            result = future.result()
            if result:
                found_directories.append(result)

            if (index + 1) % 1 == 0 or index + 1 == total_directories:
                update_progress(index + 1, total_directories)

    print()
    return found_directories


def read_directories_from_file(filename):
    try:
        with open(filename, 'r') as file:
            directories = [line.strip()
                           for line in file.readlines() if line.strip()]
            return directories
    except FileNotFoundError:
        print(f"File {filename} tidak ditemukan.")
        return []


if __name__ == "__main__":
    base_url = input("Masukkan URL website yang ingin di-scan: ")

    directories = read_directories_from_file('dirWebList.txt')

    print(f"Scanning direktori pada {base_url}...")
    found_dirs = scan_directories(base_url, directories)

    print("\nHasil scan:")
    for dir in found_dirs:
        print(dir)

    print(f"\nTotal direktori ditemukan: {len(found_dirs)}")
