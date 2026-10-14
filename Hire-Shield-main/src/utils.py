import re
import pdfplumber

def extract_resume_details(file):
    text = ""
    if file.filename.lower().endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
    elif file.filename.lower().endswith('.txt'):
        text = file.read().decode('utf-8')
    else:
        raise ValueError("Please upload PDF or TXT.")
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = ' '.join(text.split())
    details = {}
    patterns = {
        '10th': [r'class\s*x[,\s]*.*?percentage[:\s]*(\d{1,3}(?:\.\d{1,2})?)'],
        '12th': [r'class\s*xii[,\s]*.*?percentage[:\s]*(\d{1,3}(?:\.\d{1,2})?)'],
        'CGPA': [r'cgpa[:\s]*(\d+(?:\.\d{1,2})?)'],
    }
    for key, regex_list in patterns.items():
        for regex in regex_list:
            m = re.search(regex, text, re.I)
            if m:
                details[key] = float(m.group(1))
                break
    return details
