#!/usr/bin/env python3
"""
Download O*NET Database text files and extract the tables needed
for the AI-Adaptive Onboarding skill taxonomy.

Uses O*NET 29.2 (February 2025) — a stable, well-documented release.
"""

import os
import sys
import zipfile
import urllib.request
import shutil

# O*NET 29.2 text-format download URL
ONET_VERSION = "29_2"
ONET_URL = f"https://www.onetcenter.org/dl_files/database/db_{ONET_VERSION}_text.zip"

# Where to store raw O*NET files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "onet_raw")
ZIP_PATH = os.path.join(RAW_DIR, f"db_{ONET_VERSION}_text.zip")

# Files we actually need (tab-separated text inside the zip)
NEEDED_FILES = [
    "Technology Skills.txt",
    "Skills.txt",
    "Knowledge.txt",
    "Occupation Data.txt",
    "Alternate Titles.txt",
    "Task Statements.txt",
    "Content Model Reference.txt",
    "Scales Reference.txt",
]


def download_onet():
    """Download the O*NET zip if not already present."""
    os.makedirs(RAW_DIR, exist_ok=True)

    if os.path.exists(ZIP_PATH):
        print(f"✅ Zip already exists: {ZIP_PATH}")
        return

    print(f"⬇️  Downloading O*NET {ONET_VERSION} text database...")
    print(f"   URL: {ONET_URL}")
    try:
        urllib.request.urlretrieve(ONET_URL, ZIP_PATH)
        print(f"✅ Downloaded to {ZIP_PATH}")
    except Exception as e:
        print(f"❌ Download failed: {e}")
        print("💡 You can manually download from: https://www.onetcenter.org/db_releases.html")
        sys.exit(1)


def extract_needed_files():
    """Extract only the files we need from the zip."""
    print(f"\n📦 Extracting needed files from zip...")

    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        # List all files in the zip to find the subfolder name
        all_names = zf.namelist()

        # O*NET zips typically have a top-level folder like "db_29_2_text/"
        top_folders = set()
        for name in all_names:
            parts = name.split("/")
            if len(parts) > 1 and parts[0]:
                top_folders.add(parts[0])

        prefix = ""
        if top_folders:
            prefix = sorted(top_folders)[0] + "/"

        extracted = 0
        for needed in NEEDED_FILES:
            # Try with and without the prefix
            candidates = [needed, f"{prefix}{needed}"]
            found = False
            for candidate in candidates:
                if candidate in all_names:
                    # Extract to RAW_DIR with flat name
                    source = zf.open(candidate)
                    target_path = os.path.join(RAW_DIR, needed)
                    with open(target_path, "wb") as out:
                        shutil.copyfileobj(source, out)
                    print(f"   ✅ {needed}")
                    extracted += 1
                    found = True
                    break
            if not found:
                print(f"   ⚠️  {needed} not found in zip")

        print(f"\n📊 Extracted {extracted}/{len(NEEDED_FILES)} files to {RAW_DIR}")


def verify():
    """Quick verification that key files exist."""
    print("\n🔍 Verifying extraction...")
    ok = True
    for needed in NEEDED_FILES[:4]:  # Check the 4 most important
        path = os.path.join(RAW_DIR, needed)
        if os.path.exists(path):
            size_kb = os.path.getsize(path) / 1024
            print(f"   ✅ {needed} ({size_kb:.0f} KB)")
        else:
            print(f"   ❌ {needed} MISSING")
            ok = False

    if ok:
        print("\n🎉 O*NET data ready! Run build_taxonomy.py next.")
    else:
        print("\n⚠️  Some files missing. Check download.")


if __name__ == "__main__":
    print("=" * 60)
    print("O*NET Database Downloader for AI-Adaptive Onboarding")
    print("=" * 60)
    download_onet()
    extract_needed_files()
    verify()
