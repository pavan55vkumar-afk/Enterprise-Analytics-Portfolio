import sys
import os

# Root entry point router
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import project_1_operations_rca.app
