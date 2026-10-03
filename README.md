# AuraTrace-IR
# 🛡️ AuraTrace-IR: Elite Live-Response & AI Forensics

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-brightgreen.svg)](#)
[![Platform: Linux | Windows](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows-lightgrey.svg)](#)
[![AI Engine](https://img.shields.io/badge/AI_Powered-aiaura.me-purple.svg)](https://aiaura.me)
[![Build Status](https://img.shields.io/github/actions/workflow/status/YOUR_GITHUB_USERNAME/AuraTrace-IR/build.yml?branch=main)](https://github.com/YOUR_GITHUB_USERNAME/AuraTrace-IR/actions)

**AuraTrace-IR** is an elite, zero-dependency digital forensics and incident response (DFIR) triage engine. Built for rapid deployment on compromised infrastructure, it hunts for fileless malware, extracts volatile indicators of compromise (IoCs), and leverages the AIAura engine to provide both automated executive reports and a **live interactive forensic chat interface**.

---

## 🔬 Elite Forensic Capabilities

When adversaries delete payloads from disk and hide in memory, traditional file scanners fail. AuraTrace-IR captures the live state of the machine before the attacker can react:

*   **Linux Deep Triage:** Uncovers deleted-but-running binaries (`lsof +L1`), hidden root users, anomalous promiscuous network interfaces, and unlinked kernel modules.
*   **Windows Telemetry:** Extracts decoded PowerShell Script Blocks (Event 4104), DNS resolver caches, rogue WMI persistence, and active SMB shares.
*   **Cryptographic Sealing:** Automatically hashes all extracted evidence (SHA-256) to maintain a strict chain of custody.
*   **Zero-Dependency:** Core collectors run natively on bare-metal systems without requiring third-party library installations.

## ⚙️ Architecture Workflow

```text
[ Compromised Target Host ] 
 ├── 1. Volatile Triage (RAM pointers, Sockets, Processes, Persistence)
 ├── 2. Hash & Seal (SHA-256 Chain of Custody manifest)
 ├── 3. AI Copilot Ingestion (aiaura.me/api/v1/analyze)
 └── 4. Automated Containment (iptables / netsh host isolation)
