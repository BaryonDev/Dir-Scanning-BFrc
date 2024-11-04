import requests
from urllib.parse import urljoin
import concurrent.futures
import signal
import sys

found_directories = []
total_directories = 0
scanned_count = 0

def check_directory(base_url, directory):
    url = urljoin(base_url, directory)
    response = requests.get(url)
    if response.status_code == 200:
        print(f"[+] Directory found: {url}")
        return url
    return None

        
def update_progress(current, total):
    
    percentage = (current / total) * 100
    print(f"\rDir scanned {current}/{total} at {percentage:.1f}%", end='')


def scan_directories(base_url, directories, max_threads=100):
    global scanned_count
    global found_directories
    total = len(directories)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_dir = {executor.submit(
            check_directory, base_url, directory): directory for directory in directories}

        try:
            for index, future in enumerate(concurrent.futures.as_completed(future_to_dir)):
                result = future.result()
                if result:
                    found_directories.append(result)

                scanned_count += 1
                update_progress(scanned_count, total)
        except KeyboardInterrupt:
            print("\nScanning interrupted.")
            executor.shutdown(wait=False)
            return

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


def signal_handler(sig, frame):

    print("\nScanning interrupted.")
    print(f"Total directories scanned: {scanned_count}")
    print(f"Directories found: {len(found_directories)}")

    with open('found_directories.txt', 'w') as f:
        for directory in found_directories:
            f.write(f"{directory}\n")

    print("Found directories saved to 'found_directories.txt'.")
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)

    base_url = input("Masukkan URL website yang ingin di-scan: ")

    directories = read_directories_from_file('dirWebList.txt')
    total_directories = len(directories)

    print(f"Scanning direktori pada {base_url}...")
    found_dirs = scan_directories(base_url, directories)

    print("\nHasil scan:")
    for dir in found_dirs:
        print(dir)

    print(f"\nTotal direktori ditemukan: {len(found_dirs)}")

    with open('found_directories.txt', 'w') as f:
        for directory in found_dirs:
            f.write(f"{directory}\n")

    print("Found directories saved to 'found_directories.txt'.")
    sys.exit()
