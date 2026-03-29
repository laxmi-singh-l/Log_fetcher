import requests
import json
import re
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
from typing import List, Dict, Any
import urllib.parse

app = Flask(__name__)

# HTML template with network log viewer style
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Log Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Roboto', 'Monaco', 'Courier New', monospace;
            background: #1e1e1e;
            color: #cccccc;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        /* Header Section */
        .header {
            background: #2d2d2d;
            border-bottom: 1px solid #3e3e3e;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .title-section {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .title-section h1 {
            font-size: 18px;
            font-weight: 500;
            color: #ffffff;
        }
        
        .badge {
            background: #007acc;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }
        
        .url-input {
            background: #3c3c3c;
            border: 1px solid #555;
            color: #cccccc;
            padding: 8px 15px;
            border-radius: 4px;
            width: 400px;
            font-family: monospace;
            font-size: 13px;
        }
        
        .url-input:focus {
            outline: none;
            border-color: #007acc;
        }
        
        .btn {
            background: #0e639c;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            transition: background 0.2s;
        }
        
        .btn:hover {
            background: #1177bb;
        }
        
        .btn-clear {
            background: #5a5a5a;
        }
        
        .btn-clear:hover {
            background: #6a6a6a;
        }
        
        /* Toolbar */
        .toolbar {
            background: #252526;
            padding: 8px 20px;
            border-bottom: 1px solid #3e3e3e;
            display: flex;
            gap: 20px;
            font-size: 12px;
        }
        
        .toolbar-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .toolbar-label {
            color: #858585;
        }
        
        .toolbar-value {
            color: #cccccc;
            font-weight: 500;
        }
        
        /* Table Container */
        .table-container {
            flex: 1;
            overflow: auto;
            position: relative;
        }
        
        /* Network Log Table */
        .log-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Segoe UI', 'Roboto', monospace;
            font-size: 12px;
            min-width: 800px;
        }
        
        .log-table thead {
            position: sticky;
            top: 0;
            z-index: 10;
        }
        
        .log-table th {
            background: #2d2d2d;
            color: #bbbbbb;
            padding: 10px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            border-bottom: 1px solid #3e3e3e;
            white-space: nowrap;
            user-select: none;
        }
        
        .log-table th.sortable {
            cursor: pointer;
        }
        
        .log-table th.sortable:hover {
            background: #3e3e3e;
        }
        
        .log-table td {
            padding: 8px 12px;
            border-bottom: 1px solid #2d2d2d;
            white-space: nowrap;
        }
        
        .log-table tbody tr:hover {
            background: #2a2a2a;
        }
        
        /* Status badges */
        .status-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: 500;
            font-size: 11px;
        }
        
        .status-200, .status-201, .status-204 {
            background: #2c5a2c;
            color: #8bc34a;
        }
        
        .status-300 {
            background: #5a4a2c;
            color: #ffc107;
        }
        
        .status-400, .status-401, .status-403, .status-404 {
            background: #5a2c2c;
            color: #ff6b6b;
        }
        
        .status-500 {
            background: #5a2c2c;
            color: #ff4444;
        }
        
        /* Type badges */
        .type-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 500;
        }
        
        .type-xhr {
            background: #0e639c;
            color: white;
        }
        
        .type-fetch {
            background: #6c3483;
            color: white;
        }
        
        .type-js, .type-css {
            background: #2c5a2c;
            color: #8bc34a;
        }
        
        .type-img, .type-media {
            background: #5a4a2c;
            color: #ffc107;
        }
        
        /* Size formatting */
        .size-bytes {
            color: #cccccc;
        }
        
        /* Error message */
        .error-message {
            background: #5a2c2c;
            color: #ff6b6b;
            padding: 12px 20px;
            margin: 10px 20px;
            border-left: 4px solid #ff4444;
            border-radius: 4px;
            font-size: 13px;
        }
        
        /* Loading indicator */
        .loading {
            text-align: center;
            padding: 40px;
            color: #858585;
        }
        
        .loading::after {
            content: '';
            display: inline-block;
            width: 16px;
            height: 16px;
            margin-left: 10px;
            border: 2px solid #858585;
            border-top-color: #007acc;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #1e1e1e;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #3e3e3e;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #4e4e4e;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .url-input {
                width: 250px;
            }
            
            .log-table {
                font-size: 11px;
            }
            
            .log-table th,
            .log-table td {
                padding: 6px 8px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="title-section">
            <h1>🌐 Network Log Viewer</h1>
            <div class="badge">Developer Tools Style</div>
        </div>
        <div class="controls">
            <input type="text" id="urlInput" class="url-input" 
                   placeholder="Enter URL to fetch logs (JSON, HAR, or text)" 
                   value="{{ request_url }}">
            <button class="btn" onclick="fetchLogs()">📡 Fetch Logs</button>
            <button class="btn btn-clear" onclick="clearLogs()">🗑 Clear</button>
        </div>
    </div>
    
    <div class="toolbar">
        <div class="toolbar-item">
            <span class="toolbar-label">Total Requests:</span>
            <span class="toolbar-value" id="totalCount">0</span>
        </div>
        <div class="toolbar-item">
            <span class="toolbar-label">XHR/Fetch:</span>
            <span class="toolbar-value" id="xhrCount">0</span>
        </div>
        <div class="toolbar-item">
            <span class="toolbar-label">Last Updated:</span>
            <span class="toolbar-value" id="timestamp">-</span>
        </div>
    </div>
    
    <div id="errorContainer"></div>
    
    <div class="table-container">
        <table class="log-table" id="logTable">
            <thead>
                <tr>
                    <th class="sortable" onclick="sortTable(0)">Name ⬍</th>
                    <th class="sortable" onclick="sortTable(1)">Status ⬍</th>
                    <th class="sortable" onclick="sortTable(2)">Type ⬍</th>
                    <th class="sortable" onclick="sortTable(3)">Initiator ⬍</th>
                    <th class="sortable" onclick="sortTable(4)">Size ⬍</th>
                    <th class="sortable" onclick="sortTable(5)">Time ⬍</th>
                </tr>
            </thead>
            <tbody id="logTableBody">
                <tr>
                    <td colspan="6" style="text-align: center; padding: 40px; color: #858585;">
                        Enter a URL above to fetch and display logs
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    
    <script>
        let currentLogs = [];
        
        function fetchLogs() {
            const url = document.getElementById('urlInput').value;
            if (!url) {
                showError('Please enter a URL');
                return;
            }
            
            showLoading();
            
            fetch('/fetch-logs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showError(data.error);
                } else {
                    currentLogs = data.logs;
                    renderTable(currentLogs);
                    updateStats(currentLogs);
                    document.getElementById('timestamp').innerText = data.timestamp;
                    hideError();
                }
            })
            .catch(error => {
                showError('Error fetching logs: ' + error.message);
            });
        }
        
        function renderTable(logs) {
            const tbody = document.getElementById('logTableBody');
            
            if (!logs || logs.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 40px; color: #858585;">No logs to display</td></tr>';
                return;
            }
            
            tbody.innerHTML = logs.map(log => `
                <tr>
                    <td title="${escapeHtml(log.name || '-')}">${escapeHtml(truncate(log.name || '-', 60))}</td>
                    <td>${getStatusBadge(log.status)}</td>
                    <td>${getTypeBadge(log.type)}</td>
                    <td>${escapeHtml(log.initiator || '-')}</td>
                    <td>${formatSize(log.size)}</td>
                    <td>${escapeHtml(log.time || '-')}</td>
                </tr>
            `).join('');
        }
        
        function getStatusBadge(status) {
            if (!status) return '<span class="status-badge">-</span>';
            const statusCode = parseInt(status);
            let statusClass = '';
            if (statusCode >= 200 && statusCode < 300) statusClass = 'status-200';
            else if (statusCode >= 300 && statusCode < 400) statusClass = 'status-300';
            else if (statusCode >= 400 && statusCode < 500) statusClass = 'status-400';
            else if (statusCode >= 500) statusClass = 'status-500';
            else statusClass = 'status-badge';
            
            return `<span class="status-badge ${statusClass}">${status}</span>`;
        }
        
        function getTypeBadge(type) {
            if (!type) return '<span class="type-badge">-</span>';
            const typeLower = type.toLowerCase();
            let typeClass = 'type-badge';
            if (typeLower === 'xhr') typeClass += ' type-xhr';
            else if (typeLower === 'fetch') typeClass += ' type-fetch';
            else if (typeLower.includes('js')) typeClass += ' type-js';
            else if (typeLower.includes('css')) typeClass += ' type-css';
            else if (typeLower.includes('img') || typeLower.includes('png') || typeLower.includes('jpg')) typeClass += ' type-img';
            
            return `<span class="${typeClass}">${escapeHtml(type)}</span>`;
        }
        
        function formatSize(size) {
            if (!size) return '-';
            const sizeStr = String(size);
            if (sizeStr.includes('kB') || sizeStr.includes('MB')) return sizeStr;
            
            const bytes = parseFloat(sizeStr);
            if (isNaN(bytes)) return sizeStr;
            
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' kB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        let sortColumn = -1;
        let sortAscending = true;
        
        function sortTable(columnIndex) {
            if (sortColumn === columnIndex) {
                sortAscending = !sortAscending;
            } else {
                sortColumn = columnIndex;
                sortAscending = true;
            }
            
            const sorted = [...currentLogs].sort((a, b) => {
                let aVal, bVal;
                const columns = ['name', 'status', 'type', 'initiator', 'size', 'time'];
                const key = columns[columnIndex];
                
                aVal = a[key] || '';
                bVal = b[key] || '';
                
                if (key === 'status') {
                    aVal = parseInt(aVal) || 0;
                    bVal = parseInt(bVal) || 0;
                } else if (key === 'size') {
                    aVal = parseFloat(aVal) || 0;
                    bVal = parseFloat(bVal) || 0;
                }
                
                if (aVal < bVal) return sortAscending ? -1 : 1;
                if (aVal > bVal) return sortAscending ? 1 : -1;
                return 0;
            });
            
            renderTable(sorted);
            updateTableHeaders(columnIndex);
        }
        
        function updateTableHeaders(sortedColumn) {
            const headers = document.querySelectorAll('.log-table th');
            headers.forEach((header, idx) => {
                header.innerHTML = header.innerHTML.replace(/[⬍⬎]/, '');
                if (idx === sortedColumn) {
                    header.innerHTML += sortAscending ? ' ⬍' : ' ⬎';
                } else {
                    header.innerHTML += ' ⬍';
                }
            });
        }
        
        function updateStats(logs) {
            document.getElementById('totalCount').innerText = logs.length;
            const xhrCount = logs.filter(log => 
                log.type && (log.type.toLowerCase() === 'xhr' || log.type.toLowerCase() === 'fetch')
            ).length;
            document.getElementById('xhrCount').innerText = xhrCount;
        }
        
        function showLoading() {
            const tbody = document.getElementById('logTableBody');
            tbody.innerHTML = '<tr><td colspan="6" class="loading">Loading logs...</td></tr>';
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('errorContainer');
            errorDiv.innerHTML = `<div class="error-message">⚠️ ${escapeHtml(message)}</div>`;
        }
        
        function hideError() {
            const errorDiv = document.getElementById('errorContainer');
            errorDiv.innerHTML = '';
        }
        
        function clearLogs() {
            currentLogs = [];
            renderTable([]);
            updateStats([]);
            document.getElementById('timestamp').innerText = '-';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function truncate(str, length) {
            if (str.length <= length) return str;
            return str.substring(0, length) + '...';
        }
        
        // Allow Enter key to trigger fetch
        document.getElementById('urlInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                fetchLogs();
            }
        });
    </script>
