// PAC Proxy Demo JavaScript
class PACDemo {
    constructor() {
        this.domains = new Set();
        this.proxyServer = "162.159.138.110:443";
        this.performanceChart = null;
        this.performanceData = [];
        
        this.init();
    }

    init() {
        this.loadDefaultDomains();
        this.renderDomainList();
        this.generatePACCode();
        this.initPerformanceChart();
        this.startPerformanceMonitoring();
    }

    loadDefaultDomains() {
        // Sample domains from the PAC file
        const defaultDomains = [
            "facebook.com", "twitter.com", "youtube.com", "google.com",
            "instagram.com", "github.com", "stackoverflow.com", "wikipedia.org",
            "reddit.com", "twitch.tv", "discord.com", "telegram.org",
            "dropbox.com", "netflix.com", "spotify.com", "amazon.com",
            "bbc.com", "cnn.com", "reuters.com", "bloomberg.com",
            "slideshare.net", "pinterest.com", "tumblr.com", "vimeo.com"
        ];
        
        defaultDomains.forEach(domain => this.domains.add(domain));
    }

    renderDomainList() {
        const domainList = document.getElementById('domainList');
        domainList.innerHTML = '';
        
        const sortedDomains = Array.from(this.domains).sort();
        
        sortedDomains.forEach(domain => {
            const domainItem = document.createElement('div');
            domainItem.className = 'd-flex justify-content-between align-items-center py-1 border-bottom';
            domainItem.innerHTML = `
                <span class="text-truncate">${domain}</span>
                <button class="btn btn-sm btn-outline-danger" onclick="demo.removeDomain('${domain}')">
                    <i class="fas fa-times"></i>
                </button>
            `;
            domainList.appendChild(domainItem);
        });

        // Update stats
        document.getElementById('totalDomains').textContent = this.domains.size.toLocaleString();
    }

    addDomain() {
        const input = document.getElementById('newDomain');
        const domain = input.value.trim().toLowerCase();
        
        if (domain && this.isValidDomain(domain)) {
            this.domains.add(domain);
            input.value = '';
            this.renderDomainList();
            this.generatePACCode();
            this.showNotification('Domain added successfully!', 'success');
        } else {
            this.showNotification('Please enter a valid domain name.', 'error');
        }
    }

    removeDomain(domain) {
        this.domains.delete(domain);
        this.renderDomainList();
        this.generatePACCode();
        this.showNotification('Domain removed successfully!', 'warning');
    }

    isValidDomain(domain) {
        const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
        return domainRegex.test(domain);
    }

    generatePACCode() {
        const proxyServer = document.getElementById('proxyServer').value || this.proxyServer;
        const domainsArray = Array.from(this.domains);
        
        const pacCode = `function FindProxyForURL(url, host) {
    var proxy = "PROXY ${proxyServer};";
    var direct = "DIRECT;";
    
    var domains = {
${domainsArray.map(domain => `        "${domain}": 1`).join(',\n')}
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
}`;

        document.getElementById('pacCode').textContent = pacCode;
        
        // Re-highlight code
        if (window.Prism) {
            Prism.highlightAll();
        }
    }

