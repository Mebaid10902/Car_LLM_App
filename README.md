## 🚀 Clone the Repository

To get a local copy up and running, run:

- git clone https://github.com/Mebaid10902/Car_LLM_App.git
- cd Car_LLM_App

# CAR LLM App

A Streamlit application that uses **LangChain** + **Azure OpenAI GPT-4o-mini** to process natural language car-related descriptions into JSON based on a defined schema.

---

## Features
- Converts free-form text into a structured JSON format
- Uses Azure OpenAI GPT models via LangChain
- Prevent Prompt Injection
- Process text processed into a structured JSON format.
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

```mermaid
flowchart TD
    A[User Input: Text and Image -Optional] --> B[Streamlit UI]
    B --> C[Security Layer: Sanitize and Safety Check]
    C --> D{Image Provided?}

    D -->|Yes| E[Image Classifier Dummy Function]
    D -->|No| F[Skip Image Classification]

    E --> G[LLM via LangChain Azure OpenAI]
    F --> G

    G --> H[Json parsing and retry if invalid]
    H --> I[Show JSON and Image in UI]
    I --> J[Download JSON]
    I --> K[Validate Email]
    K --> L[Send JSON and Image via SMTP]
