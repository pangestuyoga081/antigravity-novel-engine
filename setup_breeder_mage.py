import os
import zipfile
import re
import json
import time
import urllib.request
from xml.etree import ElementTree as ET

EPUB_PATH = r"D:\JV\novel yoga\Breeder_Mage_1_-_Marc_Robert.epub"
OUTPUT_DIR = r"D:\JV\novel yoga\Breeder_Mage_1_work"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Inspect and extract spine chapters
with zipfile.ZipFile(EPUB_PATH, "r") as z:
    z.extractall(OUTPUT_DIR)

print("Extracted EPUB to:", OUTPUT_DIR)