    testPAC() {
        const testUrl = document.getElementById('testUrl').value;
        const resultDiv = document.getElementById('testResult');
        
        if (!testUrl) {
            this.showNotification('Please enter a URL to test.', 'error');
            return;
        }

        // Show testing status
        resultDiv.innerHTML = `
            <div class="alert alert-info">
                <span class="status-indicator status-testing"></span>
                Testing configuration for: <strong>${testUrl}</strong>
            </div>
        `;

        // Simulate PAC testing
        setTimeout(() => {
            try {
                const url = new URL(testUrl);
                const hostname = url.hostname;
                const result = this.checkDomainInPAC(hostname);
                
                const proxyServer = document.getElementById('proxyServer').value || this.proxyServer;
                const action = result ? `PROXY ${proxyServer}` : 'DIRECT';
                const statusClass = result ? 'success' : 'primary';
                const statusIcon = result ? 'route' : 'link';
                
                resultDiv.innerHTML = `
                    <div class="alert alert-${statusClass}">
                        <h6><i class="fas fa-${statusIcon} me-2"></i>Test Result</h6>
                        <p><strong>URL:</strong> ${testUrl}</p>
                        <p><strong>Host:</strong> ${hostname}</p>
                        <p><strong>Action:</strong> ${action}</p>
                        <p><strong>Status:</strong> ${result ? 'Will use proxy' : 'Direct connection'}</p>
                    </div>
                `;

                // Update performance data
                this.addPerformanceData(result ? 'proxy' : 'direct');
                
            } catch (error) {
                resultDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Invalid URL format. Please enter a valid URL.
                    </div>
                `;
            }
        }, 1000);
    }

    checkDomainInPAC(hostname) {
        // Check if hostname or any parent domain is in our domains list
        const parts = hostname.split('.');
        for (let i = 0; i < parts.length - 1; i++) {
            const domain = parts.slice(i).join('.');
            if (this.domains.has(domain)) {
                return true;
            }
        }
        return false;
    }

    copyPAC() {
        const pacCode = document.getElementById('pacCode').textContent;
        navigator.clipboard.writeText(pacCode).then(() => {
            this.showNotification('PAC configuration copied to clipboard!', 'success');
        }).catch(() => {
            this.showNotification('Failed to copy to clipboard.', 'error');
        });
    }

    downloadPAC() {
        const pacCode = document.getElementById('pacCode').textContent;
        const blob = new Blob([pacCode], { type: 'application/x-ns-proxy-autoconfig' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = 'proxy.pac';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showNotification('PAC file downloaded successfully!', 'success');
    }

    initPerformanceChart() {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        
        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.1)',
                    tension: 0.1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 200
                    },
                    x: {
                        display: false
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                elements: {
                    point: {
                        radius: 2
                    }
                }
            }
        });
    }

    startPerformanceMonitoring() {
        this.lastUpdateTime = 0;
        this.updateInterval = 2000; // 2 seconds
        this.lastMetrics = {}; // Cache for change detection
        this.animationFrameId = null;
        
        this.scheduleNextUpdate();
    }

    scheduleNextUpdate() {
        this.animationFrameId = requestAnimationFrame((currentTime) => {
            if (currentTime - this.lastUpdateTime >= this.updateInterval) {
                this.updatePerformanceMetrics();
                this.lastUpdateTime = currentTime;
            }
            this.scheduleNextUpdate();
        });
    }

    updatePerformanceMetrics() {
        // Simulate real-time metrics
        const newMetrics = {
            latency: Math.floor(Math.random() * 50) + 70, // 70-120ms
            activeProxies: Math.floor(Math.random() * 5) + 10,
            successRate: (98 + Math.random() * 2).toFixed(1)
        };
        
        // Only update if values have changed significantly
        const shouldUpdate = this.shouldUpdateMetrics(newMetrics);
        
        if (shouldUpdate.chart) {
            this.updateChart(newMetrics.latency);
        }
        
        if (shouldUpdate.stats) {
            // Batch DOM updates using requestAnimationFrame for smooth updates
            requestAnimationFrame(() => {
                this.batchUpdateStats(newMetrics);
            });
        }
        
        this.lastMetrics = { ...newMetrics };
    }

    shouldUpdateMetrics(newMetrics) {
        const thresholds = {
            latency: 5,     // Update if latency changes by more than 5ms
            activeProxies: 1, // Update if proxy count changes
            successRate: 0.1  // Update if success rate changes by more than 0.1%
        };
        
        return {
            chart: !this.lastMetrics.latency || 
                   Math.abs(newMetrics.latency - this.lastMetrics.latency) >= thresholds.latency,
            stats: !this.lastMetrics.activeProxies || 
                   newMetrics.activeProxies !== this.lastMetrics.activeProxies ||
                   Math.abs(parseFloat(newMetrics.successRate) - parseFloat(this.lastMetrics.successRate || 0)) >= thresholds.successRate
        };
    }

    updateChart(latency) {
        const time = new Date().toLocaleTimeString();
        
        // Update chart data
        if (this.performanceChart.data.labels.length > 20) {
            this.performanceChart.data.labels.shift();
            this.performanceChart.data.datasets[0].data.shift();
        }
        
        this.performanceChart.data.labels.push(time);
        this.performanceChart.data.datasets[0].data.push(latency);
        
        // Use more efficient chart update with animation disabled
        this.performanceChart.update('none');
    }

    batchUpdateStats(metrics) {
        // Batch all DOM updates together to minimize layout thrashing
        const updates = [
            { id: 'avgLatency', value: metrics.latency + 'ms' },
            { id: 'activeProxies', value: metrics.activeProxies },
            { id: 'successRate', value: metrics.successRate + '%' }
        ];
        
        // Use document fragment for efficient DOM updates
        updates.forEach(update => {
            const element = document.getElementById(update.id);
            if (element && element.textContent !== update.value.toString()) {
                element.textContent = update.value;
            }
        });
    }

    addPerformanceData(type) {
        const timestamp = new Date().toLocaleTimeString();
        this.performanceData.push({
            timestamp,
            type,
            latency: Math.floor(Math.random() * 100) + 50
        });
    }

    stopPerformanceMonitoring() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }

    showNotification(message, type) {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 3000);
    }
}

// Global functions for button handlers
let demo;

function scrollToDemo() {
    document.getElementById('demo').scrollIntoView({ behavior: 'smooth' });
}

function testPAC() {
    demo.testPAC();
}

function addDomain() {
    demo.addDomain();
}

function copyPAC() {
    demo.copyPAC();
}

function downloadPAC() {
    demo.downloadPAC();
}

// Initialize demo when page loads
document.addEventListener('DOMContentLoaded', function() {
    demo = new PACDemo();
    
    // Add enter key handler for domain input
    document.getElementById('newDomain').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addDomain();
        }
    });
    
    // Add change handlers for input fields
    document.getElementById('proxyServer').addEventListener('input', function() {
        demo.generatePACCode();
    });
    
    // Animate stats on load
    setTimeout(() => {
        const stats = document.querySelectorAll('.stats-card h3');
        stats.forEach((stat, index) => {
            setTimeout(() => {
                stat.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    stat.style.transform = 'scale(1)';
                }, 200);
            }, index * 100);
        });
    }, 500);
});