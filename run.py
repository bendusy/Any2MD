import sys
from unittest.mock import MagicMock

# Mock magika to prevent onnxruntime dependency
class MockMagika:
    def identify_stream(self, stream):
        return MagicMock(output=MagicMock(ct_label="application/octet-stream"))

    def identify_path(self, path):
         return MagicMock(output=MagicMock(ct_label="application/octet-stream"))

sys.modules["magika"] = MagicMock()
sys.modules["magika"].Magika = MockMagika

from any2md.cli import app

if __name__ == "__main__":
    app()
