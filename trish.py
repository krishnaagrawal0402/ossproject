from flask import Flask, request, render_template
import os
import hashlib
import requests

app = Flask(__name__)

SERP_API_KEY = '87cbc9490b7c6897e79387fd7879e4bfba8115abd0bdb2db1cf860b4b28d4bb9'

plagiarized_files = []

def calculate_code_hash(file_path):
    with open(file_path, "r") as f:
        code = f.read()
    code_hash = hashlib.md5(code.encode()).hexdigest()
    return code_hash

def compare_codes(directory):
    global plagiarized_files
    code_hashes = {}
    plagiarized_files = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):  
                file_path = os.path.join(root, file)
                code_hash = calculate_code_hash(file_path)
                if code_hash in code_hashes:
                    code_hashes[code_hash].append({"file_path": file_path, "code": open(file_path, "r").read()})
                else:
                    code_hashes[code_hash] = [{"file_path": file_path, "code": open(file_path, "r").read()}]

    plagiarized_files = [files for files in code_hashes.values() if len(files) > 1]
    return plagiarized_files

def generate_anti_plagiarism_code(code):
    """
    This function returns a predefined code instead of generating it using the SERP API.
    """
    predefined_code = '''
    import pandas as pd
import requests
from dotenv import load_dotenv
import os
import streamlit as st

# Load the SERP API key from environment variables
load_dotenv()
SERP_API_KEY = os.getenv('SERP_API_KEY')

# Load the hospital data from CSV file
hospitals_data = pd.read_csv('Help Files/HospitalsInIndia.csv')

# Function to fetch disease info from SERP API based on symptoms
def fetch_disease_info(symptoms):
    api_url = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&q=disease info based on symptoms: {symptoms}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        disease_info = response.json().get('organic_results', [{}])[0].get('snippet', 'No information found.')
        if 'COVID-19' in disease_info:
            disease_info = "COVID-19: A viral disease caused by SARS-CoV-2. Symptoms include fever, cough, and difficulty breathing."
        return disease_info
    except requests.exceptions.RequestException as e:
        return f"Error fetching disease data: {str(e)}"

# Function to find hospitals near the user's location
def find_nearby_hospitals(city):
    return hospitals_data[hospitals_data['City'].str.contains(city, case=False, na=False)]['Hospital'].tolist()

# Function to get common medicines based on symptoms
def get_medicines_for_symptoms(symptoms):
    api_url = f"https://serpapi.com/search.json?api_key={SERP_API_KEY}&q=common medicines for {symptoms}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json().get('organic_results', [{}])[0].get('snippet', 'No medicine info found.')
    except requests.exceptions.RequestException as e:
        return f"Error fetching medicines: {str(e)}"

# Initialize Streamlit App
st.title("Health and Disease Information Portal")

# Display a logo or image
logo_path = "Help Files/Logo.jpg"
st.image(logo_path, width=150)

# Sidebar for user input
st.sidebar.header("Symptom and Location Input")

# Combine symptoms and custom input into one string
selected_symptoms = [symptom for symptom in ["Fever", "Cough", "Headache", "Nausea", "Fatigue", "Body Pain", "Chills"] if st.sidebar.checkbox(symptom)]
custom_symptoms_input = st.sidebar.text_input("Custom symptoms (optional)")
symptoms_str = ', '.join(selected_symptoms + [custom_symptoms_input]).strip()

location_input = st.sidebar.text_input("Enter your location (city name)", '')

# Button to trigger information fetching
if st.sidebar.button('Get Health Info'):
    if symptoms_str:
        # Fetch and display disease information
        st.subheader("Disease Information")
        st.write(fetch_disease_info(symptoms_str))

        # Fetch and display nearby hospitals if location is provided
        if location_input:
            st.subheader("Nearby Hospitals")
            hospitals = find_nearby_hospitals(location_input)
            if hospitals:
                st.write("Hospitals found near you:")
                st.write(hospitals)
            else:
                st.write("No hospitals found in your location.")

        # Fetch and display recommended medicines for the symptoms
        st.subheader("Recommended Medicines")
        st.write(get_medicines_for_symptoms(symptoms_str))
    else:
        st.warning("Please enter at least one symptom.")
else:
    st.info("Select symptoms and your location, then click 'Get Health Info'.")
'''
    return predefined_code

@app.route("/", methods=["GET", "POST"])
def index():
    global plagiarized_files

    if request.method == "POST":
        directory = request.form["directory"]
        plagiarized_files = compare_codes(directory)

    return render_template("index.html", plagiarized_files=[file[0]["file_path"] for file in plagiarized_files])

@app.route("/generate", methods=["POST"])
def generate_anti_plagiarism_files():
    output_dir = "E:/trish-output"  
    updated_files = []

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for files in plagiarized_files:
        for file in files:
            original_code = file["code"]
            
            anti_plagiarized_code = generate_anti_plagiarism_code(original_code)

            new_file_path = os.path.join(output_dir, os.path.basename(file["file_path"]).replace('.py', '_anti_plagiarized.py'))
            with open(new_file_path, 'w') as f:
                f.write(anti_plagiarized_code)

            updated_files.append({
                'original_file': file["file_path"],
                'new_file': new_file_path,
                'original_code': original_code,
                'anti_plagiarized_code': anti_plagiarized_code
            })

    return render_template("index.html", updated_files=updated_files)

if __name__ == "__main__":
    app.run(debug=True)