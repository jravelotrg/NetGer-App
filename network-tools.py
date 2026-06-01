from flask import Flask, request, render_template_string, jsonify
import subprocess
import re
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import base64
from io import BytesIO
import socket
import os
import threading 
import webbrowser

app = Flask(__name__)

# ============================================
# HTML TEMPLATE - COMPLETE WEB APPLICATION
# ============================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Firewall & Network Tools Pro</title>
    <style>
        :root {
            --bg-primary: #0a0a1a;
            --bg-secondary: #1a1a2e;
            --bg-card: rgba(26, 26, 46, 0.8);
            --accent: #6c5ce7;
            --accent-hover: #5b4cdb;
            --success: #00b894;
            --danger: #ff7675;
            --warning: #fdcb6e;
            --info: #74b9ff;
            --text-primary: #e0e0e0;
            --text-secondary: #a0a0a0;
            --border: rgba(108, 92, 231, 0.3);
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(108, 92, 231, 0.1) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(0, 184, 148, 0.1) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        /* Header Styles */
        .header {
            text-align: center;
            padding: 40px 20px;
            position: relative;
        }

        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 4px;
            background: var(--gradient);
            border-radius: 2px;
        }

        .header h1 {
            font-size: 2.8em;
            margin-bottom: 10px;
            background: var(--gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeInDown 0.6s ease;
        }

        .header p {
            color: var(--text-secondary);
            font-size: 1.1em;
            animation: fadeInUp 0.6s ease;
        }

        /* Menu Grid */
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
            animation: fadeIn 0.8s ease;
        }

        .menu-card {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 40px 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
        }

        .menu-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient);
            transform: scaleX(0);
            transition: transform 0.4s ease;
        }

        .menu-card:hover {
            transform: translateY(-10px);
            box-shadow: var(--shadow);
            border-color: var(--border);
        }

        .menu-card:hover::before {
            transform: scaleX(1);
        }

        .menu-card.active {
            border-color: var(--accent);
            background: rgba(108, 92, 231, 0.15);
            transform: translateY(-5px);
            box-shadow: 0 8px 32px rgba(108, 92, 231, 0.2);
        }

        .menu-icon {
            font-size: 64px;
            margin-bottom: 20px;
            animation: pulse 2s infinite;
        }

        .menu-card h2 {
            font-size: 1.5em;
            margin-bottom: 10px;
            color: var(--text-primary);
        }

        .menu-card p {
            color: var(--text-secondary);
            font-size: 0.95em;
        }

        /* Panel Styles */
        .panel {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 35px;
            margin-top: 20px;
            display: none;
            animation: slideIn 0.5s ease;
            box-shadow: var(--shadow);
        }

        .panel.active {
            display: block;
        }

        .panel h2 {
            font-size: 1.8em;
            margin-bottom: 30px;
            color: var(--accent);
            position: relative;
            padding-bottom: 15px;
        }

        .panel h2::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 60px;
            height: 3px;
            background: var(--gradient);
            border-radius: 2px;
        }

        /* Form Styles */
        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 10px;
            font-weight: 500;
            color: var(--text-secondary);
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input, textarea, select {
            width: 100%;
            padding: 14px 18px;
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            background: rgba(10, 10, 26, 0.8);
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.3s ease;
            font-family: inherit;
        }

        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 3px rgba(108, 92, 231, 0.1);
        }

        textarea {
            resize: vertical;
            min-height: 150px;
            font-family: 'Courier New', monospace;
        }

        select option {
            background: var(--bg-secondary);
            color: var(--text-primary);
        }

        /* Button Styles */
        button {
            background: var(--gradient);
            color: white;
            padding: 14px 35px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            letter-spacing: 0.5px;
            position: relative;
            overflow: hidden;
        }

        button::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s ease;
        }

        button:hover::before {
            left: 100%;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(108, 92, 231, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        button.success {
            background: linear-gradient(135deg, #00b894 0%, #55efc4 100%);
        }

        button.danger {
            background: linear-gradient(135deg, #ff7675 0%, #d63031 100%);
        }

        /* Log Container */
        .log-container {
            background: rgba(10, 10, 26, 0.9);
            border-radius: 12px;
            padding: 15px;
            margin-top: 20px;
            max-height: 350px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        .log-container::-webkit-scrollbar {
            width: 6px;
        }

        .log-container::-webkit-scrollbar-track {
            background: transparent;
        }

        .log-container::-webkit-scrollbar-thumb {
            background: var(--accent);
            border-radius: 3px;
        }

        .log-entry {
            padding: 6px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-family: 'Courier New', monospace;
            animation: fadeIn 0.3s ease;
        }

        .log-success { color: var(--success); }
        .log-error { color: var(--danger); }
        .log-info { color: var(--info); }
        .log-warning { color: var(--warning); }

        /* Progress Bar */
        .progress-container {
            margin-top: 20px;
            display: none;
        }

        .progress-bar {
            width: 100%;
            height: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            overflow: hidden;
        }

        .progress-fill {
            height: 100%;
            background: var(--gradient);
            width: 0%;
            transition: width 0.5s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, 
                transparent 0%, 
                rgba(255, 255, 255, 0.2) 50%, 
                transparent 100%);
            animation: shimmer 2s infinite;
        }

        /* Results Grid */
        .results-grid {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .result-card {
            background: rgba(10, 10, 26, 0.9);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .result-card:hover {
            border-color: var(--accent);
            box-shadow: 0 4px 16px rgba(108, 92, 231, 0.2);
        }

        .result-header {
            background: rgba(108, 92, 231, 0.1);
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .result-header h4 {
            margin: 0;
            font-size: 16px;
            color: var(--accent);
        }

        .result-content {
            padding: 20px;
            background: rgba(10, 10, 26, 0.5);
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.6;
        }

        .result-content pre {
            margin: 0;
            padding: 0;
            background: transparent;
            color: var(--text-primary);
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        /* Copy Button */
        .copy-btn {
            background: rgba(0, 184, 148, 0.2);
            border: 1px solid var(--success);
            padding: 10px 20px;
            border-radius: 8px;
            color: var(--success);
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }

        .copy-btn:hover {
            background: rgba(0, 184, 148, 0.3);
            transform: translateY(-1px);
        }

        .copy-btn.copied {
            background: rgba(0, 184, 148, 0.4);
            animation: pulse 0.6s ease;
        }

        /* Results Table */
        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 13px;
            background: rgba(10, 10, 26, 0.8);
            border-radius: 12px;
            overflow: hidden;
        }

        .results-table th {
            background: rgba(108, 92, 231, 0.2);
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: var(--accent);
            border-bottom: 2px solid rgba(108, 92, 231, 0.3);
        }

        .results-table td {
            padding: 12px 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }

        .results-table tr:hover {
            background: rgba(108, 92, 231, 0.05);
        }

        .resolved { color: var(--success); }
        .error { color: var(--danger); }

        /* Summary Grid */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 25px;
        }

        .summary-card {
            background: rgba(108, 92, 231, 0.1);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(108, 92, 231, 0.2);
            transition: all 0.3s ease;
        }

        .summary-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(108, 92, 231, 0.2);
        }

        .summary-card strong {
            display: block;
            font-size: 1.2em;
            color: var(--accent);
            margin-bottom: 8px;
        }

        /* DNS Info */
        .dns-info {
            background: rgba(0, 184, 148, 0.1);
            padding: 12px 18px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-size: 13px;
            color: var(--success);
            border: 1px solid rgba(0, 184, 148, 0.2);
        }

        /* Toast */
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: rgba(0, 184, 148, 0.9);
            color: white;
            padding: 15px 25px;
            border-radius: 12px;
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 9999;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }

        .toast.show {
            opacity: 1;
            transform: translateY(0);
        }

        /* IP Tooltip */
        .ip-tooltip {
            cursor: help;
            border-bottom: 1px dotted var(--info);
            position: relative;
            color: var(--info);
        }

        .ip-list-popup {
            display: none;
            position: absolute;
            background: var(--bg-secondary);
            border: 1px solid var(--accent);
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 11px;
            white-space: nowrap;
            z-index: 1000;
            bottom: 100%;
            left: 0;
            margin-bottom: 10px;
            box-shadow: var(--shadow);
        }

        .ip-tooltip:hover .ip-list-popup {
            display: block;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .container { padding: 10px; }
            .header h1 { font-size: 2em; }
            .menu-grid { grid-template-columns: 1fr; }
            .panel { padding: 20px; }
            .results-table { font-size: 11px; }
            .results-table td, .results-table th { padding: 8px; }
            .result-content { font-size: 11px; padding: 12px; }
            .summary-grid { grid-template-columns: repeat(2, 1fr); }
        }

        @media (max-width: 480px) {
            .summary-grid { grid-template-columns: 1fr; }
            button { width: 100%; }
        }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🛡️ Firewall & Network Tools</h1>
        <p>Professional Network Administration Toolkit</p>
    </div>
    
    <div class="menu-grid">
        <div class="menu-card" onclick="selectMenu('firewall')" id="menu-firewall">
            <div class="menu-icon">🔥</div>
            <h2>Firewall Command Generator</h2>
            <p>Generate firewall configuration scripts for IP blocking</p>
        </div>
        <div class="menu-card" onclick="selectMenu('nslookup')" id="menu-nslookup">
            <div class="menu-icon">🌐</div>
            <h2>NSLookup Pro Tool</h2>
            <p>Advanced DNS lookup with multiple server options</p>
        </div>
    </div>
    
    <!-- Panel Firewall -->
    <div id="panel-firewall" class="panel">
        <h2>🔥 Firewall Command Generator</h2>
        <div class="form-group">
            <label>📁 Group Name:</label>
            <input type="text" id="group-name" value="BLOCKLIST_GROUP" placeholder="Enter group name...">
        </div>
        <div class="form-group">
            <label>📝 IP List (one per line):</label>
            <textarea id="ip-list" rows="8" placeholder="192.168.1.10/32&#10;192.168.1.20/32&#10;10.0.0.0/24"></textarea>
        </div>
        <button onclick="generateFirewall()">⚡ GENERATE CONFIGURATION</button>
        <div id="firewall-results" style="margin-top: 30px;"></div>
    </div>
    
    <!-- Panel NSLookup -->
    <div id="panel-nslookup" class="panel">
        <h2>🌐 NSLookup Pro Tool</h2>
        
        <div class="form-group">
            <label>🌍 DNS Server:</label>
            <select id="dns-server">
                <option value="default">🌐 Default System DNS</option>
                <option value="8.8.8.8">☁️ Google DNS (8.8.8.8)</option>
                <option value="8.8.4.4">☁️ Google DNS (8.8.4.4)</option>
                <option value="1.1.1.1">☁️ Cloudflare DNS (1.1.1.1)</option>
                <option value="1.0.0.1">☁️ Cloudflare DNS (1.0.0.1)</option>
                <option value="9.9.9.9">☁️ Quad9 DNS (9.9.9.9)</option>
                <option value="208.67.222.222">☁️ OpenDNS (208.67.222.222)</option>
            </select>
        </div>
        
        <div class="dns-info" id="dns-info">
            ℹ️ Using DNS server: <strong>Default System DNS</strong>
        </div>
        
        <div class="form-group">
            <label>📝 Domain List (one per line):</label>
            <textarea id="domains" rows="8" placeholder="google.com&#10;facebook.com&#10;github.com&#10;stackoverflow.com"></textarea>
        </div>
        
        <div class="form-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
            <div>
                <label>⚡ Threads (1-20):</label>
                <input type="number" id="threads" value="5" min="1" max="20">
            </div>
            <div>
                <label>⏱️ Timeout (seconds):</label>
                <input type="number" id="timeout" value="5" min="1" max="30">
            </div>
        </div>
        
        <button onclick="runNSLookup()">🔍 RUN NSLOOKUP</button>
        
        <div class="log-container" id="log-container">
            <div class="log-entry log-info">📋 Ready to run NSLookup...</div>
        </div>
        
        <div class="progress-container" id="progress-container">
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill">0%</div>
            </div>
        </div>
        
        <div id="nslookup-results" style="margin-top: 30px;"></div>
    </div>
</div>

<div id="toast" class="toast">✅ Copied to clipboard!</div>

<script>
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
</script>
</body>
</html>
'''

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
# API ROUTES
# ============================================

@app.route('/')
def index():
    """Serve the main application"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/firewall', methods=['POST'])
def api_firewall():
    """
    Generate firewall configuration scripts
    """
    try:
        data = request.json
        group_name = data.get('group_name', 'BLOCKLIST_GROUP').strip()
        ip_text = data.get('ip_list', '')
        
        # Clean IP list
        ip_text_cleaned = ip_text.replace('[', '').replace(']', '')
        ip_list_raw = [
            ip.strip() for ip in ip_text_cleaned.split('\n') 
            if ip.strip() and not ip.strip().startswith('#')
        ]
        
        # Remove duplicates while preserving order
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
            nama = ip.replace('/', '_')
            fortigate_address += f'    edit "block_{nama}-m32"\n'
            fortigate_address += f'        set subnet {ip}\n'
            fortigate_address += '    next\n'
        fortigate_address += "end\n"
        
        # Generate FortiGate Group Configuration
        fortigate_group = "config firewall addrgrp\n"
        fortigate_group += f'    edit "{group_name}"\n'
        for ip in ip_list:
            nama = ip.replace('/', '_')
            fortigate_group += f'        append member "block_{nama}-m32"\n'
        fortigate_group += "    next\n"
        fortigate_group += "end\n"
        
        # Generate CheckPoint Configuration
        checkpoint_address = ""
        for ip in ip_list:
            nama = ip.replace('/', '_')
            ip_addr = ip.split('/')[0] if '/' in ip else ip
            checkpoint_address += (
                f'add host name "block_{nama}-m32" '
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
        
        # Parse domains
        domains = [
            d.strip() for d in domains_text.split('\n') 
            if d.strip() and not d.strip().startswith('#')
        ]
        
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
            '8.8.8.8': 'Google DNS (8.8.8.8)',
            '8.8.4.4': 'Google DNS (8.8.4.4)',
            '1.1.1.1': 'Cloudflare DNS (1.1.1.1)',
            '1.0.0.1': 'Cloudflare DNS (1.0.0.1)',
            '9.9.9.9': 'Quad9 DNS (9.9.9.9)',
            '208.67.222.222': 'OpenDNS (208.67.222.222)'
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
            
            dns = dns_server if dns_server != 'default' else None
            return nslookup_detailed(domain, timeout, dns, log_callback)
        
        with ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_domain = {
                executor.submit(process_domain, domain): domain 
                for domain in domains
            }
            
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'domain': domain,
                        'ip_address': 'N/A',
                        'status': 'ERROR',
                        'answer_type': 'N/A',
                        'dns_server': dns_server,
                        'all_ips': [],
                        'response_time': -1
                    })
                    add_log(f"💥 {domain} -> Critical error: {str(e)[:50]}", 'error')
        
        # Sort results alphabetically
        results.sort(key=lambda x: x['domain'])
        
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

@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'error': 'Route not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ============================================
# APPLICATION STARTUP
# ============================================

# Tambahkan fungsi untuk membuka browser otomatis
def open_browser():
    """Open browser after server starts"""
    webbrowser.open('http://127.0.0.1:5000')

# Tambahkan route untuk cek status
@app.route('/api/status')
def status():
    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'host': request.host
    })

# Main entry point
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
    
    # Buka browser otomatis setelah 1 detik
    threading.Timer(1.5, open_browser).start()
    
    # Jalankan server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()