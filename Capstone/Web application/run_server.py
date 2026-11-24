import uvicorn
import os
import sys

# Ensure current directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 65)
    print("  JobGuard AI: Intelligent Fake Job Posting Detection System")
    print("  Models: Logistic Regression & Support Vector Machine (SVM)")
    print("=" * 65)
    print("Starting server on: http://127.0.0.1:8000")
    print("Press CTRL+C to stop the server.")
    print("=" * 65)
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
