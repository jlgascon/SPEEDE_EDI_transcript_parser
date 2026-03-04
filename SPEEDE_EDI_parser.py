import re
import pandas as pd

def parse_edi_transcripts(text_content):
    """
    Parses a raw SPEEDE/EDI transcript text file to extract student metadata
    and classify the overall transcript status.
    """
    extracted_data = []
    
    # Step 1: Tokenize the raw text into individual student transcript blocks.
    # We split based on the "Page 1" header which denotes the start of a new transcript record.
    # (Note: '\s+' handles variable spacing in the raw text)
    transcript_blocks = re.split(r'SPEEDE Transcript\s+Page\s+1', text_content)
    
    # Skip the first split chunk as it contains preamble prior to the first actual record
    for block in transcript_blocks[1:]: 
        
        # --- 2. Extract Routing Information ---
        sent_by_match = re.search(r'Sent by:\s+([^\n]+)', block)
        sent_by = sent_by_match.group(1).strip() if sent_by_match else "Unknown"
        
        # --- 3. Block-Restricted Parsing for Student Information ---
        # Isolate the specific Student Information block to safely extract IDs and Names

        # I WILL DEPRECIATE THIS, JUST A FIRST ROUND , doesnt give us the correct header drill down to create the right keyvalue pairs later
        # Also need to double check that when we append to dictionary, we keep each record line straight (when students have multiple transcripts such that Agency ID is 
        # successfully extracted - keep the drill down clean

        
        student_info_match = re.search(
            r'----------------------------- Student Information ------------------------------(.*?)-----------------------------', 
            block, 
            re.DOTALL
        )
        
        student_name = "Unknown"
        agency_id = "Null"
        
        if student_info_match:
            student_info_text = student_info_match.group(1)
            
            # Extract Name of Record
            name_match = re.search(r'Name of Record:\s+([^\n]+)', student_info_text)
            if name_match:
                student_name = name_match.group(1).strip()
                
            # Extract Agency's Student Number
            # Using \d+ ensures we only capture the integer ID and stop before any 
            # trailing noisy string data (like "State Student ID Number") on the same line.
            id_match = re.search(r"Agency's Student Number:\s*(\d+)", student_info_text)
            if id_match:
                agency_id = id_match.group(1)
        
        # --- 4. Transcript Status Classification Engine ---
        status = "Unknown"
        
        # Rule A: Check for official completion/graduation
        # We need to add date extraction and validation
        if "Academic Degree Information" in block or "Degree Awarded" in block:
            status = "Complete"
            
        else:
            # Rule B: Check for active/in-progress indicators
            # This handles institutional variance ('--', 'INP', 'CIP', or 'Registered' flags)
            in_progress_patterns = [r'\s--\s', r'\sINP\s', r'\sCIP\s', r'REG STATUS Registered']
            
            is_in_progress = any(re.search(pattern, block) for pattern in in_progress_patterns)
            
            if is_in_progress:
                status = "In-Progress"
            else:
                # Rule C: If not complete and not actively in-progress, student has withdrawn/stopped
                status = "Incomplete / Withdrawn"
                
        # --- 5. Append Record ---
        extracted_data.append({
            "Student Name": student_name,
            "Agency's Student Number": agency_id,
            "Sent by Institution": sent_by,
            "Transcript Status": status
        })
        
    # Return as a structured Pandas DataFrame for easy export or database insertion
    return pd.DataFrame(extracted_data)

# ==========================================
# Execution Example
# ==========================================
if __name__ == "__main__":
    # Load the raw EDI export file
    file_path = 'C:\yourfilepath'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_text = file.read()
            
        # Process the text
        results_df = parse_edi_transcripts(raw_text)
        
        # Output the summary table
        print(results_df.to_markdown(index=False))
        
        # Optional: Export to CSV for later database ingestion
        # results_df.to_csv('classified_transcripts.csv', index=False)
        # COULD ALSO ADD SQL or WHATEVER needed by downstream report production (ie INFORMER)
        
    except FileNotFoundError:
        print(f"Error: Could not locate {file_path}. Please ensure the file is in the correct directory.")
