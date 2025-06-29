#!/usr/bin/env python3
"""
Simple validation script for DreamEngine AI Platform
Tests basic configuration without external dependencies
"""

import os
import sys
import json
from datetime import datetime

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header():
    """Print validation header"""
    print("\n" + "="*60)
    print(f"{Colors.BOLD}🔍 DREAMENGINE AI PLATFORM - SETUP VALIDATION{Colors.END}")
    print("="*60 + "\n")

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{Colors.GREEN}✅{Colors.END} {description}: Found")
        return True
    else:
        print(f"{Colors.RED}❌{Colors.END} {description}: Missing")
        return False

def check_env_file():
    """Check .env file and configuration"""
    print(f"{Colors.BLUE}🧪 Checking Environment Configuration...{Colors.END}")
    
    env_exists = check_file_exists(".env", ".env file")
    
    if env_exists:
        # Read .env file
        with open(".env", "r") as f:
            lines = f.readlines()
        
        # Check for critical variables
        critical_vars = ["DATABASE_URL", "SECRET_KEY"]
        found_vars = []
        
        for line in lines:
            if "=" in line and not line.strip().startswith("#"):
                var_name = line.split("=")[0].strip()
                if var_name in critical_vars:
                    found_vars.append(var_name)
        
        for var in critical_vars:
            if var in found_vars:
                print(f"  {Colors.GREEN}✅{Colors.END} {var}: Configured")
            else:
                print(f"  {Colors.YELLOW}⚠️{Colors.END}  {var}: Not found (will use default)")
    
    return env_exists

def check_project_structure():
    """Check project structure"""
    print(f"\n{Colors.BLUE}🧪 Checking Project Structure...{Colors.END}")
    
    critical_dirs = [
        ("app", "Application directory"),
        ("app/routes", "API routes"),
        ("app/utils", "Utilities"),
        ("app/database", "Database modules"),
        ("app/templates", "Frontend templates")
    ]
    
    critical_files = [
        ("app/main.py", "Main application"),
        ("app/config.py", "Configuration"),
        ("app/services.py", "Service manager"),
        ("requirements.txt", "Dependencies"),
        ("Dockerfile", "Docker configuration"),
        ("docker-compose.yml", "Docker Compose")
    ]
    
    all_good = True
    
    # Check directories
    for dir_path, description in critical_dirs:
        if not check_file_exists(dir_path, description):
            all_good = False
    
    # Check files
    for file_path, description in critical_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    return all_good

def check_database_url():
    """Check database URL format"""
    print(f"\n{Colors.BLUE}🧪 Checking Database Configuration...{Colors.END}")
    
    # Try to read from .env
    db_url = None
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("DATABASE_URL="):
                    db_url = line.split("=", 1)[1].strip()
                    break
    
    if db_url:
        if db_url.startswith("postgresql://"):
            print(f"{Colors.GREEN}✅{Colors.END} Database URL: Valid PostgreSQL format")
            # Parse database name
            try:
                db_name = db_url.split("/")[-1].split("?")[0]
                print(f"  Database name: {db_name}")
            except:
                pass
            return True
        else:
            print(f"{Colors.RED}❌{Colors.END} Database URL: Invalid format")
            return False
    else:
        print(f"{Colors.YELLOW}⚠️{Colors.END}  Database URL: Using default")
        return True

def check_optional_features():
    """Check optional features configuration"""
    print(f"\n{Colors.BLUE}🧪 Checking Optional Features...{Colors.END}")
    
    features = {
        "OPENAI_API_KEY": "OpenAI Integration",
        "ANTHROPIC_API_KEY": "Anthropic Claude",
        "GITHUB_TOKEN": "GitHub Integration",
        "VOICE_API_KEY": "Voice Processing",
        "WEB3_PROVIDER_URL": "Smart Contracts"
    }
    
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_content = f.read()
        
        for key, feature in features.items():
            if key in env_content and not f"# {key}" in env_content:
                print(f"{Colors.GREEN}✅{Colors.END} {feature}: Configured")
            else:
                print(f"{Colors.YELLOW}⚠️{Colors.END}  {feature}: Not configured (optional)")

def generate_summary(results):
    """Generate validation summary"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}📊 VALIDATION SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    total_checks = len(results)
    passed = sum(1 for r in results if r)
    
    print(f"Total Checks: {total_checks}")
    print(f"{Colors.GREEN}✅ Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}❌ Failed: {total_checks - passed}{Colors.END}")
    
    success_rate = (passed / total_checks * 100) if total_checks > 0 else 0
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")
    
    if passed == total_checks:
        print(f"\n{Colors.GREEN}🎉 All checks passed! Your setup looks good.{Colors.END}")
        print("\nNext steps:")
        print("1. Add your API keys to the .env file")
        print("2. Run: docker-compose up --build")
        print("3. Visit: http://localhost:8000")
    elif passed > total_checks / 2:
        print(f"\n{Colors.YELLOW}⚠️  Some issues detected but basic setup is OK.{Colors.END}")
        print("\nRecommended actions:")
        print("1. Review missing files/configurations")
        print("2. Add API keys for features you want to use")
        print("3. Test with: docker-compose up --build")
    else:
        print(f"\n{Colors.RED}❌ Critical issues detected. Setup incomplete.{Colors.END}")
        print("\nRequired actions:")
        print("1. Ensure all project files are present")
        print("2. Create .env file with basic configuration")
        print("3. Review the setup guide")

def main():
    """Run validation"""
    print_header()
    
    results = []
    
    # Run checks
    results.append(check_env_file())
    results.append(check_project_structure())
    results.append(check_database_url())
    check_optional_features()
    
    # Generate summary
    generate_summary(results)
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}\n")

if __name__ == "__main__":
    main()