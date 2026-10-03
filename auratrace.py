#!/usr/bin/env python3
"""
AuraTrace-IR: Advanced Cross-Platform DFIR Engine with Interactive AI
"""

import os
import sys
import platform
import subprocess
import json
import datetime
import hashlib
import argparse
import urllib.request

VERSION = "2.0.0"
DEFAULT_AI_URL = os.getenv("AIAURA_API_URL", "https://aiaura.me/api/v1/analyze")
DEFAULT_AI_KEY = os.getenv("AIAURA_API_KEY", "")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def execute(cmd: str) -> str:
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=45)
        return res.stdout.strip()
    except Exception as e:
        return f"[ERROR executing {cmd}]: {str(e)}"

def collect_linux() -> dict:
    return {
        "network_sockets": execute("ss -tupna"),
        "promiscuous_interfaces": execute("ip link | grep PROMISC"),
        "process_tree": execute("ps auxf"),
        "deleted_running_files": execute("lsof +L1 2>/dev/null | grep -i deleted"),
        "kernel_modules": execute("lsmod | head -n 30"),
        "persistence": execute("find /etc/cron* /var/spool/cron -type f -exec ls -la {} + 2>/dev/null"),
        "hidden_root_users": execute("awk -F: '$3 == 0 {print $1}' /etc/passwd"),
        "suid_bins": execute("find / -perm -4000 -type f 2>/dev/null | head -n 50"),
        "auth_logs": execute("tail -n 200 /var/log/auth.log 2>/dev/null || journalctl -u ssh -n 200 --no-pager"),
        "bash_history": execute("cat ~/.bash_history 2>/dev/null | tail -n 50")
    }

def collect_windows() -> dict:
    return {
        "processes": execute("powershell -NoProfile -Command \"Get-WmiObject Win32_Process | Select-Object ProcessId,ParentProcessId,Name,CommandLine | ConvertTo-Json -Depth 2\""),
        "network": execute("powershell -NoProfile -Command \"Get-NetTCPConnection | Where-Object State -eq 'Established' | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess | ConvertTo-Json\""),
        "dns_cache": execute("ipconfig /displaydns"),
        "smb_sessions": execute("powershell -NoProfile -Command \"Get-SmbSession | ConvertTo-Json\""),
        "autoruns": execute("powershell -NoProfile -Command \"Get-ItemProperty 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue | ConvertTo-Json\""),
        "security_events": execute("powershell -NoProfile -Command \"Get-WinEvent -FilterHashtable @{LogName='Security'; Id=4624,4625,7045} -MaxEvents 50 -ErrorAction SilentlyContinue | Select-Object TimeCreated,Id,Message | ConvertTo-Json\""),
        "powershell_payloads": execute("powershell -NoProfile -Command \"Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational'; Id=4104} -MaxEvents 10 -ErrorAction SilentlyContinue | Select-Object TimeCreated,Message | ConvertTo-Json\"")
    }

def call_ai(messages: list, api_url: str, api_key: str) -> str:
    payload = {"model": "aura-forensics-v1", "messages": messages, "temperature": 0.2}
    req = urllib.request.Request(api_url, data=json.dumps(payload).encode("utf-8"), headers={
        "Content-Type": "application/json", "Authorization": f"Bearer {api_key}"
    })
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("choices", [{}])[0].get("message", {}).get("content", str(data))
    except Exception as e:
        return f"[AIAura API Error]: {str(e)}"

