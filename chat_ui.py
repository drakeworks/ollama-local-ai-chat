#!/usr/bin/env python3
"""
Ollama Local AI Chat - Enhanced Version
A comprehensive Gradio interface for chatting with local LLMs via Ollama.
"""

import gradio as gr
import requests
import json
import psutil
import subprocess
import os
import datetime
from typing import Iterator, List, Dict, Tuple
from pathlib import Path


# Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
CURRENT_MODEL = "codellama:7b"  # Default model

# Constants
REQUEST_TIMEOUT = 5  # seconds
GPU_DETECTION_TIMEOUT = 5  # seconds

# Global state
chat_history = []



def check_ollama_status() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    except (requests.exceptions.RequestException, requests.exceptions.Timeout):
        return False

def get_available_models() -> List[str]:
    """Get list of available models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return [model['name'] for model in data.get('models', [])]
    except (requests.exceptions.RequestException, requests.exceptions.Timeout, json.JSONDecodeError):
        pass
    return [CURRENT_MODEL]

def get_system_resources() -> Dict[str, str]:
    """Get system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_gb = memory.used / (1024**3)
        memory_total_gb = memory.total / (1024**3)
        
        gpu_info = "Not detected"
        try:
            if os.path.exists('/usr/bin/nvidia-smi'):
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=GPU_DETECTION_TIMEOUT)
                if result.returncode == 0:
                    gpu_info = result.stdout.strip()
            else:
                result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                      capture_output=True, text=True, timeout=GPU_DETECTION_TIMEOUT)
                if 'Apple Silicon' in result.stdout:
                    gpu_info = "Apple Silicon (M1/M2/M3)"
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return {
            "cpu": f"{cpu_percent:.1f}%",
            "memory": f"{memory_gb:.1f}/{memory_total_gb:.1f} GB",
            "gpu": gpu_info,
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
        }
    except Exception:
        return {
            "cpu": "N/A",
            "memory": "N/A", 
            "gpu": "N/A",
            "timestamp": "N/A"
        }

def generate_response(message: str, history: list, model: str, temperature: float = 0.7, max_tokens: int = 2048) -> Iterator[str]:
    """Generate a response from the model."""
    
    if not check_ollama_status():
        yield "❌ Error: Ollama is not running or the model is not available."
        return
    
    try:
        conversation = ""
        for msg in history:
            if msg["role"] == "user":
                conversation += f"User: {msg['content']}\n"
            elif msg["role"] == "assistant" and msg["content"]:
                conversation += f"Assistant: {msg['content']}\n"
        
        conversation += f"User: {message}\nAssistant:"
        
        data = {
            "model": model,
            "prompt": conversation,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        response = requests.post(
            OLLAMA_API_URL,
            json=data,
            stream=True,
            timeout=300
        )
        
        if response.status_code != 200:
            yield f"❌ Error: HTTP {response.status_code}"
            return
        
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

def export_chat_history(history: list, model: str, temperature: float, max_tokens: int) -> Tuple[str, str]:
    """Export chat history to JSON file."""
    try:
        if not history:
            return "No chat history to export", ""
        
        export_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model": model,
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            "conversation": history
        }
        
        filename = f"chat_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(filename)
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return f"✅ Chat exported to {filename}", str(filepath.absolute())
    except Exception as e:
        return f"❌ Export failed: {str(e)}", ""

def import_chat_history(file) -> Tuple[str, list, str, float, int]:
    """Import chat history from JSON file."""
    try:
        if file is None:
            return "No file selected", [], "", 0.7, 2048
        
        with open(file.name, 'r') as f:
            data = json.load(f)
        
        # Validate file structure
        if not all(key in data for key in ["conversation", "model", "parameters"]):
            return "❌ Invalid file format", [], "", 0.7, 2048
        
        conversation = data["conversation"]
        model = data["model"]
        params = data["parameters"]
        
        return f"✅ Imported {len(conversation)} messages", conversation, model, params.get("temperature", 0.7), params.get("max_tokens", 2048)
    except Exception as e:
        return f"❌ Import failed: {str(e)}", [], "", 0.7, 2048



