# Pepper AI Tutor - Complete Beginner's Guide

## Table of Contents
1. [Understanding the Two Projects](#understanding-the-two-projects)
2. [Which Files to Keep](#which-files-to-keep)
3. [How the Combined System Works](#how-the-combined-system-works)
4. [Setting Up Your Computer](#setting-up-your-computer)
5. [Running the Project](#running-the-project)
6. [Testing with Choregraphe](#testing-with-choregraphe)
7. [Creating Your GitHub Repository](#creating-your-github-repository)
8. [Troubleshooting](#troubleshooting)

---

## 1. Understanding the Two Projects

You have uploaded files from **TWO different projects**. Let me explain each one:

### Project 1: OpenLLM WebUI (The "Brain")

**What it does:** This is a web application that lets you chat with AI models running on your computer. Think of it as your own personal ChatGPT that runs locally!

**Main files:**
- `app.py` - The simpler version (607 lines)
- `hello.py` - The enhanced version with more features (1466 lines)

**Key features:**
- User login system (so multiple people can use it)
- Chat interface (like texting with AI)
- Document analysis (upload PDFs and ask questions about them)
- Works with Ollama (a tool that runs AI models on your computer)

### Project 2: Pepper Connection (The "Body")

**What it does:** This small script connects to the Pepper robot and makes it speak responses from an AI.

**Main file:**
- `pepper_to_api.py` - Connects Pepper to OpenAI's API

**How it works:**
1. You type a message
2. The message goes to OpenAI (ChatGPT)
3. ChatGPT sends back a response
4. Pepper speaks the response out loud

### The Problem with the Current Setup

The `pepper_to_api.py` file has some issues:
1. ⚠️ **SECURITY RISK**: It has an API key visible in the code (this is dangerous!)
2. It uses OpenAI which costs money
3. It doesn't save conversation history

### The Goal: Combine Them!

We want to create a system where:
1. The **OpenLLM WebUI** handles the AI conversations (using free local models)
2. **Pepper** speaks the responses
3. Everything is saved and secure

---

## 2. Which Files to Keep

Here's a breakdown of all your files:

### ✅ KEEP (Essential)

| File | Why Keep It |
|------|-------------|
| `app.py` | The main web application |
| `requirements.txt` | Lists all needed Python packages |
| `readme_file.md` | Documentation (we'll update it) |

### ⚠️ MODIFY (Needs Changes)

| File | What to Change |
|------|----------------|
| `pepper_to_api.py` | Remove API key, connect to local Ollama instead |

### ❌ DELETE (Not Needed)

| File | Why Delete |
|------|------------|
| `hello.py` | Same as app.py but more complex (choose one) |
| `deepseek_api.py` | Separate experiment, not needed |
| `deepseek_chat.py` | Separate experiment, not needed |
| `deepseek_hf.py` | Separate experiment, not needed |
| `deepseek_nn.py` | Incomplete training code |
| `cuda.py` | Just a GPU test, not needed |
| `openllm_webui.db` | Database file (auto-created when you run) |
| `openllm_webui.log` | Log file (auto-created when you run) |
| `chat_history.json` | DeepSeek experiment history |
| `README.md` | Incomplete notes |
| `README_md_-_Complete_Project_Documentation.pdf` | Same as readme_file.md |

---

## 3. How the Combined System Works

Here's a simple diagram of how everything connects:

```
┌─────────────────────────────────────────────────────────────────┐
│                        YOUR COMPUTER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐   │
│   │              │     │              │     │              │   │
│   │   OLLAMA     │────▶│   OPENLLM    │────▶│   PEPPER     │   │
│   │   (AI Brain) │     │   WEBUI      │     │   CONNECTOR  │   │
│   │              │◀────│   (Web App)  │◀────│              │   │
│   └──────────────┘     └──────────────┘     └──────────────┘   │
│         │                    │                     │            │
│         │                    │                     │            │
│   Runs AI models      Web interface         Sends text to      │
│   like DeepSeek,      where you chat        Pepper robot       │
│   Llama, Mistral      and upload docs                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                                │
                                │ WiFi/Network
                                ▼
                    ┌──────────────────────┐
                    │                      │
                    │    PEPPER ROBOT      │
                    │    (or Choregraphe   │
                    │     Virtual Robot)   │
                    │                      │
                    └──────────────────────┘
```

**Step-by-step flow:**
1. You open the web interface in your browser
2. You type a message or upload a document
3. The web app sends your message to Ollama
4. Ollama (running a model like DeepSeek) generates a response
5. The response appears in the web interface
6. The Pepper connector sends the response to the robot
7. Pepper speaks the response!

---

## 4. Setting Up Your Computer

### Step 1: Install Python

**Check if Python is installed:**
Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:

```bash
python --version
```

You should see something like `Python 3.11.5`. If not, download Python from https://python.org

### Step 2: Install Ollama

Ollama is what runs AI models on your computer.

**On Windows:**
1. Go to https://ollama.ai
2. Download and install the Windows version
3. After installation, open Command Prompt and verify:
```bash
ollama --version
```

**On Mac:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**On Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 3: Download an AI Model

After installing Ollama, download a model. I recommend starting with a smaller one:

```bash
ollama pull llama2
```

Or if you have a good computer (16GB+ RAM):
```bash
ollama pull deepseek-r1:7b
```

### Step 4: Create a Project Folder

**On Windows (Command Prompt):**
```bash
mkdir C:\Projects\PepperAI
cd C:\Projects\PepperAI
```

**On Mac/Linux (Terminal):**
```bash
mkdir ~/Projects/PepperAI
cd ~/Projects/PepperAI
```

### Step 5: Create a Virtual Environment

A virtual environment keeps your project's packages separate from other projects.

```bash
python -m venv venv
```

**Activate it:**

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your command line.

### Step 6: Install Required Packages

Create a file called `requirements.txt` with this content:
```
streamlit
python-dotenv
langchain-openai
langchain-community
langchain-core==0.3.52
langchain
pdfplumber
bcrypt
requests
python-multipart
ollama
faiss-cpu
pandas
langchain-ollama
pypdf
```

Then install everything:
```bash
pip install -r requirements.txt
```

---

## 5. Running the Project

### Terminal 1: Start Ollama

Open a terminal and run:
```bash
ollama serve
```

**Leave this terminal open!** You should see something like:
```
Couldn't find '/Users/you/.ollama/id_ed25519'. Generating new private key...
time=2024-XX-XX level=INFO source=...
```

### Terminal 2: Start the Web App

Open a **NEW** terminal (keep the first one running), navigate to your project:

**Windows:**
```bash
cd C:\Projects\PepperAI
venv\Scripts\activate
streamlit run app.py
```

**Mac/Linux:**
```bash
cd ~/Projects/PepperAI
source venv/bin/activate
streamlit run app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 3: Open in Browser

Open your web browser and go to: `http://localhost:8501`

You should see the OpenLLM WebUI!

**First time setup:**
1. Click "Register" tab
2. Create a username and password
3. Click "Login" tab
4. Enter your credentials
5. Start chatting!

---

## 6. Testing with Choregraphe

### What is Choregraphe?

Choregraphe is software that lets you:
- Control a virtual Pepper robot (no real robot needed!)
- Write and test programs for Pepper
- Connect to a real Pepper robot when you have one

### Setting Up the Virtual Robot

1. Open Choregraphe
2. Go to **Connection** → **Connect to virtual robot**
3. Select a robot (e.g., "Pepper" or "NAO")
4. Click **Start**

The virtual robot runs on port `9559` by default.

### Testing the Pepper Connection

I've created a new, safe version of `pepper_to_api.py` that connects to your local Ollama instead of OpenAI. Here's how to test it:

**Terminal 3: Run Pepper Connector**

Open another terminal:
```bash
cd C:\Projects\PepperAI
venv\Scripts\activate
python pepper_connector.py
```

You should see:
```
Testing Ollama connection...
Ollama is working! Connected to model: llama2
Testing Pepper connection...
Connected to Pepper robot!
You: 
```

Now type a message and press Enter. The virtual robot should speak!

---

## 7. Creating Your GitHub Repository

### Step 1: Create a GitHub Account (if you don't have one)

Go to https://github.com and sign up.

### Step 2: Install Git

**Check if Git is installed:**
```bash
git --version
```

If not installed:
- **Windows:** Download from https://git-scm.com/download/win
- **Mac:** Install Xcode Command Line Tools: `xcode-select --install`
- **Linux:** `sudo apt install git`

### Step 3: Configure Git

Open terminal and run (use your GitHub email and name):
```bash
git config --global user.name "Your Name"
git config --global user.email "your-email@example.com"
```

### Step 4: Create Repository on GitHub

1. Go to https://github.com
2. Click the **+** icon → **New repository**
3. Name it: `pepper-ai-tutor`
4. Select: **Public** (or Private if you prefer)
5. Check: **Add a README file**
6. Click: **Create repository**

### Step 5: Clone the Repository

```bash
cd C:\Projects  # or ~/Projects on Mac/Linux
git clone https://github.com/YOUR-USERNAME/pepper-ai-tutor.git
cd pepper-ai-tutor
```

### Step 6: Copy Your Files

Copy the project files into this folder:
- `app.py`
- `pepper_connector.py`
- `requirements.txt`
- `README.md`
- `.env.example`
- `.gitignore`

### Step 7: Create .gitignore File

This tells Git which files NOT to upload (like passwords!):

Create a file called `.gitignore`:
```
# Virtual environment
venv/
env/

# Environment variables (secrets!)
.env

# Database and logs
*.db
*.log

# Python cache
__pycache__/
*.pyc

# Temporary files
temp_*

# IDE files
.vscode/
.idea/
```

### Step 8: Upload to GitHub

```bash
git add .
git commit -m "Initial commit: Pepper AI Tutor project"
git push origin main
```

If it asks for authentication:
1. Go to GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate a new token (classic)
3. Use that token as your password

---

## 8. Troubleshooting

### Problem: "Can't connect to Ollama"

**Solution:**
1. Make sure Ollama is running: `ollama serve`
2. Check if a model is installed: `ollama list`
3. If no models, install one: `ollama pull llama2`

### Problem: "No models installed"

**Solution:**
```bash
ollama pull llama2
```
Wait for the download to complete.

### Problem: "Can't connect to virtual robot"

**Solution:**
1. Open Choregraphe
2. Make sure the virtual robot is started
3. Check the port (default is 9559)
4. The IP should be `127.0.0.1` (localhost)

### Problem: "ModuleNotFoundError"

**Solution:**
Make sure your virtual environment is activated:
- Windows: `venv\Scripts\activate`
- Mac/Linux: `source venv/bin/activate`

Then reinstall packages:
```bash
pip install -r requirements.txt
```

### Problem: "Permission denied" on GitHub push

**Solution:**
Use a Personal Access Token instead of password:
1. GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate new token (classic)
3. Select permissions: `repo` (full control)
4. Copy the token
5. Use it as your password when Git asks

---

## Quick Reference: Terminal Commands

| What You Want | Command |
|---------------|---------|
| Start Ollama | `ollama serve` |
| List models | `ollama list` |
| Download a model | `ollama pull llama2` |
| Start web app | `streamlit run app.py` |
| Activate virtual env (Windows) | `venv\Scripts\activate` |
| Activate virtual env (Mac/Linux) | `source venv/bin/activate` |
| Install packages | `pip install -r requirements.txt` |
| Push to GitHub | `git add . && git commit -m "message" && git push` |

---

## Next Steps

Once everything is working:

1. **Customize the AI**: Try different models (mistral, codellama, etc.)
2. **Upload Documents**: Test the RAG feature with PDFs
3. **Connect Real Pepper**: When you have access to the real robot, just change the IP address
4. **Add Features**: Voice input, better UI, etc.

Good luck with your project, Aashi! 🤖
