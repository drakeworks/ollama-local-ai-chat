#!/bin/bash

# Ollama Intelligent Installation Script with Model Selection
# This script analyzes your system and lets you choose the best model

set -e  # Exit on any error

# System analysis variables
SYSTEM_RAM_GB=0
SYSTEM_CPU_CORES=0
SYSTEM_GPU_TYPE=""
SYSTEM_GPU_VRAM_GB=0
SELECTED_MODEL=""
SELECTED_MAX_TOKENS=2048
SELECTED_TEMPERATURE=0.7

echo "Ollama Local AI Chat - Intelligent Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}[HEADER]${NC} $1"
}

# Function to analyze system capabilities
analyze_system() {
    print_status "Analyzing your system capabilities..."
    echo ""
    
    # Get system RAM
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        SYSTEM_RAM_GB=$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
        SYSTEM_CPU_CORES=$(sysctl -n hw.ncpu)
        
        # Check for Apple Silicon
        if [[ $(uname -m) == "arm64" ]]; then
            SYSTEM_GPU_TYPE="Apple Silicon (M1/M2/M3)"
            SYSTEM_GPU_VRAM_GB=0  # Unified memory
            print_success "Detected Apple Silicon with unified memory"
        else
            SYSTEM_GPU_TYPE="Intel Integrated"
            SYSTEM_GPU_VRAM_GB=0
            print_success "Detected Intel Mac"
        fi
    else
        # Linux
        SYSTEM_RAM_GB=$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / 1024 / 1024))
        SYSTEM_CPU_CORES=$(nproc)
        
        # Check for NVIDIA GPU
        if command -v nvidia-smi &> /dev/null; then
            GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1)
            SYSTEM_GPU_TYPE=$(echo $GPU_INFO | cut -d',' -f1 | tr -d ' ')
            SYSTEM_GPU_VRAM_GB=$(($(echo $GPU_INFO | cut -d',' -f2 | tr -d ' ') / 1024))
            print_success "Detected NVIDIA GPU: $SYSTEM_GPU_TYPE"
        else
            SYSTEM_GPU_TYPE="CPU Only"
            SYSTEM_GPU_VRAM_GB=0
            print_success "No dedicated GPU detected, will use CPU"
        fi
    fi
    
    echo ""
    print_status "System Analysis Results:"
    echo "   RAM: ${SYSTEM_RAM_GB}GB"
    echo "   CPU Cores: ${SYSTEM_CPU_CORES}"
    echo "   GPU: ${SYSTEM_GPU_TYPE}"
    if [[ $SYSTEM_GPU_VRAM_GB -gt 0 ]]; then
        echo "   GPU VRAM: ${SYSTEM_GPU_VRAM_GB}GB"
    fi
    echo ""
}

