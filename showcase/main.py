"""Launch Fluent Blue Design Studio from a source checkout: ``python showcase/main.py``."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fluent_blue.studio.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
