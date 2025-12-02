from flask import Flask, render_template, request
import os
import json
import pandas as pd
from PIL import Image
import google.generativeai as genai

# ---------- FLASK APP ----------
app = Flask(__name__)

# ---------- CONFIG ----------
os.environ["GOOGLE_API_KEY"] = "AIzaSyB9mPE1BHaXFRFzviyLxMvZY7tevaj5TtM"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')


# ---------- YOUR ORIGINAL FUNCTION (UNTOUCHED) ----------
def extract_data_with_gemini(file_path):

    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        img = Image.open(file_path)

        prompt = """
        You are an expert Resume Parser. Analyze this resume image and extract the following details.
        Return ONLY a valid JSON object.

        - Name
        - Contact
        - Email
        - College
        - Degree
        - Department
        - Location
        - Passed Out

        If not found, set "Not specified".
        """

        try:
            response = model.generate_content([prompt, img])
            clean_text = response.text.strip()

            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            return json.loads(clean_text)

        except Exception as e:
            print("Gemini Error:", e)
            return None

    else:
        return {"Name": "File format not supported by Vision Parser (Use JPG/PNG)"}


# ---------------- FLASK ROUTES ----------------

@app.route("/")
def upload_page():
    return render_template("index.html")


@app.route("/process", methods=["POST"])
def process_files():
    if "files" not in request.files:
        return "No files uploaded"

    files = request.files.getlist("files")
    results = []
    excel_file = "Resume_Extracted_Data.xlsx"

    for f in files:
        filepath = f"uploads_{f.filename}"
        f.save(filepath)

        extracted = extract_data_with_gemini(filepath)
        if extracted:
            extracted["File Name"] = f.filename
            results.append(extracted)

    # ------- Convert results to DataFrame -------
    if results:
        new_df = pd.DataFrame(results)

        cols = ["Name", "Contact", "Email", "Degree", "Department",
                "College", "Location", "Passed Out", "File Name"]

        for c in cols:
            if c not in new_df.columns:
                new_df[c] = "Not specified"

        new_df = new_df[cols]

        # Append if file exists
        if os.path.exists(excel_file):
            old_df = pd.read_excel(excel_file)
            final_df = pd.concat([old_df, new_df], ignore_index=True)
        else:
            final_df = new_df

        final_df.to_excel(excel_file, index=False)

    return render_template("result.html", results=results)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
