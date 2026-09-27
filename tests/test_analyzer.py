import unittest
import os
import tempfile
from analyzer.scanner import scan_repository
from analyzer.security import scan_for_secrets
from analyzer.scoring import calculate_release_readiness

class TestShipSafeAnalyzer(unittest.TestCase):

    def test_scanner_detects_clean_repo(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create README
            with open(os.path.join(tmp_dir, "README.md"), "w") as f:
                f.write("# Clean Project\nInstallation:\npip install -r requirements.txt\nUsage: python app.py")
            
            # Create requirements.txt
            with open(os.path.join(tmp_dir, "requirements.txt"), "w") as f:
                f.write("streamlit>=1.0.0\n")
                
            # Create test file
            os.makedirs(os.path.join(tmp_dir, "tests"), exist_ok=True)
            with open(os.path.join(tmp_dir, "tests", "test_main.py"), "w") as f:
                f.write("def test_ok(): assert True")
                
            # Create app.py
            with open(os.path.join(tmp_dir, "app.py"), "w") as f:
                f.write("print('Hello World')")

            scan_data = scan_repository(tmp_dir)
            self.assertTrue(scan_data["has_readme"])
            self.assertTrue(scan_data["has_tests"])
            self.assertTrue(scan_data["has_dependencies"])
            self.assertFalse(scan_data["has_env_file"])

            secrets = scan_for_secrets(tmp_dir, scan_data["file_list"])
            self.assertEqual(len(secrets), 0)

            score_data = calculate_release_readiness(scan_data, secrets)
            self.assertGreaterEqual(score_data["total_score"], 80)

    def test_security_scanner_flags_hardcoded_keys(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = os.path.join(tmp_dir, "config.py")
            with open(config_path, "w") as f:
                f.write('OPENAI_API_KEY = "sk-abcdef1234567890abcdef1234567890abcdef"\n')
                f.write('DB_URL = "postgres://root:mySecretPass123!@localhost:5432/mydb"\n')

            scan_data = scan_repository(tmp_dir)
            secrets = scan_for_secrets(tmp_dir, scan_data["file_list"])
            self.assertGreaterEqual(len(secrets), 2)
            severities = [s["severity"] for s in secrets]
            self.assertIn("Critical", severities)

if __name__ == "__main__":
    unittest.main()
