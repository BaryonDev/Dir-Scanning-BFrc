import asyncio
import aiohttp
from urllib.parse import urljoin
import signal
import sys
import time
import logging
import multiprocessing
import os
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

found_directories = multiprocessing.Manager().list()
scanned_count = multiprocessing.Value('i', 0)
total_directories = multiprocessing.Value('i', 0)
interrupt_event = multiprocessing.Event()

def read_directories_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"File {filename} tidak ditemukan.")
        return []
    except Exception as e:
        logging.error(f"Error saat membaca file: {e}")
        return []

def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

async def check_directory(session, base_url, directory, semaphore, pbar):
    if interrupt_event.is_set():
        return
    url = urljoin(base_url, directory)
    async with semaphore:
        try:
            async with session.get(url, timeout=5, ssl=False) as response:
                if response.status == 200:
                    logging.info(f"[+] Directory found: {url}")
                    found_directories.append(url)
        except asyncio.TimeoutError:
            pass
        except Exception:
            pass
    with scanned_count.get_lock():
        scanned_count.value += 1
    pbar.update(1)

async def scan_directories(base_url, directories, max_concurrent=100):
    semaphore = asyncio.Semaphore(max_concurrent)
    connector = aiohttp.TCPConnector(limit=max_concurrent, ssl=False, ttl_dns_cache=300)
    async with aiohttp.ClientSession(connector=connector) as session:
        with tqdm(total=len(directories), desc="Scanning Progress", unit="dir") as pbar:
            tasks = [check_directory(session, base_url, directory, semaphore, pbar) for directory in directories]
            await asyncio.gather(*tasks, return_exceptions=True)

def worker(base_url, directories):
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(scan_directories(base_url, directories))
    except KeyboardInterrupt:
        logging.info("Worker process interrupted")
    except Exception as e:
        logging.error(f"Worker process error: {e}")

def signal_handler(signum, frame):
    logging.info("\nInterrupt received, stopping processes...")
    interrupt_event.set()

def save_results():
    logging.info("\nMenyimpan hasil yang sudah didapat...")
    with open('found_directories.txt', 'w') as f:
        for directory in found_directories:
            f.write(f"{directory}\n")
    logging.info(f"Total direktori ditemukan: {len(found_directories)}")
    logging.info(f"Total direktori di-scan: {scanned_count.value}/{total_directories.value}")
    logging.info("Found directories saved to 'found_directories.txt'.")

def main():
    original_sigint_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal_handler)
    
    base_url = input("Masukkan URL website yang ingin di-scan: ")
    directories = read_directories_from_file('dirWebList.txt')
    
    with total_directories.get_lock():
        total_directories.value = len(directories)
    
    logging.info(f"Total direktori yang akan di-scan: {total_directories.value}")
    
    num_processes = multiprocessing.cpu_count()
    split_directories = split_list(directories, num_processes)
    
    processes = []
    try:
        for i in range(num_processes):
            p = multiprocessing.Process(target=worker, args=(base_url, split_directories[i]))
            processes.append(p)
            p.start()
        
        while any(p.is_alive() for p in processes):
            if interrupt_event.is_set():
                break
            time.sleep(1)
    
    except KeyboardInterrupt:
        logging.info("Main process interrupted")
    finally:
        interrupt_event.set()
        for p in processes:
            p.join(timeout=5)
            if p.is_alive():
                p.terminate()
        
        save_results()
        
        signal.signal(signal.SIGINT, original_sigint_handler)

if __name__ == "__main__":
    main()