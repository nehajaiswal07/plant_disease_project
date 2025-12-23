from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import os

# ================= FLASK SETUP =================
app = Flask(__name__)
CORS(app)

# ================= PATHS =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "solanaceae_leaf_model.keras")
CLASSES_PATH = os.path.join(BASE_DIR, "classes.txt")

# ================= LOAD MODEL =================
model = tf.keras.models.load_model(MODEL_PATH)
# 🔥 Warm-up model (prevents long first prediction)
dummy_input = np.zeros((1, 128, 128, 3))
model.predict(dummy_input)
print("✅ Model warmed up and ready")

# ================= LOAD CLASSES =================
with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    CLASS_NAMES = [line.strip() for line in f.readlines()]

# ================= DISEASE DETAILS =================
DISEASE_DETAILS = {
    "Cercospora Leaf Spot": {
        "cause": "Fungal disease caused by Cercospora species. Spreads in humid conditions.",
        "remedy": "Remove infected leaves and spray fungicide like Mancozeb."
    },
    "Bacterial Spot": {
        "cause": "Caused by Xanthomonas bacteria. Spread via water splash and tools.",
        "remedy": "Use copper-based bactericide and disease-free seeds."
    },
    "Leaf Mold": {
        "cause": "Fungal disease due to high humidity and poor air circulation.",
        "remedy": "Improve ventilation and apply recommended fungicides."
    },
    "Septoria Leaf Spot": {
        "cause": "Fungal infection spread through rain splash.",
        "remedy": "Remove affected leaves and spray fungicide."
    },
    "Powdery Mildew": {
        "cause": "Fungal disease common in warm and dry weather.",
        "remedy": "Apply sulfur-based fungicide and prune infected parts."
    },
    "Healthy": {
        "cause": "No disease detected.",
        "remedy": "Maintain proper watering, nutrients, and sunlight."
    }
}

# ================= IMAGE PREPROCESS =================
def preprocess_image(image):
    image = image.resize((128, 128))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# ================= EXTRACT PLANT & DISEASE =================
def extract_plant_disease(label):
    clean = label.replace("_", " ")

    if "brinjal" in clean.lower():
        plant = "Brinjal"
    elif "pepper" in clean.lower():
        plant = "Bell Pepper"
    elif "tomato" in clean.lower():
        plant = "Tomato"
    else:
        plant = "Unknown"

    if "healthy" in clean.lower() or "fresh" in clean.lower():
        disease = "Healthy"
    elif "cercospora" in clean.lower():
        disease = "Cercospora Leaf Spot"
    elif "bacterial" in clean.lower():
        disease = "Bacterial Spot"
    elif "leaf mold" in clean.lower():
        disease = "Leaf Mold"
    elif "septoria" in clean.lower():
        disease = "Septoria Leaf Spot"
    elif "powdery" in clean.lower():
        disease = "Powdery Mildew"
    else:
        disease = "Unknown Disease"

    return plant, disease

# ================= PREDICT API =================
@app.route("/predict", methods=["POST"])
def predict():
    print("🔥 /predict API HIT 🔥", flush=True)

    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = Image.open(request.files["file"]).convert("RGB")
    processed = preprocess_image(image)

    preds = model.predict(processed)
    index = int(np.argmax(preds))
    confidence = float(np.max(preds)) * 100

    label = CLASS_NAMES[index]
    plant, disease = extract_plant_disease(label)

    info = DISEASE_DETAILS.get(disease, {
        "cause": "Information not available.",
        "remedy": "Consult agricultural expert."
    })

    return jsonify({
        "plant": plant,
        "disease": disease,
        "confidence": f"{confidence:.2f}%",
        "cause": info["cause"],
        "remedy": info["remedy"]
    })

# ================= RUN SERVER =================
if __name__ == "__main__":
    app.run(debug=True)
