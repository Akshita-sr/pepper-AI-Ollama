# app.py - OpenLLM-WebUI Complete Version (Fixed)
# Pepper AI Tutor - Web Interface
# Author: Aashi
# Date: 2025

import streamlit as st
import sqlite3
import requests
import hashlib
import os
import json
import base64
import threading
import time
from dotenv import load_dotenv
from datetime import datetime

# LangChain imports - using updated packages to avoid deprecation warnings
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama, OllamaEmbeddings  # Updated imports
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import (
    PDFPlumberLoader,
    TextLoader,
    CSVLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_core.prompts import ChatPromptTemplate
import bcrypt

# Load environment variables
load_dotenv()

# --------------------------
# Database Initialization
# --------------------------


def init_db():
    """Initialize SQLite database for users, conversations, and models"""
    conn = sqlite3.connect('openllm_webui.db')
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password_hash TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Conversations table
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  title TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))''')

    # Messages table
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  conversation_id INTEGER,
                  content TEXT,
                  role TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(conversation_id) REFERENCES conversations(id))''')

    # Feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  message_id INTEGER,
                  rating INTEGER,
                  comment TEXT,
                  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(message_id) REFERENCES messages(id))''')

    conn.commit()
    conn.close()


init_db()  # Initialize database on startup

# --------------------------
# Authentication Functions
# --------------------------


def create_user(username, password):
    """Create new user with hashed password"""
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    conn = sqlite3.connect('openllm_webui.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username exists
    finally:
        conn.close()


def verify_user(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect('openllm_webui.db')
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()

    if result and bcrypt.checkpw(password.encode(), result[1]):
        return result[0]  # Return user ID
    return None


# --------------------------
# Ollama Model Management
# --------------------------
OLLAMA_API_URL = "http://localhost:11434/api"


def get_installed_models():
    """Fetch list of installed models from Ollama API"""
    try:
        response = requests.get(f"{OLLAMA_API_URL}/tags")
        if response.status_code == 200:
            return [model['name'] for model in response.json()['models']]
        else:
            return []
    except requests.exceptions.ConnectionError:
        return []


def download_model(model_name):
    """Download model with progress tracking"""
    def download_thread():
        try:
            response = requests.post(
                f"{OLLAMA_API_URL}/pull",
                json={'name': model_name},
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    status = json.loads(line)
                    if 'completed' in status and 'total' in status:
                        progress = status['completed'] / status['total']
                        st.session_state.download_progress[model_name] = progress
                    elif 'error' in status:
                        st.error(f"Download error: {status['error']}")
        except Exception as e:
            st.error(f"Download failed: {str(e)}")

    threading.Thread(target=download_thread).start()


def delete_model(model_name):
    """Delete model via Ollama API"""
    try:
        response = requests.delete(
            f"{OLLAMA_API_URL}/delete", json={'name': model_name})
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


# --------------------------
# UI Configuration & Styles
# --------------------------
st.set_page_config(page_title="OpenLLM WebUI", layout="wide")

custom_css = """
<style>
    :root {
        --primary: #2563eb;
        --background: #0f172a;
        --surface: #1e293b;
    }

    .stApp {
        background-color: var(--background);
        color: white;
    }

    .stTextInput input, .stTextArea textarea {
        background-color: var(--surface) !important;
        color: white !important;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: var(--surface) !important;
    }

    .stProgress > div > div > div {
        background-color: var(--primary) !important;
    }

    .model-card {
        background: var(--surface);
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --------------------------
# Session State Management
# --------------------------


def init_session_state():
    """Initialize all session state variables"""
    # Get available models
    available_models = get_installed_models()
    default_model = available_models[0] if available_models else "llama2"

    defaults = {
        "authenticated": False,
        "current_user": None,
        "current_conversation": None,
        "model_settings": {
            "temperature": 0.3,
            "max_tokens": 1000,
            "selected_model": default_model
        },
        "document_store": None,
        "download_progress": {},
        "active_tab": "chat"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Initialize document store with proper embedding model
    if st.session_state.document_store is None and available_models:
        try:
            embedding_model = available_models[0]  # Use first available model
            st.session_state.document_store = InMemoryVectorStore(
                OllamaEmbeddings(model=embedding_model)
            )
        except Exception as e:
            st.warning(f"Could not initialize document store: {e}")


init_session_state()

# --------------------------
# Document Processing
# --------------------------


def process_uploaded_file(file):
    """Process uploaded file based on type"""
    if st.session_state.document_store is None:
        st.error("Document store not initialized. Please check Ollama connection.")
        return False

    file_type = file.type.split('/')[-1]
    temp_path = f"temp_{file.name}"

    with open(temp_path, "wb") as f:
        f.write(file.getbuffer())

    try:
        if file_type == "pdf":
            loader = PDFPlumberLoader(temp_path)
        elif file_type == "csv":
            loader = CSVLoader(temp_path)
        elif file_type == "plain":
            loader = TextLoader(temp_path)
        else:
            raise ValueError("Unsupported file type")

        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        st.session_state.document_store.add_documents(chunks)
        return True
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return False
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# --------------------------
# Chat & Conversation Handling
# --------------------------


def save_message(content, role):
    """Save message to current conversation"""
    if st.session_state.current_conversation is None:
        return

    conn = sqlite3.connect('openllm_webui.db')
    c = conn.cursor()
    c.execute("INSERT INTO messages (conversation_id, content, role) VALUES (?, ?, ?)",
              (st.session_state.current_conversation, content, role))
    conn.commit()
    conn.close()


def load_conversation_history(conversation_id):
    """Load messages for a specific conversation"""
    conn = sqlite3.connect('openllm_webui.db')
    c = conn.cursor()
    c.execute("SELECT content, role FROM messages WHERE conversation_id = ? ORDER BY timestamp",
              (conversation_id,))
    messages = [{"content": row[0], "role": row[1]} for row in c.fetchall()]
    conn.close()
    return messages


def new_conversation():
    """Create new conversation entry"""
    if st.session_state.current_user is None:
        return

    conn = sqlite3.connect('openllm_webui.db')
    c = conn.cursor()
    c.execute("INSERT INTO conversations (user_id, title) VALUES (?, ?)",
              (st.session_state.current_user, f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"))
    st.session_state.current_conversation = c.lastrowid
    conn.commit()
    conn.close()


def save_feedback(query, answer, rating):
    """Save user feedback"""
    # This would need to be implemented to save feedback to database
    pass

# --------------------------
# Main Application Components
# --------------------------


def authentication_section():
    """Handle user authentication and registration"""
    if not st.session_state.authenticated:
        auth_tab, reg_tab = st.tabs(["Login", "Register"])

        with auth_tab:
            with st.form("Login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    user_id = verify_user(username, password)
                    if user_id:
                        st.session_state.authenticated = True
                        st.session_state.current_user = user_id
                        new_conversation()
                        st.rerun()
                    else:
                        st.error("Invalid credentials")

        with reg_tab:
            with st.form("Register"):
                new_user = st.text_input("New Username")
                new_pass = st.text_input("New Password", type="password")
                if st.form_submit_button("Create Account"):
                    if create_user(new_user, new_pass):
                        st.success("Account created! Please login")
                    else:
                        st.error("Username already exists")


def model_management_sidebar():
    """Model management interface in sidebar"""
    with st.sidebar:
        st.header("⚙️ Model Management")

        # Model selection and settings
        available_models = get_installed_models()
        if available_models:
            current_model = st.session_state.model_settings.get(
                "selected_model", available_models[0])
            if current_model not in available_models:
                current_model = available_models[0]

            st.session_state.model_settings["selected_model"] = st.selectbox(
                "Select Model",
                available_models,
                index=available_models.index(
                    current_model) if current_model in available_models else 0
            )
        else:
            st.warning("No models installed. Please install a model first.")
            st.session_state.model_settings["selected_model"] = st.text_input(
                "Model Name", value="llama2"
            )

        st.session_state.model_settings["temperature"] = st.slider(
            "Temperature", 0.0, 1.0, 0.3
        )
        st.session_state.model_settings["max_tokens"] = st.slider(
            "Max Tokens", 100, 2000, 1000
        )

        # Model download section
        st.divider()
        st.subheader("Model Repository")
        new_model = st.text_input("Download Model (name:version)")
        if st.button("Download Model"):
            if new_model:
                download_model(new_model)
                st.info(f"Started downloading {new_model}")

        # Download progress display
        for model, progress in st.session_state.download_progress.items():
            st.progress(progress, text=f"Downloading {model}")

        # Installed models list
        if available_models:
            st.subheader("Installed Models")
            for model in available_models:
                with st.expander(model):
                    if st.button(f"Delete {model}", key=f"del_{model}"):
                        if delete_model(model):
                            st.success(f"Deleted {model}")
                            st.rerun()
                        else:
                            st.error("Delete failed")


def chat_interface():
    """Main chat interface with multimodal support"""
    st.header("Chat Interface")

    if not st.session_state.authenticated:
        st.warning("Please login to use the chat interface")
        return

    # Conversation history selector
    conn = sqlite3.connect('openllm_webui.db')
    conversations = conn.execute(
        "SELECT id, title FROM conversations WHERE user_id = ? ORDER BY created_at DESC",
        (st.session_state.current_user,)
    ).fetchall()
    conn.close()

    if conversations:
        current_conv_index = 0
        if st.session_state.current_conversation:
            for i, conv in enumerate(conversations):
                if conv[0] == st.session_state.current_conversation:
                    current_conv_index = i
                    break

        selected_conv = st.selectbox(
            "Conversations",
            conversations,
            format_func=lambda x: x[1],
            index=current_conv_index,
            help="Select a previous conversation or create new"
        )

        if selected_conv[0] != st.session_state.current_conversation:
            st.session_state.current_conversation = selected_conv[0]
            st.rerun()

    # New conversation button
    if st.button("New Conversation"):
        new_conversation()
        st.rerun()

    # Display chat messages
    if st.session_state.current_conversation:
        messages = load_conversation_history(
            st.session_state.current_conversation)
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Type a message...")

    if user_input:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        # Save user message
        save_message(user_input, "user")

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                try:
                    llm = ChatOllama(
                        model=st.session_state.model_settings["selected_model"],
                        temperature=st.session_state.model_settings["temperature"],
                        num_predict=st.session_state.model_settings["max_tokens"]
                    )

                    prompt_template = ChatPromptTemplate.from_template(
                        "{prompt}")
                    chain = prompt_template | llm | StrOutputParser()
                    response = chain.invoke({"prompt": user_input})

                    st.markdown(response)

                    # Save response
                    save_message(response, "assistant")
                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    save_message(error_msg, "assistant")


def document_qa_interface():
    """Document analysis and Q&A interface"""
    st.header("Document Analysis")

    if not st.session_state.authenticated:
        st.warning("Please login to use document analysis")
        return

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Document (PDF, TXT, CSV)",
        type=["pdf", "txt", "csv"]
    )

    if uploaded_file:
        if st.button("Process Document"):
            with st.spinner("Processing document..."):
                if process_uploaded_file(uploaded_file):
                    st.success("Document processed successfully!")
                else:
                    st.error("Failed to process document")

    # Question input
    if query := st.chat_input("Ask about the document..."):
        if st.session_state.document_store is None:
            st.error(
                "No document store available. Please upload and process a document first.")
            return

        try:
            docs = st.session_state.document_store.similarity_search(query)
            context = "\n\n".join([d.page_content for d in docs])

            # Generate answer
            prompt = ChatPromptTemplate.from_template("""
            Context: {context}
            Question: {query}
            Answer concisely based on the context provided:
            """)

            chain = prompt | ChatOllama(
                model=st.session_state.model_settings["selected_model"]
            ) | StrOutputParser()

            with st.spinner("Analyzing..."):
                answer = chain.invoke({"context": context, "query": query})

                # Display Q&A
                with st.chat_message("user"):
                    st.markdown(query)
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    if st.button("👍", key=f"like_{query[:10]}"):
                        save_feedback(query, answer, 1)
                        st.success("Thanks for your feedback!")
        except Exception as e:
            st.error(f"Error during document analysis: {str(e)}")

# --------------------------
# Main Application Flow
# --------------------------


def main():
    if not st.session_state.authenticated:
        authentication_section()
    else:
        model_management_sidebar()

        st.sidebar.divider()
        if st.sidebar.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.current_conversation = None
            st.rerun()

        app_tabs = st.tabs(["Chat", "Document Analysis", "Settings"])

        with app_tabs[0]:
            chat_interface()

        with app_tabs[1]:
            document_qa_interface()

        with app_tabs[2]:
            st.subheader("User Settings")
            st.info("Settings functionality can be expanded here")
            if st.button("Delete Account"):
                st.warning(
                    "This will permanently delete your account and data!")
                # Implement account deletion logic here


if __name__ == "__main__":
    main()
