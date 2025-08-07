#!/usr/bin/env python3
"""
Ollama Local AI Chat - Clean Version
A simple Gradio interface for chatting with local LLMs via Ollama.
"""

import gradio as gr
import requests
import json
import time
import psutil
import subprocess
from typing import Iterator, List, Dict
import os

# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
CURRENT_MODEL = "codellama:7b"  # Default model

def load_system_config():
    """Load system configuration from JSON file."""
    try:
        with open('system_config.json', 'r') as f:
            config = json.load(f)
            return config.get('recommended_settings', {})
    except FileNotFoundError:
        # Fallback configuration
        return {
            'model': 'codellama:7b',
            'max_tokens': 2048,
            'temperature': 0.7
        }

def check_ollama_status() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_available_models() -> List[str]:
    """Get list of available models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
    except:
        pass
    return [CURRENT_MODEL]

def get_system_resources() -> Dict[str, str]:
    """Get system resource usage."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        # GPU info (simplified)
        gpu_info = "Not detected"
        try:
            # Try to get GPU info
            if os.path.exists('/usr/bin/nvidia-smi'):
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    gpu_info = result.stdout.strip()
            else:
                # macOS GPU detection
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True, timeout=5)
                if 'Apple Silicon' in result.stdout:
                    gpu_info = "Apple Silicon (M1/M2/M3)"
        except:
            pass
        
        return {
            "cpu": f"{cpu_percent:.1f}%",
            "memory": f"{memory_gb:.1f}/{memory_total_gb:.1f} GB",
            "gpu": gpu_info
        }
    except:
        return {
            "cpu": "N/A",
            "memory": "N/A", 
            "gpu": "N/A"
        }

def generate_response(message: str, history: list, temperature: float = 0.7, max_tokens: int = 2048) -> Iterator[str]:
    """Generate a response from the model."""
    
    if not check_ollama_status():
        yield "❌ Error: Ollama is not running or the model is not available."
        return
    
    try:
        # Build conversation context
        conversation = ""
        for msg in history:
            if msg["role"] == "user":
                conversation += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant" and msg["content"]:
                conversation += f"Assistant: {msg['content']}\n"
        
        conversation += f"User: {message}\nAssistant:"
        
        # Prepare request
        data = {
            "model": CURRENT_MODEL,
            "prompt": conversation,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Make request
        response = requests.post(
            OLLAMA_API_URL,
            json=data,
            stream=True,
            timeout=300
        )
        
        if response.status_code != 200:
            yield f"❌ Error: HTTP {response.status_code}"
            return
        
        # Stream response
        full_response = ""
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line.decode('utf-8'))
                    if 'response' in chunk:
                        full_response += chunk['response']
                        yield full_response
                    elif chunk.get('done', False):
                        break
                except json.JSONDecodeError:
                    continue
                    
    except requests.exceptions.Timeout:
        yield "❌ Timeout: Model is taking too long to respond."
    except requests.exceptions.ConnectionError:
        yield "❌ Error connecting to Ollama: Please ensure Ollama is running."

