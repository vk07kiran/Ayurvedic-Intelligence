from flask import Blueprint, render_template, request, session
import torch
from torchvision import models, transforms
from PIL import Image
import torch.nn.functional as F
import csv

plantidentify_bp = Blueprint('predict', __name__)

# Plant class labels
class_names = ['Aloevera', 'Amaltas Raj Brikshya', 'Amla', 'Ank', 'Ashok', 'Ashwagandha', 'Asuro', 'Atis', 'Avacado', 'Bajradanti', 'Barberry', 'Barro', 'Bel', 'Bhoj patra', 'Bikh', 'Bojho', 'Chamomile', 'Chhatiwan', 'Chiraito', 'Chutro', 'Dalchini', 'Datiwan', 'Dhasingre', 'Dhupi', 'Ghod tapre', 'Gokul Dhup', 'Gunsi', 'Gurjo', 'Harro', 'Insulin', 'Ishwori', 'Jatamasi', 'Jethi madhu', 'Jhari Kote', 'Jhyau', 'Kakoli Ban Lasun', 'Keshar', 'Kumkum', 'Kurilo', 'Kutki', 'Kyasar', 'Laghu Patra', 'Lauth Salla', 'Majitho', 'Mango', 'Mint', 'Mirkhe Lahara', 'Nagbeli', 'Neem', 'Nirbisi', 'Okhar', 'Padamchal', 'Pakhanbed', 'Panchaune', 'Pangro', 'Pipla', 'Rhododendron', 'Rittha', 'Rose', 'Rudrakshya', 'Rukh Unyiu', 'Sarpagandha', 'Satuwa', 'Seto Musli', 'Simal', 'Somlata', 'Sugandhakokila', 'Sugandhawal', 'Timur', 'Tulasi', 'Unknown', 'Valu Kath', 'Vote Lahara', 'Vyakur', 'Yarsagumba']



# Load the trained model
model = models.resnet18()
model.fc = torch.nn.Linear(model.fc.in_features, len(class_names))
model.load_state_dict(torch.load("Information/PlantIdentificationModel.pth", map_location=torch.device('cpu')))
model.eval()

# Image preprocessing
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# Suspicious image check: avoids overly uniform or blank images
# def is_suspicious_image(pil_image):
#     img = pil_image.resize((264, 264))   
#     pixels = list(img.getdata())
#     mean_color = tuple(sum(c) / len(c) for c in zip(*pixels))
#     stddev = sum(
#         sum((c - m) ** 2 for c, m in zip(pixel, mean_color)) for pixel in pixels
#     ) / (len(pixels) * 3)
#     return stddev < 500

# Lookup plant info from CSV
def get_plant_info(plant_name):
    csv_path = r"Information/PlantDatabase.csv"
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["PlantName"].strip().lower() == plant_name.lower():
                return {
                    "scientific": row["ScientificName"],
                    "usage": row["Usage"],
                    "parts": row["PartsUsed"],
                    "region": row["Region of Nepal"]
                }
    return None

# Route: Upload form
@plantidentify_bp.route("/identify", methods=["GET"])
def index():
    return render_template("PlantDetection.html")

# Route: Predict and show result
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

    # if is_suspicious_image(image):
    #     return render_template("PlantDetection.html", result="This doesn't appear to be a valid plant photo.")

    image_tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        outputs = model(image_tensor)
        probs = F.softmax(outputs, dim=1)[0]
        top_probs, top_idxs = torch.topk(probs, 2)

        top1_conf = top_probs[0].item()
        top2_conf = top_probs[1].item()
        top_class_idx = top_idxs[0].item()

        if top1_conf < 0.85 or (top1_conf - top2_conf) < 0.2:
            return render_template("PlantDetection.html", result=f"This plant seems to match several known species. Please provide a clearer, closer image or try again from a different angle.")

        plant_name = class_names[top_class_idx]


        if plant_name == "Unknown":
            return render_template("PlantDetection.html", result=f"The uploaded image doesn't appear to be a valid plant image. Please try again.")

        details = get_plant_info(plant_name)

        if details:
            result = f"{plant_name} (Confidence: {top1_conf * 100:.2f}%)"
            return render_template("PlantDetection.html", result=result,
                                   plant_name=plant_name,
                                   scientific=details["scientific"],
                                   usage=details["usage"],
                                   parts=details["parts"],
                                   region=details["region"])
        else:
            result = f"{plant_name} (Confidence: {top1_conf * 100:.2f}%), but no additional data found."
            return render_template("PlantDetection.html", result=result)

# @plantidentify_bp.route('/logout')
# def logout():
#     session.clear()  # Clears all session data (user_id, username, etc.)
#     return redirect(url_for('login.login'))  # Redirect to login page