def interactive_chat(manifest_path: str):
    if not DEFAULT_AI_KEY:
        print("[-] Error: AIAURA_API_KEY environment variable is required for chat.")
        sys.exit(1)
    
    with open(manifest_path, "r") as f:
        manifest = f.read()

    print(f"[*] Loaded forensic payload: {manifest_path}")
    print("[*] Entering interactive AI DFIR session. Type 'exit' to quit.\n")
    
    messages = [
        {"role": "system", "content": "You are an elite DFIR analyst. You have been provided a JSON triage dump from a compromised machine. Answer the user's questions about this specific evidence. Be highly technical."},
        {"role": "user", "content": f"Here is the system triage dump:\n{manifest}\n\nReview this data and stand by for questions."}
    ]

    while True:
        try:
            user_input = input("\033[96mAuraTrace-IR>\033[0m ")
            if user_input.lower() in ['exit', 'quit']: break
            if not user_input.strip(): continue

            messages.append({"role": "user", "content": user_input})
            response = call_ai(messages, DEFAULT_AI_URL, DEFAULT_AI_KEY)
            print(f"\n\033[92mAI Copilot:\033[0m\n{response}\n")
            messages.append({"role": "assistant", "content": response})
        except KeyboardInterrupt:
            break

def isolate_host(analyst_ip: str, os_type: str):
    print(f"[*] Enforcing network containment. Whitelisting {analyst_ip}...")
    if os_type == "linux":
        cmds = [
            "iptables -F", "iptables -P INPUT DROP", "iptables -P FORWARD DROP", "iptables -P OUTPUT DROP",
            "iptables -A INPUT -i lo -j ACCEPT", "iptables -A OUTPUT -o lo -j ACCEPT",
            f"iptables -A INPUT -s {analyst_ip} -j ACCEPT", f"iptables -A OUTPUT -d {analyst_ip} -j ACCEPT"
        ]
    else:
        cmds = [
            "netsh advfirewall set allprofiles firewallpolicy blockinbound,blockoutbound",
            f"netsh advfirewall firewall add rule name=\"Aura_In\" dir=in action=allow remoteip={analyst_ip}",
            f"netsh advfirewall firewall add rule name=\"Aura_Out\" dir=out action=allow remoteip={analyst_ip}"
        ]
    for cmd in cmds:
        execute(cmd)
    print("[+] Host isolated successfully.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ai", action="store_true", help="Generate automated AI briefing")
    parser.add_argument("--chat", type=str, metavar="FILE", help="Enter interactive chat with a saved triage JSON")
    parser.add_argument("--isolate", action="store_true", help="Isolate host from network")
    parser.add_argument("--analyst-ip", default="127.0.0.1", help="Analyst IP to whitelist")
    args = parser.parse_args()

    if args.chat:
        interactive_chat(args.chat)
        return

    os_type = platform.system().lower()
    hostname = platform.node()
    
    print(f"[*] Starting Elite AuraTrace-IR Collection on {hostname} ({os_type})...")
    manifest = {
        "metadata": {"engine": f"AuraTrace-IR v{VERSION}", "timestamp": datetime.datetime.utcnow().isoformat() + "Z", "hostname": hostname},
        "artifacts": collect_linux() if os_type == "linux" else collect_windows()
    }

    manifest_bytes = json.dumps(manifest).encode("utf-8")
    manifest["metadata"]["sha256"] = sha256_bytes(manifest_bytes)
    
    filename = f"triage_{hostname}_{int(datetime.datetime.utcnow().timestamp())}.json"
    with open(filename, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"[+] Evidence acquired: {filename} (SHA256: {manifest['metadata']['sha256']})")

    if args.ai and DEFAULT_AI_KEY:
        print("[*] Generating Comprehensive AI Forensic Briefing...")
        prompt = "You are an elite DFIR investigator. Analyze this triage dump. Output exactly: 1. THREAT VERDICT 2. INTRUSION VECTOR 3. EXTRACTED IOCs (IPs, Hashes, Malicious PIDs) 4. MITRE ATT&CK MAPPING 5. REMEDIATION."
        report = call_ai([{"role": "system", "content": prompt}, {"role": "user", "content": json.dumps(manifest)}], DEFAULT_AI_URL, DEFAULT_AI_KEY)
        report_file = filename.replace(".json", "_REPORT.md")
        with open(report_file, "w") as f:
            f.write(report)
        print(f"[+] Briefing generated: {report_file}")

    if args.isolate:
        isolate_host(args.analyst_ip, os_type)

if __name__ == "__main__":
    main()
