import pandas as pd

# Import the Google Generative AI library
# Make sure to install it first: pip install google-generativeai
import google.generativeai as genai
import os
import time  # To handle potential API rate limits

# --- Configuration ---
# Use raw string literal (r"...") or forward slashes for Windows paths
# CSV_FILE_PATH = r'C:/Users/12526/crime patrol/cid/excel/US_Cases 2.csv'  # <-- User provided path
# CSV_FILE_PATH = "uploads/uploaded.csv"

# WARNING: It is strongly advised NOT to hardcode API keys directly in the script.
# Consider using environment variables or a more secure method.
GEMINI_API_KEY = 'AIzaSyBUjbUaGtwCMZYH7W5ja7_9fjiF5D4ooPk'  # <-- User provided key
CASE_ID_COLUMN = 'Case ID'  # <-- User provided column name

# --- Configure Gemini API ---
try:
    if GEMINI_API_KEY == 'YOUR_GEMINI_API_KEY' or not GEMINI_API_KEY:
        raise ValueError("Gemini API key is not set. Please replace 'YOUR_GEMINI_API_KEY' or the placeholder key in the script with your actual key.")
    if not isinstance(GEMINI_API_KEY, str) or not GEMINI_API_KEY.startswith('AIzaSy'):
        print("Warning: The provided Gemini API key format appears unusual. Ensure it is correct.")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    print("Gemini API configured successfully.")
except ValueError as ve:
    print(f"Configuration Error: {ve}")
    exit()
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    if 'API key not valid' in str(e):
        print("The provided API key appears to be invalid. Please check and correct it.")
    else:
        print("Please ensure your API key is correct and the library is installed.")
    exit()

# --- Gemini API Call Functions ---
def call_gemini_for_summary(case_data_text):
    prompt = f"""
    Based on all the following crime case details, please provide a concise summary
    in one or two sentences. Focus on the key aspects like the type of crime,
    location (if available), and main circumstances. Maintain a professional tone.

    Case Details (All Columns):
    ---
    {case_data_text}
    ---
    Summary:
    """
    try:
        time.sleep(5)
        response = model.generate_content(prompt)
        if response.parts:
            return response.text.strip()
        else:
            prompt_feedback = getattr(response, 'prompt_feedback', None)
            block_reason = getattr(prompt_feedback, 'block_reason', 'Unknown') if prompt_feedback else 'Unknown'
            safety_ratings = getattr(prompt_feedback, 'safety_ratings', []) if prompt_feedback else []
            if block_reason != 'Unknown' and block_reason is not None:
                print(f"Warning: Summary generation potentially blocked. Reason: {block_reason}. Ratings: {safety_ratings}")
                return f"Summary generation blocked: {block_reason}"
            else:
                print(f"Warning: Received an empty response for summary.")
                candidates = getattr(response, 'candidates', [])
                if candidates and getattr(candidates[0], 'finish_reason', None) == 'SAFETY':
                    print("Reason: Safety block detected in candidate.")
                    return "Summary generation blocked due to safety concerns."
                return "No summary generated (empty response)."
    except Exception as e:
        print(f"Error calling Gemini API for summary: {e}")
        if 'permission denied' in str(e).lower() or 'authentication' in str(e).lower():
            print("Authentication error: Check your API key and permissions.")
        elif 'rate limit' in str(e).lower():
            print("Rate limit exceeded. Consider increasing the delay (time.sleep).")
        return f"Error generating summary: {e}"

