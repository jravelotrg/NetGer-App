let currentSessionId = null;
let firewallContents = [];

function showToast(message = '✅ Copied to clipboard!', isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.style.background = isError ? 'rgba(255, 118, 117, 0.9)' : 'rgba(0, 184, 148, 0.9)';
    toast.classList.add('show');
    setTimeout(() => { 
        toast.classList.remove('show');
    }, 3000);
}

function selectMenu(menu) {
    // Update menu cards
    document.querySelectorAll('.menu-card').forEach(c => c.classList.remove('active'));
    document.getElementById(`menu-${menu}`).classList.add('active');
    
    // Update panels
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById(`panel-${menu}`);
    panel.classList.add('active');
    
    // Scroll to panel
    setTimeout(() => {
        panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

// DNS Server change handler
document.getElementById('dns-server').addEventListener('change', function() {
    const dnsValue = this.value;
    const dnsNames = {
        'default': 'Default System DNS',
        '8.8.8.8': 'Google DNS (8.8.8.8)',
        '8.8.4.4': 'Google DNS (8.8.4.4)',
        '1.1.1.1': 'Cloudflare DNS (1.1.1.1)',
        '1.0.0.1': 'Cloudflare DNS (1.0.0.1)',
        '9.9.9.9': 'Quad9 DNS (9.9.9.9)',
        '208.67.222.222': 'OpenDNS (208.67.222.222)'
    };
    document.getElementById('dns-info').innerHTML = 
        `ℹ️ Using DNS server: <strong>${dnsNames[dnsValue] || dnsValue}</strong>`;
});

function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    const timestamp = new Date().toLocaleTimeString();
    logEntry.innerHTML = `<span style="color: #666;">[${timestamp}]</span> ${message}`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
    
    // Limit log entries
    if (logContainer.children.length > 100) {
        logContainer.removeChild(logContainer.firstChild);
    }
}

async function copyToClipboard(text, buttonElement) {
    // Try modern clipboard API
    if (navigator.clipboard && window.isSecureContext) {
        try {
            await navigator.clipboard.writeText(text);
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = '✅ Copied!';
                buttonElement.classList.add('copied');
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                    buttonElement.classList.remove('copied');
                }, 2000);
            }
            showToast('✅ Successfully copied to clipboard!');
            return true;
        } catch (err) {
            console.error('Clipboard API failed:', err);
        }
    }
    
    // Fallback method
    try {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
            if (buttonElement) {
                const originalText = buttonElement.textContent;
                buttonElement.textContent = '✅ Copied!';
                buttonElement.classList.add('copied');
                setTimeout(() => {
                    buttonElement.textContent = originalText;
                    buttonElement.classList.remove('copied');
                }, 2000);
            }
            showToast('✅ Successfully copied to clipboard!');
            return true;
        }
    } catch (err) {
        console.error('Fallback copy failed:', err);
    }
    
    showToast('❌ Failed to copy to clipboard!', true);
    return false;
}

async function generateFirewall() {
    const groupName = document.getElementById('group-name').value.trim();
    const ipText = document.getElementById('ip-list').value.trim();
    
    if (!groupName) {
        showToast('❌ Please enter a group name!', true);
        return;
    }
    
    if (!ipText) {
        showToast('❌ Please enter IP addresses!', true);
        return;
    }
    
    // Show loading state
    const generateBtn = document.querySelector('button[onclick="generateFirewall()"]');
    const originalText = generateBtn.textContent;
    generateBtn.textContent = '⏳ Generating...';
    generateBtn.disabled = true;
    
    try {
        const response = await fetch('/api/firewall', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ group_name: groupName, ip_list: ipText })
        });
        
        const data = await response.json();
        
        if (data.success) {
            let html = '<h3 style="color: var(--success); margin-bottom: 20px;">✅ Configuration Generated Successfully</h3>';
            html += '<div class="results-grid">';
            data.files.forEach((file, idx) => {
                html += `
                    <div class="result-card">
                        <div class="result-header">
                            <h4>📁 ${escapeHtml(file.name)}</h4>
                            <button class="copy-btn" onclick="copyFileContent(${idx}, this)">📋 Copy to Clipboard</button>
                        </div>
                        <div class="result-content">
                            <pre id="file-content-${idx}">${escapeHtml(file.content)}</pre>
                        </div>
                    </div>
                `;
            });
            html += '</div>';
            document.getElementById('firewall-results').innerHTML = html;
            window.firewallContents = data.files.map(f => f.content);
            showToast('✅ Configuration generated successfully!');
        } else {
            document.getElementById('firewall-results').innerHTML = 
                `<div class="log-error">❌ Error: ${escapeHtml(data.error)}</div>`;
            showToast('❌ Error generating configuration!', true);
        }
    } catch (err) {
        document.getElementById('firewall-results').innerHTML = 
            `<div class="log-error">❌ Network error: ${escapeHtml(err.message)}</div>`;
        showToast('❌ Network error occurred!', true);
    } finally {
        generateBtn.textContent = originalText;
        generateBtn.disabled = false;
    }
}

