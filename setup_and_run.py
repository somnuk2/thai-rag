#!/usr/bin/env python3
"""
🚀 Complete Setup & Run Script for Easy Local RAG
This script automates the entire setup and starts the RAG system.

Usage:
    python setup_and_run.py                 # Full setup + run chat
    python setup_and_run.py --skip-models   # Skip model pulling (faster)
    python setup_and_run.py --chat-only     # Skip setup, just run chat
    python setup_and_run.py --help          # Show help

Requirements:
    - Python 3.8+
    - Ollama installed (https://ollama.ai)
    - internet connection (for initial setup)
"""

import os
import sys
import json
import subprocess
import argparse
import hashlib
from pathlib import Path

# ANSI Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class Setup:
    """Setup and run the RAG system"""
    
    def __init__(self, skip_models=False, chat_only=False):
        self.skip_models = skip_models
        self.chat_only = chat_only
        self.project_root = Path(__file__).parent.resolve()
        
    def print_header(self, text):
        """Print colored header"""
        print(f"\n{BOLD}{GREEN}{'=' * 60}{RESET}")
        print(f"{BOLD}{GREEN}▶ {text}{RESET}")
        print(f"{BOLD}{GREEN}{'=' * 60}{RESET}\n")
    
    def print_step(self, text):
        """Print step message"""
        print(f"{CYAN}📋 {text}{RESET}")
    
    def print_success(self, text):
        """Print success message"""
        print(f"{GREEN}✅ {text}{RESET}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{YELLOW}⚠️  {text}{RESET}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{RED}❌ {text}{RESET}")
    
    def run_command(self, cmd, description=""):
        """Run shell command"""
        if description:
            self.print_step(description)
        
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=False,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            self.print_error(f"Command failed: {e}")
            return False
    
    def check_python_version(self):
        """Check Python version"""
        self.print_header("Step 1: Checking Python Version")
        
        version = sys.version_info
        print(f"Python {version.major}.{version.minor}.{version.micro}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.print_error("Python 3.8+ required!")
            return False
        
        self.print_success("Python version OK")
        return True
    
    def check_ollama(self):
        """Check if Ollama is installed and running"""
        self.print_header("Step 2: Checking Ollama Installation")
        
        # Check if ollama command exists
        result = subprocess.run(
            "ollama --version",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.print_error("Ollama not found!")
            self.print_warning("Install from: https://ollama.ai")
            return False
        
        self.print_success(f"Ollama installed: {result.stdout.strip()}")
        
        # Check if Ollama is running
        result = subprocess.run(
            "ollama list",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            self.print_warning("Ollama not running. Starting...")
            self.print_step("Run: ollama serve (in another terminal)")
            input("Press Enter when Ollama is running...")
        else:
            self.print_success("Ollama is running")
        
        return True
    
    def install_dependencies(self):
        """Install Python dependencies"""
        self.print_header("Step 3: Installing Python Dependencies")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            self.print_error(f"requirements.txt not found at {self.project_root}")
            return False
        
        self.print_step(f"Installing from {requirements_file}")
        
        success = self.run_command(
            f"pip install -r {requirements_file}",
            "Running pip install..."
        )
        
        if success:
            self.print_success("Dependencies installed")
            return True
        else:
            self.print_error("Failed to install dependencies")
            return False
    
    def pull_models(self):
        """Pull required Ollama models"""
        if self.skip_models:
            self.print_step("Skipping model pulling (--skip-models)")
            return True
        
        self.print_header("Step 4: Pulling Ollama Models")
        
        models = [
            ("llama3", "Main chat model"),
            ("mxbai-embed-large", "Embedding model")
        ]
        
        for model_name, description in models:
            self.print_step(f"Pulling {model_name} ({description})")
            print(f"{YELLOW}This may take 5-30 minutes...{RESET}\n")
            
            success = self.run_command(
                f"ollama pull {model_name}",
                f"Downloading {model_name}..."
            )
            
            if success:
                self.print_success(f"{model_name} pulled successfully")
            else:
                self.print_warning(f"Failed to pull {model_name}")
        
        return True
    
    def prepare_vault(self):
        """Prepare vault.txt file"""
        self.print_header("Step 5: Preparing Document Vault")
        
        vault_path = self.project_root / "vault.txt"
        
        if vault_path.exists():
            file_size = vault_path.stat().st_size
            line_count = len(vault_path.read_text(encoding='utf-8').split('\n'))
            self.print_success(f"vault.txt exists ({line_count} lines, {file_size} bytes)")
            return True
        
        self.print_warning("vault.txt not found")
        self.print_step("Options to create vault.txt:")
        print("  1. Upload PDF via GUI:")
        print(f"     python {self.project_root}/original_code/upload.py")
        print("  2. Process specific PDF:")
        print(f"     python {self.project_root}/process_specific_pdf.py")
        print("  3. Manually create vault.txt with text content")
        print()
        
        choice = input("Continue without vault.txt? (y/n): ").lower()
        return choice == 'y'
    
    def verify_setup(self):
        """Verify all setup completed"""
        self.print_header("Step 6: Verifying Setup")
        
        checks = {
            "vault.txt": self.project_root / "vault.txt",
            "localrag.py": self.project_root / "localrag.py",
            "requirements.txt": self.project_root / "requirements.txt",
        }
        
        all_ok = True
        for name, path in checks.items():
            if path.exists():
                self.print_success(f"{name} found")
            else:
                self.print_warning(f"{name} not found")
                all_ok = False
        
        return all_ok
    
    def run_chat(self, model="llama3"):
        """Run the chat application"""
        self.print_header("Step 7: Starting RAG Chat System")
        
        localrag_path = self.project_root / "localrag.py"
        
        if not localrag_path.exists():
            self.print_error(f"localrag.py not found at {localrag_path}")
            return False
        
        self.print_success("Starting interactive chat...")
        print(f"{YELLOW}Type 'quit' to exit{RESET}\n")
        
        # Run the chat
        try:
            subprocess.run(
                [sys.executable, str(localrag_path), "--model", model],
                cwd=self.project_root
            )
            return True
        except KeyboardInterrupt:
            self.print_warning("Chat interrupted by user")
            return True
        except Exception as e:
            self.print_error(f"Error running chat: {e}")
            return False
    
    def run_full_setup(self):
        """Run complete setup"""
        self.print_header("🚀 Easy Local RAG - Complete Setup")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking Ollama", self.check_ollama),
            ("Installing dependencies", self.install_dependencies),
            ("Pulling models", self.pull_models),
            ("Preparing vault", self.prepare_vault),
            ("Verifying setup", self.verify_setup),
        ]
        
        for step_name, step_func in steps:
            try:
                if not step_func():
                    self.print_error(f"Failed: {step_name}")
                    return False
            except KeyboardInterrupt:
                self.print_warning("Setup interrupted by user")
                return False
            except Exception as e:
                self.print_error(f"Error in {step_name}: {e}")
                return False
        
        self.print_header("✅ Setup Complete!")
        return True
    
    def main(self):
        """Main entry point"""
        if not self.chat_only:
            if not self.run_full_setup():
                self.print_error("Setup failed. Please fix errors and try again.")
                return False
        
        # Run chat
        self.print_header("Starting RAG Chat")
        if not self.run_chat():
            self.print_error("Failed to start chat")
            return False
        
        return True


def main():
    """Entry point"""
    parser = argparse.ArgumentParser(
        description="Complete setup and run for Easy Local RAG",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_and_run.py                 # Full setup + run
  python setup_and_run.py --skip-models   # Skip model pulling
  python setup_and_run.py --chat-only     # Just run chat
        """
    )
    
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip downloading Ollama models"
    )
    
    parser.add_argument(
        "--chat-only",
        action="store_true",
        help="Skip setup, just run chat"
    )
    
    parser.add_argument(
        "--model",
        default="llama3",
        help="Model to use for chat (default: llama3)"
    )
    
    args = parser.parse_args()
    
    setup = Setup(skip_models=args.skip_models, chat_only=args.chat_only)
    
    try:
        success = setup.main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Setup cancelled by user{RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
