#!/usr/bin/env python3
"""Capture Network-Scanner screenshots using Playwright HTML mockups.

Usage:
    python scripts/capture-screenshots.py

Prerequisites:
    pip install playwright
    python -m playwright install chromium

Screenshots are saved to docs/screenshots/ for use in the README.
"""
from playwright.sync_api import sync_playwright
import time
import os

SCREENSHOT_DIR = os.environ.get("SCREENSHOT_DIR", "docs/screenshots")

NETWORK_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Scanner - Network Map</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0f1a; color: #e2e8f0; height: 100vh; display: flex; }
        .sidebar { width: 260px; background: #111827; padding: 20px; border-right: 1px solid #1f2937; }
        .logo { font-size: 20px; font-weight: 700; color: #22c55e; margin-bottom: 32px; }
        .nav-item { padding: 12px 16px; border-radius: 8px; margin-bottom: 4px; font-size: 14px; color: #9ca3af; }
        .nav-item.active { background: #22c55e; color: #0a0f1a; font-weight: 600; }
        .main { flex: 1; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .header h1 { font-size: 24px; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
        .stat-card { background: #111827; border-radius: 12px; padding: 20px; border: 1px solid #1f2937; }
        .stat-label { font-size: 12px; color: #9ca3af; text-transform: uppercase; margin-bottom: 8px; }
        .stat-value { font-size: 28px; font-weight: 700; }
        .stat-value.green { color: #22c55e; }
        .stat-value.yellow { color: #eab308; }
        .stat-value.red { color: #ef4444; }
        .stat-value.blue { color: #3b82f6; }
        .map-container { background: #111827; border-radius: 12px; padding: 24px; border: 1px solid #1f2937; height: 400px; position: relative; }
        .node { position: absolute; padding: 8px 12px; border-radius: 8px; font-size: 11px; font-weight: 600; }
        .node.router { background: #1e40af; color: white; }
        .node.switch { background: #7c3aed; color: white; }
        .node.server { background: #059669; color: white; }
        .node.device { background: #d97706; color: white; }
        .node.firewall { background: #dc2626; color: white; }
    </style>
</head>
<body>
    <div class="sidebar">
        <div class="logo">🔍 Network Scanner</div>
        <div class="nav-item active">🗺️ Network Map</div>
        <div class="nav-item">🛡️ Vulnerabilities</div>
        <div class="nav-item">📊 Scan Results</div>
    </div>
    <div class="main">
        <div class="header"><h1>Network Map</h1></div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-label">Hosts Discovered</div><div class="stat-value blue">24</div></div>
            <div class="stat-card"><div class="stat-label">Active</div><div class="stat-value green">21</div></div>
            <div class="stat-card"><div class="stat-label">Vulnerabilities</div><div class="stat-value red">7</div></div>
            <div class="stat-card"><div class="stat-label">Open Ports</div><div class="stat-value yellow">156</div></div>
        </div>
        <div class="map-container">
            <div class="node firewall" style="top: 20px; left: 50%; transform: translateX(-50%);">🔥 Firewall</div>
            <div class="node router" style="top: 80px; left: 30%;">🌐 Router</div>
            <div class="node router" style="top: 80px; left: 60%;">🌐 Router 2</div>
            <div class="node switch" style="top: 160px; left: 20%;">🔌 Core Switch</div>
            <div class="node switch" style="top: 160px; left: 50%;">🔌 Dist Switch</div>
            <div class="node switch" style="top: 160px; left: 75%;">🔌 Access SW</div>
            <div class="node server" style="top: 260px; left: 10%;">🖥️ Web Server</div>
            <div class="node server" style="top: 260px; left: 35%;">🗄️ DB Server</div>
            <div class="node server" style="top: 260px; left: 60%;">📧 Mail Server</div>
            <div class="node device" style="top: 340px; left: 25%;">💻 Workstation 1</div>
            <div class="node device" style="top: 340px; left: 55%;">💻 Workstation 2</div>
        </div>
    </div>
</body></html>
"""

VULN_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Network Scanner - Vulnerabilities</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0f1a; color: #e2e8f0; padding: 40px; }
        h1 { font-size: 24px; margin-bottom: 24px; }
        .vuln-list { display: flex; flex-direction: column; gap: 12px; }
        .vuln-card { background: #111827; border-radius: 12px; padding: 20px; border-left: 4px solid; }
        .vuln-card.critical { border-left-color: #ef4444; }
        .vuln-card.high { border-left-color: #f97316; }
        .vuln-card.medium { border-left-color: #eab308; }
        .vuln-card.low { border-left-color: #22c55e; }
        .vuln-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .vuln-title { font-weight: 600; font-size: 16px; }
        .severity { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; text-transform: uppercase; }
        .severity.critical { background: #7f1d1d; color: #fca5a5; }
        .severity.high { background: #7c2d12; color: #fed7aa; }
        .severity.medium { background: #713f12; color: #fef08a; }
        .severity.low { background: #14532d; color: #bbf7d0; }
        .vuln-desc { font-size: 13px; color: #9ca3af; line-height: 1.6; margin-bottom: 12px; }
        .vuln-meta { display: flex; gap: 16px; font-size: 12px; color: #6b7280; }
    </style>
</head>
<body>
    <h1>🛡️ Vulnerability Report</h1>
    <div class="vuln-list">
        <div class="vuln-card critical"><div class="vuln-header"><span class="vuln-title">CVE-2024-21762 - FortiOS RCE</span><span class="severity critical">Critical</span></div><div class="vuln-desc">Remote code execution vulnerability in FortiOS SSL VPN.</div><div class="vuln-meta"><span>🖥️ 10.0.0.1</span><span>⏱️ CVSS: 9.8</span></div></div>
        <div class="vuln-card high"><div class="vuln-header"><span class="vuln-title">CVE-2024-3400 - PAN-OS Command Injection</span><span class="severity high">High</span></div><div class="vuln-desc">Command injection vulnerability in GlobalProtect gateway.</div><div class="vuln-meta"><span>🖥️ 10.0.0.2</span><span>⏱️ CVSS: 8.1</span></div></div>
        <div class="vuln-card medium"><div class="vuln-header"><span class="vuln-title">Open SSH Port with Weak Ciphers</span><span class="severity medium">Medium</span></div><div class="vuln-desc">SSH server supports weak cryptographic algorithms.</div><div class="vuln-meta"><span>🖥️ 10.0.1.10</span><span>⏱️ CVSS: 5.3</span></div></div>
        <div class="vuln-card low"><div class="vuln-header"><span class="vuln-title">HTTP Server Banner Disclosure</span><span class="severity low">Low</span></div><div class="vuln-desc">Web server exposes version information in HTTP headers.</div><div class="vuln-meta"><span>🖥️ 10.0.1.10</span><span>⏱️ CVSS: 2.6</span></div></div>
    </div>
</body></html>
"""

SCAN_HTML = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Network Scanner - Scan Results</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #0a0f1a; color: #e2e8f0; padding: 40px; }
        h1 { font-size: 24px; margin-bottom: 24px; }
        table { width: 100%; border-collapse: collapse; background: #111827; border-radius: 12px; overflow: hidden; }
        th { text-align: left; padding: 14px 16px; background: #1f2937; font-size: 12px; text-transform: uppercase; color: #9ca3af; }
        td { padding: 14px 16px; border-bottom: 1px solid #1f2937; font-size: 14px; }
        .host { font-weight: 600; }
        .port { color: #22c55e; font-family: monospace; }
        .service { color: #3b82f6; }
        .status { padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
        .open { background: #14532d; color: #bbf7d0; }
        .filtered { background: #713f12; color: #fef08a; }
    </style>
</head>
<body>
    <h1>📊 Scan Results</h1>
    <table>
        <thead><tr><th>Host</th><th>IP</th><th>Port</th><th>Service</th><th>Version</th><th>Status</th></tr></thead>
        <tbody>
            <tr><td class="host">Web Server</td><td>10.0.1.10</td><td class="port">80</td><td class="service">HTTP</td><td>Apache/2.4.58</td><td><span class="status open">Open</span></td></tr>
            <tr><td class="host">Web Server</td><td>10.0.1.10</td><td class="port">443</td><td class="service">HTTPS</td><td>Apache/2.4.58</td><td><span class="status open">Open</span></td></tr>
            <tr><td class="host">DB Server</td><td>10.0.1.20</td><td class="port">5432</td><td class="service">PostgreSQL</td><td>16.1</td><td><span class="status open">Open</span></td></tr>
            <tr><td class="host">Mail Server</td><td>10.0.1.30</td><td class="port">25</td><td class="service">SMTP</td><td>Postfix</td><td><span class="status open">Open</span></td></tr>
            <tr><td class="host">Firewall</td><td>10.0.0.1</td><td class="port">443</td><td class="service">HTTPS</td><td>FortiOS 7.2</td><td><span class="status open">Open</span></td></tr>
        </tbody>
    </table>
</body></html>
"""

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def capture_screenshots():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        
        for name, html in [("network-map.png", NETWORK_HTML), ("vulnerabilities.png", VULN_HTML), ("scan-results.png", SCAN_HTML)]:
            print(f"Capturing {name}...")
            page.set_content(html)
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            path = os.path.join(SCREENSHOT_DIR, name)
            page.screenshot(path=path, full_page=False)
            print(f"Saved: {path} ({os.path.getsize(path):,} bytes)")
        
        browser.close()
    print("\nAll screenshots captured successfully!")

if __name__ == "__main__":
    capture_screenshots()
