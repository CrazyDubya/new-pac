#!/usr/bin/env python3
"""
Enhanced PAC Configuration Manager
Improved version with error handling, logging, and additional features
"""

import re
import os
import json
import base64
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

try:
    import pytz
except ImportError:
    print("Warning: pytz not installed. Using system timezone.")
    pytz = None


class PACConfigManager:
    """Enhanced PAC Configuration Manager with improved error handling and features"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.setup_logging()
        self.config = self.load_config(config_file)
        self.stats = {
            'domains_updated': 0,
            'files_processed': 0,
            'errors': 0
        }
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('pac_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_config(self, config_file: Optional[str] = None) -> Dict:
        """Load configuration from file or use defaults"""
        default_config = {
            'proxy_servers': [
                '162.159.138.110:443',
                '172.67.243.247:443',
                '2402:d0c0:0:2e8::11:25'
            ],
            'backup_dir': 'backups',
            'timezone': 'Asia/Shanghai',
            'domain_increment': 1,
            'auto_backup': True
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    self.logger.info(f"Loaded configuration from {config_file}")
            except Exception as e:
                self.logger.warning(f"Failed to load config file: {e}. Using defaults.")
        
        return default_config
    
    def get_current_time(self) -> str:
        """Get current time in specified timezone"""
        if pytz:
            try:
                tz = pytz.timezone(self.config['timezone'])
                current_time = datetime.now(tz).strftime("%Y年%m月%d日%H点%M分")
            except Exception as e:
                self.logger.warning(f"Timezone error: {e}. Using system time.")
                current_time = datetime.now().strftime("%Y年%m月%d日%H点%M分")
        else:
            current_time = datetime.now().strftime("%Y年%m月%d日%H点%M分")
        
        return current_time
    
    def backup_file(self, file_path: str) -> bool:
        """Create backup of file before modification"""
        if not self.config['auto_backup']:
            return True
            
        try:
            backup_dir = Path(self.config['backup_dir'])
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{Path(file_path).name}.{timestamp}.bak"
            backup_path = backup_dir / backup_name
            
            with open(file_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            self.logger.info(f"Created backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
    
    def update_pac_file(self, pac_file: str, new_proxy: Optional[str] = None) -> bool:
        """Update PAC file with new proxy server and timestamp"""
        try:
            if not os.path.exists(pac_file):
                self.logger.error(f"PAC file not found: {pac_file}")
                return False
            
            # Create backup
            if not self.backup_file(pac_file):
                self.logger.warning("Continuing without backup...")
            
            with open(pac_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update proxy server if provided
            if new_proxy:
                proxy_pattern = r'var proxy = "PROXY [^;]+;";'
                new_proxy_line = f'var proxy = "PROXY {new_proxy};";'
                content = re.sub(proxy_pattern, new_proxy_line, content)
                self.logger.info(f"Updated proxy server to: {new_proxy}")
            
            # Update timestamp in comments
            current_time = self.get_current_time()
            timestamp_patterns = [
                r'北京时间\d{4}年\d{2}月\d{2}日\d{2}点\d{2}分更新',
                r'// Updated: [^\n]*'
            ]
            
            new_timestamp = f"北京时间{current_time}更新"
            for pattern in timestamp_patterns:
                content = re.sub(pattern, new_timestamp, content)
            
            # Add timestamp comment if not present
            if '北京时间' not in content and '// Updated:' not in content:
                header_comment = f"// PAC Configuration - Updated: {new_timestamp}\n"
                content = header_comment + content
            
            with open(pac_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.stats['files_processed'] += 1
            self.logger.info(f"Successfully updated PAC file: {pac_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update PAC file {pac_file}: {e}")
            self.stats['errors'] += 1
            return False
    
    def update_domain_list(self, domains_file: str, operation: str = 'increment') -> bool:
        """Update domain list by incrementing numbers or other operations"""
        try:
            if not os.path.exists(domains_file):
                self.logger.error(f"Domains file not found: {domains_file}")
                return False
            
            # Create backup
            if not self.backup_file(domains_file):
                self.logger.warning("Continuing without backup...")
            
            with open(domains_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if operation == 'increment':
                # Increment numbers in domain names
                def increment_match(match):
                    prefix = match.group(1)
                    number = int(match.group(2))
                    suffix = match.group(3)
                    new_number = number + self.config['domain_increment']
                    return f"{prefix}{new_number}{suffix}"
                
                # Pattern for domains like fan123.example.com
                domain_pattern = r'([a-zA-Z]+)(\d+)(\.[\w\.]+)'
                content = re.sub(domain_pattern, increment_match, content)
                
                self.stats['domains_updated'] += len(re.findall(domain_pattern, content))
            
            # Update timestamp
            current_time = self.get_current_time()
            timestamp_pattern = r'北京时间\d{4}年\d{2}月\d{2}日\d{2}点\d{2}分更新'
            new_timestamp = f"北京时间{current_time}更新"
            content = re.sub(timestamp_pattern, new_timestamp, content)
            
            with open(domains_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.stats['files_processed'] += 1
            self.logger.info(f"Successfully updated domains file: {domains_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update domains file {domains_file}: {e}")
            self.stats['errors'] += 1
            return False
    
    def update_vmess_config(self, vmess_string: str) -> Optional[str]:
        """Update vmess configuration with new host"""
        try:
            # Decode base64 vmess string
            vmess_data = vmess_string.replace('vmess://', '')
            decoded_data = base64.b64decode(vmess_data).decode('utf-8')
            vmess_config = json.loads(decoded_data)
            
            # Update host if present
            if 'host' in vmess_config:
                host_pattern = r'([a-zA-Z]+)(\d+)(\.[\w\.]+)'
                match = re.match(host_pattern, vmess_config['host'])
                if match:
                    prefix, number, suffix = match.groups()
                    new_number = int(number) + self.config['domain_increment']
                    vmess_config['host'] = f"{prefix}{new_number}{suffix}"
                    
                    # Encode back to base64
                    new_vmess_data = base64.b64encode(
                        json.dumps(vmess_config).encode('utf-8')
                    ).decode('utf-8')
                    
                    return f"vmess://{new_vmess_data}"
            
            return vmess_string
            
        except Exception as e:
            self.logger.error(f"Failed to update vmess config: {e}")
            return vmess_string
    
    def validate_pac_syntax(self, pac_file: str) -> bool:
        """Validate PAC file JavaScript syntax"""
        try:
            with open(pac_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic syntax checks
            if 'function FindProxyForURL(' not in content:
                self.logger.warning(f"PAC file missing FindProxyForURL function: {pac_file}")
                return False
            
            # Check for balanced braces
            open_braces = content.count('{')
            close_braces = content.count('}')
            if open_braces != close_braces:
                self.logger.warning(f"Unbalanced braces in PAC file: {pac_file}")
                return False
            
            self.logger.info(f"PAC file syntax validation passed: {pac_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate PAC syntax: {e}")
            return False
    
    def generate_statistics_report(self) -> str:
        """Generate statistics report"""
        current_time = self.get_current_time()
        report = f"""
