import os
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import wikipedia
from googleapiclient.discovery import build

# Load model
model_path = 'plant_model.h5'
model = load_model(model_path)

# Define your dataset path to get class names
dataset_path = r'C:\Users\MSI\Desktop\A\Ayurvedic-Intelligence\Pages\HerbScanner\plant_dataset'
class_names = sorted([
    d for d in os.listdir(dataset_path)
    if os.path.isdir(os.path.join(dataset_path, d)) and d.lower() != "unknown"
])

def detect_plant(image):
    """
    Detects the plant species from an input image using a trained CNN model.

    Args:
        image (PIL.Image): The input image object.

    Returns:
        tuple: Predicted plant class name and confidence level
    """
    try:
        img = image.convert('RGB')
        img = img.resize((150, 150))
        img_array = img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0

        prediction = model.predict(img_array)

        if prediction.shape[1] == 1:
            # Binary classification
            confidence = prediction[0][0]
            label = class_names[1] if confidence > 0.5 else class_names[0]
        else:
            # Multi-class classification
            predicted_class_index = np.argmax(prediction)
            confidence = np.max(prediction)
            label = class_names[predicted_class_index]

        print(f"[DEBUG] Predicted class: {label}, Confidence: {confidence:.2f}")

        if confidence < 0.7:
            return "Uncertain", confidence

        return label, confidence

    except Exception as e:
        print("Error during prediction:", e)
        return "Unknown", 0.0

def get_herb_info(herb_name):
    """
    Retrieves information about the herb from Wikipedia.
    Falls back to Google Custom Search if Wikipedia doesn't have the info.
    """
    try:
        return wikipedia.summary(herb_name, sentences=2)
    except (wikipedia.exceptions.DisambiguationError, wikipedia.exceptions.PageError):
        return get_herb_info_google(herb_name)

def get_herb_info_google(query):
    """
    Retrieves information about the herb using Google Custom Search.
    """
    api_key = "AIzaSyCPdUYZSEuwXc65y-SAYythJktEpxJ38UI"
    search_engine_id = "16c3e04429ca34e9b"

    try:
        service = build("customsearch", "v1", developerKey=api_key)
        res = service.cse().list(q=query, cx=search_engine_id, num=1).execute()
        if "items" in res:
            return res["items"][0]["snippet"]
        else:
            return "No information found on Google."
    except Exception as e:
        return f"Error using Google Search: {e}"