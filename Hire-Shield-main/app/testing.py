import pandas as pd
import joblib

# Load your trained model (adjust path as needed)
model = joblib.load('placement_xgb_model.joblib')

# Sample input with exact feature names and integer encoding for categorical variables
sample_input = {
    'Gender': 1,          # Male
    '10th': 85.0,         # 10th Grade %
    '12th': 90.0,         # 12th Grade %
    'Board': 0,           # CBSE=0, ICSE=1, State=2
    'CGPA': 8.5,          # CGPA out of 10
    'Program': 1,         # BTech=1, BCA=0
    'Internship': 1,      # Yes=1, No=0
    'Aptitude_score': 75.0,
    'Specialisation': 3   # Data Analytics=3
}

# Order features exactly as model was trained
feature_order = ['Gender', '10th', '12th', 'Board', 'CGPA',
                 'Program', 'Internship', 'Aptitude_score', 'Specialisation']

# Convert input dict to DataFrame
input_df = pd.DataFrame([sample_input], columns=feature_order)

# Predict using the model
probs = model.predict_proba(input_df)[0]
placement_label = "Placed" if probs[1] > 0.459 else "Not Placed"
placement_prob = probs[1]

print(f"Placement Label: {placement_label}")
print(f"Placement Probability: {placement_prob:.4f}")
