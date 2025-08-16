from PIL import Image

def classify_car_type(uploaded_file) -> str:
    """
    Dummy car type classifier.
    Receives an uploaded file from Streamlit.
    Returns a string representing the car's body type.
    Replace with real CV model later.
    """
    if uploaded_file is None:
        return "unknown"

    try:
        # Open image with PIL
        image = Image.open(uploaded_file)
        # For now, just a dummy logic:
        # TODO: Replace with real CV model to detect body type
        return "hatchback"  # example hard-coded body type
    except Exception as e:
        print("Failed to process image:", e)
        return "unknown"