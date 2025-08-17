import asyncio
import json
import logging
from langchain_openai import AzureChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.schema import SystemMessage, HumanMessage
from config import AZURE_DEPLOYMENT_NAME, AZURE_ENDPOINT, AZURE_OPENAI_KEY, MAX_RETRIES 
from security import sanitize_input, is_safe, flagged_words
from classifier import classify_car_type

logging.basicConfig(level=logging.INFO)

llm = AzureChatOpenAI(
    azure_endpoint=AZURE_ENDPOINT.rstrip("/"),
    api_key=AZURE_OPENAI_KEY,
    deployment_name=AZURE_DEPLOYMENT_NAME,
    api_version="2025-01-01-preview",
    temperature=0.1
)


async def guarded_llm_call(prompt_messages):
    """
    Call LLM safely with retries for unsafe-output and invalid JSON.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        # Check each message for unsafe content
        for msg in prompt_messages:
            content = getattr(msg, "content", str(msg))
            if not is_safe(content):
                terms = flagged_words(content)
                logging.warning(f"Unsafe content in prompt: {terms}")
                raise ValueError(f"Unsafe content detected in prompt: {terms}")

        # Call LLM
        response = await asyncio.to_thread(llm, messages=prompt_messages)
        output = sanitize_input(response.content).strip()

        # Check output safety
        if not is_safe(output):
            terms = flagged_words(output)
            logging.warning(f"Unsafe content detected in LLM output: {terms}")
        else:
            # Try parsing JSON
            try:
                parsed = json.loads(output)
                return parsed
            except json.JSONDecodeError:
                logging.warning(f"Invalid JSON detected. Retry {attempt}/{MAX_RETRIES}")

        # Append system message for retry
        prompt_messages.append(SystemMessage(content="Previous response was unsafe or invalid JSON. Please regenerate a safe, valid JSON output."))

    terms = flagged_words(output)
    raise ValueError(f"Failed to get safe JSON after {MAX_RETRIES} retries. Last flagged terms: {terms}")


async def process_description_to_json(description: str, image_file=None) -> dict:
    """
    Convert a car text description into structured JSON .
    """
    # Step 0: Input safety
    if not is_safe(description):
        unsafe_terms = flagged_words(description)
        raise ValueError(f"Description contains unsafe content: {unsafe_terms}")

    clean_desc = sanitize_input(description).strip()
    body_type_hint = classify_car_type(image_file) if image_file else None

    # Step 1: System & human prompts
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

    # Step 2: Call LLM safely
    parsed = await guarded_llm_call(final_prompt.to_messages())

    # Step 3: Ensure top-level "car" key
    if "car" not in parsed:
        parsed = {"car": parsed}

    return parsed


__all__ = ["process_description_to_json"]
