# 🚀 Quick Setup Guide

This guide will help you get the Ollama GPT-OSS-20B project up and running quickly.

## Prerequisites

- **macOS** (this setup is optimized for macOS)
- **Homebrew** installed
- **Python 3** and **pip3** installed
- **At least 16GB RAM** (32GB recommended)
- **~13GB free storage** for the model
- **Internet connection** for initial download

## 🎯 Quick Start (3 Steps)

### Step 1: Run the Automated Setup
```bash
./scripts/install.sh
```

This script will:
- ✅ Install Ollama via Homebrew
- ✅ Start the Ollama service
- ✅ Download the GPT-OSS-20B model (~13GB)
- ✅ Install Python dependencies
- ✅ Make all scripts executable

### Step 2: Test the Setup
```bash
./scripts/test_model.sh
```

This will verify everything is working correctly.

### Step 3: Start Using It!

**Terminal Chat:**
```bash
ollama run gpt-oss:20b
```

**Web UI:**
```bash
./start_webui.sh
```
Then open http://localhost:7860 in your browser.

## 🔧 Manual Setup (Alternative)

If you prefer to set up manually:

1. **Install Ollama:**
   ```bash
   brew install ollama
   brew services start ollama
   ```

2. **Download the model:**
   ```bash
   ollama pull gpt-oss:20b
   ```

3. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Start the web UI:**
   ```bash
   ./start_webui.sh
   ```

## 🎮 Usage Examples

### Terminal Chat
```bash
ollama run gpt-oss:20b
```
Type your messages and press Enter. Type `exit` to quit.

### Web UI
```bash
./start_webui.sh
```
- Open http://localhost:7860
- Adjust temperature and max tokens
- Chat with the model in a beautiful interface

### API Access
```bash
# Start Ollama API server (if not already running)
ollama serve

# Test with curl
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:20b",
    "prompt": "Hello, how are you?",
    "stream": false
  }'
```

## ⚠️ Troubleshooting

### "Ollama not found"
```bash
brew install ollama
brew services start ollama
```

### "Model not found"
```bash
ollama pull gpt-oss:20b
```

### "Out of memory"
- Close other applications
- Ensure you have at least 16GB RAM
- Restart Ollama: `brew services restart ollama`

### "Port 7860 already in use"
- The web UI will automatically find an available port
- Or kill the process using port 7860: `lsof -ti:7860 | xargs kill -9`

## 📊 System Requirements

- **RAM**: 16GB minimum (32GB recommended)
- **Storage**: ~13GB for the model
- **CPU**: Any modern CPU (optimized for Apple Silicon)
- **Network**: Required for initial model download

## 🎉 Benefits

- **Local**: No data sent to external servers
- **Fast**: Optimized for local inference
- **Private**: Your conversations stay on your machine
- **Free**: No API costs or usage limits
- **Customizable**: Adjust temperature, tokens, etc.

## 📝 Next Steps

1. Try different prompts and parameters
2. Explore the API for integration
3. Check out other Ollama models
4. Join the Ollama community

Happy chatting! 🤖✨ 