PAC Configuration Manager - Statistics Report
Generated: {current_time}

Files Processed: {self.stats['files_processed']}
Domains Updated: {self.stats['domains_updated']}
Errors Encountered: {self.stats['errors']}
Success Rate: {(1 - self.stats['errors']/max(1, self.stats['files_processed'])) * 100:.1f}%

Configuration:
- Timezone: {self.config['timezone']}
- Auto Backup: {self.config['auto_backup']}
- Domain Increment: {self.config['domain_increment']}
- Proxy Servers: {len(self.config['proxy_servers'])} configured
"""
        return report
    
    def run_update_cycle(self, target_files: List[str]) -> bool:
        """Run complete update cycle on target files"""
        self.logger.info("Starting PAC configuration update cycle...")
        success = True
        
        for file_path in target_files:
            if file_path.endswith('.pac') or 'pac' in file_path.lower():
                if not self.update_pac_file(file_path):
                    success = False
            elif file_path.endswith('.md'):
                if not self.update_domain_list(file_path):
                    success = False
            else:
                self.logger.warning(f"Unsupported file type: {file_path}")
        
        # Generate and log statistics
        stats_report = self.generate_statistics_report()
        self.logger.info(stats_report)
        
        return success


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Enhanced PAC Configuration Manager')
    parser.add_argument('files', nargs='*', help='Files to update')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--proxy', '-p', help='New proxy server')
    parser.add_argument('--validate', '-v', action='store_true', help='Validate PAC syntax only')
    parser.add_argument('--stats', '-s', action='store_true', help='Show statistics only')
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = PACConfigManager(args.config)
    
    if args.stats:
        print(manager.generate_statistics_report())
        return
    
    if not args.files:
        # Default files if none specified
        args.files = ['pac', 'pac5', 'README.md']
    
    if args.validate:
        for file_path in args.files:
            if file_path.endswith('.pac') or 'pac' in file_path.lower():
                manager.validate_pac_syntax(file_path)
        return
    
    # Run update cycle
    success = manager.run_update_cycle(args.files)
    
    if success:
        print("✅ Update cycle completed successfully!")
    else:
        print("❌ Update cycle completed with errors. Check logs for details.")
        exit(1)


if __name__ == "__main__":
    main()