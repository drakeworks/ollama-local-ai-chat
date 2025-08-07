# Ollama Local AI Chat

> **A modern web interface for chatting with local AI models using Ollama**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-green.svg)](https://ollama.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A clean, responsive web interface for chatting with local AI models powered by Ollama. Features real-time system monitoring, chat export/import, and model comparison capabilities.

## Features

- **Modern Web Interface** - Clean, responsive design with tabbed navigation
- **Real-time System Monitoring** - Live CPU, memory, and GPU usage display
- **Chat Export/Import** - Save and restore conversations in JSON format
- **Model Comparison** - Compare responses from different models side-by-side
- **System Analytics** - Performance monitoring and resource tracking
- **Easy Model Switching** - Seamlessly switch between available models
- **Enter Key Support** - Send messages with Enter key for quick interaction

## Quick Start

### Prerequisites
- **Python**: 3.8 or higher
- **Ollama**: [Install from ollama.ai](https://ollama.ai)
- **RAM**: 8GB minimum (16GB+ recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/drakeworks/ollama-local-ai-chat.git
cd ollama-local-ai-chat
```

2. **Set up Python environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Install and start Ollama**
```bash
# Follow instructions at https://ollama.ai
# Then pull a model:
ollama pull codellama:7b
```

4. **Launch the web interface**
```bash
python chat_ui.py
```

Open your browser to `http://localhost:7860` and start chatting!

## Usage

### Chat Interface
- **Type messages** in the text input and press Enter to send
- **Adjust parameters** using the sliders in the Chat Settings panel
- **Switch models** using the dropdown menu
- **Monitor system resources** in the System Status panel

### Data Management
- **Export conversations** to JSON files with metadata
- **Import previous chats** to restore conversations
- **Backup and restore** your chat history

### Model Comparison
- **Compare two models** side-by-side with the same prompt
- **Analyze differences** in response quality and length
- **Test model performance** before committing to one

### Analytics
- **Monitor system performance** in real-time
- **Track resource usage** during conversations
- **View performance ratings** and recommendations

## Project Structure

```
ollama-local-ai-chat/
├── chat_ui.py               # Main Gradio web interface
├── requirements.txt         # Python dependencies
├── scripts/
│   └── install.sh          # Installation script
├── README.md               # This file
├── LICENSE                 # MIT License
└── .gitignore              # Git exclusions
```

## Configuration

### Model Parameters
- **Temperature** (0.1-2.0): Controls response creativity
- **Max Tokens** (100-4096): Maximum response length
- **Model Selection**: Choose from available Ollama models

### System Monitoring
- **Real-time CPU usage** display
- **Memory usage** tracking
- **GPU detection** and monitoring
- **Resource refresh** button for manual updates

## Troubleshooting

### Common Issues

**"Ollama not available"**
- Ensure Ollama is running: `ollama serve`
- Check if models are downloaded: `ollama list`

**"No models available"**
- Download a model: `ollama pull codellama:7b`
- Check available models: `ollama list`

**"Out of memory"**
- Try a smaller model
- Close other applications
- Restart Ollama service

### Getting Help
1. Check Ollama status: `ollama list`
2. View Ollama logs: `ollama serve`
3. Restart the application: `python chat_ui.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Ollama](https://ollama.ai) for the local LLM framework
- [Gradio](https://gradio.app) for the web interface framework
- The open-source AI community for the models 