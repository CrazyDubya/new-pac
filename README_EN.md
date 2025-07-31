# PAC Proxy Configuration Demo

## Overview

This repository provides **PAC (Proxy Auto-Configuration)** files and automation tools for intelligent proxy routing. PAC files enable browsers to automatically determine whether to use a proxy server based on the requested URL, providing efficient and selective internet access.

## 🌟 Key Features

- **Smart Proxy Routing**: Automatically route specific domains through proxy servers
- **Extensive Domain Database**: Over 2000+ domains configured for proxy routing
- **Automated Updates**: GitHub Actions workflow for continuous configuration updates
- **Multi-Protocol Support**: Compatible with various proxy protocols (HTTP, SOCKS5)
- **CloudFlare Optimization**: Optimized IP addresses for better performance

## 📁 Repository Structure

```
new-pac/
├── pac                     # Main PAC file with comprehensive domain list
├── pac5                    # Alternative PAC configuration
├── demo/                   # Interactive demo (added)
├── scripts/
│   ├── update_wiki_page.py     # Wiki page automation
│   └── update_v2ray_wiki.py    # V2Ray configuration updates
├── docs/                   # Documentation (Chinese)
├── .github/workflows/      # Automated update workflows
└── CloudFlare优质IP        # Optimized CloudFlare IP addresses
```

## 🚀 Quick Start

### Option 1: Use Pre-configured PAC Files

1. **Download PAC file**:
   ```bash
   wget https://raw.githubusercontent.com/CrazyDubya/new-pac/main/pac
   ```

2. **Configure your browser**:
   - Chrome: Settings → Advanced → System → Open proxy settings → Automatic proxy configuration
   - Firefox: Settings → Network Settings → Automatic proxy configuration URL
   - Safari: Preferences → Advanced → Proxies → Automatic Proxy Configuration

3. **Set PAC URL**:
   ```
   https://raw.githubusercontent.com/CrazyDubya/new-pac/main/pac
   ```

### Option 2: Use the Interactive Demo

Visit our web-based demo to:
- Test PAC file functionality
- Customize domain lists
- Generate personalized configurations
- Validate proxy settings

[**🎯 Launch Interactive Demo**](demo/index.html)

## 🔧 Technical Details

### PAC File Structure

PAC files use JavaScript to determine proxy routing:

```javascript
function FindProxyForURL(url, host) {
    // Check if domain requires proxy
    if (hasOwnProperty.call(domains, suffix)) {
        return "PROXY your-proxy-server:port;";
    }
    return "DIRECT;";  // Direct connection
}
```

### Supported Domains

The configuration includes popular services that may require proxy access:
- Social Media: Facebook, Twitter, Instagram
- Video Platforms: YouTube, Vimeo, Dailymotion
- News & Information: BBC, CNN, Reuters
- Developer Tools: GitHub, Stack Overflow
- And 2000+ more domains

### Automation Features

- **Scheduled Updates**: Every 10 minutes via GitHub Actions
- **Domain Rotation**: Automatic cycling of proxy endpoints
- **Timestamp Management**: Beijing timezone timestamp updates
- **Configuration Validation**: Automatic testing of proxy settings

## 🛠️ Installation & Setup

### Prerequisites

```bash
# Python 3.6+
pip install pytz

# Optional: Node.js for demo server
npm install -g http-server
```

### Local Development

1. **Clone repository**:
   ```bash
   git clone https://github.com/CrazyDubya/new-pac.git
   cd new-pac
   ```

2. **Run automation scripts**:
   ```bash
   python scripts/update_wiki_page.py
   python scripts/update_v2ray_wiki.py
   ```

3. **Start demo server**:
   ```bash
   cd demo
   python -m http.server 8080
   ```

## 📊 Demo Features

Our interactive demo showcases:

1. **PAC File Tester**: Real-time testing of domain routing
2. **Configuration Generator**: Custom PAC file creation
3. **Performance Analyzer**: Proxy speed and reliability testing
4. **Domain Manager**: Add/remove domains from proxy lists
5. **Export Tools**: Download customized configurations

## 🔒 Security & Privacy

- **No Data Collection**: All processing happens client-side
- **Open Source**: Full transparency of all configurations
- **Regular Updates**: Continuous security improvements
- **Minimal Logging**: No personal information stored

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📖 Documentation

- [Chinese Documentation](README.md) - Original Chinese version
- [VPN Setup Tutorials](docs/) - Server configuration guides
- [API Reference](docs/api.md) - Automation script documentation
- [Troubleshooting](docs/troubleshooting.md) - Common issues and solutions

## 📈 Performance

- **Fast Routing**: Optimized domain lookup algorithms
- **Low Latency**: CloudFlare CDN integration
- **High Availability**: Multiple backup proxy endpoints
- **Automatic Failover**: Seamless switching between servers

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/CrazyDubya/new-pac/issues)
- **Discussions**: [GitHub Discussions](https://github.com/CrazyDubya/new-pac/discussions)
- **Wiki**: [Project Wiki](https://github.com/CrazyDubya/new-pac/wiki)

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

**⚠️ Disclaimer**: This tool is provided for educational and research purposes. Users are responsible for compliance with local laws and regulations regarding internet access and proxy usage.