#create_dataset.py

import os
import csv

# Dictionary mapping musical genres to their corresponding emotional mood labels.
genre_to_mood = {
    'blues':     'Sad',
    'classical': 'Calm',
    'country':   'Sad',
    'disco':     'Energetic',
    'hiphop':    'Angry',
    'jazz':      'Calm',
    'metal':     'Angry',
    'pop':       'Happy',
    'reggae':    'Happy',
    'rock':      'Energetic',
}

dataset_path = r'C:\Users\orial\OneDrive\Desktop\archive\Data\genres_original'
output_csv   = 'mood_labels.csv'

rows = []
for genre, mood in genre_to_mood.items():
    folder = os.path.join(dataset_path, genre)
    for filename in os.listdir(folder):
        # Process only WAV audio files.
        if filename.endswith('.wav'):
            filepath = os.path.join(folder, filename)
            rows.append({'filename': filepath, 'mood': mood})

# Write the processed dataset into a CSV file.
with open(output_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['filename', 'mood'])
    writer.writeheader()
    writer.writerows(rows)


