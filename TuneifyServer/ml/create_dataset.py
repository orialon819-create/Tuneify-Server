import os
import csv

# Your mood mapping
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
        if filename.endswith('.wav'):
            filepath = os.path.join(folder, filename)
            rows.append({'filename': filepath, 'mood': mood})

with open(output_csv, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['filename', 'mood'])
    writer.writeheader()
    writer.writerows(rows)

print(f"Done! {len(rows)} songs written to {output_csv}")