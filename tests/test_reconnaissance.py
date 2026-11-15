import sys
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from modules.reconnaissance import ReconModule


def test_certificate_names_are_trimmed_filtered_and_deduplicated():
    response = Mock(status_code=200)
    response.json.return_value = [
        {"name_value": " www.example.test \napi.example.test\nexample.test"},
        {"name_value": "api.example.test\nother.test\nnotexample.test"},
        {},
    ]
    module = ReconModule.__new__(ReconModule)
    with patch("modules.reconnaissance.requests.get", return_value=response) as get:
        assert set(module._cert_transparency_search("example.test")) == {
            "www.example.test", "api.example.test", "example.test"
        }
    get.assert_called_once_with("https://crt.sh/?q=%.example.test&output=json", timeout=10)