</body>
</html>
"""

def parse_network_logs(data: Any) -> List[Dict[str, Any]]:
    """Parse various log formats into network log format"""
    logs = []
    
    # If data is already in network log format
    if isinstance(data, list) and len(data) > 0:
        for item in data:
            if isinstance(item, dict):
                log = {
                    'name': item.get('name', item.get('url', item.get('file', '-'))),
                    'status': str(item.get('status', item.get('statusCode', '200'))),
                    'type': item.get('type', item.get('method', item.get('contentType', 'xhr'))),
                    'initiator': item.get('initiator', item.get('source', item.get('caller', 'unknown'))),
                    'size': format_size_value(item.get('size', item.get('bytes', item.get('contentLength', '0')))),
                    'time': format_time_value(item.get('time', item.get('duration', item.get('elapsed', '0'))))
                }
                logs.append(log)
        return logs
    
    # If data is a HAR (HTTP Archive) format
    if isinstance(data, dict):
        if 'log' in data and 'entries' in data['log']:
            for entry in data['log']['entries']:
                log = {
                    'name': entry.get('request', {}).get('url', '-').split('/')[-1] or '-',
                    'status': str(entry.get('response', {}).get('status', '200')),
                    'type': entry.get('request', {}).get('method', 'GET'),
                    'initiator': entry.get('initiator', {}).get('type', 'unknown'),
                    'size': format_size_value(entry.get('response', {}).get('bodySize', 0)),
                    'time': f"{entry.get('time', 0):.0f} ms"
                }
                logs.append(log)
            return logs
    
    # Parse text-based logs
    if isinstance(data, str):
        lines = data.strip().split('\n')
        
        # Check if it's a table format (like from the image)
        if '|' in lines[0] and ('Name' in lines[0] or 'name' in lines[0].lower()):
            # Parse markdown table
            headers = [h.strip() for h in lines[0].split('|') if h.strip()]
            for line in lines[2:]:  # Skip header and separator line
                if '|' in line:
                    values = [v.strip() for v in line.split('|') if v.strip()]
                    if len(values) >= len(headers):
                        log = {}
                        for i, header in enumerate(headers):
                            log[header.lower()] = values[i] if i < len(values) else '-'
                        logs.append({
                            'name': log.get('name', '-'),
                            'status': log.get('status', '200'),
                            'type': log.get('type', 'xhr'),
                            'initiator': log.get('initiator', 'unknown'),
                            'size': log.get('size', '0'),
                            'time': log.get('time', '0 ms')
                        })
            return logs
        
        # Parse JSON lines format
        for line in lines:
            try:
                item = json.loads(line)
                if isinstance(item, dict):
                    logs.append({
                        'name': item.get('name', item.get('url', '-')),
                        'status': str(item.get('status', '200')),
                        'type': item.get('type', item.get('method', 'xhr')),
                        'initiator': item.get('initiator', 'unknown'),
                        'size': format_size_value(item.get('size', item.get('bytes', 0))),
                        'time': format_time_value(item.get('time', item.get('duration', 0)))
                    })
            except json.JSONDecodeError:
                continue
    
    return logs

def format_size_value(size):
    """Format size value to human readable format"""
    if isinstance(size, str):
        if 'kB' in size or 'MB' in size or 'B' in size:
            return size
        try:
            size = float(size)
        except:
            return size
    
    if isinstance(size, (int, float)):
        if size < 1024:
            return f"{size:.0f} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} kB"
        else:
            return f"{size/(1024*1024):.1f} MB"
    
    return str(size)

def format_time_value(time):
    """Format time value to include ms"""
    if isinstance(time, str):
        if 'ms' in time or 's' in time:
            return time
        try:
            time = float(time)
        except:
            return time
    
    if isinstance(time, (int, float)):
        if time < 1000:
            return f"{time:.0f} ms"
        else:
            return f"{time/1000:.2f} s"
    
    return str(time)

@app.route('/')
def index():
    """Render the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/fetch-logs', methods=['POST'])