async function copyFileContent(index, buttonElement) {
    if (window.firewallContents && window.firewallContents[index]) {
        await copyToClipboard(window.firewallContents[index], buttonElement);
    } else {
        showToast('❌ No content to copy!', true);
    }
}

async function runNSLookup() {
    const domains = document.getElementById('domains').value.trim();
    const threads = document.getElementById('threads').value;
    const timeout = document.getElementById('timeout').value;
    const dnsServer = document.getElementById('dns-server').value;
    
    if (!domains) {
        showToast('❌ Please enter domain names!', true);
        return;
    }
    
    // Validate threads
    if (threads < 1 || threads > 20) {
        showToast('❌ Threads must be between 1 and 20!', true);
        return;
    }
    
    // Reset UI
    document.getElementById('log-container').innerHTML = '<div class="log-entry log-info">📋 Starting NSLookup...</div>';
    document.getElementById('nslookup-results').innerHTML = '';
    
    const progressDiv = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    progressDiv.style.display = 'block';
    progressFill.style.width = '0%';
    progressFill.textContent = '0%';
    
    const dnsNames = {
        'default': 'Default System DNS',
        '8.8.8.8': 'Google DNS (8.8.8.8)',
        '8.8.4.4': 'Google DNS (8.8.4.4)',
        '1.1.1.1': 'Cloudflare DNS (1.1.1.1)',
        '1.0.0.1': 'Cloudflare DNS (1.0.0.1)',
        '9.9.9.9': 'Quad9 DNS (9.9.9.9)',
        '208.67.222.222': 'OpenDNS (208.67.222.222)'
    };
    
    addLog(`🚀 Starting NSLookup with ${dnsNames[dnsServer]}`, 'info');
    addLog(`📊 Processing domains with ${threads} thread(s)...`, 'info');
    
    // Disable button
    const runBtn = document.querySelector('button[onclick="runNSLookup()"]');
    const originalText = runBtn.textContent;
    runBtn.textContent = '⏳ Processing...';
    runBtn.disabled = true;
    
    try {
        const response = await fetch('/api/nslookup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                domains: domains, 
                threads: parseInt(threads), 
                timeout: parseInt(timeout),
                dns_server: dnsServer
            })
        });
        
        const data = await response.json();
        progressDiv.style.display = 'none';
        
        if (data.success) {
            // Display logs
            if (data.logs) {
                data.logs.forEach(log => {
                    addLog(log.message, log.type);
                });
            }
            
            // Display results
            displayResults(data.results, data.summary, dnsServer);
            
            // Add download button
            if (data.excel_data) {
                const downloadContainer = document.getElementById('nslookup-results');
                const btn = document.createElement('button');
                btn.className = 'success';
                btn.innerHTML = '📊 Download Excel Report';
                btn.style.marginTop = '20px';
                btn.onclick = () => downloadExcel(data.excel_data);
                downloadContainer.appendChild(btn);
            }
            
            addLog('✅ NSLookup completed successfully!', 'success');
            showToast('✅ NSLookup completed!');
        } else {
            addLog(`❌ Error: ${data.error}`, 'error');
            showToast('❌ NSLookup failed!', true);
        }
    } catch (err) {
        addLog(`❌ Network error: ${err.message}`, 'error');
        showToast('❌ Network error occurred!', true);
    } finally {
        progressDiv.style.display = 'none';
        runBtn.textContent = originalText;
        runBtn.disabled = false;
    }
}

