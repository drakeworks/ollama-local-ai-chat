#!/bin/bash

# Ollama GPT-OSS-20B Model Testing Script
# This script tests if the model is working correctly

echo "🧪 Testing Ollama GPT-OSS-20B Model"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed. Please run the installation script first."
    exit 1
fi

# Check if Ollama service is running
if ! brew services list | grep -q "ollama.*started"; then
    print_warning "Ollama service is not running. Starting it now..."
    brew services start ollama
    sleep 3
fi

# Check if the model is available
print_status "Checking if GPT-OSS-20B model is available..."
if ! ollama list | grep -q "gpt-oss:20b"; then
    print_error "GPT-OSS-20B model is not available."
    echo "   Run 'ollama pull gpt-oss:20b' to download it."
    exit 1
fi
print_success "Model is available"

# Test 1: Simple API test
print_status "Testing API connectivity..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    print_success "API is responding"
else
    print_error "API is not responding. Make sure Ollama is running."
    exit 1
fi

# Test 2: Simple generation test
print_status "Testing model generation..."
echo ""

# Create a temporary test file
cat > /tmp/test_prompt.json << EOF
{
  "model": "gpt-oss:20b",
  "prompt": "Hello! Please respond with a short greeting to confirm you're working.",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "num_predict": 50
  }
}
EOF

# Test the model
response=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d @/tmp/test_prompt.json)

# Check if we got a valid response
if echo "$response" | grep -q '"response"'; then
    print_success "Model generation test passed!"
    echo ""
    echo "📝 Model response:"
    echo "$response" | jq -r '.response' 2>/dev/null || echo "$response" | grep -o '"response":"[^"]*"' | cut -d'"' -f4
    echo ""
else
    print_error "Model generation test failed!"
    echo "Response: $response"
    exit 1
fi

# Clean up
rm -f /tmp/test_prompt.json

# Test 3: Performance test
print_status "Testing model performance..."
echo ""

# Time the response
start_time=$(date +%s.%N)

response=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss:20b",
    "prompt": "Write a one-sentence summary of artificial intelligence.",
    "stream": false,
    "options": {
      "temperature": 0.7,
      "num_predict": 100
    }
  }')

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "unknown")

if echo "$response" | grep -q '"response"'; then
    print_success "Performance test passed!"
    echo "⏱️  Response time: ${duration}s"
    echo ""
    echo "📝 Performance test response:"
    echo "$response" | jq -r '.response' 2>/dev/null || echo "$response" | grep -o '"response":"[^"]*"' | cut -d'"' -f4
    echo ""
else
    print_error "Performance test failed!"
    echo "Response: $response"
fi

# Test 4: System information
print_status "System information:"
echo ""

# Check available models
echo "📋 Available models:"
ollama list

echo ""

# Check Ollama version
echo "🔧 Ollama version:"
ollama --version

echo ""

# Check system resources
echo "💻 System resources:"
echo "Memory: $(sysctl -n hw.memsize 2>/dev/null | awk '{print $0/1024/1024/1024 " GB"}' || echo "Unknown")"
echo "CPU: $(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Unknown")"

echo ""

print_success "✅ All tests completed successfully!"
echo ""
echo "🎉 Your Ollama GPT-OSS-20B setup is working correctly!"
echo ""
echo "You can now:"
echo "  • Use terminal chat: ollama run gpt-oss:20b"
echo "  • Start web UI: ./start_webui.sh"
echo "  • Use API: curl -X POST http://localhost:11434/api/generate" 