import sys
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def _ts():
    return datetime.now().strftime("%H:%M:%S")

def success(msg):
    print(f"{Fore.GREEN}  [✓] {msg}{Style.RESET_ALL}")

def info(msg):
    print(f"{Fore.CYAN}  [→] {msg}{Style.RESET_ALL}")

def warning(msg):
    print(f"{Fore.YELLOW}  [⚠] {msg}{Style.RESET_ALL}")

def error(msg):
    print(f"{Fore.RED}  [✗] {msg}{Style.RESET_ALL}")

def step(icon, msg):
    print(f"{Fore.CYAN}  [{icon}] {msg}{Style.RESET_ALL}")

def log(level, msg):
    ts = _ts()
    if level == "success":
        print(f"{Fore.GREEN}  [{ts}] ✓ {msg}{Style.RESET_ALL}")
    elif level == "info":
        print(f"{Fore.CYAN}  [{ts}] → {msg}{Style.RESET_ALL}")
    elif level == "warning":
        print(f"{Fore.YELLOW}  [{ts}] ⚠ {msg}{Style.RESET_ALL}")
    elif level == "error":
        print(f"{Fore.RED}  [{ts}] ✗ {msg}{Style.RESET_ALL}")

def divider():
    print(f"{Fore.WHITE}  {'─' * 60}{Style.RESET_ALL}")

def header(text):
    print(f"\n{Fore.CYAN}  {text}{Style.RESET_ALL}")
