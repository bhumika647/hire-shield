import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

def detect_bias(model, test_df, protected_attribute='Gender', privileged_group=1, unprivileged_group=0, label_col='Status'):
    gender_map = {'M': 1, 'F': 0}
    board_map = {'Central': 0, 'State': 1, 'ICSE': 2, 'Others': 3}
    program_map = {'BCA': 0, 'BTech': 1}
    internship_map = {'No': 0, 'Yes': 1}
    specialisation_map = {
        'AI/ML': 0,
        'Computer Applications': 1,
        'CS/IT': 2,
        'Data Analytics': 3,
        'Data Science': 4
    }

    test_df = test_df.drop(columns=['Sl_no', 'Salary'], errors='ignore').copy()

    # Map and fill missing with default (example: -1)
    test_df['Gender'] = test_df['Gender'].map(gender_map).fillna(-1).astype(int)
    test_df['Board'] = test_df['Board'].map(board_map).fillna(-1).astype(int)
    test_df['Program'] = test_df['Program'].map(program_map).fillna(-1).astype(int)
    test_df['Internship'] = test_df['Internship'].map(internship_map).fillna(-1).astype(int)
    test_df['Specialisation'] = test_df['Specialisation'].map(specialisation_map).fillna(-1).astype(int)

    # Proceed as usual with filtered or flagged unmapped rows if needed
    # Optionally drop rows with missing mapped values:
    test_df = test_df[(test_df['Gender'] != -1) & (test_df['Board'] != -1) & 
                      (test_df['Program'] != -1) & (test_df['Internship'] != -1) & 
                      (test_df['Specialisation'] != -1)]

    # Map label to numeric
    label_map = {'Not Placed': 0, 'Placed': 1}
    test_df[label_col] = test_df[label_col].map(label_map)

    # Drop rows with label mapping failures
    test_df = test_df.dropna(subset=[label_col])
    test_df[label_col] = test_df[label_col].astype(int)

    # Now safe to extract X, y and run predictions
    X = test_df.drop(columns=[label_col])
    y_true = test_df[label_col].values
    y_pred = model.predict(X)

    privileged_idx = test_df[protected_attribute] == privileged_group
    unprivileged_idx = test_df[protected_attribute] == unprivileged_group

    p_priv = np.mean(y_pred[privileged_idx])
    p_unpriv = np.mean(y_pred[unprivileged_idx])
    stat_parity_diff = p_unpriv - p_priv
    disparate_impact = p_unpriv / p_priv if p_priv > 0 else np.nan

    def group_metrics(idx):
        tn, fp, fn, tp = confusion_matrix(y_true[idx], y_pred[idx], labels=[0,1]).ravel()
        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        return tpr, fpr

    tpr_priv, fpr_priv = group_metrics(privileged_idx)
    tpr_unpriv, fpr_unpriv = group_metrics(unprivileged_idx)

    eq_opp_diff = tpr_unpriv - tpr_priv
    avg_odds_diff = 0.5 * ((fpr_unpriv - fpr_priv) + (tpr_unpriv - tpr_priv))

    return {
        'statistical_parity_difference': stat_parity_diff,
        'disparate_impact': disparate_impact,
        'equal_opportunity_difference': eq_opp_diff,
        'average_odds_difference': avg_odds_diff,
        'tpr_privileged': tpr_priv,
        'tpr_unprivileged': tpr_unpriv,
        'fpr_privileged': fpr_priv,
        'fpr_unprivileged': fpr_unpriv,
        'disparity_ratio': disparate_impact
    }