def call_gemini_for_priority(case_data_text):
    prompt = f"""
    Objectively analyze all the following crime case details. Assign a priority level: High, Medium, or Low.
    Provide a detailed, professional justification for this priority level. Your reasoning should explicitly reference specific details or data points from the case information provided below that influenced your assessment. Consider factors such as:
    - Severity, violence, or nature of the crime described.
    - Urgency suggested by dates, timelines, or ongoing threats mentioned.
    - Indications of victim vulnerability (e.g., age, circumstances).
    - Status or nature of evidence mentioned (e.g., availability, type).
    - Any other factors objectively derived from the provided data.

    Format your response as follows:
    Priority Level: [High/Medium/Low]
    Reasoning: [Detailed justification referencing specific case details]

    Case Details (All Columns):
    ---
    {case_data_text}
    ---
    Priority Assessment:
    """
    try:
        time.sleep(10)
        response = model.generate_content(prompt)
        if response.parts:
            return response.text.strip()
        else:
            prompt_feedback = getattr(response, 'prompt_feedback', None)
            block_reason = getattr(prompt_feedback, 'block_reason', 'Unknown') if prompt_feedback else 'Unknown'
            safety_ratings = getattr(prompt_feedback, 'safety_ratings', []) if prompt_feedback else []
            if block_reason != 'Unknown' and block_reason is not None:
                print(f"Warning: Priority generation potentially blocked. Reason: {block_reason}. Ratings: {safety_ratings}")
                return f"Priority generation blocked: {block_reason}"
            else:
                print(f"Warning: Received an empty response for priority.")
                candidates = getattr(response, 'candidates', [])
                if candidates and getattr(candidates[0], 'finish_reason', None) == 'SAFETY':
                    print("Reason: Safety block detected in candidate.")
                    return "Priority generation blocked due to safety concerns."
                return "No priority generated (empty response)."
    except Exception as e:
        print(f"Error calling Gemini API for priority: {e}")
        if 'permission denied' in str(e).lower() or 'authentication' in str(e).lower():
            print("Authentication error: Check your API key and permissions.")
        elif 'rate limit' in str(e).lower():
            print("Rate limit exceeded. Consider increasing the delay (time.sleep).")
        return f"Error generating priority: {e}"

# --- Main Processing Logic ---
def process_crime_data(input_csv):
    try:
        try:
            df = pd.read_csv(input_csv, encoding='utf-8')
        except UnicodeDecodeError:
            print("UTF-8 decoding failed, trying latin1 encoding...")
            df = pd.read_csv(input_csv, encoding='latin1')
        df = df.fillna('').astype(str)
        print(f"Successfully read {len(df)} rows from {input_csv}")
        if CASE_ID_COLUMN not in df.columns:
            print(f"\nWarning: Column '{CASE_ID_COLUMN}' not found in the CSV.")
            print(f"Available columns are: {list(df.columns)}")
            print("Using row index as the case identifier instead.")
            use_index_as_id = True
        else:
            use_index_as_id = False
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at '{input_csv}'. Please ensure the path is correct.")
        return
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file '{input_csv}' is empty.")
        return
    except Exception as e:
        print(f"Error reading or processing CSV file: {e}")
        return

    print("\n--- Processing Cases ---")
    for index, row in df.iterrows():
        print(f"\nProcessing row {index + 1}/{len(df)}...")
        try:
            all_data_dict = row.to_dict()
            case_text = "\n".join([f"'{col}': '{val}'" for col, val in all_data_dict.items() if val.strip()])
            if not case_text:
                print(f"  Skipping row {index + 1} as it contains no data after filtering empty values.")
                continue
        except Exception as e:
            print(f"  Error formatting data for row {index + 1}: {e}. Skipping row.")
            continue

        if use_index_as_id:
            case_id = f"Row {index + 1}"
        else:
            case_id = row[CASE_ID_COLUMN]

        print(f"  Generating Summary for Case ID: {case_id}...")
        summary = call_gemini_for_summary(case_text)

        print(f"  Generating Priority for Case ID: {case_id}...")
        priority = call_gemini_for_priority(case_text)

        print("=" * 40)
        print(f"Case Identifier: {case_id}")
        print("=" * 40)
        print(f"\nSummary:")
        print(summary)
        print(f"\nPriority Assessment:")
        print(priority)
        print("-" * 40)

    print("\n--- Processing Complete ---")

# --- Run the script ---
if __name__ == "__main__":
    process_crime_data(CSV_FILE_PATH)
