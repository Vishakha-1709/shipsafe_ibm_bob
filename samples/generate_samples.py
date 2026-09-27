import os
import zipfile
import shutil

SAMPLE_DIR = os.path.dirname(os.path.abspath(__file__))

def build_bad_sample():
    """Builds a deliberately flawed demo repository."""
    bad_dir = os.path.join(SAMPLE_DIR, "raw_bad_repo")
    os.makedirs(bad_dir, exist_ok=True)
    
    # 1. Main code with hardcoded secret
    predict_code = """import os
import requests

# Hardcoded secret (Critical Security Violation)
API_KEY = "sk-live-99238472918347102938471928347192"
DB_CONNECTION = "postgres://admin:superSecretPass123!@localhost:5432/production_db"

def predict(input_data):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    response = requests.post("https://api.internal-service.com/v1/predict", json=input_data, headers=headers)
    return response.json()

if __name__ == "__main__":
    print("Running predictor service...")
"""
    with open(os.path.join(bad_dir, "predict.py"), "w", encoding="utf-8") as f:
        f.write(predict_code)

    # 2. requirements.txt
    with open(os.path.join(bad_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("requests>=2.28.0\n")

    # 3. Accidental .env file committed
    with open(os.path.join(bad_dir, ".env"), "w", encoding="utf-8") as f:
        f.write("STRIPE_SECRET_KEY=sk_test_51NzABC1234567890\n")

    # Package into ZIP
    zip_path = os.path.join(SAMPLE_DIR, "sample_bad_repo.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(bad_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, bad_dir)
                zipf.write(full_path, rel_path)

    shutil.rmtree(bad_dir)
    print(f"Created {zip_path}")


def build_clean_sample():
    """Builds a clean, remediated repository."""
    clean_dir = os.path.join(SAMPLE_DIR, "raw_clean_repo")
    os.makedirs(clean_dir, exist_ok=True)
    os.makedirs(os.path.join(clean_dir, "tests"), exist_ok=True)

    # 1. Clean app code
    app_code = """import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

def run():
    print("Service initialized securely.")

if __name__ == "__main__":
    run()
"""
    with open(os.path.join(clean_dir, "app.py"), "w", encoding="utf-8") as f:
        f.write(app_code)

    # 2. Tests
    test_code = """def test_initialization():
    assert True
"""
    with open(os.path.join(clean_dir, "tests", "test_app.py"), "w", encoding="utf-8") as f:
        f.write(test_code)

    # 3. README
    readme_code = """# Clean Sample Application

## Setup & Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python app.py
```

## Tests
```bash
pytest tests/
```
"""
    with open(os.path.join(clean_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_code)

    # 4. requirements.txt
    with open(os.path.join(clean_dir, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("python-dotenv>=1.0.0\npytest>=7.0.0\n")

    # 5. .gitignore
    with open(os.path.join(clean_dir, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(".env\n__pycache__/\n*.pyc\n")

    # 6. LICENSE
    with open(os.path.join(clean_dir, "LICENSE"), "w", encoding="utf-8") as f:
        f.write("MIT License\n")

    # Package into ZIP
    zip_path = os.path.join(SAMPLE_DIR, "sample_clean_repo.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(clean_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, clean_dir)
                zipf.write(full_path, rel_path)

    shutil.rmtree(clean_dir)
    print(f"Created {zip_path}")


def build_all_samples():
    build_bad_sample()
    build_clean_sample()

if __name__ == "__main__":
    build_all_samples()
