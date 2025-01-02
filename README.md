# The Veiled Realm

## Installation

1. First, clean up any existing installation artifacts:
   ```bash
   rm -rf *.egg-info build dist
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package and dependencies in development mode:
   ```bash
   pip install -e .
   ```

4. Install additional required packages:
   ```bash
   pip install python-dotenv google-generativeai