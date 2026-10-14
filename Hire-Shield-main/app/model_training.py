import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv('Placement_Data_Updated.csv')

# Drop irrelevant columns
df = df.drop(columns=['Sl_no', 'Salary'], errors='ignore')

# Encode Status target
df['Status'] = df['Status'].map({'Not Placed': 0, 'Placed': 1})

# Encode categorical columns with '_encoded' suffix
label_encoders = {}
categorical_cols = ['Gender', 'Board', 'Program', 'Internship', 'Specialisation']
for col in categorical_cols:
    le = LabelEncoder()
    encoded_col = f"{col}_encoded"
    df[encoded_col] = le.fit_transform(df[col])
    label_encoders[col] = le

# Drop original categorical columns
df = df.drop(columns=categorical_cols)

# Drop rows with missing values
df = df.dropna()

# Features to train on (all encoded categorical + numeric)
feature_cols = [col for col in df.columns if col != 'Status']
X = df[feature_cols]
y = df['Status']

# Split into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost model
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(f'Accuracy: {accuracy_score(y_test, y_pred):.4f}')
print(classification_report(y_test, y_pred))

# Save model and label encoders
joblib.dump(model, 'placement_xgb_model.joblib')
joblib.dump(label_encoders, 'label_encoders.joblib')
