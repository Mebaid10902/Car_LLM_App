import streamlit as st
import asyncio
import tempfile
import shutil
import json
import os

from process import process_description_to_json
from emailer import send_email_with_attachment, validate_and_normalize_email

# -------------------------------
# Streamlit Page Config
# -------------------------------
st.set_page_config(page_title="Car info Parser", page_icon="", layout="centered")

st.title("LLM Car app")
st.write("Upload a car image, enter a description, and send the parsed JSON + image via email.")

# -------------------------------
# Inputs
# -------------------------------
uploaded_file = st.file_uploader("Upload Car Image", type=["png", "jpg", "jpeg"])
description = st.text_area(
    "Car Description",
    placeholder="Example: Blue Ford Fusion produced in 2015 featuring a 2.0-liter engine..."
)
recipient_email = st.text_input("Recipient Email", placeholder="example@gmail.com")


# -------------------------------
# Async helper
# -------------------------------
def run_async(coro):
    """Safely run async functions inside Streamlit."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        return asyncio.ensure_future(coro)
    else:
        return loop.run_until_complete(coro)


# -------------------------------
# Processing Workflow
# -------------------------------
def process_and_send(description: str, recipient_email: str, uploaded_file):
    temp_dir = tempfile.mkdtemp()
    temp_image_path = None
    result = None

    try:
        with st.spinner("Processing..."):
            # Step 1: Save uploaded image
            if uploaded_file is not None:
                temp_image_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_image_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.image(temp_image_path, caption="Uploaded Car Image", use_container_width=True)

            # Step 2: Generate JSON
            result = run_async(process_description_to_json(description, temp_image_path))
            st.subheader("Parsed JSON")
            st.json(result)

            # Add Download JSON button
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(result, indent=2),
                file_name="car_listing.json",
                mime="application/json"
            )

            # Step 3: Save JSON locally
            temp_json_path = os.path.join(temp_dir, "car_listing.json")
            with open(temp_json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)

            # Step 4: Send email
            run_async(send_email_with_attachment(
                to_email=recipient_email,
                subject="Car Listing JSON & Image",
                body="Attached is the car listing JSON and image.",
                attachment_paths=[temp_json_path, temp_image_path] if temp_image_path else [temp_json_path]
            ))

            st.success(f"Processed and sent successfully to {recipient_email}!")

    except Exception as e:
        st.error(f"Error: {str(e)}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# -------------------------------
# Button Action
# -------------------------------
if st.button("Process and Send"):
    if not description.strip():
        st.error("Please enter a description.")
    elif not recipient_email.strip():
        st.error("Please enter the recipient email.")
    else:
        # Validate email before proceeding
        try:
            recipient_email = validate_and_normalize_email(recipient_email)
        except ValueError as e:
            st.error(str(e))
            st.stop()

        process_and_send(description, recipient_email, uploaded_file)
