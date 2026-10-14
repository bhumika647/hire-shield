from flask import Flask, render_template, request
import joblib
import numpy as np

app = Flask(__name__)

# Load the trained model
model = joblib.load('placement_xgb_model.joblib')

# No need to load encoders, inputs are already encoded

@app.route('/')
def home():
    return render_template('index.html', prediction=None)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Collect encoded inputs directly from the form as integers
        gender_enc = int(request.form['Gender_encoded'])
        board_enc = int(request.form['Board_encoded'])
        program_enc = int(request.form['Program_encoded'])
        internship_enc = int(request.form['Internship_encoded'])
        specialisation_enc = int(request.form['Specialisation_encoded'])
        tenth = float(request.form['10th'])
        twelfth = float(request.form['12th'])
        cgpa = float(request.form['CGPA'])
        

        # Create feature vector in the same order as training
        aptitude_score = float(request.form['Aptitude_score'])

        features = np.array([[
            gender_enc,
            board_enc,
            program_enc,
            internship_enc,
            specialisation_enc,
            tenth,
            twelfth,
            cgpa,
            aptitude_score  # Add this feature
        ]])

        prediction = model.predict(features)[0]
        pred_text = 'Placed' if prediction == 1 else 'Not Placed'

        return render_template('index.html', prediction=pred_text)

    except Exception as e:
        return render_template('index.html', prediction=f"Error: {str(e)}")

if __name__ == "__main__":
    app.run(debug=True)
