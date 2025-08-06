from flask import Flask, render_template, request, send_file
import pandas as pd
import google.generativeai as genai
import time
import os

app = Flask(__name__)

# === Configure Gemini API Key ===
genai.configure(api_key="AIzaSyCqXNsHEsxlNXoW7JbuA8X4SuWJzRzjf1s")

# === Function to Get Founders ===
def get_founder(company_name):
    prompt = f"""
    Who is/are the founder(s) of the company named '{company_name}'?
    Please only return the actual founder names (comma-separated) and nothing else.
    Make sure they are correctly associated with this company.
    """
    try:
        model = genai.GenerativeModel("gemini-2.0-flash-lite")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# === Flask Routes ===
@app.route('/', methods=['GET', 'POST'])
def index():
    results = None
    error = None
    file_download = None

    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file uploaded."
            return render_template('index.html', error=error)

        file = request.files['file']
        if file.filename == '':
            error = "Please select a CSV file."
            return render_template('index.html', error=error)

        try:
            df = pd.read_csv(file)

            if "Company" not in df.columns:
                error = "CSV must contain a column named 'Company'."
                return render_template('index.html', error=error)

            founders = []
            for company in df["Company"]:
                founder = get_founder(company)
                founders.append(founder)
                time.sleep(1)

            df["Founder(s)"] = founders
            output_path = "company_with_founders.csv"
            df.to_csv(output_path, index=False)
            file_download = output_path
            results = df.to_dict(orient="records")

        except Exception as e:
            error = f"Something went wrong: {e}"

    return render_template('index.html', results=results, error=error, file_download=file_download)

@app.route('/download')
def download_file():
    path = "company_with_founders.csv"
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
