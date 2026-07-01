import os
import re
import urllib.request
import ssl
from urllib.parse import urljoin

ssl._create_default_https_context = ssl._create_unverified_context

base_url = "https://eventrix.pro/"
html_file = "index.html"

with open(html_file, "r") as f:
    html = f.read()

# Find all href and src
pattern = re.compile(r'(href|src)="(/_next/[^"]+)"')
matches = pattern.findall(html)

for attr, path in matches:
    url = urljoin(base_url, path)
    local_path = path.lstrip('/')
    
    # Create directories
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    
    if not os.path.exists(local_path):
        print(f"Downloading {url} to {local_path}...")
        try:
            urllib.request.urlretrieve(url, local_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

# Download background images
bg_pattern = re.compile(r'url\("(/templates/[^"]+)"\)')
bg_matches = bg_pattern.findall(html)
for path in bg_matches:
    url = urljoin(base_url, path)
    local_path = path.lstrip('/')
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not os.path.exists(local_path):
        print(f"Downloading {url} to {local_path}...")
        try:
            urllib.request.urlretrieve(url, local_path)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

print("Done!")