function displayResults(results, summary, dnsServer) {
    const dnsNames = {
        'default': 'Default System DNS',
        '8.8.8.8': 'Google DNS (8.8.8.8)',
        '8.8.4.4': 'Google DNS (8.8.4.4)',
        '1.1.1.1': 'Cloudflare DNS (1.1.1.1)',
        '1.0.0.1': 'Cloudflare DNS (1.0.0.1)',
        '9.9.9.9': 'Quad9 DNS (9.9.9.9)',
        '208.67.222.222': 'OpenDNS (208.67.222.222)'
    };
    
    let html = `
        <div class="dns-info">
            🌍 DNS Server Used: <strong>${dnsNames[dnsServer] || dnsServer}</strong>
        </div>
        <div class="summary-grid">
            <div class="summary-card">
                <strong>${summary.total}</strong>
                Total Domains
            </div>
            <div class="summary-card" style="border-color: rgba(0, 184, 148, 0.3);">
                <strong style="color: var(--success);">✅ ${summary.resolved} (${summary.resolved_percent}%)</strong>
                Successfully Resolved
            </div>
            <div class="summary-card" style="border-color: rgba(255, 118, 117, 0.3);">
                <strong style="color: var(--danger);">❌ ${summary.failed} (${summary.failed_percent}%)</strong>
                Failed
            </div>
            <div class="summary-card">
                <strong>🔵 ${summary.authoritative}</strong>
                Authoritative
            </div>
            <div class="summary-card">
                <strong>🟡 ${summary.non_authoritative}</strong>
                Non-authoritative
            </div>
        </div>
        <div style="overflow-x: auto;">
            <table class="results-table">
                <thead>
                    <tr>
                        <th>Domain</th>
                        <th>IP Addresses</th>
                        <th>Count</th>
                        <th>Status</th>
                        <th>Answer Type</th>
                        <th>DNS Server</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    for (const r of results) {
        const statusClass = r.status === 'RESOLVED' ? 'resolved' : 'error';
        const ipCount = r.all_ips ? r.all_ips.length : (r.ip_address === 'N/A' ? 0 : r.ip_address.split(',').length);
        
        let ipDisplay = escapeHtml(r.ip_address || 'N/A');
        
        if (r.all_ips && r.all_ips.length > 3) {
            const firstThree = r.all_ips.slice(0, 3).join(', ');
            const remaining = r.all_ips.slice(3);
            ipDisplay = `${firstThree} 
                <span class="ip-tooltip">
                    (+${remaining.length} more)
                    <span class="ip-list-popup">
                        ${remaining.join('<br>')}
                    </span>
                </span>`;
        }
        
        html += `
            <tr>
                <td><strong>${escapeHtml(r.domain)}</strong></td>
                <td style="font-size:12px;">${ipDisplay}</td>
                <td style="text-align:center;">${ipCount > 0 ? ipCount : '-'}</td>
                <td class="${statusClass}">${r.status}</td>
                <td>${r.answer_type || '-'}</td>
                <td>${escapeHtml(r.dns_server || '-')}</td>
            </tr>
        `;
    }
    
    html += '</tbody> </table></div>';
    document.getElementById('nslookup-results').innerHTML = html;
}

function downloadExcel(base64Data) {
    const link = document.createElement('a');
    link.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,' + base64Data;
    link.download = `nslookup_result_${new Date().toISOString().slice(0,10)}.xlsx`;
    link.click();
    showToast('📊 Excel report downloaded!');
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize with firewall panel
selectMenu('firewall');

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case '1':
                e.preventDefault();
                selectMenu('firewall');
                break;
            case '2':
                e.preventDefault();
                selectMenu('nslookup');
                break;
        }
    }
});