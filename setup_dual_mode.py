"""
Updated Setup Script - Supports both Local and Supabase modes
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# ANSI Colors
GREEN = '\033[92m'
BLUE = '\033[94m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class SetupWithModes:
    """Setup supporting both Local and Supabase modes"""
    
    def __init__(self, mode="local", skip_models=False, chat_only=False):
        self.mode = mode
        self.skip_models = skip_models
        self.chat_only = chat_only
        self.project_root = Path(__file__).parent.resolve()
    
    def print_header(self, text):
        print(f"\n{BOLD}{GREEN}{'=' * 70}{RESET}")
        print(f"{BOLD}{GREEN}▶ {text}{RESET}")
        print(f"{BOLD}{GREEN}{'=' * 70}{RESET}\n")
    
    def print_step(self, text):
        print(f"{CYAN}📋 {text}{RESET}")
    
    def print_success(self, text):
        print(f"{GREEN}✅ {text}{RESET}")
    
    def print_warning(self, text):
        print(f"{YELLOW}⚠️  {text}{RESET}")
    
    def print_error(self, text):
        print(f"{RED}❌ {text}{RESET}")
    
    def run_command(self, cmd, description=""):
        if description:
            self.print_step(description)
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
            return result.returncode == 0
        except Exception as e:
            self.print_error(f"Command failed: {e}")
            return False
    
    def setup_env(self):
        """Setup .env file with selected mode"""
        self.print_header(f"Configuring RAG Mode: {self.mode.upper()}")
        
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        # Check if .env exists
        if env_file.exists():
            self.print_warning(".env already exists")
        else:
            if env_example.exists():
                self.print_step("Creating .env from .env.example")
                with open(env_example, 'r') as src:
                    content = src.read()
                
                # Replace mode
                content = content.replace('RAG_MODE=local', f'RAG_MODE={self.mode}')
                
                with open(env_file, 'w') as dst:
                    dst.write(content)
                
                self.print_success(".env created")
        
        # Ask for Supabase credentials if needed
        if self.mode == "supabase":
            self.print_header("Supabase Configuration Required")
            print("Visit https://supabase.com to create a project")
            print("\nYou need:")
            print("  1. SUPABASE_URL (from Settings > API)")
            print("  2. SUPABASE_KEY (anon key)")
            
            url = input(f"\n{CYAN}Enter SUPABASE_URL: {RESET}").strip()
            key = input(f"{CYAN}Enter SUPABASE_KEY: {RESET}").strip()
            
            if url and key:
                # Update .env
                with open(env_file, 'r') as f:
                    content = f.read()
                
                content = content.replace('SUPABASE_URL=https://your-project-id.supabase.co', f'SUPABASE_URL={url}')
                content = content.replace('SUPABASE_KEY=your-anon-key-here', f'SUPABASE_KEY={key}')
                
                with open(env_file, 'w') as f:
                    f.write(content)
                
                self.print_success("Supabase credentials saved")
            else:
                self.print_warning("Supabase setup skipped")
    
    def full_setup(self):
        """Run full setup"""
        self.print_header(f"🚀 Easy Local RAG - Setup for {self.mode.upper()} Mode")
        
        # Check Python
        import sys
        print(f"Python {sys.version_info.major}.{sys.version_info.minor}")
        if sys.version_info < (3, 8):
            self.print_error("Python 3.8+ required")
            return False
        
        # Check Ollama
        self.print_header("Checking Ollama")
        result = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            self.print_error("Ollama not found. Install from https://ollama.ai")
            return False
        self.print_success(f"Ollama found: {result.stdout.strip()}")
        
        # Setup environment
        self.setup_env()
        
        if not self.chat_only:
            # Install dependencies
            self.print_header("Installing Dependencies")
            if not self.run_command("pip install -r requirements.txt", "Running pip install..."):
                self.print_error("Failed to install dependencies")
                return False
            self.print_success("Dependencies installed")
            
            # Pull models
            if not self.skip_models:
                self.print_header("Pulling Ollama Models")
                print(f"{YELLOW}This may take 10-30 minutes...{RESET}\n")
                
                for model in ["llama3", "mxbai-embed-large"]:
                    self.run_command(f"ollama pull {model}", f"Pulling {model}...")
        
        return True
    
    def run_chat(self):
        """Run the chat application"""
        self.print_header(f"Starting RAG Chat ({self.mode.upper()} mode)")
        
        try:
            subprocess.run(
                [sys.executable, "localrag_dual.py", "--mode", self.mode],
                cwd=self.project_root
            )
            return True
        except Exception as e:
            self.print_error(f"Error running chat: {e}")
            return False
    
    def main(self):
        """Main entry point"""
        if not self.chat_only:
            if not self.full_setup():
                return False
        
        if not self.run_chat():
            return False
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Easy Local RAG - Setup supporting Local and Supabase modes"
    )
    parser.add_argument(
        "--mode",
        choices=["local", "supabase"],
        default="local",
        help="Storage mode (default: local)"
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="Skip downloading models"
    )
    parser.add_argument(
        "--chat-only",
        action="store_true",
        help="Skip setup, just run chat"
    )
    
    args = parser.parse_args()
    
    setup = SetupWithModes(
        mode=args.mode,
        skip_models=args.skip_models,
        chat_only=args.chat_only
    )
    
    try:
        success = setup.main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Setup cancelled{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
