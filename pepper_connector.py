"""
Pepper AI Connector - Connects Pepper Robot to Local AI (Ollama)

This script connects to a Pepper robot (real or virtual in Choregraphe)
and makes it speak responses from a local AI model running on Ollama.

IMPORTANT: The NAOqi SDK (for Pepper) only works with Python 2.7!
This script will automatically run in simulation mode if the SDK isn't available.

For full robot functionality, you need to either:
1. Run this script with Python 2.7 (from Choregraphe), OR
2. Use the bridge architecture (pepper_bridge.py)

Author: Aashi
Date: 2025
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ===========================================
# CONFIGURATION - Edit these if needed
# ===========================================

# Ollama settings (the local AI that runs on your computer)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")  # Change to your preferred model

# Pepper robot settings
# Use 127.0.0.1 for virtual robot in Choregraphe
# Use the robot's IP address for real Pepper (e.g., "192.168.1.100")
PEPPER_IP = os.getenv("PEPPER_IP", "127.0.0.1")
PEPPER_PORT = int(os.getenv("PEPPER_PORT", "9559"))

# Bridge mode settings (for connecting via HTTP bridge)
BRIDGE_URL = os.getenv("BRIDGE_URL", "http://localhost:5000")

# ===========================================
# HELPER FUNCTIONS
# ===========================================


def test_ollama_connection():
    """
    Test if Ollama is running and accessible.
    Returns True if connected, False otherwise.
    """
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Ollama is running with {len(models)} model(s) installed:")
                for model in models:
                    print(f"   - {model['name']}")
                return True
            else:
                print("⚠️  Ollama is running but no models are installed!")
                print("   Run: ollama pull llama2")
                return False
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama!")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama: {e}")
        return False


def get_ollama_response(user_message, conversation_history=None):
    """
    Send a message to Ollama and get a response.
    
    Args:
        user_message: The text the user typed
        conversation_history: List of previous messages (optional)
    
    Returns:
        The AI's response as a string, or None if there was an error
    """
    try:
        # Build the prompt with conversation history
        if conversation_history:
            # Include previous messages for context
            full_prompt = ""
            for msg in conversation_history:
                if msg["role"] == "user":
                    full_prompt += f"User: {msg['content']}\n"
                else:
                    full_prompt += f"Assistant: {msg['content']}\n"
            full_prompt += f"User: {user_message}\nAssistant:"
        else:
            full_prompt = f"User: {user_message}\nAssistant:"

        # Send request to Ollama
        response = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 500  # Limit response length for speech
                }
            },
            timeout=120  # AI can take a while to respond
        )

        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            print(f"❌ Ollama error: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        print("❌ Ollama took too long to respond")
        return None
    except Exception as e:
        print(f"❌ Error getting AI response: {e}")
        return None


def check_naoqi_available():
    """
    Check if NAOqi SDK is available and compatible with current Python version.
    Returns (available, message) tuple.
    """
    python_version = sys.version_info
    
    # NAOqi SDK requires Python 2.7
    if python_version.major >= 3:
        return False, (
            f"⚠️  You're running Python {python_version.major}.{python_version.minor}\n"
            f"   The NAOqi SDK requires Python 2.7\n"
            f"   \n"
            f"   Options:\n"
            f"   1. Run in SIMULATION MODE (AI chat without robot speech)\n"
            f"   2. Use Choregraphe's Python 2.7 for robot connection\n"
            f"   3. Use the HTTP bridge (pepper_bridge.py)"
        )
    
    # Try to import qi
    try:
        import qi
        return True, "✅ NAOqi SDK is available"
    except ImportError as e:
        return False, f"❌ NAOqi SDK not found: {e}"
    except SyntaxError as e:
        return False, f"❌ NAOqi SDK syntax error (Python version mismatch): {e}"


def connect_to_pepper():
    """
    Connect to the Pepper robot using the NAOqi SDK.
    Returns the session object if successful, None otherwise.
    """
    # First check if NAOqi is available
    available, message = check_naoqi_available()
    print(message)
    
    if not available:
        return None

    try:
        import qi
        
        # Create a session and connect
        session = qi.Session()
        connection_url = f"tcp://{PEPPER_IP}:{PEPPER_PORT}"
        print(f"📡 Connecting to Pepper at {connection_url}...")
        session.connect(connection_url)
        print("✅ Connected to Pepper!")
        return session
    except RuntimeError as e:
        print(f"❌ Cannot connect to Pepper: {e}")
        print("   Make sure:")
        print("   1. Choregraphe is running with a virtual robot, OR")
        print("   2. You're connected to a real Pepper robot")
        print(f"   3. The IP ({PEPPER_IP}) and port ({PEPPER_PORT}) are correct")
        return None


def check_bridge_available():
    """
    Check if the HTTP bridge to Pepper is running.
    """
    try:
        response = requests.get(f"{BRIDGE_URL}/status", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False


def speak_via_bridge(text):
    """
    Send text to Pepper via the HTTP bridge.
    """
    try:
        response = requests.post(
            f"{BRIDGE_URL}/speak",
            json={"text": text},
            timeout=30
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Bridge error: {e}")
        return False


def make_pepper_speak(session, text):
    """
    Make Pepper speak the given text.
    
    Args:
        session: The NAOqi session connected to Pepper (can be None for bridge mode)
        text: The text Pepper should say
    """
    # Clean the text for better speech
    clean_text = text.replace("*", "").replace("#", "").replace("`", "")
    clean_text = clean_text.replace("\n\n", ". ").replace("\n", ". ")
    
    if session is not None:
        try:
            # Direct NAOqi connection
            tts = session.service("ALTextToSpeech")
            print(f"🔊 Pepper says: {clean_text[:100]}...")
            tts.say(clean_text)
        except Exception as e:
            print(f"❌ Error making Pepper speak: {e}")
    elif check_bridge_available():
        # Try HTTP bridge
        print(f"🔊 Pepper says (via bridge): {clean_text[:100]}...")
        speak_via_bridge(clean_text)
    else:
        # Simulation mode - just print
        print(f"\n🤖 [SIMULATION] Pepper would say:\n{clean_text}\n")


def run_simulation_mode():
    """
    Run in simulation mode (without a real robot).
    Just prints what Pepper would say.
    """
    print("\n" + "="*50)
    print("🤖 SIMULATION MODE (AI Chat Without Robot)")
    print("="*50)
    print("Type messages to chat with the AI.")
    print("Responses will be printed (not spoken by robot).")
    print("Type 'quit' or 'exit' to stop.\n")

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Goodbye!")
            break

        # Get AI response
        print("🤔 Thinking...")
        response = get_ollama_response(user_input, conversation_history)

        if response:
            # Save to history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Print what Pepper would say
            print(f"\n🤖 AI Response:\n{response}\n")
        else:
            print("❌ Failed to get response. Check Ollama is running.\n")


def run_with_robot(session):
    """
    Run with a real or virtual Pepper robot.
    """
    print("\n" + "="*50)
    print("🤖 PEPPER AI ASSISTANT")
    print("="*50)
    print("Type messages to chat with Pepper.")
    print("Pepper will speak the responses!")
    print("Type 'quit' or 'exit' to stop.\n")

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'bye']:
            make_pepper_speak(session, "Goodbye! It was nice talking with you.")
            print("👋 Goodbye!")
            break

        # Get AI response
        print("🤔 Thinking...")
        response = get_ollama_response(user_input, conversation_history)

        if response:
            # Save to history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Make Pepper speak
            make_pepper_speak(session, response)
            print(f"Pepper: {response}\n")
        else:
            error_msg = "I'm sorry, I couldn't process that. Please try again."
            make_pepper_speak(session, error_msg)
            print(f"❌ {error_msg}\n")


def run_with_bridge():
    """
    Run using the HTTP bridge to connect to Pepper.
    """
    print("\n" + "="*50)
    print("🤖 PEPPER AI ASSISTANT (Bridge Mode)")
    print("="*50)
    print("Type messages to chat with Pepper.")
    print("Pepper will speak the responses via bridge!")
    print("Type 'quit' or 'exit' to stop.\n")

    conversation_history = []

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ['quit', 'exit', 'bye']:
            speak_via_bridge("Goodbye! It was nice talking with you.")
            print("👋 Goodbye!")
            break

        # Get AI response
        print("🤔 Thinking...")
        response = get_ollama_response(user_input, conversation_history)

        if response:
            # Save to history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Make Pepper speak via bridge
            speak_via_bridge(response)
            print(f"Pepper: {response}\n")
        else:
            error_msg = "I'm sorry, I couldn't process that. Please try again."
            speak_via_bridge(error_msg)
            print(f"❌ {error_msg}\n")


# ===========================================
# MAIN PROGRAM
# ===========================================

def main():
    """
    Main entry point for the Pepper AI Connector.
    """
    print("\n" + "="*50)
    print("🚀 PEPPER AI CONNECTOR")
    print("="*50)
    print(f"Python version: {sys.version}")
    print("")

    # Step 1: Test Ollama connection
    print("📋 Step 1: Testing Ollama connection...")
    if not test_ollama_connection():
        print("\n❌ Cannot proceed without Ollama.")
        print("   Make sure Ollama is running: ollama serve")
        print("   And that you have a model installed: ollama pull llama2")
        return

    # Step 2: Check connection options
    print(f"\n📋 Step 2: Checking robot connection options...")
    
    # Check Python version
    python_version = sys.version_info
    
    if python_version.major >= 3:
        print(f"\n⚠️  Python {python_version.major}.{python_version.minor} detected")
        print("   The NAOqi SDK requires Python 2.7")
        print("")
        
        # Check if bridge is available
        if check_bridge_available():
            print("✅ HTTP Bridge is running!")
            print("\nOptions:")
            print("  1. Use Bridge Mode (robot speaks via bridge)")
            print("  2. Simulation Mode (AI chat, no robot speech)")
            
            try:
                choice = input("\nChoose mode (1 or 2): ").strip()
                if choice == "1":
                    run_with_bridge()
                else:
                    run_simulation_mode()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
        else:
            print("ℹ️  HTTP Bridge is not running")
            print("")
            print("To connect to Pepper, you have these options:")
            print("")
            print("  OPTION A: Simulation Mode (easiest)")
            print("    - Chat with AI without robot")
            print("    - Good for testing the AI")
            print("")
            print("  OPTION B: Use Choregraphe's Python")
            print("    - Open Choregraphe")
            print("    - Start a virtual robot")
            print("    - Run pepper_bridge.py with Choregraphe's Python")
            print("    - Then run this script again")
            print("")
            print("  OPTION C: Real Pepper Robot")
            print("    - Connect to Pepper's network")
            print("    - Run pepper_bridge.py on a Python 2.7 system")
            print("    - Or run directly on Pepper itself")
            print("")
            
            try:
                choice = input("Press Enter for Simulation Mode, or Ctrl+C to quit: ")
                run_simulation_mode()
            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")
    else:
        # Python 2.7 - try direct connection
        print("✅ Python 2.7 detected - attempting direct connection...")
        session = connect_to_pepper()
        
        if session:
            run_with_robot(session)
        else:
            print("\n⚠️  Running in simulation mode (no robot)")
            run_simulation_mode()


if __name__ == "__main__":
    main()
