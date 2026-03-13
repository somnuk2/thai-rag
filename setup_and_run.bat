@echo off
REM Windows Batch Script for Easy Local RAG Setup & Run
REM This script automates the complete setup and starts the RAG system

setlocal enabledelayedexpansion

echo.
echo ================================================================================
echo     Easy Local RAG - Complete Setup and Run
echo ================================================================================
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Ollama
echo.
echo Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama not found. Please install from https://ollama.ai
    pause
    exit /b 1
)
echo [OK] Ollama found

REM Check if Ollama is running
echo.
echo Checking if Ollama is running...
ollama list >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not running
    echo Please run: ollama serve (in another terminal)
    pause
)

REM Install dependencies
echo.
echo ================================================================================
echo Step 1: Installing Python Dependencies
echo ================================================================================
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Pull models (unless --skip-models was passed)
if not "%1"=="--skip-models" (
    echo.
    echo ================================================================================
    echo Step 2: Pulling Ollama Models
    echo ================================================================================
    echo This may take 10-30 minutes on first run...
    echo.
    
    echo Pulling llama3...
    ollama pull llama3
    if errorlevel 1 echo [WARNING] Failed to pull llama3
    
    echo.
    echo Pulling mxbai-embed-large...
    ollama pull mxbai-embed-large
    if errorlevel 1 echo [WARNING] Failed to pull mxbai-embed-large
) else (
    echo Step 2: Skipping model pulling (--skip-models)
)

REM Prepare vault
echo.
echo ================================================================================
echo Step 3: Checking Vault
echo ================================================================================
if exist vault.txt (
    echo [OK] vault.txt found
) else (
    echo [WARNING] vault.txt not found
    echo You can:
    echo   - Run: python original_code/upload.py (to upload PDF)
    echo   - Run: python process_specific_pdf.py (to process PDF)
    echo   - Create vault.txt manually with text content
    echo.
    echo Continuing without vault.txt...
)

REM Run chat
echo.
echo ================================================================================
echo Step 4: Starting RAG Chat System
echo ================================================================================
echo.
python localrag.py
if errorlevel 1 (
    echo [ERROR] Failed to start chat
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo Setup Complete!
echo ================================================================================
pause
