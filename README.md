# CAR LLM App

A Streamlit application that uses **LangChain** + **Azure OpenAI GPT-4o-mini** to process natural language car-related descriptions into structured JSON based on a defined schema.

---

## 📦 Features
- Converts free-form text into a structured JSON format  
- Uses Azure OpenAI GPT models via LangChain  
- Schema-based validation to ensure JSON output matches requirements  
- Prevents prompt injection & unsafe inputs  
- Sends parsed data (JSON + Image) via email  
- Streamlit UI for easy text input & result viewing  

---

## 📊 Flow
```mermaid
flowchart TD
    A[User Text / Image] --> B[Streamlit UI]
    B --> C[Security Check: Sanitize + Safety Check]
    C --> D{Image Provided?}
    D -->|Yes| E[Classify Body Type using CV]
    D -->|No| F[Skip Image Classification]
    E --> G[LangChain LLM → JSON]
    F --> G[LangChain LLM → JSON]
    G --> H[Output JSON + Image to User]
    H --> I[Send JSON + Image to Specific Email]
---
🛠 Configuration
Update config.py with your settings.

To generate an App Password for Gmail:

Open your Gmail → Go to Manage Your Account

Navigate to Security

Enable 2-Step Verification

Search for App Passwords

Enter app name (e.g., CarApp)

Copy the generated 16-character key (remove spaces)

Paste it into config.py along with your email

Add your Azure OpenAI API credentials in config.py.

⚙️ Installation
Run these commands in your terminal:

bash
# 1. Install dependencies
pip install -r requirements.txt
# 2. Start Streamlit
streamlit run app.py
📩 Usage
Upload a car image

Enter a car description

Provide a recipient email

Click Process and Send

The app will:

Sanitize inputs

Process via Azure OpenAI GPT

Validate JSON against schema

Display results + allow download

Email JSON & image to recipient
