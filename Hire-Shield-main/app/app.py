import os
import sys
import json
import re
import joblib
import pdfplumber
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from bias_detection import detect_bias


app = Flask(__name__)
app.secret_key = 'your-secret-key'

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='hireshield.team@gmail.com',
    MAIL_PASSWORD='miim hnkd bqvb muvh',
    MAIL_DEFAULT_SENDER='hireshield.team@gmail.com',
)

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)
DATA_FILE = 'applicants.json'

def load_applicants():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_applicants(applicants):
    with open(DATA_FILE, 'w') as f:
        json.dump(applicants, f, indent=2)

def find_applicant(email):
    applicants = load_applicants()
    for applicant in applicants:
        if applicant['email'] == email:
            return applicant
    return None

import base64

@app.route('/applicant_access')
def applicant_access():
    return render_template('applicant_access.html')


@app.route('/applicant_signup', methods=['GET', 'POST'])
def applicant_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')  # Remember to hash passwords for production
        phone = request.form.get('phone_number', '').strip()
        college = request.form.get('college', '').strip()
        terms = request.form.get('terms')

        if not terms:
            flash('You must accept the terms and privacy policy.', 'error')
            return render_template('applicant_signup.html')

        applicants = load_applicants()
        if any(a['email'].lower() == email.lower() for a in applicants):
            flash('Email already registered.', 'error')
            return render_template('applicant_signup.html')

        new_applicant = {
            'id': len(applicants) + 1,
            'full_name': full_name,
            'email': email,
            'password': password,
            'phone_number': phone,
            'college': college,
            'active': True
        }

        applicants.append(new_applicant)
        save_applicants(applicants)

        # Embed logo for email
        with open('static/images/Hire-Shield-Logo.png', 'rb') as image_file:
            encoded_logo = base64.b64encode(image_file.read()).decode('utf-8')

        msg = Message('Welcome to Hire Shield – Your Campus Hiring Journey Begins!', recipients=[email])

        # HTML email with embedded base64 logo
        msg.html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700&family=Open+Sans&display=swap');

  body {{
    background: linear-gradient(135deg, #121b28 0%, #23335a 100%);
    margin: 0; padding: 40px 20px;
    font-family: 'Open Sans', Arial, sans-serif;
    color: #e4ebff;
    text-align: center;
  }}
  .container {{
    max-width: 520px;
    margin: auto;
    background: linear-gradient(145deg, rgba(33,54,92,0.9), rgba(12,29,56,0.9));
    padding: 36px 40px;
    border-radius: 1.6rem;
    box-shadow: 0 0 68px #3f7ffbaa;
    border: 1.5px solid #4a78f022;
    position: relative;
    overflow: hidden;
  }}

  /* subtle moving background gradient animation */
  .container::before {{
    content: '';
    position: absolute;
    top: -25%;
    left: -50%;
    width: 200%;
    height: 150%;
    background: linear-gradient(45deg, #36ccf9 0%, #8f4afb 100%);
    filter: blur(118px);
    animation: moveGradient 10s linear infinite alternate;
    opacity: 0.38;
    z-index: 0;
  }}

  @keyframes moveGradient {{
    0% {{ transform: translateX(0) translateY(0) rotate(0deg); }}
    100% {{ transform: translateX(20%) translateY(10%) rotate(360deg); }}
  }}

  h1 {{
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    font-size: 2.8rem;
    color: #36ccf9;
    text-shadow:
      0 0 7px #36ccf9,
      0 0 14px #8f4afb60,
      0 0 22px #36ccf980;
    position: relative;
    z-index: 1;
    margin-bottom: 1rem;
  }}
  p {{
    font-size: 1.15rem;
    line-height: 1.6;
    margin: 1em 0;
    position: relative;
    z-index: 1;
  }}
  .signature {{
    font-style: italic;
    font-size: 1rem;
    color: #a3b9ffcc;
    margin-top: 1.5rem;
    position: relative;
    z-index: 1;
  }}
  .footer {{
    font-size: 0.85rem;
    color: #7c91ccaa;
    margin-top: 3rem;
    letter-spacing: 0.04em;
    position: relative;
    z-index: 1;
    user-select:none;
  }}
</style>
</head>
<body>
  <div class="container">
    <h1>Welcome to Hire Shield!</h1>
    <p>Hi <strong>{full_name}</strong>,</p>
    <p>Thank you for registering as an applicant on <b>Hire Shield</b>, the cutting-edge platform for bias-free, AI-driven campus hiring.</p>
    <p>We're excited to have you with us and look forward to supporting your career journey!</p>
    <p class="signature">— The Hire Shield Team</p>
    <p class="footer">If you did not register, please disregard this message.</p>
  </div>
</body>
</html>
"""

        mail.send(msg)

        flash('Registration successful! A welcome email has been sent.', 'success')
        return render_template('applicant_signup.html')

    return render_template('applicant_signup.html')





@app.route('/applicant_login', methods=['GET', 'POST'])
def applicant_login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        applicants = load_applicants()
        
        user = next((a for a in applicants if a['email'].lower() == email.lower() and a['password'] == password), None)
        
        if user:
            # Save session or mark logged in as needed
            # For example:
            session['applicant_logged_in'] = True
            session['applicant_email'] = email
            return redirect(url_for('applicant_method'))
        else:
            error = "Invalid email or password."
            
    return render_template('applicant_login.html', error=error)

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirm-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or expired.', 'error')
        return redirect(url_for('applicant_signup'))

    applicants = load_applicants()
    for applicant in applicants:
        if applicant['email'] == email:
            applicant['active'] = True
            save_applicants(applicants)
            flash('Your email is verified! You can now login.', 'success')
            return redirect(url_for('applicant_login'))

    flash('Email not found.', 'error')
    return redirect(url_for('applicant_signup'))

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
src_dir = os.path.join(root_dir, 'src')

from datetime import datetime

def log_prediction(applicant_features, predicted_label, review_status="pending", resume_file=None):
    log_path = os.path.join(root_dir, 'data', 'review_logs.json')
    log = {
        "features": applicant_features,
        "prediction": predicted_label,
        "review_status": review_status,
        "timestamp": datetime.now().isoformat(),
        "resume_file": resume_file,
        "review_label": None,
        "review_note": None
    }
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            try:
                logs = json.load(f)
            except:
                logs = []
    logs.append(log)
    with open(log_path, 'w') as f:
        json.dump(logs, f, indent=2)

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from bias_detection_placement import detect_bias_placement as detect_bias
from visualization_placement import plot_placement_bias as plot_bias


model_path = os.path.join(root_dir, 'models', 'placement_model_mitigated.pkl')
test_data_path = os.path.join(root_dir, 'data', 'processed', 'test_sample_mitigated.csv')
RECRUITER_FILE = os.path.join(current_dir, 'recruiters.json')

def load_recruiters():
    try:
        if not os.path.exists(RECRUITER_FILE):
            return []
        with open(RECRUITER_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except Exception:
        return []

def save_recruiters(recruiters):
    with open(RECRUITER_FILE, 'w') as f:
        json.dump(recruiters, f, indent=2)

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/role_select')
def role_select():
    return render_template('role_select.html')

@app.route('/recruiter_login', methods=['GET', 'POST'])
def recruiter_login():
    error = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        recruiters = load_recruiters()
        user = next((r for r in recruiters if r['username'] == username and r['password'] == password), None)
        if user:
            session['logged_in'] = True
            session['username'] = username
            session['name'] = user['name']
            session['company'] = user['company']
            session['email'] = user['email']
            return redirect(url_for('review_predictions'))
        else:
            error = "Invalid credentials."
    return render_template('recruiter_login.html', error=error)

@app.route('/recruiter_signup', methods=['GET', 'POST'])
def recruiter_signup():
    error = ""
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        name = request.form['name'].strip()
        company = request.form['company'].strip()
        email = request.form['email'].strip()
        recruiters = load_recruiters()

        if not re.match("^[A-Za-z0-9_]{4,20}$", username):
            error = "Invalid username."
        elif len(password) < 8:
            error = "Password too short."
        elif not name or not company:
            error = "Name and company are required."
        elif not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            error = "Invalid email."
        elif any(r['username'] == username for r in recruiters):
            error = "Username exists."
        elif any(r['email'] == email for r in recruiters):
            error = "Email exists."
        else:
            recruiters.append({
                'username': username,
                'password': password,
                'name': name,
                'company': company,
                'email': email
            })
            save_recruiters(recruiters)
            return redirect(url_for('recruiter_login'))
    return render_template('recruiter_signup.html', error=error)


@app.route('/dashboard')
def dashboard():
    df = pd.read_csv('Placement_Data_Updated.csv')

    # KPIs
    total_candidates = len(df)
    total_placed = (df['Status'] == 'Placed').sum()
    total_internships = (df['Internship'] == 'Yes').sum()  # adjust as needed if values are string/int
    total_specialisations = df['Specialisation'].nunique()
    avg_cgpa = round(df['CGPA'].mean(), 2)

    # Gender charts
    gender_counts = df['Gender'].value_counts().to_dict()
    gender_pie = {'M': gender_counts.get('M', 0), 'F': gender_counts.get('F', 0)}

    # Salary by Gender
    salary_avg_by_gender = df.groupby('Gender')['Salary'].mean().to_dict()
    salary_labels = ['F', 'M']
    salary_avgs = [
        round(salary_avg_by_gender.get(label, 0), 2) for label in salary_labels
    ]

    # Specialisation by gender (line chart)
    spec_labels = list(df['Specialisation'].unique())
    spec_salary_pivot = df.pivot_table(
        values='Salary', index='Specialisation', columns='Gender', aggfunc='mean'
    ).fillna(0)
    spec_f = [
        round(spec_salary_pivot.at[spec, 'F'], 2) if 'F' in spec_salary_pivot.columns else 0 for spec in spec_labels
    ]
    spec_m = [
        round(spec_salary_pivot.at[spec, 'M'], 2) if 'M' in spec_salary_pivot.columns else 0 for spec in spec_labels
    ]

    # Gender by Internship (bar chart)
    g_intern_group = df.groupby(['Internship', 'Gender']).size().unstack(fill_value=0)
    g_intern_x = list(g_intern_group.index)
    g_intern_f = g_intern_group.get('F', pd.Series(0, index=g_intern_group.index)).tolist()
    g_intern_m = g_intern_group.get('M', pd.Series(0, index=g_intern_group.index)).tolist()
    g_intern = {'x': g_intern_x, 'F': g_intern_f, 'M': g_intern_m}

    # Average Aptitude Score by Board (simpler last chart)
    avg_aptitude_by_board = df.groupby('Board')['Aptitude_score'].mean().round(2).to_dict()
    board_labels = list(avg_aptitude_by_board.keys())
    board_aptitudes = list(avg_aptitude_by_board.values())

    return render_template(
        'dashboard.html',
        total_candidates=total_candidates,
        total_placed=total_placed,
        total_internships=total_internships,
        total_specialisations=total_specialisations,
        avg_cgpa=avg_cgpa,
        gender_pie=gender_pie,
        salary_labels=salary_labels,
        salary_avgs=salary_avgs,
        specialisations=spec_labels,
        spec_f=spec_f,
        spec_m=spec_m,
        g_intern=g_intern,
        board_labels=board_labels,
        board_aptitudes=board_aptitudes
    )





@app.route('/applicant_method')
def applicant_method():
    return render_template('applicant_method.html')

@app.route('/choose_input', methods=['POST'])
def choose_input():
    method = request.form.get('method')
    if method == "resume":
        return redirect(url_for('upload_resume'))
    else:
        return redirect(url_for('manual_details'))

@app.route('/manual_details', methods=['GET', 'POST'])
def manual_details():
    if request.method == 'POST':
        details = {
            '10th': float(request.form['tenth_score']),
            '12th': float(request.form['twelfth_score']),
            'CGPA': float(request.form['cgpa']),
            'Aptitude_score': float(request.form['aptitude_score']),
            'Program_encoded': int(request.form['program']),
            'Internship_encoded': int(request.form['internship']),
            'Specialisation_encoded': int(request.form['specialisation'])
    }
        return redirect(url_for('applicant_result', **details))
    return render_template('manual_details.html')

def extract_resume_details(file):
    text = ""
    if file.filename.lower().endswith('.pdf'):
        with pdfplumber.open(file) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
    elif file.filename.lower().endswith('.txt'):
        text = file.read().decode('utf-8')
    else:
        raise ValueError("Unsupported file format; please upload PDF or TXT.")
    
    text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    text = ' '.join(text.split())

    details = {}

    # More flexible regex patterns with multiple variations
    patterns = {
        '10th': [
            r'class\s*x[,\s]*(?:cbse|state|board)?[:\s]*percentage[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'class\s*x\s*(?:cbse|state|board)?[^0-9]*percentage[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'10th\s*(?:grade|marks|percentage|score|%)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'tenth\s*(?:grade|marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'class\s*x\s*(?:marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'x\s*board\s*(?:marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'secondary\s*(?:marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)'
        ],
        '12th': [
            r'class\s*xi+i?[,\s]*(?:cbse|state|board)?[:\s]*percentage[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'class\s*xii\s*(?:cbse|state|board)?[^0-9]*percentage[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'12th\s*(?:grade|marks|percentage|score|%)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'twelfth\s*(?:grade|marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'class\s*xii\s*(?:marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'xii\s*board\s*(?:marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'senior\s*secondary\s*(?:marks|percentage)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)'
        ],
        'CGPA': [
            r'cgpa[:\s]*(\d+(?:\.\d{1,2})?)',
            r'cumulative\s*gpa[:\s]*(\d+(?:\.\d{1,2})?)',
            r'gpa[:\s]*(\d+(?:\.\d{1,2})?)',
            r'aggregate[:\s]*(\d+(?:\.\d{1,2})?)',
            r'overall\s*(?:gpa|cgpa)[:\s]*(\d+(?:\.\d{1,2})?)'
        ],
        'Aptitude_score': [
            r'aptitude\s*(?:score|test|marks)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'apt\s*(?:score|marks)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'reasoning\s*(?:score|marks)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)',
            r'quantitative\s*(?:score|marks)?[:\s]*(\d{1,3}(?:\.\d{1,2})?)'
        ],
        'Gender_encoded': [
            r'gender\s*[:\s]*(male|female|m|f|m\.?|f\.?)',
            r'sex\s*[:\s]*(male|female|m|f)',
            r'(?:mr|ms|mrs|dr\.?)\s+',
        ],
        'Board_encoded': [
            r'(?:class\s*x+i*i?[,\s]*)(cbse|state|icse|isc)',
            r'board\s*[:\s]*(central|state|icse|cbse|isc)',
            r'school\s*board[:\s]*(central|state|icse|cbse|isc)',
        ],
        'Program_encoded': [
            r'(?:bachelor\s*of\s*)?technology\s*in\s*(?:computer\s*science|b\.?tech|btech)',
            r'(?:program|course|degree)\s*[:\s]*(b\.?tech|btech|b\.?ca|bca|bachelor)',
            r'(?:pursuing|studied)\s*(b\.?tech|btech|b\.?ca|bca)',
        ],
        'Internship_encoded': [
            r'internship\s*[:\s]*(yes|no|completed|done|have)',
            r'(?:completed|undergone)\s*internship',
            r'internship\s*experience\s*[:\s]*(yes|no)'
        ],
        'Specialisation_encoded': [
            r'(?:computer\s*science|data\s*science|specialisation?)\s*\[?([^\]]*)\]?',
            r'specialisation?[:\s]*(ai/ml|machine\s*learning|artificial\s*intelligence|cs/it|computer\s*science|data\s*analytics|data\s*science|computer\s*applications)',
            r'(?:major|focus)[:\s]*(ai/ml|machine\s*learning|artificial\s*intelligence|cs/it|computer\s*science|data\s*analytics|data\s*science|computer\s*applications)'
        ]
    }

    encoding_maps = {
        'Gender_encoded': {'male': 1, 'm': 1, 'mr': 1, 'female': 0, 'f': 0, 'ms': 0, 'mrs': 0, 'other': 2},
        'Board_encoded': {'central': 0, 'cbse': 0, 'state': 2, 'icse': 1, 'isc': 1},
        'Program_encoded': {'bca': 0, 'b.ca': 0, 'btech': 1, 'b.tech': 1, 'bachelor': 1, 'engineering': 1, 'computer science': 1, 'data science': 1},
        'Internship_encoded': {'yes': 1, 'completed': 1, 'done': 1, 'have': 1, 'no': 0},
        'Specialisation_encoded': {
            'ai/ml': 0,
            'machine learning': 0,
            'artificial intelligence': 0,
            'computer applications': 1,
            'cs/it': 2,
            'computer science': 2,
            'data science': 4,
            'data analytics': 3
        }
    }

    for key, regex_list in patterns.items():
        found_value = None
        for regex in regex_list:
            matches = re.findall(regex, text, re.IGNORECASE)
            if matches:
                # Handle both single and grouped matches
                val = matches[0] if isinstance(matches[0], str) else matches[0][0]
                found_value = val.strip()
                break
        
        if found_value is not None:
            if key in encoding_maps:
                encoded_val = encoding_maps[key].get(found_value.lower(), None)
                if encoded_val is not None:
                    details[key] = encoded_val
            else:
                try:
                    details[key] = float(found_value)
                except ValueError:
                    pass
        
    return details


def calculate_segmented_score(features):
    score = 0

    # Gender (Female gets base point, Male slightly higher)

    # 10th Grade Percentage
    if features['10th'] >= 90:
        score += 5
    elif features['10th'] >= 80:
        score += 4
    elif features['10th'] >= 70:
        score += 3
    else:
        score += 1

    # 12th Grade Percentage
    if features['12th'] >= 90:
        score += 5
    elif features['12th'] >= 80:
        score += 4
    elif features['12th'] >= 70:
        score += 3
    else:
        score += 1

    # Board (CBSE and ICSE valued slightly higher than State)
    # CGPA tiers
    if features['CGPA'] >= 9.0:
        score += 5
    elif features['CGPA'] >= 8.0:
        score += 4
    elif features['CGPA'] >= 6.5:
        score += 3
    else:
        score += 1

    # Program (BTech valued slightly higher)
    score += 5 if features['Program_encoded'] == 1 else 3

    # Internship
    score += 4 if features['Internship_encoded'] == 1 else 1

    # Aptitude Score
    if features['Aptitude_score'] >= 90:
        score += 5
    elif features['Aptitude_score'] >= 75:
        score += 4
    elif features['Aptitude_score'] >= 60:
        score += 3
    else:
        score += 1

    # Specialisation weighted by area
    if features['Specialisation_encoded'] in [0, 3]:  # AI/ML or Data Analytics
        score += 5
    elif features['Specialisation_encoded'] in [1, 2]:  # Computer Applications or CS/IT
        score += 3
    else:  # Data Science
        score += 4

    return score



# ... rest of your app.py code with routes and functions ...

@app.route('/upload_resume', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        file = request.files.get('resume')
        if not file:
            return render_template('upload_resume.html', error="Please upload a file.")
        
        try:
            parsed_details = extract_resume_details(file)
        except Exception as e:
            return render_template('upload_resume.html', error=str(e))
        
        # Required fields for prediction
        required_keys = ['10th', '12th', 'CGPA', 'Aptitude_score', 'Program_encoded', 'Gender_encoded',
                         'Internship_encoded', 'Specialisation_encoded']
        
        # Check which fields are missing
        missing_fields = [key for key in required_keys if key not in parsed_details or parsed_details[key] is None]
        
        if missing_fields:
            # Pass extracted details and missing fields to manual form
            return redirect(url_for('complete_resume_details', extracted=json.dumps(parsed_details), missing=','.join(missing_fields)))
        else:
            # All fields found, proceed to prediction
            mapping = {key: parsed_details[key] for key in required_keys}
            return redirect(url_for('applicant_result', **mapping))
    
    return render_template('upload_resume.html')

@app.route('/complete_resume_details', methods=['GET', 'POST'])
def complete_resume_details():
    extracted = json.loads(request.args.get('extracted', '{}'))
    missing = request.args.get('missing', '').split(',')
    
    if request.method == 'POST':
        # Combine extracted details with manually entered ones
        complete_details = extracted.copy()
        
        required_keys = ['10th', '12th', 'CGPA', 'Aptitude_score', 'Program_encoded', 'Gender_encoded',
                         'Internship_encoded', 'Specialisation_encoded']
        
        for key in required_keys:
            if key in request.form:
                try:
                    if key in ['10th', '12th', 'CGPA', 'Aptitude_score']:
                        complete_details[key] = float(request.form[key])
                    else:
                        complete_details[key] = int(request.form[key])
                except ValueError:
                    return render_template('complete_resume_details.html', 
                                         extracted=extracted, missing=missing, 
                                         error=f"Invalid value for {key}")
        
        # Verify all required fields are now present
        all_present = all(key in complete_details for key in required_keys)
        if not all_present:
            return render_template('complete_resume_details.html', 
                                 extracted=extracted, missing=missing, 
                                 error="Please fill all required fields.")
        
        mapping = {key: complete_details[key] for key in required_keys}
        return redirect(url_for('applicant_result', **mapping))
    
    return render_template('complete_resume_details.html', extracted=extracted, missing=missing)

@app.route('/review_predictions')
def review_predictions():
    log_path = os.path.join(root_dir, 'data', 'review_logs.json')
    logs = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            logs = json.load(f)
    return render_template('review_dashboard.html', logs=logs)


@app.route('/review_prediction/<int:log_id>', methods=['GET', 'POST'])
def review_prediction(log_id):
    log_path = os.path.join(root_dir, 'data', 'review_logs.json')
    with open(log_path, 'r') as f:
        logs = json.load(f)
    log = logs[log_id]

    error = None

    if request.method == 'POST':
        review_label = request.form.get('review_label')
        review_note = request.form.get('review_note', '')
        max_length = 500

        # Validate comment length
        if len(review_note) > max_length:
            error = f"Comment too long! Maximum {max_length} characters allowed."
            return render_template('review_form.html', log=log, log_id=log_id, error=error)

        # Update log entry
        log['review_status'] = "reviewed"
        log['review_label'] = review_label
        log['review_note'] = review_note
        logs[log_id] = log

        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)

        return redirect(url_for('review_predictions'))

    return render_template('review_form.html', log=log, log_id=log_id, error=error)

model = joblib.load('placement_xgb_model.joblib')
label_encoders = joblib.load('label_encoders.joblib')

PROGRAM_MAP = {0: "BCA", 1: "BTech"}
INTERNSHIP_MAP = {0: "No", 1: "Yes"}
SPECIALISATION_MAP = {
    0: "AI/ML",
    1: "Computer Applications",
    2: "CS/IT",
    3: "Data Analytics",
    4: "Data Science"
}
GENDER_MAP = {0: "Female", 1: "Male"}
BOARD_MAP = {0: "CBSE", 1: "ICSE", 2: "State"}



@app.route('/applicant_result')
def applicant_result():
    PROGRAM_MAP = {0: "BCA", 1: "BTech"}
    INTERNSHIP_MAP = {0: "No", 1: "Yes"}
    SPECIALISATION_MAP = {
        0: "AI/ML",
        1: "Computer Applications",
        2: "CS/IT",
        3: "Data Analytics",
        4: "Data Science"
    }

    user_input_encoded = {
        '10th': float(request.args.get('10th', 0)),
        '12th': float(request.args.get('12th', 0)),
        'CGPA': float(request.args.get('CGPA', 0)),
        'Aptitude_score': float(request.args.get('Aptitude_score', 0)),
        'Program_encoded': int(request.args.get('Program_encoded', 0)),
        'Internship_encoded': int(request.args.get('Internship_encoded', 0)),
        'Specialisation_encoded': int(request.args.get('Specialisation_encoded', 0)),
    }
    user_input_readable = {
        '10th': user_input_encoded['10th'],
        '12th': user_input_encoded['12th'],
        'CGPA': user_input_encoded['CGPA'],
        'Aptitude_score': user_input_encoded['Aptitude_score'],
        'Program': PROGRAM_MAP.get(user_input_encoded['Program_encoded'], 'Unknown'),
        'Internship': INTERNSHIP_MAP.get(user_input_encoded['Internship_encoded'], 'Unknown'),
        'Specialisation': SPECIALISATION_MAP.get(user_input_encoded['Specialisation_encoded'], 'Unknown'),
    }

    features_order = ['10th', '12th', 'CGPA', 'Aptitude_score', 'Program_encoded', 'Internship_encoded', 'Specialisation_encoded']
    input_for_model = {k: user_input_encoded[k] for k in features_order}
    user_df = pd.DataFrame([input_for_model], columns=features_order)

    model = joblib.load(model_path)
    probs = model.predict_proba(user_df)[0]
    pred_class = int(probs[1] > 0.579)

    score = calculate_segmented_score(user_input_encoded)
    threshold = 20
    placement_label = "Placed" if score >= threshold else "Not Placed"

    test_data = pd.read_csv(test_data_path)
    bias_results = detect_bias(model, test_data)
    gender_disparity = bias_results.get('Gender', {}).get('disparity_ratio', 1.0)
    bias_detected = gender_disparity < 0.7

    bias_label = "Bias Detected" if bias_detected else "Fair"

    log_prediction(user_input_readable, f"{placement_label}, {bias_label}")

    return render_template(
        'applicant_result.html',
        placement_label=placement_label,
        bias_label=bias_label,
        user_profile=user_input_readable,
    )






@app.route('/about')
def about():
    # Simply render the about.html template (the about us page you created)
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
