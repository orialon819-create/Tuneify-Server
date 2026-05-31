# evaluate.py

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load the extracted feature dataset.
df = pd.read_csv('features.csv')
X = df.drop(columns=['mood'])
y = df['mood']

# Load the saved label encoder and encode mood labels.
le = joblib.load('label_encoder.pkl')
y_encoded = le.transform(y)

# Use the same random_state used during training
# to reproduce the identical test dataset.
_, X_test, _, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Load the trained machine learning model.
model = joblib.load('mood_model.pkl')

# Generate predictions for the test dataset.
y_pred = model.predict(X_test)

# Calculate and display model accuracy.
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy * 100:.1f}%")
print(f"({int(accuracy * len(y_test))} correct out of {len(y_test)} songs)\n")

# Generate and display the confusion matrix.
mood_names = le.classes_
cm = confusion_matrix(y_test, y_pred)

print("Confusion Matrix:")
print(f"{'':12}", end="")
for name in mood_names:
    print(f"{name:12}", end="")
print()

for i, row in enumerate(cm):
    print(f"{mood_names[i]:12}", end="")
    for val in row:
        print(f"{val:<12}", end="")
    print()

# Display performance metrics for each mood category.
print("\nPer-mood breakdown:")
print(classification_report(y_test, y_pred, target_names=mood_names))

# Display feature importance scores used by the model.
importances = model.feature_importances_
feature_names = X.columns.tolist()

pairs = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)

print("Top 5 most important features:")
for name, score in pairs[:5]:
    bar = "█" * int(score * 200)
    print(f"  {name:15} {score:.3f}  {bar}")

