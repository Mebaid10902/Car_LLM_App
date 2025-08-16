## 🖼 System Architecture

```mermaid
flowchart TD
    A[User Input: Text or Image] --> B[Streamlit UI]
    B --> C[Security Layer: Sanitize and Safety Check]
    C --> D{Image Provided?}

    D -->|Yes| E[Image Classifier Dummy Function]
    D -->|No| F[Skip Image Classification]

    E --> G[LLM via LangChain Azure OpenAI]
    F --> G

    G --> H[Schema Validation and Retry if Invalid]
    H --> I[Show JSON and Image in UI]
    I --> J[Download JSON]
    I --> K[Validate Email]
    K --> L[Send JSON and Image via SMTP]

# CAR LLM App

A Streamlit application that uses **LangChain** + **Azure OpenAI GPT-4o-mini** to process natural language car-related descriptions into JSON based on a defined schema.

---

## Features
- Converts free-form text into a structured JSON format
- Uses Azure OpenAI GPT models via LangChain
- Schema-based validation to ensure JSON output matches requirements
- Prevent Prompt Injection
- Send the Data via Email
- Streamlit UI for easy text input & viewing of results

## 🛠 Configuration

1. Add Configurations in config.py
To generate app password for gmail account follow these steps.
Open your gmail 
Go to Manage Your Account
Go to Security
Open 2-Step Verification and turn on
Go back and search for App password
Enter App name like CarApp
Copy your 16 key (remove spaces after you copy it)
Go to config.py
Enter your email and app password

## 🛠 Installation
Run these commands in your terminal
1. Install dependencies
pip install -r requirements.txt
2.Start Streamlit
streamlit run app.py
