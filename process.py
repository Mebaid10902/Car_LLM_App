import asyncio
import json
from langchain_openai import AzureChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from config import AZURE_DEPLOYMENT_NAME, AZURE_ENDPOINT, AZURE_OPENAI_KEY
from security import sanitize_input, is_safe, flagged_words  # enhanced versions
from classifier import classify_car_type

# Initialize Azure GPT-4o mini
llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT.rstrip("/"),
    api_key=AZURE_OPENAI_KEY,
    deployment_name=AZURE_DEPLOYMENT_NAME,
    api_version="2025-01-01-preview",
    temperature=0.1
)

async def process_description_to_json(description: str, image_file=None) -> dict:
    """
    Convert a raw car listing description into structured JSON with a top-level "car" key.
    If an image is provided, use the classifier to detect the body_type and pass it as a hint to the GPT.
    """
    # --- Step 0: Check safety using enhanced fuzzy-safe functions ---
    if not is_safe(description):
        unsafe_terms = flagged_words(description)
        raise ValueError(f"Description contains unsafe content: {unsafe_terms}")

    clean_desc = sanitize_input(description).strip()

    # --- Step 1: Get body_type from image if provided ---
    body_type_hint = None
    if image_file is not None:
        body_type_hint = classify_car_type(image_file)

    # --- Step 2: System & Human prompt ---
    system_prompt_text = """
        You are a strict car listing parser.
        Convert the text into JSON with schema like a top-level key called "car".
        The "car" object should include the following fields:
        body_type, color, brand, model, manufactured_year, motor_size_cc,
        tires (with type and manufactured_year), windows,
        notices (list of type and description), price (amount and currency).

        Requirements:
        - Extract all information from the description text.
        - If a field is missing, infer reasonable values based on real car specs.
        - If any field is missing or not mentioned in the text, fill it with a reasonable default or typical value for the given brand, model, and year. Do not leave fields as "unknown".
        - Output must be valid JSON.
        - No extra keys, comments, or text outside the JSON.
    """
    if body_type_hint:
        system_prompt_text += f"\n- Use this body_type from the image: {body_type_hint}"

    system_prompt = SystemMessagePromptTemplate.from_template(system_prompt_text)
    human_prompt = HumanMessagePromptTemplate.from_template("{desc}")
    chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])
    final_prompt = chat_prompt.format_prompt(desc=clean_desc)

    # --- Step 3: First GPT call ---
    response = await asyncio.to_thread(llm, messages=final_prompt.to_messages())
    raw_json = response.content.strip()

    # --- Step 4: Try parsing JSON ---
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError:
        # Retry GPT to fix invalid JSON
        retry_prompt = f"Fix this JSON so it has a single top-level 'car' key and is valid:\n{raw_json}"
        retry_response = await asyncio.to_thread(
            llm,
            messages=[
                {"role": "system", "content": "Return corrected JSON only."},
                {"role": "user", "content": retry_prompt},
            ]
        )
        raw_json = retry_response.content.strip()
        parsed = json.loads(raw_json)

    # --- Step 5: Ensure "car" key exists ---
    if "car" not in parsed:
        parsed = {"car": parsed}

    return parsed

__all__ = ["process_description_to_json"]
