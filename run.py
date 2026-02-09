"""Development server entry point for ProjectFlow.

Usage:
    python run.py

The server starts on http://localhost:5000 with debug mode enabled.
"""

from projectflow import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
