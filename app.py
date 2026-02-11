import streamlit as st
import easyocr
import json
import numpy as np
from PIL import Image

st.set_page_config(page_title="Smart Allergy Detection", page_icon="🥗")

reader = easyocr.Reader(['en'])

# Load data
with open("allergens.json", encoding="utf-8") as f:
    ALLERGENS = json.load(f)

with open("products.json", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

# -------------------------
# FUNCTIONS
# -------------------------

def extract_text_from_image(image):
    img = np.array(image.convert('RGB'))
    results = reader.readtext(img, detail=0)
    return " ".join(results)

def find_product(product_name):
    product_name = product_name.lower()
    for product in PRODUCTS:
        if product_name in product["product_name"].lower():
            return product
    return None

def detect_allergens(ingredients, selected_allergies):
    detected = []

    for ingredient in ingredients:
        ing_text = ingredient.lower()

        for allergy in selected_allergies:
            for term in ALLERGENS[allergy]["terms"]:
                if term.lower() in ing_text:
                    detected.append(allergy)

    return list(set(detected))


# -------------------------
# UI
# -------------------------

st.title("🥗 Smart Allergy Detection System")

mode = st.radio("Choose Mode", ["Scan Label", "Search Product"])

selected_allergies = st.multiselect(
    "Select Your Allergies",
    [k for k in ALLERGENS.keys() if ALLERGENS[k]["type"] == "direct_allergen"]
)

# -------------------------
# SCAN MODE
# -------------------------

if mode == "Scan Label":

    image = st.camera_input("Take photo of label")

    if image:
        img = Image.open(image)
        st.image(img, use_container_width=True)

        with st.spinner("Extracting text..."):
            text = extract_text_from_image(img)

        st.text_area("Extracted Text", text)

        if st.button("Check Allergies"):
            detected = detect_allergens([text], selected_allergies)

            if detected:
                st.error(f"❌ NOT SAFE – contains {', '.join(detected)}")
            else:
                st.success("✅ SAFE")

# -------------------------
# PRODUCT SEARCH MODE
# -------------------------

elif mode == "Search Product":

    product_name = st.text_input("Enter Product Name (or use phone voice keyboard 🎤)")

    if st.button("Check Product"):

        product = find_product(product_name)

        if not product:
            st.error("Product not found in database.")
        else:
            st.write("###", product["product_name"])
            st.write(", ".join(product["ingredients"]))

            detected = detect_allergens(product["ingredients"], selected_allergies)

            if detected:
                st.error(f"❌ NOT SAFE – contains {', '.join(detected)}")
            else:
                st.success("✅ SAFE")
