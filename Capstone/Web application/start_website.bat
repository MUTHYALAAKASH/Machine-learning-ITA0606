@echo off
title JobGuard AI - Fake Job Posting Detection System
color 0B
echo =========================================================================
echo   JobGuard AI: Intelligent Fake Job Posting Detection System
echo   Powered by Logistic Regression and Support Vector Machine (LinearSVC)
echo =========================================================================
echo.
echo [1/2] Checking Python environment and ML models...
python -c "from src.predictor import FakeJobDetector; d = FakeJobDetector.get_instance(); print('Models ready:', d.is_ready())"
echo.
echo [2/2] Launching Fast and Interactive Web Application on http://127.0.0.1:8000
echo Open your web browser and navigate to: http://127.0.0.1:8000
echo.
echo Press CTRL+C in this terminal window to terminate the web server.
echo =========================================================================
python run_server.py
pause
