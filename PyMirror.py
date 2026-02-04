#!/usr/bin/env python3
# ---------------------------------------------------
# PyMirror Installer v2.2 (Updated & Professional)
# High-Speed Python Package Installer (Mirrors)
# Auto-install missing modules
# Detect all pip executables and corresponding Python interpreters
# Enhanced error handling and user experience
# ---------------------------------------------------

import os
import sys
import socket
import subprocess
from typing import Optional, Tuple

try:
    from colorama import init, Fore, Style
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import init, Fore, Style

init(autoreset=True)

MIRRORS = {
    "Runflare": "https://mirror-pypi.runflare.com/simple/",
    "TUNA": "https://pypi.tuna.tsinghua.edu.cn/simple/",
    "Aliyun": "https://mirrors.aliyun.com/pypi/simple/",
    "USTC": "https://pypi.mirrors.ustc.edu.cn/simple/",
    "Huawei": "https://repo.huaweicloud.com/repository/pypi/simple/",
    "Douban": "http://pypi.douban.com/simple/",
    "SDUT": "http://pypi.sdutlinux.org/simple/"
}

BANNER = f"""
┌──────────────────────────────────────────────────────────┐
│                  PyMirror Installer v2.2                 │
│        High-Speed Python Package Installer (Mirrors)     │
│     Coded by Mohammad Taha Hatami | Updated by GPT-5     │
└──────────────────────────────────────────────────────────┘
"""

# -------------------------
# Utility functions
# -------------------------
def check_internet(timeout: int = 3) -> bool:
    print(f"{Fore.CYAN}[i]{Style.RESET_ALL} Checking internet connection ...")
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} Internet connection OK.\n")
        return True
    except Exception:
        print(f"{Fore.RED}[✗]{Style.RESET_ALL} No internet connection!\n")
        return False

def find_all_pip() -> list[Tuple[str, Optional[str]]]:
    paths = os.environ.get("PATH", "").split(os.pathsep)
    pip_list = []
    for path in paths:
        if not os.path.isdir(path):
            continue
        for f in os.listdir(path):
            full = os.path.join(path, f)
            if f.lower().startswith("pip") and os.access(full, os.X_OK):
                pip_list.append((full, None))
    pip_list.append((f"{sys.executable} -m pip", sys.executable))
    return pip_list

def find_pip() -> Tuple[str, str]:
    print(f"{Fore.CYAN}[i]{Style.RESET_ALL} Searching for pip executables in PATH ...")
    for pip_cmd, interpreter in find_all_pip():
        try:
            output = subprocess.check_output(pip_cmd.split() + ["--version"], text=True)
            if "from" in output:
                interpreter = output.strip().split("from")[-1].strip()
            print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} Detected pip: {Fore.YELLOW}{pip_cmd}{Style.RESET_ALL} | Python: {Fore.GREEN}{interpreter or 'unknown'}{Style.RESET_ALL}")
            return pip_cmd, interpreter or sys.executable
        except Exception:
            continue

    # Ask user manually
    while True:
        user_cmd = input(f"{Fore.YELLOW}Enter pip command → {Style.RESET_ALL}").strip()
        try:
            subprocess.check_output(user_cmd.split() + ["--version"], text=True)
            interpreter = sys.executable
            if user_cmd.startswith("python") and "-m pip" in user_cmd:
                interpreter = user_cmd.split()[0]
            return user_cmd, interpreter
        except Exception:
            print(f"{Fore.RED}[!] Invalid pip command! Try again.{Style.RESET_ALL}")

def install_package(pip_cmd: str, package: str, mirror_name: str) -> None:
    index_url = MIRRORS[mirror_name]
    trusted_host = index_url.split("//")[1].split("/")[0]
    print(f"\n{Fore.CYAN}[i]{Style.RESET_ALL} Installing {Fore.YELLOW}{package}{Style.RESET_ALL} via mirror: {Fore.GREEN}{mirror_name}{Style.RESET_ALL}")
    cmd = pip_cmd.split() + ["install", "--trusted-host", trusted_host, "-i", index_url, package]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode == 0:
        print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} Successfully installed {package}.\n")
    else:
        print(f"{Fore.RED}[✗]{Style.RESET_ALL} Failed to install {package}.\n")

def auto_import(pip_cmd: str, mirror_name: str, module_name: str):
    try:
        return __import__(module_name)
    except ImportError:
        print(f"{Fore.RED}[!] Module '{module_name}' not found!{Style.RESET_ALL}")
        if not check_internet():
            print(f"{Fore.RED}[!] Cannot download '{module_name}' because internet is offline.{Style.RESET_ALL}")
            sys.exit(1)
        install_package(pip_cmd, module_name, mirror_name)
        try:
            return __import__(module_name)
        except ImportError:
            print(f"{Fore.RED}[✗]{Style.RESET_ALL} Failed to import '{module_name}' after installation.")
            sys.exit(1)

# -------------------------
# Main
# -------------------------
def main():
    print(BANNER)
    pip_cmd, python_interpreter = find_pip()
    print(f"{Fore.CYAN}[i]{Style.RESET_ALL} Using Python interpreter: {Fore.GREEN}{python_interpreter}{Style.RESET_ALL}\n")

    # Select mirror
    print(f"{Fore.CYAN}Available Mirrors:{Style.RESET_ALL}")
    mirrors = list(MIRRORS.keys())
    for i, m in enumerate(mirrors, 1):
        print(f"{Fore.YELLOW}{i}. {m}{Style.RESET_ALL}")
    while True:
        try:
            idx = int(input(f"{Fore.CYAN}Select mirror number → {Style.RESET_ALL}"))
            if 1 <= idx <= len(mirrors):
                mirror_name = mirrors[idx - 1]
                break
        except ValueError:
            pass
        print(f"{Fore.RED}[!] Invalid choice. Try again.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}[✓]{Style.RESET_ALL} Selected mirror: {Fore.YELLOW}{mirror_name}{Style.RESET_ALL}\n")

    print(f"{Fore.CYAN}Enter package names to install. Type 'exit' to quit.\n{Style.RESET_ALL}")
    while True:
        package = input(f"{Fore.CYAN}Package → {Style.RESET_ALL}").strip()
        if package.lower() in ("exit", "quit"):
            print(f"{Fore.RED}[!] Exiting PyMirror Installer...{Style.RESET_ALL}")
            break
        if package:
            install_package(pip_cmd, package, mirror_name)

if __name__ == "__main__":
    main()