def create_interface():
    """Create the Gradio interface."""
    
    # Minimal CSS for better spacing
    css = """
    .gradio-group {
        padding: 16px !important;
    }
    .gradio-group h3 {
        margin-top: 0 !important;
        margin-bottom: 16px !important;
    }
    .gradio-group .markdown {
        padding: 0 !important;
        margin: 0 !important;
    }
    .gradio-group .markdown h3 {
        padding: 0 !important;
        margin: 0 0 16px 0 !important;
    }
    """
    
    with gr.Blocks(title="Ollama Local AI Chat", css=css) as interface:
        gr.Markdown("# Ollama Local AI Chat")
        gr.Markdown("Chat with large language models running locally on your machine.")
        
        with gr.Row():
            # Chat section
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(
                    label="Chat",
                    height=600,
                    type="messages",
                    show_copy_button=True
                )
                
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Type your message here...",
                    lines=1
                )
                
                with gr.Row():
                    send_btn = gr.Button("Send", variant="primary")
                    clear_btn = gr.Button("Clear Chat", variant="secondary")
            
            # Sidebar section
            with gr.Column(scale=1):
                # System Status
                with gr.Group():
                    gr.Markdown("### System Status")
                    
                    available_models = get_available_models()
                    model_dropdown = gr.Dropdown(
                        choices=available_models,
                        value=CURRENT_MODEL,
                        label="Select Model"
                    )
                    
                    status_text = gr.Textbox(
                        label="Ollama Status",
                        value="Checking...",
                        interactive=False
                    )
                    refresh_status_btn = gr.Button("Refresh Status")
                
                # Model Parameters
                with gr.Group():
                    gr.Markdown("### Model Parameters")
                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=0.7,
                        step=0.1,
                        label="Temperature"
                    )
                    max_tokens = gr.Slider(
                        minimum=100,
                        maximum=4096,
                        value=2048,
                        step=100,
                        label="Max Tokens"
                    )
                
                # System Resources
                with gr.Group():
                    gr.Markdown("### System Resources")
                    cpu_text = gr.Textbox(
                        label="CPU",
                        value="Loading...",
                        interactive=False
                    )
                    memory_text = gr.Textbox(
                        label="Memory",
                        value="Loading...",
                        interactive=False
                    )
                    gpu_text = gr.Textbox(
                        label="GPU",
                        value="Loading...",
                        interactive=False
                    )
                    refresh_resources_btn = gr.Button("Refresh Resources")
        
        # Event handlers
        def user_input(message, history, temp, max_tok):
            if not message.strip():
                return "", history
            history.append({"role": "user", "content": message})
            return "", history
        
        def bot_response(history, temp, max_tok):
            if not history:
                return history
            
            user_message = history[-1]["content"]
            
            # Add empty assistant message to start
            history.append({"role": "assistant", "content": ""})
            
            # Stream the response
            for chunk in generate_response(user_message, history[:-2], temp, max_tok):
                history[-1]["content"] = chunk
                yield history
            
            return history
        
        def clear_chat():
            return []
        
        def update_status():
            status = "✅ Connected and ready" if check_ollama_status() else "❌ Ollama not available"
            return status
        
        def update_resources():
            resources = get_system_resources()
            return resources["cpu"], resources["memory"], resources["gpu"]
        
        def switch_model(selected_model):
            global CURRENT_MODEL
            if selected_model:
                CURRENT_MODEL = selected_model
                return f"Switched to {selected_model}"
            return "No model selected"
        
        # Connect events
        msg.submit(
            user_input,
            [msg, chatbot, temperature, max_tokens],
            [msg, chatbot],
            queue=False
        ).then(
            bot_response,
            [chatbot, temperature, max_tokens],
            chatbot,
            api_name="generate"
        )
        
        send_btn.click(
            user_input,
            [msg, chatbot, temperature, max_tokens],
            [msg, chatbot],
            queue=False
        ).then(
            bot_response,
            [chatbot, temperature, max_tokens],
            chatbot,
            api_name="generate"
        )
        
        clear_btn.click(clear_chat, outputs=chatbot)
        refresh_status_btn.click(update_status, outputs=status_text)
        refresh_resources_btn.click(update_resources, outputs=[cpu_text, memory_text, gpu_text])
        model_dropdown.change(switch_model, inputs=model_dropdown, outputs=status_text)
        
        # Initialize
        interface.load(update_status, outputs=status_text)
        interface.load(update_resources, outputs=[cpu_text, memory_text, gpu_text])
    
    return interface

if __name__ == "__main__":
    print("Starting Ollama Local AI Chat...")
    print("Opening interface at http://localhost:7860")
    print("Press Ctrl+C to stop the server")
    print()
    
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
        show_api=True
    ) 