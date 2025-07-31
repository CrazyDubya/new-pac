#!/bin/bash

# PAC Proxy Demo Launcher
# Easy script to launch different demo modes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "======================================"
echo "    PAC Proxy Configuration Demo"
echo "======================================"
echo -e "${NC}"

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
    exit 1
fi

# Check Flask
if ! python3 -c "import flask" &> /dev/null; then
    echo -e "${YELLOW}⚠️  Flask not found.${NC}"
    read -p "Do you want to install Flask (version 2.1.3)? [y/N]: " confirm
    if [[ $confirm == [yY] ]]; then
        pip3 install --user flask==2.1.3
    else
        echo -e "${RED}❌ Flask is required. Exiting.${NC}"
        exit 1
    fi
fi

# Check pytz
if ! python3 -c "import pytz" &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytz not found.${NC}"
    read -p "Do you want to install pytz (version 2022.1)? [y/N]: " confirm
    if [[ $confirm == [yY] ]]; then
        pip3 install --user pytz==2022.1
    else
        echo -e "${RED}❌ pytz is required. Exiting.${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Dependencies checked${NC}"
echo

# Menu function
show_menu() {
    echo -e "${BLUE}Choose demo mode:${NC}"
    echo "1. 🌐 Interactive Web Demo (Browser-based)"
    echo "2. 🔧 PAC Web Tester (Local Flask server)"
    echo "3. 📋 Command Line Tools Demo"
    echo "4. 🧪 Run All Tests"
    echo "5. 📊 Generate Statistics Report"
    echo "6. ℹ️  Show Documentation"
    echo "0. Exit"
    echo
    echo -n "Enter your choice [0-6]: "
}

# Function to run web demo
run_web_demo() {
    echo -e "${GREEN}🌐 Starting Interactive Web Demo...${NC}"
    echo -e "${YELLOW}Opening browser demo at http://localhost:8080${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo
    
    cd demo
    if command -v python3 &> /dev/null; then
        python3 -m http.server 8080
    else
        python -m http.server 8080
    fi
}

# Function to run PAC web tester
run_pac_tester() {
    echo -e "${GREEN}🔧 Starting PAC Web Tester...${NC}"
    echo -e "${YELLOW}Opening PAC tester at http://localhost:5000${NC}"
    echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
    echo
    
    python3 scripts/pac_web_tester.py
}

# Function to run CLI demo
run_cli_demo() {
    echo -e "${GREEN}📋 Command Line Tools Demo${NC}"
    echo
    
    echo -e "${BLUE}1. Validating PAC files...${NC}"
    python3 scripts/pac_manager.py --config scripts/config.json --validate pac pac5
    echo
    
    echo -e "${BLUE}2. Testing configuration update...${NC}"
    python3 scripts/pac_manager.py --config scripts/config.json --stats
    echo
    
    echo -e "${BLUE}3. Generating backup...${NC}"
    python3 scripts/pac_manager.py --config scripts/config.json pac
    echo
    
    echo -e "${GREEN}✅ CLI demo completed!${NC}"
    echo
    read -p "Press Enter to continue..."
}

# Function to run all tests
run_all_tests() {
    echo -e "${GREEN}🧪 Running All Tests...${NC}"
    echo
    
    echo -e "${BLUE}Testing PAC syntax validation...${NC}"
    python3 scripts/pac_manager.py --validate pac pac5
    echo
    
    echo -e "${BLUE}Testing configuration management...${NC}"
    python3 scripts/pac_manager.py --config scripts/config.json --stats
    echo
    
    echo -e "${BLUE}Testing web tester import...${NC}"
    python3 -c "
import sys
sys.path.append('scripts')
from pac_web_tester import PACTester
tester = PACTester()
print(f'✅ Loaded {len(tester.domains)} domains')
result = tester.test_url('https://facebook.com')
print(f'✅ Test result: {result[\"action\"]}')
"
    echo
    
    echo -e "${GREEN}✅ All tests passed!${NC}"
    echo
    read -p "Press Enter to continue..."
}

# Function to generate stats
generate_stats() {
    echo -e "${GREEN}📊 Generating Statistics Report...${NC}"
    echo
    
    python3 scripts/pac_manager.py --config scripts/config.json --stats
    echo
    
    echo -e "${BLUE}Domain Analysis:${NC}"
    python3 -c "
import sys
sys.path.append('scripts')
from pac_web_tester import PACTester
tester = PACTester()
domains = list(tester.domains)
print(f'Total domains loaded: {len(domains)}')
if domains:
    print(f'Sample domains: {domains[:5]}')
    print(f'Domain categories detected:')
    social = [d for d in domains if any(x in d for x in ['facebook', 'twitter', 'instagram'])]
    tech = [d for d in domains if any(x in d for x in ['github', 'stackoverflow', 'google'])]
    news = [d for d in domains if any(x in d for x in ['bbc', 'cnn', 'reuters'])]
    print(f'  - Social Media: {len(social)} domains')
    print(f'  - Tech/Dev: {len(tech)} domains')
    print(f'  - News: {len(news)} domains')
"
    echo
    read -p "Press Enter to continue..."
}

# Function to show docs
show_docs() {
    echo -e "${GREEN}ℹ️  Documentation${NC}"
    echo
    
    if [ -f "docs/QUICKSTART.md" ]; then
        echo -e "${BLUE}Quick Start Guide:${NC}"
        head -20 docs/QUICKSTART.md
        echo "..."
        echo
    fi
    
    if [ -f "README_EN.md" ]; then
        echo -e "${BLUE}English README:${NC}"
        head -15 README_EN.md
        echo "..."
        echo
    fi
    
    echo -e "${BLUE}Available files:${NC}"
    echo "📁 demo/ - Interactive web demo"
    echo "📁 scripts/ - Enhanced automation tools"
    echo "📁 docs/ - Documentation"
    echo "📄 pac - Main PAC configuration file"
    echo "📄 pac5 - Alternative PAC configuration"
    echo "📄 README_EN.md - English documentation"
    echo
    
    read -p "Press Enter to continue..."
}

# Main loop
while true; do
    show_menu
    read choice
    
    case $choice in
        1)
            run_web_demo
            ;;
        2)
            run_pac_tester
            ;;
        3)
            run_cli_demo
            ;;
        4)
            run_all_tests
            ;;
        5)
            generate_stats
            ;;
        6)
            show_docs
            ;;
        0)
            echo -e "${GREEN}👋 Thanks for trying the PAC Proxy Demo!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid option. Please choose 0-6.${NC}"
            echo
            ;;
    esac
done