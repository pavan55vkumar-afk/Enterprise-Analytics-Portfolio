import sys
import os

# Forwarding stub for Streamlit Cloud entry point
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import project_1_operations_rca.app
