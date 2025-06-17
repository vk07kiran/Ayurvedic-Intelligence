from flask import Flask, request, render_template
from herb_model import detect_plant, get_herb_info
from PIL import Image
import io

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('PlantDetection.html')

@app.route('/scan', methods=['GET', 'POST'])
def scan():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('PlantDetection.html', result={"label": "No image uploaded", "confidence": 0, "info": "Upload a valid image."})

        file = request.files['image']

        if file.filename == '':
            return render_template('PlantDetection.html', result={"label": "No file selected", "confidence": 0, "info": "Select an image before submitting."})

        try:
            # Read and process image
            image = Image.open(io.BytesIO(file.read()))
            label, confidence = detect_plant(image)

            if label not in ['Uncertain', 'Unknown']:
                info = get_herb_info(label)
            else:
                info = "Could not confidently identify the herb."

            result = {
                "label": label,
                "confidence": f"{confidence * 100:.2f}",
                "info": info
            }

            return render_template('PlantDetection.html', result=result)

        except Exception as e:
            print("Error handling image upload:", e)
            result = {
                "label": "Error",
                "confidence": 0,
                "info": "There was a problem processing the image."
            }
            return render_template('PlantDetection.html', result=result)

    return render_template('PlantDetection.html')

if __name__ == '__main__':
    app.run(debug=True)
