import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib   # for saving the model to a file

# ── Step 1: Load the features CSV we built in Phase 2 ──────────────────
df = pd.read_csv('features.csv')

# X = the input numbers (every column except mood)
# y = the correct answers (just the mood column)
X = df.drop(columns=['mood'])
y = df['mood']

# ── Step 2: Encode moods as numbers ────────────────────────────────────
# The model only understands numbers, not text
# So: Happy→0, Sad→1, Calm→2, Energetic→3, Angry→4 (order auto-assigned)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print("Mood mapping:", dict(zip(le.classes_, le.transform(le.classes_))))
# e.g. → {'Angry': 0, 'Calm': 1, 'Energetic': 2, 'Happy': 3, 'Sad': 4}

# ── Step 3: Split into training and test sets ───────────────────────────
# test_size=0.2 means 20% goes to testing
# random_state=42 means the split is the same every time you run it
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

print(f"Training on {len(X_train)} songs, testing on {len(X_test)} songs")

# ── Step 4: Create and train the Random Forest ──────────────────────────
# n_estimators=100 means 100 trees vote on each prediction
# random_state=42 keeps results reproducible
model = RandomForestClassifier(n_estimators=100, random_state=42)

# This single line does ALL the learning — it reads all 800 training rows
# and builds the 100 decision trees
model.fit(X_train, y_train)

print("Training complete!")

# ── Step 5: Save the model to disk ─────────────────────────────────────
# joblib saves the trained model so you never have to retrain it
# Your server will just load this file and use it instantly
joblib.dump(model, 'mood_model.pkl')
joblib.dump(le,    'label_encoder.pkl')   # save the encoder too!

print("Model saved to mood_model.pkl")
print("Label encoder saved to label_encoder.pkl")