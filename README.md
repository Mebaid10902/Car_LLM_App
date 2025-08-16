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
## 🖼 System Architecture

```mermaid
flowchart TD
    subgraph UI["Streamlit UI"]
        A[User Input: Text / Image]
        B[Process Button]
        C[Display JSON + Image]
        D[Download JSON]
    end

    subgraph Security["Security Layer"]
        E[Sanitize Input]
        F[Safety Check]
    end

    subgraph Classifier["Image Classifier"]
        G[Dummy Function → Predict Car Type]
    end

    subgraph LLM["Azure OpenAI (via LangChain)"]
        H[Generate JSON]
        I[Validate Schema]
        J[Retry / Fix JSON if invalid]
    end

    subgraph Email["Email Service"]
        K[Validate Recipient Email]
        L[Send JSON + Image via SMTP]
    end

    %% Connections
    A --> E
    E --> F
    F --> B
    B -->|If Image| G
    B -->|If No Image| H
    G --> H
    H --> I --> J --> C
    C --> D
    C --> K --> L

This diagram illustrates the **main components** and how they interact:

- **UI** → takes text/image input  
- **Security** → sanitizes & validates input  
- **Classifier** → dummy body type classifier (future implementation)  
- **LLM** → generates & validates JSON schema, retries if needed  
- **Email Service** → validates email, sends JSON + image  

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
