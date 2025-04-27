import pandas as pd
import google.generativeai as genai
import time
 
# --- Configuration ---
GEMINI_API_KEY = 'AIzaSyCqB87H3hK8MzUMt_gonMRrvts3e-h221g'
 
# --- Configure Gemini API ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash-preview-04-17')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    exit()
 
# --- Gemini API Call Functions ---
 
def call_gemini_for_summary(case_data_text):
    prompt = f"""
    Based on the following crime case details, please provide a concise summary
    in one or two sentences. Focus on key aspects like the type of crime,
    location (if available), and the main circumstances. Maintain a professional tone.
 
    Case Details:
    ---
    {case_data_text}
    ---
 
    Write the Summary directly without adding extra headers.
    """
    try:
        time.sleep(5)
        response = model.generate_content(prompt)
        return response.text.strip() if response.parts else "No summary generated."
    except Exception as e:
        return f"Error generating summary: {e}"
 
def call_gemini_for_priority(case_data_text):
    prompt = f"""
    Analyze the following crime case details carefully.
 
    1. Assign a Priority Level: High, Medium, or Low.
    2. Provide a Reasoning Based on all the following crime case details, please provide a concise summary
    in one or two sentences. Focus on the key aspects like the type of crime,
    location (if available), and main circumstances. Maintain a professional tone.
    3. Format your answer strictly like this:
 
    Priority Level: <High/Medium/Low>
    Reasoning: <your explanation>
 
    Do not add any extra text.
 
    Case Details:
    ---
    {case_data_text}
    ---
    """
    try:
        time.sleep(10)
        response = model.generate_content(prompt)
        return response.text.strip() if response.parts else "No priority generated."
    except Exception as e:
        return f"Error generating priority: {e}"
 
# --- Main Processing Logic ---
 
def process_uploaded_file(file_path):
    try:
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='latin1')
 
        df = df.fillna('').astype(str)
 
    except Exception as e:
        print(f"Error reading or processing CSV file: {e}")
        return
 
    results = []  # To store results for frontend later
 
    for index, row in df.iterrows():
        try:
            all_data_dict = row.to_dict()
            case_text = "\n".join([f"{col}: {val}" for col, val in all_data_dict.items() if val.strip()])
            if not case_text:
                continue
        except:
            continue
 
        case_no = index + 1  # Numbering 1, 2, 3, 4...
 
        # Generate concise summary and priority reasoning
        summary = call_gemini_for_summary(case_text)
        priority = call_gemini_for_priority(case_text)
 
        result = {
            "Case_No": case_no,
            "Summary": summary,
            "Priority": priority
        }
        results.append(result)
 
    return results  # Return results instead of printing
 
 
# --- Example how you would call it ---
if __name__ == "__main__":
    # Example hardcoded path for now
    file_path = "uploads/uploaded.csv"
    output = process_uploaded_file(file_path)
 
    # You can print the results if needed
    for res in output:
        print(f"Case No. {res['Case_No']}")
        print(f"Summary: {res['Summary']}")
        print(f"{res['Priority']}")
        print("-" * 50)
 
 