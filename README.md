# 🗎 AI-Powered Chatbot for Google Docs

This is a **Flask-based chatbot** built with **LangChain** and **RAG-powered LLM**, designed to analyze **Google Docs** and generate test cases.  

<img src="https://github.com/user-attachments/assets/7248169c-c69d-4542-96e4-b253d263ffaa" alt="Chatbot screenshot" width="300">

---

## 📑 Table of Contents
1. [Architecture Overview](#architecture-overview)
   - [Retrieval Layer](#1️⃣-retrieval-layer)
   - [Orchestration & Prompting Layer](#2️⃣-orchestration--prompting-layer)
   - [Tools Layer](#3️⃣-tools-layer)
   - [Memory & State Management](#4️⃣-memory--state-management)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Setup Instructions](#setup-instructions)
   - [Clone the Repository](#1️⃣-clone-the-repository)
   - [Set Up a Virtual Environment](#2️⃣-set-up-a-virtual-environment)
   - [Install Dependencies](#3️⃣-install-dependencies)
   - [Configure Environment Variables](#4️⃣-configure-environment-variables)
   - [Run the Application](#5️⃣-run-the-application)
5. [API Setup](#api-setup)
   - [Google Docs API](#google-docs-api)
   - [Hugging Face Inference API](#hugging-face-inference-api)
6. [How It Works](#how-it-works)
7. [How to Test](#how-to-test)
8. [License](#license)

---

## 🧱 Architecture Overview
This application is built as an **AI-powered RAG (Retrieval-Augmented Generation) system** orchestrated with **LangChain agents and tools**.

### 1️⃣ Retrieval Layer

1. **Google Docs** are used as the primary data source:

  - Specification document
  - Test cases document

2. Documents are parsed, chunked, and embedded using **Hugging Face embedding models**.
3. Embeddings are stored in **FAISS** for efficient semantic similarity search.
4. Retrieval is performed per user session to keep contexts isolated.

### 2️⃣ Orchestration & Prompting Layer

1. The chatbot logic is implemented using a **LangChain StructuredChatAgent**.
2. The agent decides which action to take based on:
  - Current conversation step
  - User input
  - Retrieved contextual information
3. Prompt templates guide the agent through a multi-step workflow:
  - Load specification
  - Load test cases
  - Select feature
  - Generate test cases

### 3️⃣ Tools Layer

1. The agent interacts with the system exclusively through **LangChain tools**, including:
  - Loading specification and test case documents
  - Tracking conversation state
  - Generating test cases using retrieved content
  - Managing user sessions and resets

### 4️⃣ Memory & State Management

1. **ConversationBufferMemory** is used to retain chat history.
2. A custom memory manager tracks:
  - Uploaded documents
  - Current conversation step
  - Selected feature

---

## Tech Stack
- **Python** - core backend
- **Flask** – web interface / API layer
- **LangChain** – RAG orchestration and prompt management
- **FAISS** – vector storage
- **Hugging Face Inference API** – LLM and embedding models
- **Google Docs** – external knowledge base

---

## Prerequisites
- Python 3.10+
- Hugging Face account
- Google account with access to target Google Docs

---

## 🛠️ Setup Instructions

### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/deedmitrij/googledoc-chatbot.git
cd googledoc-chatbot
```

### **2️⃣ Set Up a Virtual Environment**
```sh
python -m venv .venv
.venv\Scripts\activate
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Configure Environment Variables**
Create a `.env` file in the project root and add the following:

```ini
HF_API_KEY=your_huggingface_api_key
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

📌 **Note:** Replace `your_huggingface_api_key` with your actual Hugging Face API key.  
📌 **Note:** Place `credentials.json` (your Google API credentials) in the **root directory** of the project.

### **5️⃣ Run the Application**
```sh
python -m run
```

The chatbot will start and be accessible at **http://localhost:5000**.

---

## 🔗 API Setup

### 🗒️ Google Docs API
To access Google Docs, you need a **Google Cloud service account**:

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Enable the **Google Docs API**.
3. Create a new **service account** and generate a **JSON key file**.
4. Save the `credentials.json` file in the root of this project.


### 🤖 Hugging Face Inference API
To get access to Hugging Face models:

1. Visit **https://huggingface.co/**
2. Sign in or create a **Hugging Face account**.
3. Go to **Settings → Access Tokens**.
4. Create a new token with **Make calls to Inference Providers** permission.
5. Copy the token and add it to your `.env` file as `HF_API_KEY`.
   
---

## 🚀 How It Works  
1. **Upload Documents**: Provide a **specification document** and a **test cases document**.  
2. **Input a Query**: Enter a **feature query** or a **custom user query**.  
3. **Processing with RAG**: The chatbot retrieves relevant sections, processes them with **Hugging Face-hosted LLM**, and generates new test cases.  
4. **Receive Results**: Get an updated set of **test cases tailored to user query and document content**.  

## 🔎 How to Test
You can test the chatbot manually using the web UI.

### Basic Flow (Happy Path)
1. Start the application.
2. Open http://localhost:5000 in your browser.
3. Provide a **Google Docs link** to a specification document.
4. Provide a **Google Docs link** to a test cases document.
5. Enter a **feature name** (e.g., User login).
6. Review the generated test cases.

### Reset & Retry
1. After test case generation, you can:
  - Extract test cases for another feature
  - Upload new documents
  - Clear the session and restart

### Error Handling
  - Invalid or missing links are handled by the agent.
  - The chatbot guides the user back to the expected step.

---

## 🐝 License
This project is **open-source** and available under the [MIT License](LICENSE).
