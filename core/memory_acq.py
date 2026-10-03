#!/usr/bin/env python3
"""
AuraTrace-IR: Raw Memory Dump Orchestrator
"""
import os
import platform
import subprocess
import datetime

def acquire_memory():
    os_type = platform.system().lower()
    ts = int(datetime.datetime.utcnow().timestamp())
    output_file = f"memdump_{ts}.raw"

    print(f"[*] Initiating raw memory capture for {os_type}...")

    if os_type == "linux":
        if not os.path.exists("./lime.ko"):
            print("[-] FATAL: lime.ko missing. You must compile the LiME module for this specific Linux kernel version before dumping RAM.")
            return

        print("[+] Loading LiME Kernel Module...")
        cmd = f"insmod ./lime.ko \"path={output_file} format=lime\""
        if subprocess.run(cmd, shell=True).returncode == 0:
            print(f"[+] Memory secured: {output_file}. Removing module from kernel space...")
            subprocess.run("rmmod lime", shell=True)
        else:
            print("[-] Capture failed. Verify SecureBoot is disabled or module is signed.")

    elif os_type == "windows":
        if not os.path.exists(".\\winpmem.exe"):
            print("[-] FATAL: winpmem.exe missing. Download WinPmem from the Rekall project.")
            return

        print("[+] Engaging WinPmem driver...")
        cmd = f".\\winpmem.exe -o {output_file}"
        if subprocess.run(cmd, shell=True).returncode == 0:
            print(f"[+] Memory secured: {output_file}")
        else:
            print("[-] Capture failed. Verify Administrator privileges.")

if __name__ == "__main__":
    acquire_memory()
