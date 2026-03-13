# PowerShell Script for Easy Local RAG Setup & Run
# This script automates the complete setup and starts the RAG system
#
# Usage:
#   .\setup_and_run.ps1                 # Full setup + run
#   .\setup_and_run.ps1 -SkipModels     # Skip model pulling
#   .\setup_and_run.ps1 -ChatOnly       # Just run chat

param(
    [switch]$SkipModels = $false,
    [switch]$ChatOnly = $false,
    [string]$Model = "llama3"
)

# Set execution policy for this session
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Colors
$GREEN = "`e[92m"
$BLUE = "`e[94m"
$YELLOW = "`e[93m"
$RED = "`e[91m"
$CYAN = "`e[96m"
$RESET = "`e[0m"
$BOLD = "`e[1m"

function Write-Header {
    param([string]$Text)
    Write-Host ""
    Write-Host "$BOLD$GREEN$("=" * 70)$RESET"
    Write-Host "$BOLD$GREEN▶ $Text$RESET"
    Write-Host "$BOLD$GREEN$("=" * 70)$RESET"
    Write-Host ""
}

function Write-Step {
    param([string]$Text)
    Write-Host "$CYAN📋 $Text$RESET"
}

function Write-Success {
    param([string]$Text)
    Write-Host "$GREEN✅ $Text$RESET"
}

function Write-Warning {
    param([string]$Text)
    Write-Host "$YELLOW⚠️  $Text$RESET"
}

function Write-Error-Custom {
    param([string]$Text)
    Write-Host "$RED❌ $Text$RESET"
}

Write-Header "Easy Local RAG - Complete Setup & Run"

# Step 1: Check Python
Write-Header "Step 1: Checking Python"
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Python not found. Please install Python 3.8+"
    exit 1
}
Write-Success "Python found: $pythonVersion"

# Step 2: Check Ollama
Write-Header "Step 2: Checking Ollama"
$ollamaVersion = ollama --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Ollama not found. Please install from https://ollama.ai"
    exit 1
}
Write-Success "Ollama found: $ollamaVersion"

# Check if Ollama is running
Write-Step "Checking if Ollama is running..."
$ollamaList = ollama list 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Ollama is not running"
    Write-Host "Please run: ollama serve (in another terminal or Ollama app)"
    Read-Host "Press Enter when Ollama is running"
}
else {
    Write-Success "Ollama is running"
}

if (-not $ChatOnly) {
    # Step 3: Install dependencies
    Write-Header "Step 3: Installing Python Dependencies"
    Write-Step "Running: pip install -r requirements.txt"
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Failed to install dependencies"
        exit 1
    }
    Write-Success "Dependencies installed"

    # Step 4: Pull models
    if (-not $SkipModels) {
        Write-Header "Step 4: Pulling Ollama Models"
        Write-Host "$YELLOW`nThis may take 10-30 minutes on first run...`n$RESET"

        Write-Step "Pulling llama3 (main chat model)..."
        ollama pull llama3
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to pull llama3"
        }
        else {
            Write-Success "llama3 pulled"
        }

        Write-Step "Pulling mxbai-embed-large (embeddings model)..."
        ollama pull mxbai-embed-large
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Failed to pull mxbai-embed-large"
        }
        else {
            Write-Success "mxbai-embed-large pulled"
        }
    }
    else {
        Write-Header "Step 4: Skipping Model Pull"
        Write-Step "Skipping model pulling (--SkipModels)"
    }

    # Step 5: Check vault
    Write-Header "Step 5: Preparing Vault"
    if (Test-Path "vault.txt") {
        $vaultSize = (Get-Item "vault.txt").Length
        $vaultLines = (Get-Content "vault.txt" | Measure-Object -Line).Lines
        Write-Success "vault.txt found ($vaultLines lines, $vaultSize bytes)"
    }
    else {
        Write-Warning "vault.txt not found"
        Write-Host "Options to create vault.txt:"
        Write-Host "  1. python original_code/upload.py (GUI upload)"
        Write-Host "  2. python process_specific_pdf.py (CLI process)"
        Write-Host "  3. Create vault.txt manually with text content"
        Write-Host ""
    }
}

# Step 6: Run chat
Write-Header "Starting RAG Chat System"
Write-Host "$YELLOW`nType 'quit' to exit`n$RESET"

python localrag.py --model $Model

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Failed to start chat"
    exit 1
}

Write-Header "Chat Session Ended"
Write-Success "Thank you for using Easy Local RAG!"