def fetch_logs():
    """Fetch logs from provided URL"""
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'Please provide a URL'})
        
        # Fetch data from URL
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        content = response.text
        
        # Try to parse as JSON
        parsed_data = None
        if 'application/json' in content_type or content.strip().startswith(('{', '[')):
            try:
                parsed_data = response.json()
            except:
                parsed_data = content
        else:
            parsed_data = content
        
        # Parse into network log format
        logs = parse_network_logs(parsed_data)
        
        if not logs:
            # Create sample data if no logs found
            logs = [
                {
                    'name': 'operatorParams',
                    'status': '200',
                    'type': 'xhr',
                    'initiator': 'chat_load.js:116',
                    'size': '1.0 kB',
                    'time': '159 ms'
                },
                {
                    'name': 'reload?k=6LcA2tEZAAAAaJJ7FTYTF9cZ4NL3ShgB...',
                    'status': '200',
                    'type': 'xhr',
                    'initiator': 'recaptcha_en.js:1115',
                    'size': '23.8 kB',
                    'time': '250 ms'
                },
                {
                    'name': 'cir?k=6LcA2tEZAAAAaJJ7FTYTF9cZ4NL3ShgBCB...',
                    'status': '200',
                    'type': 'fetch',
                    'initiator': 'recaptcha_en.js:1570',
                    'size': '0.3 kB',
                    'time': '112 ms'
                },
                {
                    'name': 'browserinfo?fsid=8938489990766186326&bl=bob...',
                    'status': '200',
                    'type': 'xhr',
                    'initiator': 'm=b_tp:313',
                    'size': '0.3 kB',
                    'time': '120 ms'
                }
            ]
        
        return jsonify({
            'logs': logs[:500],  # Limit to 500 logs for performance
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'})
    except Exception as e:
        return jsonify({'error': f'Error processing logs: {str(e)}'})

if __name__ == '__main__':
    import subprocess
    import sys
    
    # Install required packages
    required_packages = ['flask', 'requests']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("=" * 60)
    print("🌐 Network Log Viewer Started")
    print("=" * 60)
    print(f"📍 Access at: http://127.0.0.1:5000")
    print(f"📊 Style: Developer Tools Network Tab")
    print("=" * 60)
    print("\nTips:")
    print("  • Enter any URL that returns logs in JSON or text format")
    print("  • Supports HAR format, JSON arrays, and text tables")
    print("  • Click column headers to sort")
    print("  • Sample data is shown if URL doesn't return logs")
    print("=" * 60)
    
    app.run(debug=True, host='127.0.0.1', port=5000)
