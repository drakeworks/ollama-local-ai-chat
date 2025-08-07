# Ollama Local AI Chat

> **A smart, system-optimized web interface for running large language models locally using Ollama**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-green.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A modern, responsive web interface that makes it easy to chat with local AI models. Features intelligent system analysis, automatic model recommendations, and real-time system monitoring.

## Features

- **Smart Model Selection** - Analyzes your hardware and recommends optimal models
- **Modern Web UI** - Beautiful, responsive interface with dark theme
- **Real-time Monitoring** - Live CPU, RAM, and GPU usage display
- **Performance Optimized** - Automatic parameter tuning based on your system
- **Model Switching** - Easily switch between different models on the fly
- **Mobile Friendly** - Works perfectly on desktop and mobile devices
- **Easy Setup** - One-command installation with intelligent configuration

## Quick Start

### Prerequisites
- **RAM**: 8GB minimum (16GB+ recommended)
- **Storage**: 1-20GB depending on model choice
- **OS**: macOS, Linux, or Windows
- **Python**: 3.8 or higher

### 1. Clone & Setup
```bash
git clone https://github.com/drakeworks/ollama-local-ai-chat.git
cd ollama-local-ai-chat

# Run the intelligent installer
chmod +x scripts/install.sh
./scripts/install.sh
```

### 2. Start Chatting
```bash
# Launch the web interface
./start_webui.sh

# Or use terminal chat
ollama run [your-model-name]
```

Open your browser to `http://localhost:7860` and start chatting!

## Project Structure

```
ollama-local-ai-chat/
├── README.md                 # This file
├── chat_ui.py               # Main Gradio web interface
├── system_config.json       # Auto-generated system configuration
├── requirements.txt         # Python dependencies
├── start_webui.sh          # Web UI startup script
├── SETUP.md                # Detailed setup instructions
├── scripts/                # Utility scripts
│   ├── install.sh          # Intelligent installation script
│   └── test_model.sh       # Model testing script
└── .gitignore              # Git exclusions (excludes large model files)
```

## Model Recommendations

### Lightweight Systems (8-16GB RAM)
| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| `llama3.2:1b` | 0.8GB | Basic tasks, quick responses | Fast |
| `phi3:mini` | 1.8GB | General purpose, good quality | Medium |
| `llama3.2:3b` | 2.1GB | Balanced performance | Medium |

### Mid-range Systems (16-32GB RAM)
| Model | Size | Best For | Quality |
|-------|------|----------|---------|
| `llama3.2:8b` | 4.7GB | Excellent all-around | High |
| `mistral:7b` | 4.1GB | Great reasoning | High |
| `codellama:7b` | 4.1GB | Programming tasks | High |

### High-end Systems (32GB+ RAM)
| Model | Size | Best For | Quality |
|-------|------|----------|---------|
| `llama3.2:14b` | 7.8GB | High-quality responses | Very High |
| `mistral:14b` | 7.8GB | Advanced reasoning | Very High |
| `gpt-oss:20b` | 13GB | Maximum quality | Maximum |

## Installation Options

### Automated Setup (Recommended)
The intelligent installer analyzes your system and sets everything up automatically:

```bash
./scripts/install.sh
```

**What it does:**
- Analyzes your hardware (RAM, CPU, GPU)
- Shows recommended models for your system
- Lets you choose the perfect model
- Configures optimal settings automatically
- Installs all dependencies
- Sets up everything ready to use

### Manual Setup
If you prefer manual installation:

```bash
# 1. Install Ollama
brew install ollama  # macOS
# or visit https://ollama.ai for other platforms

# 2. Start Ollama service
brew services start ollama

# 3. Download a model
ollama pull llama3.2:8b

# 4. Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface
```bash
./start_webui.sh
```
Then open `http://localhost:7860` in your browser.

**Features:**
- Real-time chat interface
- Adjustable temperature and token limits
- Live system resource monitoring
- Easy model switching
- Chat history persistence

### Terminal Chat
```bash
ollama run [model-name]
```

### API Access
```bash
# Start Ollama API server
ollama serve

# Use with any OpenAI-compatible client
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:8b",
    "prompt": "Hello, how are you?",
    "stream": false
  }'
```

## Configuration

### Automatic Configuration
The installer automatically optimizes settings based on your model:

- **Small Models (1-3B)**: Conservative settings for stability
- **Medium Models (7-8B)**: Balanced performance settings  
- **Large Models (13B+)**: Generous settings for quality

### Manual Configuration
Edit `system_config.json` to customize:

```json
{
  "recommended_settings": {
    "model": "llama3.2:8b",
    "max_tokens": 2048,
    "temperature": 0.7
  }
}
```

### Parameters Explained
- **Temperature** (0.1-2.0): Controls creativity vs consistency
- **Max Tokens** (1-4096): Maximum response length
- **Auto-refresh**: Optional system monitoring toggle

## Troubleshooting

### Common Issues & Solutions

**"Ollama not found"**
```bash
brew install ollama
brew services start ollama
```

**"Model not found"**
```bash
ollama pull [model-name]
ollama list  # Check available models
```

**"Out of memory"**
- Try a smaller model: `ollama pull llama3.2:3b`
- Close other applications
- Restart Ollama: `brew services restart ollama`

**"Model loads slowly"**
- Normal for large models on first load
- Subsequent responses are much faster
- Consider switching to a smaller model

### Getting Help

1. **Check Ollama status**: `ollama list`
2. **View Ollama logs**: `brew services info ollama`
3. **Restart Ollama**: `brew services restart ollama`
4. **Re-run installer**: `./scripts/install.sh`

## Why Choose This Project?

- **Intelligent**: Automatically finds the best model for your hardware
- **Fast**: Optimized for performance with smart defaults
- **Beautiful**: Modern, responsive web interface
- **Easy**: One-command setup and configuration
- **Informative**: Real-time system monitoring
- **Flexible**: Easy model switching and parameter adjustment
- **Universal**: Works on any device with a browser

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- [Ollama](https://ollama.ai) for the amazing local LLM framework
- [Gradio](https://gradio.app) for the beautiful web interface
- The open-source AI community for the incredible models

---

**Made with ❤️ for the local AI community** 