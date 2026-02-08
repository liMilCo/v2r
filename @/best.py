import os
import requests


# Define a fixed value
TIMEOUT = 15  # seconds
Best_URL = "https://btc.limil.ir/pages"

print(f"\nUpdate Best Configs ...")
output_folder = os.path.join(os.path.dirname(__file__), "..")
best_file = os.path.join(output_folder, 'best.txt')

print(f"Remove {best_file}")
if os.path.exists(best_file):
    os.remove(best_file)

print(f"Get Best Configs ...")

response = requests.get(Best_URL, timeout=TIMEOUT)
best_text = response.text

with open(best_file, "w", encoding="utf-8") as f:
    f.write(best_text)

print(f"Update Best successfully!")    
