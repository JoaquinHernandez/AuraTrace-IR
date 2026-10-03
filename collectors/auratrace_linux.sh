#!/usr/bin/env bash
# AuraTrace-IR: Elite Standalone Linux Native Collector

set -euo pipefail
if [[ $EUID -ne 0 ]]; then echo "[-] FATAL: Must run as root to access memory pointers and raw sockets."; exit 1; fi

TIMESTAMP=$(date -u +%Y%m%d_%H%M%SZ)
HOST=$(hostname)
DIR="/tmp/auratrace_${HOST}_${TIMESTAMP}"
mkdir -p "${DIR}"

echo "[*] Harvesting Volatile State & Fileless Indicators..."
ss -tupna > "${DIR}/network.txt" 2>/dev/null || netstat -tupna > "${DIR}/network.txt"
ip link | grep PROMISC > "${DIR}/promiscuous_interfaces.txt" || true
ps auxf > "${DIR}/processes.txt"
lsof +L1 2>/dev/null | grep -i deleted > "${DIR}/deleted_running_binaries.txt" || true
lsmod > "${DIR}/loaded_kernel_modules.txt"

echo "[*] Ripping Persistence Mechanisms & Logs..."
find /etc/cron* /var/spool/cron -type f -exec ls -la {} + > "${DIR}/crons.txt" 2>/dev/null || true
find / -perm -4000 -type f > "${DIR}/suid_bins.txt" 2>/dev/null || true
awk -F: '$3 == 0 {print $1}' /etc/passwd > "${DIR}/root_users.txt"
journalctl -u ssh -n 2000 --no-pager > "${DIR}/ssh_logs.txt" 2>/dev/null || true
dmesg -T > "${DIR}/kernel_dmesg.txt" 2>/dev/null || true
cp ~/.bash_history "${DIR}/root_bash_history.txt" 2>/dev/null || true

echo "[*] Cryptographically Sealing Artifacts..."
cd "${DIR}"
sha256sum * > SHA256SUMS.txt
cd /tmp
tar -czf "auratrace_${HOST}_${TIMESTAMP}.tar.gz" -C "/tmp" "auratrace_${HOST}_${TIMESTAMP}"
rm -rf "${DIR}"

echo "[+] Chain of Custody Sealed: /tmp/auratrace_${HOST}_${TIMESTAMP}.tar.gz"
