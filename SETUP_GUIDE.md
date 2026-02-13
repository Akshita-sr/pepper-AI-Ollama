# Pepper AI Tutor - Complete Setup Guide

This guide will walk you through setting up and running the Pepper AI Tutor project step by step.

---

## Table of Contents

1. [What You Need](#what-you-need)
2. [Understanding the Output](#understanding-the-output)
3. [Fixing the "Socket not connected" Error](#fixing-the-socket-not-connected-error)
4. [Step-by-Step Running Guide](#step-by-step-running-guide)
5. [Creating Your GitHub Repository](#creating-your-github-repository)
6. [Quick Reference](#quick-reference)

---

## What You Need

Based on your system, you have:

| Component | Status | Path/Version |
|-----------|--------|--------------|
| Python 3 | ✅ Installed | 3.13.4 |
| Python 2.7 | ✅ Installed | `C:\Python27\python.exe` |
| Ollama | ✅ Running | 10 models installed |
| Choregraphe | ✅ Installed | `C:\Program Files (x86)\Aldebaran\Choregraphe Suite 2.5` |
| Virtual Robot | ⚠️ Not Running | Needs to be started in Choregraphe |

---

## Understanding the Output

Let's analyze what happened in your test:

### ✅ What Worked

1. **Ollama is running perfectly** - All 10 models detected
2. **Bridge connected to Pepper** - "Connected to Pepper!" message appeared
3. **AI is generating responses** - You got answers about planets!
4. **Bridge received the requests** - HTTP logs show POST /speak requests

### ❌ What Didn't Work

The error "Socket is not connected" means the virtual robot in Choregraphe wasn't actively running. Let me explain:

When you look at your Choregraphe screenshot:
- It says **"Not running"** at the top (next to the stop button)
- There's a warning: **"the motors are not updated, the robot will not move"**

This means the virtual robot is connected but not "alive" - it's like a robot that's plugged in but turned off!

---

## Fixing the "Socket not connected" Error

### Step 1: Start the Virtual Robot Properly

1. **Open Choregraphe** (you already have it open)

2. **Connect to virtual robot** (you've done this - it shows "Connected to a virtual robot")

3. **IMPORTANT: Click the GREEN PLAY BUTTON (▶)** at the top toolbar
   - This "wakes up" the robot
   - The status should change from "Not running" to "Running"
   - The warning about motors should disappear

4. **Alternative: Double-click "Life" in Robot applications**
   - Look at the right panel called "Robot applications"
   - Double-click on "Life" to start the autonomous life behavior
   - This makes the robot "alive" and able to speak

### Step 2: Test That It's Working

In Choregraphe:
1. Go to **Box libraries** → **Speech** (or search for "Say")
2. Drag a "Say" box onto the main canvas
3. Double-click it and type some text
4. Click the green Play button
5. You should hear the robot speak!

If you hear it speak, the robot is ready for our project.

---

## Step-by-Step Running Guide

### Preparation

1. **Close everything first** (all terminals, Choregraphe)
2. **Open Choregraphe**
3. **Connect to virtual robot**: Connection → Connect to virtual robot → Connect
4. **Start the robot**: Click the **▶ Play button** at the top
5. Wait until you see "Running" (not "Not running")

### Terminal 1: Start Ollama

```cmd
ollama serve
```

Leave this running. You should see:
```
Listening on 127.0.0.1:11434
```

### Terminal 2: Start the Bridge

**Important**: Use Python 2.7, NOT your virtual environment!

```cmd
cd C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama
"C:\Python27\python.exe" pepper_bridge.py
```

You should see:
```
==================================================
PEPPER BRIDGE - Python 2.7 HTTP Server
==================================================
Python version: 2.7.18 ...

Connecting to Pepper at 127.0.0.1:9559...
Connected to Pepper!

==================================================
Pepper Bridge HTTP Server
==================================================
Listening on http://127.0.0.1:5000
```

### Terminal 3: Start the Connector

```cmd
cd C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama
venv\Scripts\activate
python pepper_connector.py
```

When prompted, choose **1** for Bridge Mode:
```
Choose mode (1 or 2): 1
```

### Terminal 4 (Optional): Start Web Interface

```cmd
cd C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama
venv\Scripts\activate
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

---

## Creating Your GitHub Repository

### Step 1: Create Repository on GitHub

1. Go to https://github.com
2. Click the **+** icon → **New repository**
3. Fill in:
   - **Repository name**: `pepper-ai-tutor`
   - **Description**: "AI-powered tutoring system for Pepper robot using local LLMs"
   - **Public** or **Private**: Your choice
   - ✅ Check "Add a README file"
4. Click **Create repository**

### Step 2: Clone to Your Computer

Open a new terminal:

```cmd
cd C:\Users\akshi\OneDrive\Desktop
git clone https://github.com/YOUR-USERNAME/pepper-ai-tutor.git
cd pepper-ai-tutor
```

### Step 3: Copy Your Project Files

Copy these files from `pepper-AI-Ollama` to `pepper-ai-tutor`:
- `app.py`
- `pepper_connector.py`
- `pepper_bridge.py`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `README.md`

Or use command line:
```cmd
copy C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama\*.py .
copy C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama\requirements.txt .
copy C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama\.env.example .
copy C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama\.gitignore .
copy C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama\README.md .
```

### Step 4: Push to GitHub

```cmd
git add .
git commit -m "Initial commit: Pepper AI Tutor with local LLM support"
git push origin main
```

If asked for credentials:
1. Enter your GitHub username
2. For password, use a **Personal Access Token** (not your actual password):
   - Go to GitHub → Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
   - Generate New Token
   - Select scopes: `repo` (full control)
   - Copy the token and use it as password

---

## Quick Reference

### Commands Cheat Sheet

| Task | Command |
|------|---------|
| Start Ollama | `ollama serve` |
| Start Bridge | `"C:\Python27\python.exe" pepper_bridge.py` |
| Start Connector | `venv\Scripts\activate` then `python pepper_connector.py` |
| Start Web UI | `venv\Scripts\activate` then `streamlit run app.py` |
| List AI models | `ollama list` |
| Download new model | `ollama pull <model-name>` |

### File Locations on Your System

| File | Location |
|------|----------|
| Project folder | `C:\Users\akshi\OneDrive\Desktop\pepper-AI-Ollama` |
| Python 2.7 | `C:\Python27\python.exe` |
| Choregraphe | `C:\Program Files (x86)\Aldebaran\Choregraphe Suite 2.5` |
| Virtual env | `pepper-AI-Ollama\venv` |

### Ports Used

| Service | Port |
|---------|------|
| Ollama API | 11434 |
| Pepper Bridge | 5000 |
| Streamlit Web UI | 8501 |
| Pepper/NAOqi | 9559 |

---

## Next Steps

Once everything is working:

1. **Try different AI models**: `ollama pull mistral` or `ollama pull phi3:mini`
2. **Change the model**: Edit `.env` file and set `OLLAMA_MODEL=mistral`
3. **Upload documents**: Use the web interface to upload PDFs and ask questions
4. **Connect real Pepper**: Change `PEPPER_IP` in `.env` to your robot's IP address

---

## Need Help?

If something isn't working:

1. Check that all terminals are running (don't close them!)
2. Make sure Choregraphe shows "Running" (not "Not running")
3. Look at the error messages in each terminal
4. The Bridge terminal shows HTTP requests - check if they're coming through

Good luck with your project! 🤖
