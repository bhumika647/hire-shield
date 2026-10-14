import pandas as pd
from sklearn.metrics import accuracy_score

def detect_bias_placement(model, test_data, bias_threshold=0.7):
    X_test = test_data.drop('placement_status', axis=1) if 'placement_status' in test_data.columns else test_data
    y_test = test_data['placement_status'] if 'placement_status' in test_data.columns else None

    y_pred = model.predict(X_test)

    results = {}
    protected_features = {
        'Gender': 4,
        'Board': 5,
        'Program': 6,
        'Internship': 7,
        'Specialisation': 8,
    }

    overall_bias_detected = False

    for attr, col_idx in protected_features.items():
        if col_idx >= X_test.shape[1]:
            continue
        unique_vals = X_test.iloc[:, col_idx].unique()
        results[attr] = {'group_metrics': {}, 'disparity_ratio': 1.0}

        selection_rates = []
        for val in unique_vals:
            mask = X_test.iloc[:, col_idx] == val
            accuracy = accuracy_score(y_test[mask], y_pred[mask]) if y_test is not None and mask.sum() > 0 else 0
            selection_rate = y_pred[mask].mean() if mask.sum() > 0 else 0
            selection_rates.append(selection_rate)
            results[attr]['group_metrics'][str(val)] = {
                'accuracy': accuracy,
                'selection_rate': selection_rate,
                'count': mask.sum()
            }

        if len(selection_rates) > 1 and max(selection_rates) > 0:
            disparity = min(selection_rates) / max(selection_rates)
            results[attr]['disparity_ratio'] = disparity
            if disparity < bias_threshold:
                overall_bias_detected = True

    results['overall_bias_detected'] = overall_bias_detected
    return results

