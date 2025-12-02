

import os
import json
import pandas as pd
from PIL import Image
from google.colab import files

# --- CONFIGURATION ---
# 1. Get your free key here: https://aistudio.google.com/
# 2. Paste it inside the quotes below
os.environ["GOOGLE_API_KEY"] = "AIzaSyAzuLdK4K9XOJbhPtfVzAtVQuQQGN8kPNw"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Initialize the Gemini 1.5 Flash model (Fast, Cheap, and Great at Vision)
model = genai.GenerativeModel('gemini-2.5-flash')

def extract_data_with_gemini(file_path):
    """
    Sends the resume image to Gemini Flash and asks for structured JSON data.
    """

    # 1. Handle Image Files
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        img = Image.open(file_path)

        # The Prompt: Instructions for the AI
        prompt = """
        You are an expert Resume Parser. Analyze this resume image and extract the following details.
        Return ONLY a valid JSON object. Do not write markdown formatting (like ```json).

        Fields to extract:
        - Name (Find the candidate's full name)
        - Contact (Phone number)
        - Email
        - College (Most recent or major college/university)
        - Degree (e.g., B.Tech, B.E, BCA)
        - Department (e.g., Computer Science, Information Technology)
        - Location (City or State mentioned in address)
        - Passed Out (Year of graduation. Check for 'Batch', 'Expected', or 'Ending Date')

        If a value is not found, use "Not specified".
        """

        try:
            # Generate content using Gemini Vision
            response = model.generate_content([prompt, img])

            # Clean up response (remove markdown if AI adds it)
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]

            return json.loads(clean_text)

        except Exception as e:
            print(f"Error processing with Gemini: {e}")
            return None

    # 2. Handle Non-Image files (Optional fallback)
    else:
        return {"Name": "File format not supported by Vision Parser (Use JPG/PNG)"}

# Assuming 'pd', 'os', 'files', 'display', and 'extract_data_with_gemini' are defined.

uploaded = files.upload()
results = []
final_df = pd.DataFrame() # Initialize final_df here

print("\n--- Starting AI Extraction ---")

for filename in uploaded.keys():
    print(f"Processing: {filename}...")

    # Call the AI function
    extracted_data = extract_data_with_gemini(filename)

    if extracted_data:
        extracted_data["File Name"] = filename
        results.append(extracted_data)
    else:
        print(f"Failed to extract data for {filename}")

# Convert new results to DataFrame
if results:
    new_df = pd.DataFrame(results)

    # Reorder columns and handle missing columns
    cols = ["Name", "Contact", "Email", "Degree", "Department", "College", "Location", "Passed Out", "File Name"]
    for c in cols:
        if c not in new_df.columns:
            new_df[c] = "Not specified"
    new_df = new_df[cols]

    # Logic to Append Data to Existing File
    excel_file = "Resume_Extracted_Data.xlsx"

    if os.path.exists(excel_file):
        existing_df = pd.read_excel(excel_file)
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        print("\n--- Data Appended to Existing File. ---")
    else:
        final_df = new_df
        print("\n--- New Data Extracted and Prepared. ---")

    print("\nFinal Consolidated Data:")
    display(final_df) # Displaying the final consolidated DataFrame
else:
    print("No new data extracted. Final DataFrame creation skipped.")

# Assuming 'final_df' is defined in the previous block.
import os
from google.colab import files
import pandas as pd  # Required for type check

# Check if final_df exists and is not empty
if 'final_df' in locals() and isinstance(final_df, pd.DataFrame) and not final_df.empty:

    print("🔎 Checking for duplicate rows...")

    # 🔍 Find duplicates based on Name, Contact & Email
    duplicate_rows = final_df[final_df.duplicated(subset=["Contact", "Email"], keep=False)]
    print(f"⚠️ Total Duplicates Found: {len(duplicate_rows)}")

    # 🧹 Remove duplicates (keep only first instance)
    final_df = final_df.drop_duplicates(subset=["Contact", "Email"], keep="first")

    print(f"✔ Duplicates Removed. Final Row Count: {len(final_df)}")

    # 🌟 Save cleaned data to JSON
    json_file = "Resume_Extracted_Data_AI.json"
    final_df.to_json(json_file, orient='records', indent=4)

    print("\n--- SUCCESS! Clean Data Saved & Download Triggered ---")
    print(f"📁 File saved as: {json_file}")

    files.download(json_file)   # Trigger download

else:
    print("❌ No valid data available. Please check previous steps.")

# Assuming 'final_df' is defined in the previous block.
# Ensure 'os' and 'files' are imported from the setup cells.
import os
from google.colab import files
import pandas as pd # Required for the 'final_df' type check

# Check if final_df was successfully created and is not empty
if 'final_df' in locals() and isinstance(final_df, pd.DataFrame) and not final_df.empty:

    # 🌟 CHANGE: Use .json extension and .to_json() method
    json_file = "Resume_Extracted_Data_AI.json"

    # Save the final consolidated DataFrame to JSON format.
    # The 'orient' parameter formats the JSON as a list of dictionaries (one dictionary per resume).
    final_df.to_json(json_file, orient='records', indent=4)

    print("\n--- SUCCESS! Data Saved and Download Triggered ---")
    print(f"File saved as {json_file}")

    # Trigger download of the JSON file
    files.download(json_file)
else:
    print("No data available to save or download. Check Block 1 output.")