# Function to get recommended models based on system
get_recommended_models() {
    local ram=$1
    local gpu_vram=$2
    
    echo ""
    print_header "RECOMMENDED MODELS FOR YOUR SYSTEM"
    echo "================================================"
    echo ""
    
    if [[ $ram -ge 32 && $gpu_vram -ge 8 ]]; then
        # High-end system
        print_success "HIGH-END SYSTEM DETECTED"
        echo "   You can run any model comfortably!"
        echo ""
        echo "   🥇 BEST CHOICE: llama3.2:14b (7.8GB)"
        echo "      - Excellent quality and speed"
        echo "      - Fast responses (5-15 seconds)"
        echo "      - Great for complex tasks"
        echo ""
        echo "   🥈 ALTERNATIVE: mistral:14b (7.8GB)"
        echo "      - Very high quality"
        echo "      - Good for reasoning tasks"
        echo ""
        echo "   🥉 EXPERIMENTAL: gpt-oss:20b (13GB)"
        echo "      - Largest available model"
        echo "      - May be slower to load"
        echo ""
    elif [[ $ram -ge 16 && $ram -lt 32 ]]; then
        # Mid-range system (like yours)
        print_success "MID-RANGE SYSTEM DETECTED"
        echo "   Good balance of performance and memory usage"
        echo ""
        echo "   🥇 BEST CHOICE: llama3.2:8b (4.7GB)"
        echo "      - Excellent quality/speed ratio"
        echo "      - Fast responses (3-10 seconds)"
        echo "      - Stays loaded in memory"
        echo ""
        echo "   🥈 ALTERNATIVE: mistral:7b (4.1GB)"
        echo "      - Very good performance"
        echo "      - Great for most tasks"
        echo ""
        echo "   🥉 CODING: codellama:7b (4.1GB)"
        echo "      - Excellent for programming"
        echo "      - Code generation and debugging"
        echo ""
        echo "   ⚠️  CHALLENGING: gpt-oss:20b (13GB)"
        echo "      - Will unload after each use"
        echo "      - 30-60 second reload time"
        echo "      - Not recommended for your RAM"
        echo ""
    elif [[ $ram -ge 8 && $ram -lt 16 ]]; then
        # Lower-end system
        print_warning "LOWER-END SYSTEM DETECTED"
        echo "   Focus on smaller, faster models"
        echo ""
        echo "   🥇 BEST CHOICE: llama3.2:3b (2.1GB)"
        echo "      - Fast and efficient"
        echo "      - Good for chat and basic tasks"
        echo "      - Stays loaded in memory"
        echo ""
        echo "   🥈 ALTERNATIVE: phi3:mini (1.8GB)"
        echo "      - Microsoft's efficient model"
        echo "      - Good performance/size ratio"
        echo ""
        echo "   🥉 LIGHTWEIGHT: llama3.2:1b (0.8GB)"
        echo "      - Very fast responses"
        echo "      - Basic tasks only"
        echo ""
    else
        # Basic system
        print_warning "BASIC SYSTEM DETECTED"
        echo "   Use only the smallest models"
        echo ""
        echo "   🥇 BEST CHOICE: llama3.2:1b (0.8GB)"
        echo "      - Fastest available model"
        echo "      - Minimal memory usage"
        echo ""
        echo "   🥈 ALTERNATIVE: gemma2:2b (1.4GB)"
        echo "      - Google's lightweight model"
        echo "      - Good for basic tasks"
        echo ""
    fi
}



