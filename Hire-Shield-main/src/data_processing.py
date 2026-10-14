# src/data_processing.py
import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def load_and_process_data():
    # Get absolute paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    
    # Define paths
    raw_path = os.path.join(root_dir, 'data', 'raw', 'adult.data')
    processed_path = os.path.join(root_dir, 'data', 'processed', 'adult_processed.csv')
    
    # Define column names
    columns = [
        'age', 'workclass', 'fnlwgt', 'education', 'education-num',
        'marital-status', 'occupation', 'relationship', 'race', 'sex',
        'capital-gain', 'capital-loss', 'hours-per-week', 'native-country', 'income'
    ]
    
    # Load data
    df = pd.read_csv(
        raw_path,
        names=columns,
        na_values=' ?',
        skipinitialspace=True
    ).dropna()
    
    # Create binary target (1 if income >50K)
    df['income'] = df['income'].apply(lambda x: 1 if '>50K' in x else 0)
    
    # Convert sensitive attributes
    df['sex'] = df['sex'].map({'Male': 0, 'Female': 1})
    df['race'] = df['race'].map({'White': 0, 'Black': 1, 'Asian-Pac-Islander': 2, 
                                'Amer-Indian-Eskimo': 3, 'Other': 4})
    
    # Bin age groups - FIXED CATEGORICAL TYPE
    df['age_group'] = pd.cut(df['age'], 
                            bins=[0, 25, 45, 65, 100],
                            labels=['<25', '25-45', '46-65', '>65']).astype(str)
    # Encode age_group as integer
    df['age_group'] = df['age_group'].map({'<25': 0, '25-45': 1, '46-65': 2, '>65': 3})

    # Encode other categorical features
    cat_cols = ['workclass', 'education', 'marital-status', 'occupation', 
               'relationship', 'native-country']
    le = LabelEncoder()
    for col in cat_cols:
        df[col] = le.fit_transform(df[col])
    
    # Save processed data
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.to_csv(processed_path, index=False)
    print(f"Processed data saved to {processed_path}")
    return df

if __name__ == "__main__":
    load_and_process_data()