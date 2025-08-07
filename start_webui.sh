#!/bin/bash

# Ollama GPT-OSS-20B Web UI Startup Script

echo "🚀 Starting Ollama GPT-OSS-20B Web UI..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install it first:"
    echo "   brew install ollama"
    exit 1
fi

# Check if Ollama service is running
if ! brew services list | grep -q "ollama.*started"; then
    echo "⚠️  Ollama service is not running. Starting it now..."
    brew services start ollama
    sleep 3
fi

# Check if the model is available
if ! ollama list | grep -q "gpt-oss:20b"; then
    echo "⚠️  Model gpt-oss:20b not found. Downloading it now..."
    echo "📥 This may take a while (13GB download)..."
    ollama pull gpt-oss:20b
fi

# Check if Python dependencies are installed
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Creating it..."
    echo "gradio>=4.0.0" > requirements.txt
    echo "requests>=2.31.0" >> requirements.txt
fi

# Install Python dependencies if needed
if ! python3 -c "import gradio" &> /dev/null; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
fi

# Start the web UI
echo "🌐 Starting web UI on http://localhost:7860"
echo "📝 Press Ctrl+C to stop the server"
echo ""

python3 chat_ui.py 