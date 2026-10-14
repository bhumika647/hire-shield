import os
import sys
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

sys.path.insert(0, current_dir)

from data_processing_placement import load_and_process_placement_data_mitigated

def train_and_save_mitigated_model():
    df, _ = load_and_process_placement_data_mitigated()

    X = df.drop('placement_status', axis=1)
    y = df['placement_status']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print(f"Mitigated Model Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(classification_report(y_test, y_pred))

    model_path = os.path.join(root_dir, 'models', 'placement_model_mitigated.pkl')
    joblib.dump(model, model_path)
    test_path = os.path.join(root_dir, 'data', 'processed', 'test_sample_mitigated.csv')
    X_test.to_csv(test_path, index=False)

    print("Mitigated model and test sample saved.")

if __name__ == '__main__':
    train_and_save_mitigated_model()