# Function to get user model selection
get_model_selection() {
    echo ""
    print_header "MODEL SELECTION"
    echo "================================================"
    echo ""
    
    # Show recommended models first
    get_recommended_models $SYSTEM_RAM_GB $SYSTEM_GPU_VRAM_GB
    
    # Show all models with numbers
    show_all_models_numbered
    
    echo ""
    print_status "Select models to download (enter numbers separated by spaces):"
    echo "   (e.g., 1 3 5 for multiple models, or just 1 for single model)"
    echo ""
    read -p "Model numbers: " SELECTED_NUMBERS
    
    # Convert numbers to model names
    SELECTED_MODELS=()
    for num in $SELECTED_NUMBERS; do
        case $num in
            1) SELECTED_MODELS+=("llama3.2:3b") ;;      # ✅ Verified
            2) SELECTED_MODELS+=("llama3.2:1b") ;;
            3) SELECTED_MODELS+=("phi3:mini") ;;
            4) SELECTED_MODELS+=("gemma2:2b") ;;
            5) SELECTED_MODELS+=("qwen2.5:3b") ;;
            6) SELECTED_MODELS+=("llama3.2:8b") ;;
            7) SELECTED_MODELS+=("llama3.1:8b") ;;
            8) SELECTED_MODELS+=("mistral:7b") ;;
            9) SELECTED_MODELS+=("codellama:7b") ;;     # ✅ Verified
            10) SELECTED_MODELS+=("qwen2.5:7b") ;;
            11) SELECTED_MODELS+=("llama3.2:14b") ;;
            12) SELECTED_MODELS+=("llama3.1:14b") ;;
            13) SELECTED_MODELS+=("mistral:14b") ;;
            14) SELECTED_MODELS+=("gpt-oss:20b") ;;     # ✅ Verified
            15) SELECTED_MODELS+=("codellama:13b") ;;
            16) SELECTED_MODELS+=("codellama:34b") ;;
            17) SELECTED_MODELS+=("neural-chat:7b") ;;
            18) SELECTED_MODELS+=("dolphin-phi:3b") ;;
            *) print_warning "Invalid number: $num (skipping)" ;;
        esac
    done
    
    if [ ${#SELECTED_MODELS[@]} -eq 0 ]; then
        print_error "No valid models selected. Please try again."
        exit 1
    fi
    
    echo ""
    print_success "Selected models:"
    for model in "${SELECTED_MODELS[@]}"; do
        echo "   - $model"
    done
    
    # Set the primary model (first selected) for configuration
    SELECTED_MODEL="${SELECTED_MODELS[0]}"
    
    # Set recommended parameters based on primary model size
    if [[ $SELECTED_MODEL == *":1b" ]] || [[ $SELECTED_MODEL == *":2b" ]] || [[ $SELECTED_MODEL == *":3b" ]]; then
        SELECTED_MAX_TOKENS=2048
        SELECTED_TEMPERATURE=0.7
        print_status "Small model detected - using conservative settings"
    elif [[ $SELECTED_MODEL == *":7b" ]] || [[ $SELECTED_MODEL == *":8b" ]]; then
        SELECTED_MAX_TOKENS=3072
        SELECTED_TEMPERATURE=0.8
        print_status "Medium model detected - using balanced settings"
    elif [[ $SELECTED_MODEL == *":13b" ]] || [[ $SELECTED_MODEL == *":14b" ]]; then
        SELECTED_MAX_TOKENS=4096
        SELECTED_TEMPERATURE=0.8
        print_status "Large model detected - using generous settings"
    elif [[ $SELECTED_MODEL == *":20b" ]] || [[ $SELECTED_MODEL == *":34b" ]]; then
        SELECTED_MAX_TOKENS=2048
        SELECTED_TEMPERATURE=0.7
        print_warning "Very large model detected - using conservative settings for stability"
    else
        SELECTED_MAX_TOKENS=2048
        SELECTED_TEMPERATURE=0.7
        print_status "Using default settings"
    fi
    
    echo ""
    print_status "📋 Primary Model Configuration:"
    echo "   Model: $SELECTED_MODEL"
    echo "   Max Tokens: $SELECTED_MAX_TOKENS"
    echo "   Temperature: $SELECTED_TEMPERATURE"
    echo ""
}

# Function to show all available models with numbers
show_all_models_numbered() {
    echo ""
    print_header "ALL AVAILABLE MODELS"
    echo "================================================"
    echo ""
    
    echo "🟢 EXCELLENT (2-4GB) - Fast, stays loaded:"
    echo "   1. llama3.2:3b     (2.0GB) - Fast, good quality ✅"
    echo "   2. llama3.2:1b     (0.8GB) - Very fast, basic"
    echo "   3. phi3:mini       (1.8GB) - Microsoft's efficient"
    echo "   4. gemma2:2b       (1.4GB) - Google's lightweight"
    echo "   5. qwen2.5:3b      (2.1GB) - Alibaba's efficient"
    echo ""
    
    echo "🟡 GOOD (4-8GB) - Balanced performance:"
    echo "   6. llama3.2:8b     (4.7GB) - Excellent quality"
    echo "   7. llama3.1:8b     (4.7GB) - Stable, well-tested"
    echo "   8. mistral:7b      (4.1GB) - Great performance"
    echo "   9. codellama:7b    (3.8GB) - Excellent for coding ✅"
    echo "   10. qwen2.5:7b     (4.7GB) - Good balance"
    echo ""
    
    echo "🔴 LARGE (8-13GB) - High quality, slower:"
    echo "   11. llama3.2:14b   (7.8GB) - High quality"
    echo "   12. llama3.1:14b   (7.8GB) - Complex tasks"
    echo "   13. mistral:14b    (7.8GB) - Better reasoning"
    echo "   14. gpt-oss:20b    (13GB)  - Largest available ✅"
    echo ""
    
    echo "🟣 SPECIALIZED - Domain-specific:"
    echo "   15. codellama:13b  (7.8GB) - Advanced coding"
    echo "   16. codellama:34b  (19GB)  - Professional coding"
    echo "   17. neural-chat:7b (4.1GB) - Conversational AI"
    echo "   18. dolphin-phi:3b (1.8GB) - Helpful assistant"
    echo ""
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_warning "This script is optimized for macOS. You may need to adapt it for your system."
fi

# Step 0: Analyze system capabilities
analyze_system

# Step 1: Check if Homebrew is installed
print_status "Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed. Please install it first:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi
print_success "Homebrew is installed"

# Step 2: Install Ollama
print_status "Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    brew install ollama
    print_success "Ollama installed successfully"
else
    print_success "Ollama is already installed"
fi

# Step 3: Start Ollama service
print_status "Starting Ollama service..."
if ! brew services list | grep -q "ollama.*started"; then
    brew services start ollama
    print_success "Ollama service started"
    
    # Wait a moment for the service to fully start
    print_status "Waiting for Ollama to fully start..."
    sleep 5
else
    print_success "Ollama service is already running"
fi

# Step 4: Get user model selection
get_model_selection

# Step 5: Download selected models
print_status "Processing model downloads..."
echo ""

# Calculate total download size
TOTAL_SIZE=0
MODELS_TO_DOWNLOAD=()

for model in "${SELECTED_MODELS[@]}"; do
    if ollama list | grep -q "$model"; then
        print_success "$model is already downloaded"
    else
        MODELS_TO_DOWNLOAD+=("$model")
        
        # Calculate size for this model (updated with actual sizes)
        if [[ $model == *":1b" ]]; then
            MODEL_SIZE=0.8
        elif [[ $model == *":2b" ]]; then
            MODEL_SIZE=1.4
        elif [[ $model == *":3b" ]]; then
            MODEL_SIZE=2.0  # Updated: llama3.2:3b is actually 2.0GB
        elif [[ $model == *":7b" ]]; then
            MODEL_SIZE=3.8  # Updated: codellama:7b is actually 3.8GB
        elif [[ $model == *":8b" ]]; then
            MODEL_SIZE=4.7
        elif [[ $model == *":13b" ]]; then
            MODEL_SIZE=7.8
        elif [[ $model == *":14b" ]]; then
            MODEL_SIZE=7.8
        elif [[ $model == *":20b" ]]; then
            MODEL_SIZE=13   # Verified: gpt-oss:20b is 13GB
        elif [[ $model == *":34b" ]]; then
            MODEL_SIZE=19
        else
            MODEL_SIZE=5
        fi
        TOTAL_SIZE=$(echo "$TOTAL_SIZE + $MODEL_SIZE" | bc -l)
    fi
done

if [ ${#MODELS_TO_DOWNLOAD[@]} -eq 0 ]; then
    print_success "All selected models are already downloaded!"
else
    echo ""
    print_status "Models to download:"
    for model in "${MODELS_TO_DOWNLOAD[@]}"; do
        echo "   - $model"
    done
    echo ""
    print_warning "Total download size: ~${TOTAL_SIZE}GB"
    print_warning "This may take a while depending on your internet connection."
    echo ""
    
    # Ask for confirmation
    read -p "Do you want to continue with the downloads? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for model in "${MODELS_TO_DOWNLOAD[@]}"; do
            print_status "Downloading $model..."
            ollama pull $model
            print_success "$model downloaded successfully"
            echo ""
        done
    else
        print_warning "Model downloads skipped. You can download them later with:"
        for model in "${MODELS_TO_DOWNLOAD[@]}"; do
            echo "   ollama pull $model"
        done
        exit 0
    fi
fi

# Step 6: Install Python dependencies
print_status "Installing Python dependencies..."
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

print_status "Activating virtual environment and installing packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
print_success "Python dependencies installed"

# Step 7: Generate system configuration
print_status "Generating system configuration..."
cat > system_config.json << EOF
{
    "system_analysis": {
        "ram_gb": $SYSTEM_RAM_GB,
        "cpu_cores": $SYSTEM_CPU_CORES,
        "gpu_type": "$SYSTEM_GPU_TYPE",
        "gpu_vram_gb": $SYSTEM_GPU_VRAM_GB
    },
    "recommended_settings": {
        "model": "$SELECTED_MODEL",
        "max_tokens": $SELECTED_MAX_TOKENS,
        "temperature": $SELECTED_TEMPERATURE
    },
    "performance_expectations": {
        "first_response_time": "$(if [[ $SELECTED_MODEL == *":1b" ]] || [[ $SELECTED_MODEL == *":2b" ]] || [[ $SELECTED_MODEL == *":3b" ]]; then echo "1-3 seconds"; elif [[ $SELECTED_MODEL == *":7b" ]] || [[ $SELECTED_MODEL == *":8b" ]]; then echo "5-15 seconds"; elif [[ $SELECTED_MODEL == *":13b" ]] || [[ $SELECTED_MODEL == *":14b" ]]; then echo "10-30 seconds"; else echo "30-60 seconds"; fi)",
        "subsequent_response_time": "$(if [[ $SELECTED_MODEL == *":1b" ]] || [[ $SELECTED_MODEL == *":2b" ]] || [[ $SELECTED_MODEL == *":3b" ]]; then echo "1-2 seconds"; elif [[ $SELECTED_MODEL == *":7b" ]] || [[ $SELECTED_MODEL == *":8b" ]]; then echo "2-5 seconds"; elif [[ $SELECTED_MODEL == *":13b" ]] || [[ $SELECTED_MODEL == *":14b" ]]; then echo "5-15 seconds"; else echo "10-30 seconds"; fi)"
    }
}
EOF
print_success "System configuration saved to system_config.json"

# Step 8: Final success message
echo ""
    print_success "Setup Complete!"
echo "================================================"
echo ""
print_status "System Analysis:"
echo "   RAM: ${SYSTEM_RAM_GB}GB"
echo "   CPU: ${SYSTEM_CPU_CORES} cores"
echo "   GPU: ${SYSTEM_GPU_TYPE}"
echo ""
print_status "Selected Model:"
echo "   Model: $SELECTED_MODEL"
echo "   Max Tokens: $SELECTED_MAX_TOKENS"
echo "   Temperature: $SELECTED_TEMPERATURE"
echo ""
print_status "Performance Expectations:"
if [[ $SELECTED_MODEL == *":1b" ]] || [[ $SELECTED_MODEL == *":2b" ]] || [[ $SELECTED_MODEL == *":3b" ]]; then
    echo "   First response: 1-3 seconds"
    echo "   Subsequent: 1-2 seconds"
    echo "   Memory: Stays loaded continuously"
elif [[ $SELECTED_MODEL == *":7b" ]] || [[ $SELECTED_MODEL == *":8b" ]]; then
    echo "   First response: 5-15 seconds"
    echo "   Subsequent: 2-5 seconds"
    echo "   Memory: Stays loaded with good performance"
elif [[ $SELECTED_MODEL == *":13b" ]] || [[ $SELECTED_MODEL == *":14b" ]]; then
    echo "   First response: 10-30 seconds"
    echo "   Subsequent: 5-15 seconds"
    echo "   Memory: May unload after use on lower RAM systems"
else
    echo "   First response: 30-60 seconds"
    echo "   Subsequent: 10-30 seconds"
    echo "   Memory: Will unload after each use"
fi
echo ""
print_status "Next Steps:"
    echo "   1. Start the web UI: python chat_ui.py"
echo "   2. Open http://localhost:7860 in your browser"
echo "   3. Start chatting with your local AI!"
echo ""
print_success "Happy chatting!" 