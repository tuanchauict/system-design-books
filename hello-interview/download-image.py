import os
import re
import requests
import sys
from urllib.parse import urlparse

def download_images(markdown_file):
    if not os.path.exists(markdown_file):
        print(f"Error: File '{markdown_file}' not found.")
        return
    doc_path = os.path.dirname(markdown_file)
    doc_name = os.path.splitext(os.path.basename(markdown_file))[0]  # Get doc name without extension

    with open(markdown_file, 'r') as f:
        content = f.read()

    image_urls = re.findall(r'!\[.*?\]\((.*?)\)', content)

    for image_index, url in enumerate(image_urls):
        if url.startswith("http://") or url.startswith("https://"):
            try:
                parsed_url = urlparse(url)
                ext = ""
                if ".png" in url:
                    ext = ".png"
                elif ".jpg" in url or ".jpeg" in url:
                    ext = ".jpg"
                elif ".gif" in url:
                    ext = ".gif"
                else:  # Guess or default
                    ext = ".jpg"

                image_file_name = f"i-{doc_name}-d{image_index}{ext}"
                filepath = os.path.join(doc_path, image_file_name)

                if not os.path.exists(filepath):
                    print(f"Downloading: {url} to {filepath}")
                    try:
                        response = requests.get(url, stream=True, timeout=10)
                        response.raise_for_status()

                        with open(filepath, 'wb') as image_file:
                            for chunk in response.iter_content(chunk_size=8192):
                                image_file.write(chunk)
                    except requests.exceptions.Timeout:
                        print(f"Download timed out: {url}")
                        continue
                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading {url}: {e}")
                        continue
                else:
                    print(f"Image already exists: {filepath}")

                content = content.replace(url, image_file_name)

            except Exception as e:
                print(f"Error processing {url}: {e}")

    with open(markdown_file, 'w') as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <markdown_file>")
        sys.exit(1)

    markdown_file = sys.argv[1]
    download_images(markdown_file)
    print("Image downloading and Markdown update complete.")