def update_analytics() -> Tuple[str, str, str, str]:
    """Update analytics with performance metrics."""
    resources = get_system_resources()
    
    # Calculate some basic metrics
    memory_used = resources["memory"].split("/")[0].strip()
    memory_total = resources["memory"].split("/")[1].strip()
    
    # Simple performance rating
    cpu_val = float(resources["cpu"].replace("%", ""))
    if cpu_val < 30:
        performance = "Excellent"
    elif cpu_val < 60:
        performance = "Good"
    elif cpu_val < 80:
        performance = "Fair"
    else:
        performance = "Poor"
    
    return (
        f"Last Update: {resources['timestamp']}",
        f"Performance: {performance}",
        f"Memory Usage: {memory_used} of {memory_total}",
        f"Auto-refresh: Disabled"
    )

def compare_models(prompt: str, model1: str, model2: str, temperature: float, max_tokens: int) -> Tuple[str, str]:
    """Compare responses from two different models."""
    if not prompt.strip():
        return "Please enter a prompt to compare models", ""
    
    # Check if models are valid
    if model1 in ["No models available", "Download another model"] or model2 in ["No models available", "Download another model"]:
        return "❌ Please download at least 2 models to use the comparison feature", ""
    
    if model1 == model2:
        return "❌ Please select two different models for comparison", ""
    
    try:
        # Get response from first model
        response1 = ""
        for chunk in generate_response(prompt, [], model1, temperature, max_tokens):
            response1 = chunk
        
        # Get response from second model
        response2 = ""
        for chunk in generate_response(prompt, [], model2, temperature, max_tokens):
            response2 = chunk
        
        comparison = f"""
**Model 1 ({model1}):**
{response1}

---
**Model 2 ({model2}):**
{response2}

---
**Comparison:**
- Model 1 length: {len(response1)} characters
- Model 2 length: {len(response2)} characters
- Response time: {datetime.datetime.now().strftime('%H:%M:%S')}
"""
        
        return comparison, f"Comparison completed at {datetime.datetime.now().strftime('%H:%M:%S')}"
    except Exception as e:
        return f"❌ Comparison failed: {str(e)}", ""

