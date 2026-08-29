"""Puts the package directory on sys.path: the modules use flat imports and run as scripts."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
