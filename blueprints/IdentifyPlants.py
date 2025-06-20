from flask import Blueprint, render_template, request
import torch
from torchvision import models, transforms
from PIL import Image
import torch.nn.functional as F

plantidentify_bp = Blueprint('predict', __name__)

# Class labels
class_names = [
    'Aloevera', 'Amla', 'Amruta_Balli', 'Arali', 'Ashoka', 'Ashwagandha', 'Avacado',
    'Bamboo', 'Basale', 'Betel', 'Betel_Nut', 'Brahmi', 'Castor', 'Curry_Leaf',
    'Doddapatre', 'Ekka', 'Ganike', 'Gauva', 'Geranium', 'Henna', 'Hibiscus',
    'Honge', 'Insulin', 'Jasmine', 'Lemon', 'Lemon_grass', 'Mango', 'Mint',
    'Nagadali', 'Neem', 'Nithyapushpa', 'Nooni', 'Pappaya', 'Pepper',
    'Pomegranate', 'Raktachandini', 'Rose', 'Sapota', 'Tulasi', 'Wood_sorel', 'Yarsagumba'
]

# Load model and transform (run once)
model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
model.load_state_dict(torch.load("plant_classifier_new.pth", map_location=torch.device('cpu')))
model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

def is_suspicious_image(pil_image):
    img = pil_image.resize((64, 64))  # Resize for fast analysis
    pixels = list(img.getdata())
    mean_color = tuple(sum(c) / len(c) for c in zip(*pixels))
    stddev = sum(
        sum((c - m) ** 2 for c, m in zip(pixel, mean_color)) for pixel in pixels
    ) / (len(pixels) * 3)
    return stddev < 500  # You can tweak this threshold

@plantidentify_bp.route("/identify", methods=["GET"])
def index():
    return render_template("PlantDetection.html")

@plantidentify_bp.route("/predict", methods=["POST"])
def predict_route():
    if "file" not in request.files:
        return render_template("PlantDetection.html", result="No file uploaded.")

    file = request.files["file"]
    if file.filename == "":
        return render_template("PlantDetection.html", result="No file selected.")

    try:
        image = Image.open(file).convert("RGB")
    except Exception:
        return render_template("PlantDetection.html", result="Invalid image format.")

    # Suspicious image check
    if is_suspicious_image(image):
        return render_template("PlantDetection.html", result="This doesn't appear to be a valid plant photo.")

    # Transform and predict
    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image_tensor)
        probs = F.softmax(outputs, dim=1)[0]
        top_probs, top_idxs = torch.topk(probs, 2)

        top1_conf = top_probs[0].item()
        top2_conf = top_probs[1].item()
        top_class_idx = top_idxs[0].item()

        if top1_conf < 0.8 or (top1_conf - top2_conf) < 0.2:
            result = f"Unknown or invalid input (Confidence: {top1_conf * 100:.2f}%)"
        else:
            plant_name = class_names[top_class_idx]
            result = f"{plant_name} (Confidence: {top1_conf * 100:.2f}%)"

    return render_template("PlantDetection.html", result=result)
