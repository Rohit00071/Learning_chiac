import os
import sys
from pathlib import Path

_root = Path(__file__).parent
os.chdir(str(_root))
sys.path.insert(0, str(_root))

import dashboard.app
