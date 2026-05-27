import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib   # for saving the model to a file

from train import X_test, y_test

# Load both files back (simulating what your server will do)
loaded_model   = joblib.load('mood_model.pkl')
loaded_encoder = joblib.load('label_encoder.pkl')

# Grab one song from the test set and predict its mood
sample = X_test.iloc[[0]]   # double brackets keep it as a DataFrame, not a plain array
prediction_number = loaded_model.predict(sample)[0]
prediction_mood = loaded_encoder.inverse_transform([prediction_number])[0]
actual_mood = loaded_encoder.inverse_transform([y_test[0]])[0]

print(f"Predicted: {prediction_mood}")
print(f"Actual:    {actual_mood}")