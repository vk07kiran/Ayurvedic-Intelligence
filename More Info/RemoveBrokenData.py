from PIL import Image
import os

dataset_path = "C:/Users/zeb/Desktop/FinalDataset"  # adjust to your dataset path

broken = 0
total = 0

for root, dirs, files in os.walk(dataset_path):
    for fname in files:
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            continue
        fpath = os.path.join(root, fname)
        total += 1
        try:
            # Load and force full pixel decoding
            with Image.open(fpath) as img:
                img = img.convert("RGB")
                img.load()  # <- this is what triggers deep decoding
        except Exception as e:
            print(f"Removing broken image: {fpath} ({e})")
            os.remove(fpath)
            broken += 1

print(f"\n✅ Done. Removed {broken} broken images out of {total} total.")
