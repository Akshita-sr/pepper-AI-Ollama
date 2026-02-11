# 🤖 Pepper AI Tutor

A modern AI-powered tutoring system for the SoftBank Pepper robot. This project combines a web-based chat interface with local AI models and Pepper robot integration.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)
![Ollama](https://img.shields.io/badge/Ollama-Compatible-green.svg)
![Pepper](https://img.shields.io/badge/Pepper-NAOqi-orange.svg)

## ✨ Features

### 💬 Chat Interface
- Modern web-based chat UI (like ChatGPT)
- Conversation history saved to database
- Multiple users supported with secure login

### 🤖 Local AI
- Runs AI models **locally** on your computer (no cloud needed!)
- Uses Ollama for model management
- Supports many models: LLaMA, Mistral, DeepSeek, etc.

### 📄 Document Analysis (RAG)
- Upload PDF, TXT, or CSV files
- Ask questions about your documents
- AI answers based on document content

### 🗣️ Pepper Integration
- Connects to real Pepper robot OR virtual robot (Choregraphe)
- AI responses spoken aloud by Pepper
- Simple Python connector script

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** - [Download](https://python.org)
2. **Ollama** - [Download](https://ollama.ai)
3. **Git** - [Download](https://git-scm.com)
4. **Choregraphe** (optional) - For virtual Pepper robot

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/pepper-ai-tutor.git
cd pepper-ai-tutor

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download an AI model
ollama pull llama2
```

### Running the Project

**Terminal 1: Start Ollama**
```bash
ollama serve
```

**Terminal 2: Start Web App**
```bash
streamlit run app.py
```

**Terminal 3: Start Pepper Connector** (optional)
```bash
python pepper_connector.py
```

Then open your browser to: http://localhost:8501

## 📁 Project Structure

```
pepper-ai-tutor/
├── app.py                 # Main web application
├── pepper_connector.py    # Pepper robot connection script
├── requirements.txt       # Python dependencies
├── .env.example          # Example configuration file
├── .gitignore            # Files to ignore in Git
└── README.md             # This file
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and edit the values:

```env
# Ollama settings
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama2

# Pepper robot settings
PEPPER_IP=127.0.0.1      # Use robot's IP for real Pepper
PEPPER_PORT=9559
```

## 🔧 Usage

### Web Interface

1. **Register**: Create an account (first time only)
2. **Login**: Enter your credentials
3. **Chat**: Type messages and get AI responses
4. **Documents**: Upload PDFs and ask questions about them

### Pepper Connection

With Choregraphe (virtual robot):
1. Open Choregraphe
2. Connect to virtual robot
3. Run `python pepper_connector.py`

With real Pepper:
1. Find Pepper's IP address
2. Update `PEPPER_IP` in `.env`
3. Run `python pepper_connector.py`

## 🛠️ Troubleshooting

### "Can't connect to Ollama"
- Make sure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`

### "No models installed"
```bash
ollama pull llama2
```

### "Can't connect to Pepper"
- Start virtual robot in Choregraphe, OR
- Check Pepper's IP address is correct
- Verify port 9559 is accessible

## 📚 Documentation

- [Ollama Documentation](https://ollama.ai/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [NAOqi Documentation](http://doc.aldebaran.com/2-5/index_dev_guide.html)
- [LangChain Documentation](https://python.langchain.com)

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m "Add amazing feature"`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local AI model hosting
- [Streamlit](https://streamlit.io) - Web framework
- [LangChain](https://langchain.com) - LLM framework
- [SoftBank Robotics](https://www.softbankrobotics.com) - Pepper robot

---

Made with ❤️ by Aashi

⭐ Star this repo if you find it helpful!
