# 🗎 AI-Powered Chatbot for Google Docs

This is a **Flask-based chatbot** powered by **Retrieval-Augmented Generation (RAG)** using **Google Gemini LLM**, designed to analyze **Google Docs** and generate test cases.  

<img src="https://github.com/user-attachments/assets/5afb31f1-3518-46cc-8441-8e966e17a65c" alt="Chatbot screenshot" width="300">

## 🚀 How It Works  
1. **Upload Documents**: Provide a **specification document** and a **test cases document**.  
2. **Input a Query**: Enter a **feature query** or a **custom user query**.  
3. **Processing with RAG**: The chatbot retrieves relevant sections, processes them with **Google Gemini LLM**, and generates new test cases.  
4. **Receive Results**: Get an updated set of **test cases tailored to user query and document content**.  
---

## 📑 Table of Contents
1. [Setup Instructions](#%EF%B8%8F-setup-instructions)
   - [Clone the Repository](#1%EF%B8%8F-clone-the-repository)
   - [Set Up a Virtual Environment](#2%EF%B8%8F-set-up-a-virtual-environment-optional-but-recommended)
   - [Install Dependencies](#3%EF%B8%8F-install-dependencies)
   - [Configure Environment Variables](#4%EF%B8%8F-configure-environment-variables)
   - [Run the Application](#5%EF%B8%8F-run-the-application)
2. [Google API Setup](#-google-api-setup)
   - [Google Docs API](#google-docs-api)
   - [Google Gemini API](#google-gemini-api)
3. [License](#-license)

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
source .venv/bin/activate  # On macOS/Linux
.venv\Scripts\activate  # On Windows
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Configure Environment Variables**
Create a `.env` file in the project root and add the following:

```ini
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_CREDENTIALS_PATH=./credentials.json
```

📌 **Note:** Replace `your_gemini_api_key` with your actual API key.  
📌 **Note:** Place `credentials.json` (your Google API credentials) in the **root directory** of the project.

### **5️⃣ Run the Application**
```sh
python backend/run.py
```

The chatbot will start and be accessible at **http://localhost:5000**.

---

## 🔗 Google API Setup

### 🗒️ Google Docs API
To access Google Docs, you need a **Google Cloud service account**:

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Enable the **Google Docs API**.
3. Create a new **service account** and generate a **JSON key file**.
4. Save the `credentials.json` file in the root of this project.


### 🤖 Google Gemini API
To get access to Google Gemini AI:

1. Visit **[Google AI Studio](https://aistudio.google.com/)**.
2. Sign in with your **Google Account**.
3. Navigate to **API Keys** in the settings.
4. Generate a new API key and copy it.
5. Add this key to your `.env` file as `GEMINI_API_KEY`.
---

## 🐝 License
This project is **open-source** and available under the [MIT License](LICENSE).
