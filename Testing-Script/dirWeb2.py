import requests
from urllib.parse import urljoin
import concurrent.futures
import time


def check_directory(base_url, directory):
    url = urljoin(base_url, directory)
    response = requests.get(url)
    if response.status_code == 200:
        print(f"[+] Directory found: {url}")
        return url
    return None


def loader():
    load_ico = 0
    loaderMask = False

    while True:
        load_ico += 1
        if load_ico == 4:
            continue  # jump ke baris berikutnya
        if load_ico == 0:
            print('\rloading |', end='')
        elif load_ico == 1:
            print('\rloading /', end='')
        elif load_ico == 2:
            print('\rloading -', end='')
        elif load_ico == 3:
            print('\rloading \\', end='')
        else:
            print('\rloading |', end='')

        time.sleep(0.2)

        if loaderMask:
            print("\r", end='')
            loaderMask = False
    

        

def scan_directories(base_url, directories, max_threads=10):
    found_directories = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_dir = {executor.submit(
            check_directory, base_url, directory): directory for directory in directories}
        for future in concurrent.futures.as_completed(future_to_dir):
            result = future.result()
            if result:
                found_directories.append(result)

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


if base_url == 12 :
    print("Echo1")
elif(base_url == 20) :
    print("Echo2")
if __name__ == "__main__":
    base_url = input("Masukkan URL website yang ingin di-scan: ")

    directories = read_directories_from_file('dirWebList.txt')

    print(f"Scanning direktori pada {base_url}...")
    found_dirs = scan_directories(base_url, directories)

    print("\nHasil scan:")
    for dir in found_dirs:
        print(dir)

    print(f"\nTotal direktori ditemukan: {len(found_dirs)}")
