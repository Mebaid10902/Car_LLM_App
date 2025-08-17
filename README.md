# CAR LLM App

A Streamlit application that uses **LangChain** + **Azure OpenAI GPT-4o-mini** to process natural language car-related descriptions into JSON based on a defined schema.

---

## Features
- Converts free-form text into a structured JSON format
- Uses Azure OpenAI GPT models via LangChain
- Prevent Prompt Injection
- Process text and force search for all fields in the schema then processed into a structured JSON format.
- 📌 JSON Parsing with Retry Logic
   - Extract JSON block
   - Clean JSON string
   - Ensure valid formatting
   - Try parsing with if successful → return result
   - If parsing fails
   - Log the error
   - Ask the LLM to fix the JSON by sending the invalid output back with an instruction:
   - Retry parsing with the LLM’s corrected JSON
   - Max retries (default = 3)
   - After 3 failed attempts, raise an error  
- Send the Data via Email
- Streamlit UI for easy text input & viewing of results

## 🛠 Configuration

Add Configurations in config.py
## Generate app password
To generate app password for gmail account follow these steps.
- Open your gmail 
- Go to Manage Your Account
- Go to Security
- Open 2-Step Verification and turn on
- Go back and search for App password
- Enter App name like CarApp
- Copy your 16 key (remove spaces after you copy it)
- Go to config.py
- Enter your email and app password
  
## 🛠 Installation
Run these commands in your terminal
Install dependencies
   
- pip install -r requirements.txt

Start Streamlit

- streamlit run app.py

## 🖼 System Architecture

flowchart TD
    %% Node style definitions
    classDef security fill:#f96,stroke:#333,stroke-width:2px,color:white;
    classDef image fill:#6cf,stroke:#333,stroke-width:2px,color:white;
    classDef llm fill:#fc6,stroke:#333,stroke-width:2px,color:white;
    classDef ui fill:#ccc,stroke:#333,stroke-width:2px,color:black;

    %% Flowchart nodes
    A[📝 User Input: Text & Image] --> B[🖥️ Streamlit UI]
    B --> C[🔒 Security Layer: sanitize_input, is_safe, flagged_words]

    C --> D{🖼️ Image Provided?}
    D -->|Yes| E[📷 Image Classifier: classify_car_type]
    D -->|No| F[⏭ Skip Image Classification]

    E --> G[🤖 Guarded LLM Call via Azure OpenAI]
    F --> G

    G --> H[🛡️ JSON Parsing & Retry: max attempts, fix invalid JSON]
    H --> I[📊 Show JSON & Image in UI]
    I --> J[💾 Download JSON]

    %% Apply styles
    class C security
    class E image
    class G,H llm
    class A,B,I,J ui
