#train.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

# Load the extracted feature dataset created in the previous step.
df = pd.read_csv('features.csv')

# X = input features (all columns except the target label)
# y = target labels (music mood)
X = df.drop(columns=['mood'])
y = df['mood']

# Encode string labels into numeric values for the model.
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print("Mood mapping:", dict(zip(le.classes_, le.transform(le.classes_))))

# Split dataset into training and testing sets.
# 80% training, 20% testing.
# random_state=42 ensures reproducible splits.
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

print(f"Training on {len(X_train)} songs, testing on {len(X_test)} songs")

# Create Random Forest model with 100 decision trees.
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model on the training dataset.
model.fit(X_train, y_train)

print("Training complete!")

# Save trained model and label encoder to disk for later use.
joblib.dump(model, 'mood_model.pkl')
joblib.dump(le,    'label_encoder.pkl')

print("Model saved to mood_model.pkl")
print("Label encoder saved to label_encoder.pkl")