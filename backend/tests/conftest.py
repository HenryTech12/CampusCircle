import sys
import os
from pathlib import Path

os.environ.setdefault("SESSION_SECRET", "test-only-secret")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