def create_interface():
    """Create the enhanced Gradio interface with tabs."""
    
    css = """
    .gradio-container,
    .gradio-container > div,
    .gradio-container > div > div,
    .gradio-container > div > div > div {
        max-width: none !important;
        width: 100% !important;
    }
    .gradio-container {
        margin: 0 auto !important;
    }
    .gradio-tabs {
        margin-bottom: 20px !important;
    }
    .gradio-accordion {
        margin-bottom: 16px !important;
    }
    .gradio-group {
        padding: 16px !important;
    }
    .comparison-container {
        display: flex;
        gap: 20px;
    }
    .comparison-column {
        flex: 1;
    }

    """
    

    
    with gr.Blocks(title="Ollama Local AI Chat", css=css) as interface:
        gr.Markdown("# Ollama Local AI Chat")
        gr.Markdown("A comprehensive local AI chat platform with advanced features.")
        
        with gr.Tabs():
            # Chat Tab
            with gr.Tab("Chat"):
                with gr.Row():
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            label="Chat",
                            height=500,
                            type="messages",
                            show_copy_button=True
                        )
                        
                        msg = gr.Textbox(
                            label="Message",
                            placeholder="Type your message here... (Press Enter to send)",
                            lines=1
                        )
                        
                        with gr.Row():
                            send_btn = gr.Button("Send", variant="primary")
                            clear_btn = gr.Button("Clear Chat", variant="secondary")
                    
                    with gr.Column(scale=1):
                        with gr.Accordion("Chat Settings", open=True):
                            # Cache available models to avoid multiple API calls
                            available_models = get_available_models()
                            # Ensure the default model is in the choices
                            if CURRENT_MODEL not in available_models:
                                available_models.insert(0, CURRENT_MODEL)
                            model_dropdown = gr.Dropdown(
                                choices=available_models,
                                value=CURRENT_MODEL,
                                label="Select Model"
                            )
                            
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
                        
                        with gr.Accordion("System Status", open=True):
                            with gr.Row():
                                status_text = gr.Textbox(
                                    label="Ollama Status",
                                    value="Checking...",
                                    interactive=False,
                                    scale=3
                                )
                                refresh_status_btn = gr.Button("Refresh Status", size="sm")
                            
                            with gr.Row():
                                cpu_text = gr.Textbox(
                                    label="CPU",
                                    value="Loading...",
                                    interactive=False,
                                    scale=1
                                )
                                memory_text = gr.Textbox(
                                    label="Memory",
                                    value="Loading...",
                                    interactive=False,
                                    scale=1
                                )
                                gpu_text = gr.Textbox(
                                    label="GPU",
                                    value="Loading...",
                                    interactive=False,
                                    scale=1
                                )
                            
                            with gr.Row():
                                last_update = gr.Textbox(
                                    label="Last Update",
                                    value="Never",
                                    interactive=False,
                                    scale=3
                                )
                                refresh_resources_btn = gr.Button("Refresh", size="sm", variant="secondary")
            
            # Data Management Tab
            with gr.Tab("Data Management"):
                gr.Markdown("### Chat Export and Import")
                gr.Markdown("Export your conversations or import previous chats.")
                
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("#### Import Chat")
                        import_file = gr.File(
                            label="Select Chat Export File (.json)",
                            file_types=[".json"]
                        )
                        import_btn = gr.Button("📥 Import Chat", variant="secondary")
                        import_status = gr.Textbox(
                            label="Import Status",
                            value="Ready to import",
                            interactive=False
                        )
                        
                        # Show import info
                        gr.Markdown("**Import will:**")
                        gr.Markdown("- Load conversation history")
                        gr.Markdown("- Restore model settings")
                        gr.Markdown("- Replace current chat")
                        gr.Markdown("- Validate file format")
                    
                    with gr.Column():
                        gr.Markdown("#### Export Chat")
                        export_btn = gr.Button("📤 Export Current Chat", variant="primary")
                        export_status = gr.Textbox(
                            label="Export Status",
                            value="Ready to export",
                            interactive=False
                        )
                        
                        # Show export info
                        gr.Markdown("**Export includes:**")
                        gr.Markdown("- Full conversation history")
                        gr.Markdown("- Model used and parameters")
                        gr.Markdown("- Timestamp and metadata")
                        gr.Markdown("- Saved as JSON file in project directory")
                
                with gr.Accordion("Export/Import Settings", open=False):
                    gr.Markdown("**Export/Import Configuration**")
                    gr.Markdown("Future export/import settings will be added here.")
            

            
            # Analytics Tab
            with gr.Tab("Analytics"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### System Performance")
                        analytics_status = gr.Textbox(
                            label="Status",
                            value="Loading analytics...",
                            interactive=False
                        )
                        performance_rating = gr.Textbox(
                            label="Performance Rating",
                            value="Calculating...",
                            interactive=False
                        )
                        memory_usage = gr.Textbox(
                            label="Memory Usage",
                            value="Loading...",
                            interactive=False
                        )
                        auto_refresh_status = gr.Textbox(
                            label="Auto-refresh Status",
                            value="Checking...",
                            interactive=False
                        )
                        update_analytics_btn = gr.Button("Update Analytics")
                    
                    with gr.Column():
                        gr.Markdown("### Usage Statistics")
                        gr.Markdown("**Future Features:**")
                        gr.Markdown("- Message count tracking")
                        gr.Markdown("- Session statistics")
                        gr.Markdown("- Model usage analytics")
            
            # Model Comparison Tab
            with gr.Tab("Model Comparison"):
                gr.Markdown("### Compare Two Models Side by Side")
                
                # Show available models info (reuse cached models)
                if len(available_models) < 2:
                    gr.Markdown(f"⚠️ **Note**: You have {len(available_models)} model(s) downloaded. Download at least 2 models to use the comparison feature.")
                else:
                    gr.Markdown(f"✅ **Available models**: {', '.join(available_models)}")
                
                with gr.Row():
                    with gr.Column():
                        comparison_prompt = gr.Textbox(
                            label="Prompt for Comparison",
                            placeholder="Enter a prompt to compare models...",
                            lines=3
                        )
                        
                        with gr.Row():
                            # Use cached available models
                            downloaded_models = available_models.copy()
                            
                            # Ensure we have at least 2 models for comparison
                            if len(downloaded_models) < 2:
                                # If we don't have enough models, add a placeholder
                                if len(downloaded_models) == 0:
                                    downloaded_models = ["No models available"]
                                elif len(downloaded_models) == 1:
                                    downloaded_models.append("Download another model")
                            
                            model1_dropdown = gr.Dropdown(
                                choices=downloaded_models,
                                value=downloaded_models[0] if downloaded_models else CURRENT_MODEL,
                                label="Model 1"
                            )
                            model2_dropdown = gr.Dropdown(
                                choices=downloaded_models,
                                value=downloaded_models[1] if len(downloaded_models) > 1 else downloaded_models[0],
                                label="Model 2"
                            )
                        
                        comparison_temperature = gr.Slider(
                            minimum=0.1,
                            maximum=2.0,
                            value=0.7,
                            step=0.1,
                            label="Temperature"
                        )
                        comparison_max_tokens = gr.Slider(
                            minimum=100,
                            maximum=4096,
                            value=2048,
                            step=100,
                            label="Max Tokens"
                        )
                        
                        compare_btn = gr.Button("Compare Models", variant="primary")
                        comparison_status = gr.Textbox(
                            label="Comparison Status",
                            value="Ready to compare",
                            interactive=False
                        )
                    
                    with gr.Column():
                        comparison_result = gr.Markdown(
                            value="## Model Comparison\n\nEnter a prompt and select two models to compare their responses."
                        )
        
        # Event handlers
        def user_input(message, history, temp, max_tok):
            if not message.strip():
                return "", history
            history.append({"role": "user", "content": message})
            return "", history
        
        def bot_response(history, temp, max_tok, model):
            if not history:
                return history
            
            user_message = history[-1]["content"]
            history.append({"role": "assistant", "content": ""})
            
            for chunk in generate_response(user_message, history[:-2], model, temp, max_tok):
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
            return resources["cpu"], resources["memory"], resources["gpu"], resources["timestamp"]
        
        def export_chat(history, model, temp, max_tok):
            return export_chat_history(history, model, temp, max_tok)
        
        def import_chat(file):
            return import_chat_history(file)
        

        
        def update_analytics_data():
            return update_analytics()
        
        def compare_models_response(prompt, model1, model2, temp, max_tok):
            return compare_models(prompt, model1, model2, temp, max_tok)
        
        # Connect events
        msg.submit(
            user_input,
            [msg, chatbot, temperature, max_tokens],
            [msg, chatbot],
            queue=False
        ).then(
            bot_response,
            [chatbot, temperature, max_tokens, model_dropdown],
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
            [chatbot, temperature, max_tokens, model_dropdown],
            chatbot,
            api_name="generate"
        )
        
        clear_btn.click(clear_chat, outputs=chatbot)
        export_btn.click(export_chat, [chatbot, model_dropdown, temperature, max_tokens], [export_status, import_file])
        import_btn.click(import_chat, [import_file], [import_status, chatbot, model_dropdown, temperature, max_tokens])
        
        refresh_status_btn.click(update_status, outputs=status_text)
        refresh_resources_btn.click(update_resources, outputs=[cpu_text, memory_text, gpu_text, last_update])
        

        update_analytics_btn.click(update_analytics_data, outputs=[analytics_status, performance_rating, memory_usage, auto_refresh_status])
        compare_btn.click(compare_models_response, [comparison_prompt, model1_dropdown, model2_dropdown, comparison_temperature, comparison_max_tokens], [comparison_result, comparison_status])
        
        # Initialize
        interface.load(update_status, outputs=status_text)
        interface.load(update_resources, outputs=[cpu_text, memory_text, gpu_text, last_update])
        interface.load(update_analytics_data, outputs=[analytics_status, performance_rating, memory_usage, auto_refresh_status])
    
    return interface

if __name__ == "__main__":
    print("Starting Ollama Local AI Chat - Enhanced...")
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