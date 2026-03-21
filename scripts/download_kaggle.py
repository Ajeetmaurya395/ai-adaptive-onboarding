"""
Script to download Kaggle Resume and Jobs datasets for evaluation and testing.
Requires kaggle.json in ~/.kaggle/ directory.
"""
import opendatasets as od
import os

# Dataset URLs
RESUME_DATASET = "https://www.kaggle.com/datasets/gauravduttakiit/resume-dataset"
JOBS_DATASET = "https://www.kaggle.com/datasets/arshkon/linkedin-job-postings"

def download_data():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "kaggle_raw")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    print(f"📥 Downloading Resume Dataset to {data_dir}...")
    od.download(RESUME_DATASET, data_dir)
    
    print(f"📥 Downloading Jobs Dataset to {data_dir}...")
    od.download(JOBS_DATASET, data_dir)
    
    print("\n✅ Kaggle datasets downloaded successfully.")
    print("Next step: Run evaluation/metrics.py to test the engine accuracy.")

if __name__ == "__main__":
    download_data()
