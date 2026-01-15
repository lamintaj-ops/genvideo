"""
Hugging Face Spaces app entry point
"""
import os
from web_app import app

# Configure for Hugging Face Spaces
os.environ['FLASK_ENV'] = 'production'

if __name__ == "__main__":
    # Hugging Face Spaces uses port 7860
    port = int(os.environ.get('PORT', 7860))
    app.run(host="0.0.0.0", port=port, debug=False)