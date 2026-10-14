import pandas as pd
from xgboost import XGBClassifier
import joblib

# Load dataset
df = pd.read_csv('Placement_Data_Updated.csv')

# Map categorical data to integer codes (must match your form's numeric codes)
df['Gender'] = df['Gender'].map({'F': 0, 'M': 1}).astype(int)
df['Board'] = df['Board'].map({'CBSE': 0, 'ICSE': 1, 'State': 2}).astype(int)
df['Program'] = df['Program'].map({'BCA': 0, 'BTech': 1}).astype(int)
df['Internship'] = df['Internship'].map({'No': 0, 'Yes': 1}).astype(int)
df['Specialisation'] = df['Specialisation'].map({
    'AI/ML': 0,
    'Computer Applications': 1,
    'CS/IT': 2,
    'Data Analytics': 3,
    'Data Science': 4
}).astype(int)

# Define features and target
df['Status_encoded'] = df['Status'].map({'Not Placed': 0, 'Placed': 1})

# Use encoded target for training
X = df[['Gender', '10th', '12th', 'Board', 'CGPA', 'Program', 'Internship', 'Aptitude_score', 'Specialisation']]
y = df['Status_encoded']  # or your target column

# Train model
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X, y)

# Save model
joblib.dump(model, 'placement_model_standard.joblib')

