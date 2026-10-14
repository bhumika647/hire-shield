import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def load_and_process_placement_data_mitigated():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)

    raw_path = os.path.join(root_dir, 'data', 'raw', 'Placement_Data_Final.csv')
    processed_path = os.path.join(root_dir, 'data', 'processed', 'placement_processed_mitigated.csv')

    df = pd.read_csv(raw_path)

    df = df.drop(['Sl_no', 'Salary'], axis=1, errors='ignore')

    # Encode categorical columns except sensitive ones (exclude Gender, Board etc)
    cols_to_encode = ['Program', 'Internship', 'Specialisation', 'Status']
    le_dict = {}

    for col in cols_to_encode:
        if col in df.columns:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col])
            le_dict[col] = le

    df['placement_status'] = (df['Status'] == 'Placed').astype(int)

    # Use only non-sensitive features (academic only)
    feature_cols = ['10th', '12th', 'CGPA', 'Aptitude_score', 'Program_encoded', 'Internship_encoded', 'Specialisation_encoded']

    df_processed = df[feature_cols + ['placement_status']].copy()
    df_processed.to_csv(processed_path, index=False)

    return df_processed, le_dict


if __name__ == '__main__':
    load_and_process_placement_data_mitigated()
    print("Mitigated data processed and saved.")
