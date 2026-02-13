# 🤖 Pepper AI Tutor

A modern AI-powered tutoring system for the SoftBank Pepper robot. This project combines a web-based chat interface with local AI models (via Ollama) and Pepper robot integration.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)
![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)
![Pepper](https://img.shields.io/badge/Pepper-NAOqi-orange.svg)

## ✨ Features

### 💬 Web Chat Interface
- Modern web-based chat UI (like ChatGPT)
- Conversation history saved to database
- Multiple users supported with secure login
- Built with Streamlit

### 🤖 Local AI (No Cloud Required!)
- Runs AI models **locally** on your computer
- Uses [Ollama](https://ollama.ai) for model management
- Supports many models: LLaMA, Mistral, DeepSeek, Phi, etc.
- **Free** - no API keys or subscriptions needed

### 📄 Document Analysis (RAG)
- Upload PDF, TXT, or CSV files
- Ask questions about your documents
- AI answers based on document content

### 🗣️ Pepper Robot Integration
- Connects to real Pepper robot OR virtual robot (Choregraphe)
- AI responses spoken aloud by Pepper
- Uses "split-brain" architecture (Python 3 for AI + Python 2.7 for robot)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR COMPUTER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Terminal 1          Terminal 2          Terminal 3             │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐            │
│  │  OLLAMA  │       │  BRIDGE  │       │CONNECTOR │            │
│  │  serve   │       │ (Py 2.7) │       │ (Py 3.x) │            │
│  └────┬─────┘       └────┬─────┘       └────┬─────┘            │
│       │                  │                  │                   │
│       │    HTTP :11434   │    HTTP :5000    │                   │
│       └──────────────────┼──────────────────┘                   │
│                          │                                      │
│                          ▼                                      │
│                    ┌──────────┐                                 │
│                    │ PEPPER   │                                 │
│                    │ (Virtual │                                 │
│                    │ or Real) │                                 │
│                    └──────────┘                                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** - [Download](https://python.org)
2. **Python 2.7** - [Download](https://www.python.org/downloads/release/python-2718/) (for Pepper connection)
3. **Ollama** - [Download](https://ollama.ai)
4. **Choregraphe** (optional) - For virtual Pepper robot

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/pepper-ai-tutor.git
cd pepper-ai-tutor

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download an AI model
ollama pull llama2
```

### Running the Project

You need **3 terminals** running simultaneously:

#### Terminal 1: Start Ollama
```bash
ollama serve
```

#### Terminal 2: Start the Bridge (Python 2.7)
```bash
# Use Python 2.7 (NOT the virtual environment)
"C:\Python27\python.exe" pepper_bridge.py
```

#### Terminal 3: Start the Connector
```bash
# Activate virtual environment first
venv\Scripts\activate
python pepper_connector.py
```

Then choose option `1` for Bridge Mode when prompted.

### Using the Web Interface

In a **4th terminal** (optional):
```bash
venv\Scripts\activate
streamlit run app.py
```

Then open: http://localhost:8501

## 📁 Project Structure

```
pepper-ai-tutor/
├── app.py                 # Web interface (Streamlit)
├── pepper_connector.py    # Main connector (Python 3)
├── pepper_bridge.py       # Robot bridge (Python 2.7)
├── requirements.txt       # Python 3 dependencies
├── .env.example          # Configuration template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and edit:

```env
# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Pepper robot settings (127.0.0.1 for virtual robot)
PEPPER_IP=127.0.0.1
PEPPER_PORT=9559

# Bridge settings
BRIDGE_URL=http://localhost:5000
```

## 🔧 Troubleshooting

### "Socket is not connected" error

This means the virtual robot in Choregraphe isn't fully active:

1. Open Choregraphe
2. Go to **Connection** → **Connect to virtual robot** → **Connect**
3. Click the **green Play button** (▶) at the top to start the robot
4. Make sure it says "Running" (not "Not running")
5. Then restart `pepper_bridge.py`

### Ollama error 500

The AI model might be loading. Wait a few seconds and try again. First request after startup takes longer.

### Bridge not detected

Make sure `pepper_bridge.py` is running with Python 2.7:
```bash
"C:\Python27\python.exe" pepper_bridge.py
```

### Virtual robot not responding

In Choregraphe:
1. Click **Connection** → **Connect to virtual robot**
2. Select a robot type and click **Connect**
3. The Robot View panel should show the robot moving/responding

## 🤖 Available AI Models

Run `ollama list` to see installed models. Popular options:

| Model | Size | Best For |
|-------|------|----------|
| `llama2` | 3.8 GB | General purpose |
| `llama3:8b` | 4.7 GB | Better quality |
| `mistral` | 4.1 GB | Fast and efficient |
| `phi3:mini` | 2.2 GB | Lightweight |
| `deepseek-r1` | 5.2 GB | Reasoning tasks |

Install new models: `ollama pull <model-name>`

## 📚 How It Works

### The "Split-Brain" Architecture

Pepper robots use an old SDK (NAOqi) that only works with Python 2.7. Modern AI libraries need Python 3. We solve this with a **bridge**:

1. **pepper_bridge.py** (Python 2.7)
   - Connects directly to Pepper using NAOqi
   - Runs an HTTP server on port 5000
   - Receives text via HTTP and makes Pepper speak

2. **pepper_connector.py** (Python 3)
   - Connects to Ollama for AI responses
   - Sends text to the bridge via HTTP
   - Handles conversation flow

### Why Local AI?

- **Free**: No API costs or subscriptions
- **Private**: Your data stays on your computer
- **Fast**: No network latency to cloud servers
- **Secure**: No API keys to expose

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local AI model hosting
- [Streamlit](https://streamlit.io) - Web framework
- [LangChain](https://langchain.com) - LLM framework
- [SoftBank Robotics](https://www.softbankrobotics.com) - Pepper robot

---

Made with ❤️ by Aashi

⭐ Star this repo if you find it helpful!
