from flask import Flask, request, render_template, jsonify
import subprocess
import re
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
from io import BytesIO
import socket
import threading
import webbrowser

app = Flask(__name__)

# ============================================
# NSLOOKUP FUNCTION
# ============================================

def nslookup_detailed(domain, timeout=5, dns_server=None, log_callback=None):
    """
    Enhanced NSLookup function with multiple resolution methods
    """
    result = {
        'domain': domain,
        'ip_address': 'N/A',
        'status': 'ERROR',
        'dns_server': dns_server if dns_server else 'Default',
        'dns_server_ip': 'N/A',
        'answer_type': 'N/A',
        'response_time': 0,
        'all_ips': []
    }
    
    try:
        start_time = time.time()
        
        # Build command based on DNS server choice
        if dns_server and dns_server != 'default':
            cmd = ['nslookup', domain, dns_server]
        else:
            cmd = ['nslookup', domain]
        
        # Execute nslookup
        process = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=timeout, 
            encoding='utf-8', 
            errors='ignore'
        )
        
        end_time = time.time()
        result['response_time'] = round((end_time - start_time) * 1000, 2)
        output = process.stdout
        
        # Check if domain not found
        if "can't find" in output.lower() or "nxdomain" in output.lower():
            result['status'] = 'NOT_FOUND'
            if log_callback:
                log_callback(f"❌ {domain} -> NOT_FOUND", "error")
            return result
        
        # Extract DNS server from response
        server_match = re.search(r'Server:\s+(.+?)(?:\r?\n|$)', output, re.IGNORECASE)
        if server_match:
            result['dns_server'] = server_match.group(1).strip()
        
        # Extract DNS server IP
        server_ip_match = re.search(r'Address:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
        if server_ip_match:
            result['dns_server_ip'] = server_ip_match.group(1)
        
        # Check answer type
        if "Non-authoritative answer" in output:
            result['answer_type'] = 'Non-authoritative'
        elif "Authoritative answer" in output:
            result['answer_type'] = 'Authoritative'
        
        # METHOD 1: Extract IPs from "Addresses:" section
        ips = []
        addresses_section = re.search(
            r'Addresses:\s+(.+?)(?:\n\s*\n|\n\S|$)', 
            output, 
            re.DOTALL | re.IGNORECASE
        )
        
        if addresses_section:
            addresses_text = addresses_section.group(1)
            ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
            found_ips = re.findall(ip_pattern, addresses_text)
            for ip in found_ips:
                if (ip not in ips and 
                    ip != result['dns_server_ip'] and 
                    not ip.startswith('127.')):
                    ips.append(ip)
        
        # METHOD 2: Extract IPs from "Address:" lines
        if not ips:
            lines = output.split('\n')
            for line in lines:
                if 'Address:' in line and '#' not in line:
                    ip_match = re.search(
                        r'Address:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', 
                        line
                    )
                    if ip_match:
                        ip = ip_match.group(1)
                        if (ip != result['dns_server_ip'] and 
                            not ip.startswith('127.') and 
                            ip not in ips):
                            ips.append(ip)
        
        # METHOD 3: Fallback to socket.getaddrinfo
        if not ips:
            try:
                if log_callback:
                    log_callback(f"🔄 Using fallback resolution for {domain}", "info")
                addrinfo = socket.getaddrinfo(domain, None)
                for addr in addrinfo:
                    ip = addr[4][0]
                    if (ip not in ips and 
                        not ip.startswith('127.') and 
                        ':' not in ip):  # IPv4 only
                        ips.append(ip)
            except Exception:
                pass
        
        # Process results
        if ips:
            result['all_ips'] = ips
            result['ip_address'] = ', '.join(ips)
            result['status'] = 'RESOLVED'
            
            if result['answer_type'] == 'N/A':
                if 'authoritative' in output.lower():
                    result['answer_type'] = 'Authoritative'
                elif 'non-authoritative' in output.lower():
                    result['answer_type'] = 'Non-authoritative'
                else:
                    result['answer_type'] = 'Resolved'
            
            if log_callback:
                answer_symbol = '🔵' if result['answer_type'] == 'Authoritative' else '🟡'
                ip_preview = ips[0] if len(ips) == 1 else f"{ips[0]} (+{len(ips)-1} more)"
                log_callback(
                    f"{answer_symbol} {domain} -> {result['answer_type']} | "
                    f"{len(ips)} IP(s): {ip_preview}", 
                    "success"
                )
        else:
            result['status'] = 'NO_RECORD'
            if log_callback:
                log_callback(f"⚠️ {domain} -> No IP addresses found", "warning")
                
    except subprocess.TimeoutExpired:
        result['status'] = 'TIMEOUT'
        result['response_time'] = -1
        if log_callback:
            log_callback(f"⏰ {domain} -> Request timeout ({timeout}s)", "error")
    except Exception as e:
        result['status'] = 'ERROR'
        result['response_time'] = -1
        if log_callback:
            log_callback(f"💥 {domain} -> Error: {str(e)[:50]}", "error")
    
    return result

# ============================================
# REVERSE DNS FUNCTIONS
# ============================================

IPV4_REGEX = r'\b(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
PUBLIC_DNS_LIST = [
    '1.1.1.1',      # Cloudflare
    '8.8.8.8',      # Google
    '8.8.4.4',      # Google Secondary
    '208.67.222.222', # OpenDNS
    '208.67.220.220', # OpenDNS Secondary
    '9.9.9.9',      # Quad9
    '8.26.56.26',   # Comodo
]

def extract_ip(text):
    """Extract first IPv4 address from text."""
    if not text or not isinstance(text, str):
        return ''
    match = re.search(IPV4_REGEX, text)
    return match.group() if match else ''

def is_private_ip(ip):
    """Check if IP is private (RFC 1918) or localhost."""
    if not ip:
        return True
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return True
        first = int(parts[0])
        if first == 10:
            return True
        if first == 172 and 16 <= int(parts[1]) <= 31:
            return True
        if first == 192 and int(parts[1]) == 168:
            return True
        if first == 127:
            return True
        return False
    except:
        return True

def reverse_dns(ip, timeout=5):
    """Perform reverse DNS lookup (PTR) using system resolver."""
    if not ip:
        return ''
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        domain = socket.gethostbyaddr(ip)[0]
        return domain
    except (socket.herror, socket.timeout, Exception):
        return ''
    finally:
        socket.setdefaulttimeout(original_timeout)

def forward_dns_public(domain, timeout=5):
    """Forward lookup (A record) using multiple public DNS servers. Returns first public IP found."""
    if not domain:
        return ''
    for dns in PUBLIC_DNS_LIST:
        try:
            cmd = ['nslookup', domain, dns]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            output = result.stdout + result.stderr
            matches = re.findall(IPV4_REGEX, output)
            ips = ['.'.join(m) for m in matches if '.'.join(m) != dns]
            for ip in ips:
                if not is_private_ip(ip):
                    return ip
        except Exception:
            continue
    return ''

def nslookup_public(domain, timeout=5):
    """
    Forward lookup using multiple public DNS servers.
    Returns dict similar to nslookup_detailed but with public DNS rotation.
    """
    result = {
        'domain': domain,
        'ip_address': 'N/A',
        'status': 'ERROR',
        'dns_server': 'Public DNS (Multi-Server)',
        'dns_server_ip': 'Multiple',
        'answer_type': 'Non-authoritative',  # public DNS selalu non-authoritative
        'response_time': 0,
        'all_ips': []
    }
    
    start_time = time.time()
    for dns in PUBLIC_DNS_LIST:
        try:
            cmd = ['nslookup', domain, dns]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            output = proc.stdout + proc.stderr
            
            # Cek apakah domain ditemukan
            if "can't find" in output.lower() or "nxdomain" in output.lower():
                continue
            
            # Extract IPs
            ips = []
            # Method: cari "Addresses:" atau "Address:"
            addresses_section = re.search(r'Addresses:\s+(.+?)(?:\n\s*\n|\n\S|$)', output, re.DOTALL | re.IGNORECASE)
            if addresses_section:
                ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                found_ips = re.findall(ip_pattern, addresses_section.group(1))
                for ip in found_ips:
                    if ip != dns and not ip.startswith('127.') and ip not in ips:
                        ips.append(ip)
            
            if not ips:
                # Fallback ke baris "Address:"
                lines = output.split('\n')
                for line in lines:
                    if 'Address:' in line and '#' not in line:
                        ip_match = re.search(r'Address:\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                        if ip_match:
                            ip = ip_match.group(1)
                            if ip != dns and not ip.startswith('127.') and ip not in ips:
                                ips.append(ip)
            
            if ips:
                # Filter private IP? Untuk public DNS, biasanya IP publik, tapi kita filter juga
                public_ips = [ip for ip in ips if not is_private_ip(ip)]
                if public_ips:
                    ips = public_ips
                result['all_ips'] = ips
                result['ip_address'] = ', '.join(ips)
                result['status'] = 'RESOLVED'
                result['dns_server_ip'] = dns
                result['response_time'] = round((time.time() - start_time) * 1000, 2)
                return result
        except Exception:
            continue
    
    # Jika semua DNS gagal
    result['response_time'] = -1
    result['status'] = 'NOT_FOUND' if result['all_ips'] else 'ERROR'
    return result

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main application"""
    return render_template('index.html')


@app.route('/api/firewall', methods=['POST'])
def api_firewall():
    """
    Generate firewall configuration scripts
    """
    try:
        data = request.json
        group_name = data.get('group_name', 'BLOCKLIST_GROUP').strip()
        ip_text = data.get('ip_list', '')

        # ============================================
        # FUNGSI NORMALISASI IP
        # ============================================
        def normalize_ip(raw_ip):
            """Membersihkan berbagai format aneh menjadi format IP dengan titik"""
            # Ganti berbagai variasi [.] (.) {.} menjadi titik
            raw_ip = raw_ip.replace('[.]', '.')
            raw_ip = raw_ip.replace('(.)', '.')
            raw_ip = raw_ip.replace('{.}', '.')
            # Hapus semua karakter kurung siku, kurung kurawal, kurung biasa
            raw_ip = raw_ip.replace('[', '')
            raw_ip = raw_ip.replace(']', '')
            raw_ip = raw_ip.replace('{', '')
            raw_ip = raw_ip.replace('}', '')
            raw_ip = raw_ip.replace('(', '')
            raw_ip = raw_ip.replace(')', '')
            # Ganti koma menjadi titik (kasus 192.168,21,33)
            raw_ip = raw_ip.replace(',', '.')
            # Bersihkan spasi
            raw_ip = raw_ip.strip()
            return raw_ip

        # ============================================
        # FUNGSI KONVERSI CIDR KE NETMASK
        # ============================================
        def cidr_to_netmask(cidr):
            """Convert CIDR prefix (e.g., 24) to netmask (e.g., 255.255.255.0)"""
            mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
            return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"

        def parse_ip_with_prefix(ip_str):
            """
            Given IP string like '192.168.11.2/27' or '123.14.41.42' or '192.168.1.1/32'
            Returns (ip_address, netmask, prefix)
            """
            if '/' in ip_str:
                ip_part, cidr_part = ip_str.split('/', 1)
                prefix = int(cidr_part)
            else:
                ip_part = ip_str
                prefix = 32
            netmask = cidr_to_netmask(prefix)
            return ip_part, netmask, prefix

        # Bersihkan semua baris IP
        ip_list_raw = []
        for line in ip_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                normalized = normalize_ip(line)
                if normalized:
                    ip_list_raw.append(normalized)

        # Hapus duplikat
        ip_list = list(dict.fromkeys(ip_list_raw))

        if not ip_list:
            return jsonify({
                'success': False, 
                'error': 'No valid IP addresses provided'
            })

        if not group_name:
            return jsonify({
                'success': False, 
                'error': 'Group name is required'
            })

        # Generate FortiGate Address Configuration
        fortigate_address = "config firewall address\n"
        for ip in ip_list:
            ip_addr, netmask, prefix = parse_ip_with_prefix(ip)
            obj_name = f"block_{ip_addr}-m{prefix}"
            fortigate_address += f'    edit "{obj_name}"\n'
            fortigate_address += f'        set subnet {ip_addr} {netmask}\n'
            fortigate_address += '    next\n'
        fortigate_address += "end\n"

        # Generate FortiGate Group Configuration
        fortigate_group = "config firewall addrgrp\n"
        fortigate_group += f'    edit "{group_name}"\n'
        for ip in ip_list:
            ip_addr, _, prefix = parse_ip_with_prefix(ip)
            obj_name = f"block_{ip_addr}-m{prefix}"
            fortigate_group += f'        append member "{obj_name}"\n'
        fortigate_group += "    next\n"
        fortigate_group += "end\n"

        # Generate CheckPoint Configuration
        checkpoint_address = ""
        for ip in ip_list:
            ip_addr, _, prefix = parse_ip_with_prefix(ip)
            obj_name = f"block_{ip_addr}-m{prefix}"
            checkpoint_address += (
                f'add host name "{obj_name}" '
                f'ip-address {ip_addr} '
                f'groups "{group_name}" '
                f'ignore-warnings true\n'
            )

        files = [
            {'name': 'FortiGate Address Configuration', 'content': fortigate_address},
            {'name': 'FortiGate Group Configuration', 'content': fortigate_group},
            {'name': 'CheckPoint Configuration', 'content': checkpoint_address}
        ]

        return jsonify({
            'success': True, 
            'files': files,
            'ip_count': len(ip_list),
            'group_name': group_name
        })

    except Exception as e:
        return jsonify({
            'success': False, 
            'error': str(e)
        })


@app.route('/api/nslookup', methods=['POST'])
def api_nslookup():
    """
    Perform NSLookup for multiple domains concurrently
    """
    try:
        data = request.json
        domains_text = data.get('domains', '')
        threads = min(max(int(data.get('threads', 5)), 1), 20)
        timeout = min(max(int(data.get('timeout', 5)), 1), 30)
        dns_server = data.get('dns_server', 'default')
        
        # ============================================
        # FUNGSI CLEAN DOMAIN - Untuk mengubah google[.]com menjadi google.com
        # ============================================

        
        def clean_domain(domain):
            """Clean domain from various malformed formats to valid domain."""
            domain = domain.strip()
            # Replace berbagai variasi titik terhalang
            domain = domain.replace('[.]', '.')
            domain = domain.replace('(.)', '.')
            domain = domain.replace('{.}', '.')
            # Hapus semua karakter kurung siku, kurung kurawal, kurung biasa
            domain = domain.replace('[', '')
            domain = domain.replace(']', '')
            domain = domain.replace('{', '')
            domain = domain.replace('}', '')
            domain = domain.replace('(', '')
            domain = domain.replace(')', '')
            # Ganti koma menjadi titik (misal google,com -> google.com)
            domain = domain.replace(',', '.')
            # Bersihkan spasi
            domain = domain.strip()
            return domain
        
        # Parse domains with cleaning
        domains = []
        for d in domains_text.split('\n'):
            d = d.strip()
            if d and not d.startswith('#'):
                # Clean domain from [.] format
                d = clean_domain(d)
                domains.append(d)
        
        if not domains:
            return jsonify({
                'success': False, 
                'error': 'No valid domains provided'
            })
        
        # Remove duplicates
        domains = list(dict.fromkeys(domains))
        
        logs = []
        results = []
        
        def add_log(message, log_type='info'):
            logs.append({
                'message': message, 
                'type': log_type
            })
        
        dns_names = {
            'default': 'Default System DNS',
            'public': 'Public DNS (Multi-Server: Cloudflare, Google, OpenDNS, Quad9, Comodo)'
        }
        
        add_log(f"📋 Processing {len(domains)} domain(s)...", 'info')
        add_log(
            f"🌍 DNS Server: {dns_names.get(dns_server, dns_server)}", 
            'info'
        )
        add_log(f"⚡ Threads: {threads}, Timeout: {timeout}s", 'info')
        
        # Process domains concurrently
        def process_domain(domain):
            def log_callback(msg, typ):
                add_log(msg, typ)
            
            if dns_server == 'public':
                # Gunakan fungsi public DNS multi-server
                return nslookup_public(domain, timeout)
            else:
                dns = None  # default
                return nslookup_detailed(domain, timeout, dns, log_callback)
        
        results = [None] * len(domains)  # tempat hasil sesuai urutan
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_index = {
                executor.submit(process_domain, domain): idx
                for idx, domain in enumerate(domains)
            }
            
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                domain = domains[idx]
                try:
                    result = future.result()
                    results[idx] = result
                except Exception as e:
                    results[idx] = {
                        'domain': domain,
                        'ip_address': 'N/A',
                        'status': 'ERROR',
                        'answer_type': 'N/A',
                        'dns_server': dns_server,
                        'all_ips': [],
                        'response_time': -1
                    }
                    add_log(f"💥 {domain} -> Critical error: {str(e)[:50]}", 'error')
        
        # Calculate summary
        resolved = [r for r in results if r['status'] == 'RESOLVED']
        total = len(results)
        
        summary = {
            'total': total,
            'resolved': len(resolved),
            'resolved_percent': round(len(resolved) * 100 / total, 1) if total > 0 else 0,
            'failed': total - len(resolved),
            'failed_percent': round((total - len(resolved)) * 100 / total, 1) if total > 0 else 0,
            'authoritative': sum(1 for r in resolved if r['answer_type'] == 'Authoritative'),
            'non_authoritative': sum(1 for r in resolved if r['answer_type'] == 'Non-authoritative')
        }
        
        # Generate Excel report
        excel_rows = []
        for r in results:
            if r['status'] == 'RESOLVED' and r.get('all_ips'):
                for ip in r['all_ips']:
                    excel_rows.append({
                        'Domain': r['domain'],
                        'IP Address': ip,
                        'Status': r['status'],
                        'Answer Type': r.get('answer_type', 'N/A'),
                        'DNS Server': r.get('dns_server', 'N/A'),
                        'Response Time (ms)': r.get('response_time', 0)
                    })
            else:
                excel_rows.append({
                    'Domain': r['domain'],
                    'IP Address': r.get('ip_address', 'N/A'),
                    'Status': r['status'],
                    'Answer Type': r.get('answer_type', 'N/A'),
                    'DNS Server': r.get('dns_server', 'N/A'),
                    'Response Time (ms)': r.get('response_time', 0)
                })
        
        # Create Excel with multiple sheets
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Detailed sheet (one IP per row)
            df_detailed = pd.DataFrame(excel_rows)
            df_detailed.to_excel(writer, sheet_name='Detailed Results', index=False)
            
            # Summary sheet
            summary_data = []
            for r in results:
                summary_data.append({
                    'Domain': r['domain'],
                    'Total IPs': len(r.get('all_ips', [])),
                    'IP Addresses': r.get('ip_address', 'N/A'),
                    'Status': r['status'],
                    'Answer Type': r.get('answer_type', 'N/A'),
                    'DNS Server': r.get('dns_server', 'N/A'),
                    'Response Time (ms)': r.get('response_time', 0)
                })
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='Domain Summary', index=False)
        
        output.seek(0)
        excel_data = base64.b64encode(output.getvalue()).decode('utf-8')
        
        add_log(
            f"✅ Completed! {summary['resolved']} resolved, "
            f"{summary['failed']} failed", 
            'success'
        )
        add_log(f"📊 Excel report generated ({len(excel_rows)} rows)", 'info')
        
        return jsonify({
            'success': True,
            'results': results,
            'summary': summary,
            'excel_data': excel_data,
            'logs': logs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/reverse-dns', methods=['POST'])
def api_reverse_dns():
    """
    Perform reverse DNS (PTR) on extracted IPs, then forward DNS to public IP.
    Input: multiline text (each line can contain an IP or text with IP)
    """
    try:
        data = request.json
        raw_data = data.get('data', '')
        threads = min(max(int(data.get('threads', 5)), 1), 20)
        timeout = min(max(int(data.get('timeout', 5)), 1), 30)

        # Parse lines
        lines = []
        for line in raw_data.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)

        if not lines:
            return jsonify({'success': False, 'error': 'No valid data provided'})

        logs = []
        results = []

        def add_log(msg, typ='info'):
            logs.append({'message': msg, 'type': typ})

        add_log(f"📋 Processing {len(lines)} entries with {threads} thread(s)...", 'info')
        add_log(f"⏱️ Timeout: {timeout}s", 'info')

        # Process each line
        def process_entry(original_text):
            ip = extract_ip(original_text)
            if not ip:
                return {
                    'original_data': original_text,
                    'extracted_ip': '',
                    'domain': '',
                    'public_ip': ''
                }
            domain = reverse_dns(ip, timeout)
            public_ip = forward_dns_public(domain, timeout) if domain else ''
            return {
                'original_data': original_text,
                'extracted_ip': ip,
                'domain': domain,
                'public_ip': public_ip
            }

        # Use ThreadPoolExecutor
        results = [None] * len(lines)  # tempat hasil sesuai urutan
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_index = {
                executor.submit(process_entry, line): idx
                for idx, line in enumerate(lines)
            }
            completed = 0
            total = len(lines)
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                original_line = lines[idx]
                try:
                    result = future.result()
                    results[idx] = result
                except Exception as e:
                    results[idx] = {
                        'original_data': original_line,
                        'extracted_ip': '',
                        'domain': '',
                        'public_ip': '',
                        'error': str(e)
                    }
                    add_log(f"💥 Error processing '{original_line[:50]}': {str(e)}", 'error')
                completed += 1
                if int(completed * 100 / total) % 10 == 0:
                    add_log(f"📊 Progress: {completed}/{total} ({int(completed*100/total)}%)", 'info')


        # Calculate summary
        reverse_success = sum(1 for r in results if r.get('domain'))
        forward_success = sum(1 for r in results if r.get('public_ip'))
        summary = {
            'total': len(results),
            'reverse_success': reverse_success,
            'forward_success': forward_success
        }

        # Generate Excel report
        excel_rows = []
        for r in results:
            excel_rows.append({
                'Original Data': r['original_data'],
                'Extracted IP': r.get('extracted_ip', ''),
                'Domain (Reverse)': r.get('domain', ''),
                'Public IP (Forward)': r.get('public_ip', '')
            })
        df = pd.DataFrame(excel_rows)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Reverse DNS Results', index=False)
        output.seek(0)
        excel_data = base64.b64encode(output.getvalue()).decode('utf-8')

        add_log(f"✅ Completed! Reverse success: {reverse_success}, Forward success: {forward_success}", 'success')
        return jsonify({
            'success': True,
            'results': results,
            'summary': summary,
            'excel_data': excel_data,
            'logs': logs
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Route not found'}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'host': request.host
    })


# ============================================
# APPLICATION STARTUP
# ============================================

def open_browser():
    """Open browser after server starts"""
    webbrowser.open('http://127.0.0.1:5000')


def main():
    """Main function for executable"""
    print("\n" + "="*60)
    print("🛡️  Firewall & Network Tools Pro v1.0.0")
    print("="*60)
    print("🚀 Server starting...")
    print("📱 Local: http://127.0.0.1:5000")
    print("🌐 Network: http://0.0.0.0:5000")
    print("="*60)
    print("⌨️  Keyboard shortcuts:")
    print("   Ctrl+1: Firewall Generator")
    print("   Ctrl+2: NSLookup Tool")
    print("="*60)
    print("📌 Close this window to stop the server")
    print("="*60 + "\n")
    
    # Buka browser otomatis setelah 1.5 detik
    threading.Timer(1.5, open_browser).start()
    
    # Jalankan server
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()