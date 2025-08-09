import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket
import os
import tempfile
import time
import re
import ctypes
import threading

def validate_input(user_input):
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    domain_pattern = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    if ip_pattern.match(user_input):
        parts = user_input.split('.')
        return all(0 <= int(part) <= 255 for part in parts)
    return domain_pattern.match(user_input) is not None

def check_admin_privileges():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except AttributeError:
        return os.getuid() == 0

def get_user_input():
    while True:
        ip = input("Enter IP address or domain to scan: ").strip()
        if validate_input(ip):
            return ip
        print("Invalid format. Enter valid IP (e.g., 192.168.1.1) or domain (e.g., google.com)")

def resolve_host(host):
    try:
        resolved_ip = socket.gethostbyname(host)
        if host != resolved_ip:
            print(f"Domain {host} resolved to IP: {resolved_ip}")
        else:
            print(f"Scanning IP: {resolved_ip}")
        return resolved_ip
    except Exception as e:
        print(f"Could not resolve host: {host}. Error: {e}")
        exit(1)

def get_port_ranges():
    print("\nSelect scan type:")
    print("1. Fast (common ports: 1-1000)")
    print("2. Full (ports 1-30000)")
    print("3. Custom")
    
    choice = input("Option (1-3): ").strip()
    
    if choice == "1":
        return [(1, 1000)]
    elif choice == "2":
        return [(1, 5000), (5001, 10000), (10001, 15000), (15001, 20000), (20001, 25000), (25001, 30000)]
    elif choice == "3":
        start_port = int(input("Start port: "))
        end_port = int(input("End port: "))
        chunk_size = min(5000, (end_port - start_port) // 6 + 1)
        return [(i, min(i + chunk_size - 1, end_port)) for i in range(start_port, end_port + 1, chunk_size)]
    else:
        print("Invalid option, using fast scan...")
        return [(1, 1000)]

def setup_logging(resolved_ip):
    logs_dir = os.path.join("src", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    log_filename = f"nmap_scan_{resolved_ip.replace('.', '_')}_{timestamp}.txt"
    log_path = os.path.join(logs_dir, log_filename)
    print(f"Saving logs to: {log_path}")
    return log_path

def run_nmap(start, end, resolved_ip, use_syn):
    ports = f"{start}-{end}"
    scan_type = "-sS" if use_syn else "-sT"
    
    print(f"\nScanning ports {ports}...")
    
    try:
        result = subprocess.run(
            ["nmap", scan_type, "-sV", "-Pn", "-T4", "--max-retries", "2", "-p", ports, resolved_ip],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return f"--- ERROR in ports {ports} ---\n{result.stderr}\n"
        
        return f"--- Result for ports {ports} ---\n{result.stdout}\n"
    
    except subprocess.TimeoutExpired:
        return f"--- TIMEOUT in ports {ports} ---\nScan exceeded time limit\n"
    except Exception as e:
        return f"--- ERROR in ports {ports} ---\nError: {str(e)}\n"

def show_timer(start_time, completed_count, total_scans, stop_timer):
    while not stop_timer[0]:
        elapsed = time.time() - start_time
        mins, secs = divmod(int(elapsed), 60)
        print(f"\rElapsed time: {mins:02d}:{secs:02d} | Completed: {completed_count[0]}/{total_scans}", end="", flush=True)
        time.sleep(1)

def main():
    print("=== Parallel Nmap Port Scanner ===")
    
    if not check_admin_privileges():
        print("WARNING: Running as administrator recommended for SYN scans (-sS)")
        use_syn = input("Continue with SYN scan? (y/n): ").lower().strip() == 'y'
    else:
        use_syn = True
    
    ip = get_user_input()
    resolved_ip = resolve_host(ip)
    port_ranges = get_port_ranges()
    log_path = setup_logging(resolved_ip)
    
    start_time = time.time()
    max_workers = min(len(port_ranges), 6)
    total_scans = len(port_ranges)
    completed_count = [0]
    stop_timer = [False]
    
    print(f"Starting scan with {max_workers} parallel threads...")
    
    timer_thread = threading.Thread(target=show_timer, args=(start_time, completed_count, total_scans, stop_timer), daemon=True)
    timer_thread.start()
    
    with open(log_path, 'w', encoding='utf-8') as log_file:
        log_file.write(f"Scan of {ip} ({resolved_ip})\n")
        log_file.write(f"Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Scan type: {'SYN' if use_syn else 'TCP Connect'}\n")
        log_file.write("=" * 50 + "\n\n")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(run_nmap, start, end, resolved_ip, use_syn): (start, end) for start, end in port_ranges}
        
        for future in as_completed(futures):
            result = future.result()
            print(f"\n{result}")
            log_file.write(result)
            log_file.flush()
            completed_count[0] += 1
            
            remaining = total_scans - completed_count[0]
            elapsed = time.time() - start_time
            if completed_count[0] > 0:
                avg_time_per_scan = elapsed / completed_count[0]
                estimated_remaining = avg_time_per_scan * remaining
                mins, secs = divmod(int(estimated_remaining), 60)
                if remaining > 0:
                    print(f"Estimated remaining time: {mins:02d}:{secs:02d}")
    
    stop_timer[0] = True
    elapsed_total = time.time() - start_time
    mins, secs = divmod(int(elapsed_total), 60)
    
    print(f"\nScan completed in: {mins:02d}:{secs:02d}")
    print(f"Logs saved to: {log_path}")

if __name__ == "__main__":
    main()