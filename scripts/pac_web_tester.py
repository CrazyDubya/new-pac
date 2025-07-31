#!/usr/bin/env python3
"""
PAC Testing Web Server
Provides a web interface for testing PAC configurations
"""

import os
import json
import re
from flask import Flask, render_template_string, request, jsonify, send_file
from urllib.parse import urlparse
import tempfile
from typing import Dict, List, Tuple

app = Flask(__name__)

class PACTester:
    """PAC Configuration Tester"""
    
    def __init__(self):
        self.domains = set()
        self.load_domains_from_pac()
    
    def load_domains_from_pac(self):
        """Load domains from PAC files"""
        pac_files = ['pac', 'pac5']
        
        for pac_file in pac_files:
            if os.path.exists(pac_file):
                try:
                    with open(pac_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract domains from PAC file
                    domain_matches = re.findall(r'"([^"]+)"\s*:\s*1', content)
                    for domain in domain_matches:
                        self.domains.add(domain)
                        
                except Exception as e:
                    print(f"Error loading {pac_file}: {e}")
    
    def test_url(self, url: str, proxy_server: str = "162.159.138.110:443") -> Dict:
        """Test if URL should use proxy"""
        try:
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname or parsed_url.netloc
            
            # Check if domain matches any in our list
            uses_proxy = self.check_domain_match(hostname)
            
            result = {
                'url': url,
                'hostname': hostname,
                'uses_proxy': uses_proxy,
                'action': f'PROXY {proxy_server};' if uses_proxy else 'DIRECT;',
                'reason': self.get_match_reason(hostname) if uses_proxy else 'Domain not in proxy list'
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'url': url
            }
    
    def check_domain_match(self, hostname: str) -> bool:
        """Check if hostname matches any domain in the list"""
        if not hostname:
            return False
            
        # Check exact match
        if hostname in self.domains:
            return True
        
        # Check parent domains
        parts = hostname.split('.')
        for i in range(len(parts)):
            parent_domain = '.'.join(parts[i:])
            if parent_domain in self.domains:
                return True
        
        return False
    
    def get_match_reason(self, hostname: str) -> str:
        """Get reason why hostname matched"""
        if hostname in self.domains:
            return f"Exact match: {hostname}"
        
        parts = hostname.split('.')
        for i in range(1, len(parts)):
            parent_domain = '.'.join(parts[i:])
            if parent_domain in self.domains:
                return f"Parent domain match: {parent_domain}"
        
        return "Unknown match"
    
    def generate_pac_content(self, proxy_server: str, custom_domains: List[str] = None) -> str:
        """Generate PAC file content"""
        domains_to_use = custom_domains or list(self.domains)
        
        pac_template = """function FindProxyForURL(url, host) {
    var proxy = "PROXY PROXY_SERVER;";
    var direct = "DIRECT;";
    
    var domains = {
DOMAIN_LIST
    };
    
    var hasOwnProperty = Object.hasOwnProperty;
    
    var suffix;
    var pos = host.lastIndexOf('.');
    while(1) {
        suffix = host.substring(pos + 1);
        if (hasOwnProperty.call(domains, suffix)) {
            return proxy;
        }
        if (pos <= 0) {
            break;
        }
        pos = host.lastIndexOf('.', pos - 1);
    }
    return direct;
}"""
        
        # Format domain list
        domain_entries = [f'        "{domain}": 1' for domain in sorted(domains_to_use)]
        domain_list = ',\n'.join(domain_entries)
        
        # Replace placeholders
        pac_content = pac_template.replace('PROXY_SERVER', proxy_server)
        pac_content = pac_content.replace('DOMAIN_LIST', domain_list)
        
        return pac_content

# Global tester instance
tester = PACTester()

@app.route('/')
def index():
    """Main page"""
    template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PAC Configuration Tester</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .test-result { margin-top: 20px; }
        .domain-info { background: #f8f9fa; padding: 15px; border-radius: 5px; }
        .pac-code { background: #2d3748; color: #e2e8f0; padding: 20px; border-radius: 5px; font-family: monospace; }
    </style>
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center mb-4">PAC Configuration Tester</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>URL Tester</h5>
                    </div>
                    <div class="card-body">
                        <form id="testForm">
                            <div class="mb-3">
                                <label for="testUrl" class="form-label">Test URL:</label>
                                <input type="url" class="form-control" id="testUrl" 
                                       placeholder="https://example.com" required>
                            </div>
                            <div class="mb-3">
                                <label for="proxyServer" class="form-label">Proxy Server:</label>
                                <input type="text" class="form-control" id="proxyServer" 
                                       value="162.159.138.110:443">
                            </div>
                            <button type="submit" class="btn btn-primary">Test URL</button>
                        </form>
                        
                        <div id="testResult" class="test-result"></div>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Domain Statistics</h5>
                    </div>
                    <div class="card-body domain-info">
                        <p><strong>Total Domains:</strong> {{ domain_count }}</p>
                        <p><strong>Sample Domains:</strong></p>
                        <ul>
                            {% for domain in sample_domains %}
                            <li>{{ domain }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header d-flex justify-content-between">
                        <h5>Generated PAC Configuration</h5>
                        <button class="btn btn-sm btn-outline-primary" onclick="downloadPAC()">Download PAC</button>
                    </div>
                    <div class="card-body">
                        <div class="pac-code" id="pacCode">
                            <!-- PAC code will be loaded here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('testForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = document.getElementById('testUrl').value;
            const proxy = document.getElementById('proxyServer').value;
            
            fetch('/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: url, proxy: proxy})
            })
            .then(response => response.json())
            .then(data => {
                displayResult(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
        
        function displayResult(data) {
            const resultDiv = document.getElementById('testResult');
            
            if (data.error) {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>Error:</strong> ${data.error}
                    </div>
                `;
                return;
            }
            
            const alertClass = data.uses_proxy ? 'alert-warning' : 'alert-success';
            const icon = data.uses_proxy ? '🔀' : '🔗';
            
            resultDiv.innerHTML = `
                <div class="alert ${alertClass}">
                    <h6>${icon} Test Result</h6>
                    <p><strong>URL:</strong> ${data.url}</p>
                    <p><strong>Hostname:</strong> ${data.hostname}</p>
                    <p><strong>Action:</strong> ${data.action}</p>
                    <p><strong>Reason:</strong> ${data.reason}</p>
                </div>
            `;
        }
        
        function downloadPAC() {
            const proxy = document.getElementById('proxyServer').value;
            window.location.href = `/download-pac?proxy=${encodeURIComponent(proxy)}`;
        }
        
        // Load PAC code on page load
        fetch('/generate-pac')
        .then(response => response.text())
        .then(data => {
            document.getElementById('pacCode').textContent = data;
        });
    </script>
</body>
</html>
    """
    
    sample_domains = list(tester.domains)[:10] if tester.domains else ['No domains loaded']
    
    return render_template_string(template, 
                                domain_count=len(tester.domains),
                                sample_domains=sample_domains)

@app.route('/test', methods=['POST'])
def test_url():
    """Test URL endpoint"""
    data = request.get_json()
    url = data.get('url', '')
    proxy = data.get('proxy', '162.159.138.110:443')
    
    result = tester.test_url(url, proxy)
    return jsonify(result)

@app.route('/generate-pac')
def generate_pac():
    """Generate PAC content endpoint"""
    proxy = request.args.get('proxy', '162.159.138.110:443')
    pac_content = tester.generate_pac_content(proxy)
    return pac_content

@app.route('/download-pac')
def download_pac():
    """Download PAC file endpoint"""
    proxy = request.args.get('proxy', '162.159.138.110:443')
    pac_content = tester.generate_pac_content(proxy)
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pac', delete=False) as f:
        f.write(pac_content)
        temp_path = f.name
    
    try:
        return send_file(temp_path, as_attachment=True, download_name='proxy.pac')
    finally:
        os.remove(temp_path)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    return jsonify({
        'total_domains': len(tester.domains),
        'domains': list(tester.domains)[:100],  # Limit to first 100
        'sample_domains': list(tester.domains)[:10]
    })

if __name__ == '__main__':
    print("🚀 Starting PAC Testing Web Server...")
    print("📱 Open http://localhost:5000 in your browser")
    print("🔧 Press Ctrl+C to stop the server")
    
    # Configure debug and host based on environment
    debug_mode = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    host_address = os.getenv('FLASK_HOST', '127.0.0.1')
    
    app.run(debug=debug_mode, host=host_address, port=5000)