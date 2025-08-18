# CAR LLM App

A Streamlit application that uses **LangChain** + **Azure OpenAI GPT-4o-mini** to process car-related descriptions into JSON based on a defined schema.

---

## System Overview
Input Handling
- Accepts free-form car description text and optional image input.
- Sanitizes the text using sanitize_input.
- Checks safety using is_safe and flags dangerous keywords/patterns with flagged_words.
  
Image Processing (Optional)
- If an image is provided, the classify_car_type function detects the car’s body type.
- This body type is used as a hint to guide the LLM in generating structured JSON.
  
LLM Processing
- Sends sanitized input and optional body type hints to Azure OpenAI GPT via LangChain.
- Uses a guarded LLM call (guarded_llm_call) to ensure output safety.
- if the output is not safe (guarded_llm_call) send to LLM again to generate safe and valid output 
- Retries the call if unsafe content or invalid JSON is detected.
  
JSON Parsing & Retry
- Extracts and validates the JSON output from the LLM.
- If JSON is invalid:
  
   - Logs the error.
   - Appends a system message instructing the LLM to regenerate safe, valid JSON.
   - Retries up to MAX_RETRIES (default = 3).
     
- Ensures the output has a top-level "car" key.
  
Output
- Returns structured JSON with all car fields populated.
- Output can be displayed in a UI or downloaded for further processing.
  
Security
- Prevents prompt injection.
- Detects and blocks unsafe keywords and patterns in both input and LLM output.

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

## video
Car_App.mp4 show the whole process
## 🖼 System Architecture
```mermaid
flowchart TD
    A[User Input: Text and Image] --> B[Streamlit UI]
    B --> C[Security Layer: sanitize_input, is_safe, flagged_words]
    C--> D[Validate email address]
    D --> E{Image Provided?}
    E -->|Yes| F[Image Classifier: classify_car_type]
    E -->|No| G[Skip Image Classification]

    F --> H[Guarded LLM Call via Azure OpenAI]
    G --> H

    H --> I[JSON Parsing and Retry, ensure safe output and fix invalid JSON]
    I --> J[Show JSON and Image in UI]
    J --> K[Download JSON]

