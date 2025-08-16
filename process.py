import asyncio
import json
import re
import logging
from langchain_openai import AzureChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from config import AZURE_DEPLOYMENT_NAME, AZURE_ENDPOINT, AZURE_OPENAI_KEY
from security import sanitize_input, is_safe
from classifier import classify_car_type

# ---------------- LLM Setup ----------------
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT.rstrip("/"),
    api_key=AZURE_OPENAI_KEY,
    deployment_name=AZURE_DEPLOYMENT_NAME,
    api_version="2025-01-01-preview",
    temperature=0
)

# ---------------- JSON Utilities ----------------
def extract_json_block(text: str) -> str:
    """Extract JSON if wrapped in ```json ... ``` fences."""
    match = re.search(r"```json(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def clean_json_string(json_str: str) -> str:
    """Fix common JSON issues before parsing."""
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)  # remove trailing commas
    json_str = json_str.replace("“", '"').replace("”", '"')  # smart quotes
    return json_str

async def parse_json_with_retry(raw_text: str, max_retries=3) -> dict:
    """Multi-step JSON parsing with retries."""
    attempt = 0
    text = raw_text

    while attempt < max_retries:
        attempt += 1
        try:
            cleaned = clean_json_string(extract_json_block(text))
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logging.warning(f"JSON parse failed (attempt {attempt}): {e}")
            if attempt == max_retries:
                raise
            # Ask LLM to repair
            fix_prompt = f"Fix this JSON so it has a single top-level 'car' key and is valid:\n{text}"
            response = await asyncio.to_thread(
                llm,
                messages=[
                    {"role": "system", "content": "Return corrected JSON only."},
                    {"role": "user", "content": fix_prompt},
                ]
            )
            text = response.content.strip()

# ---------------- Main Function ----------------
async def process_description_to_json(description: str, image_file=None) -> dict:
    """
    Convert a raw car listing description into structured JSON with a top-level "car" key.
    """
    if not is_safe(description):
        raise ValueError("Description contains unsafe content.")

    clean_desc = sanitize_input(description).strip()

    # Step 1: Optional body_type hint
    body_type_hint = classify_car_type(image_file) if image_file else None

    # Step 2: Build system + user prompts
    system_prompt_text = """
    You are a strict car listing parser.
    Convert the text into JSON with schema like a top-level key called "car".
    The "car" object should include the following fields:
    body_type, color, brand, model, manufactured_year, motor_size_cc,
    tires (with type and manufactured_year), windows,
    notices (list of type and description), price (amount and currency).

    Requirements:
    - Output must be valid JSON.
    - Output must follow the schema.
    - Include all required fields.
    - No extra keys, comments, or text outside the JSON.
    """
    if body_type_hint:
        system_prompt_text += f"\n- Use this body_type from the image: {body_type_hint}"

    system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_text)
    human_prompt = HumanMessagePromptTemplate.from_template("{desc}")
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
    final_prompt = chat_prompt.format_prompt(desc=clean_desc)

    # Step 3: First GPT call
    response = await asyncio.to_thread(llm, messages=final_prompt.to_messages())
    raw_output = response.content.strip()

    # Step 4: Multi-step JSON retry
    parsed = await parse_json_with_retry(raw_output)

    # Step 5: Ensure "car" key exists
    if "car" not in parsed:
        parsed = {"car": parsed}

    logging.info(f"Final parsed car JSON: {parsed}")
    return parsed
