import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
DATABASE_DIR = BASE_DIR / "database"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
DATABASE_DIR.mkdir(exist_ok=True)

# Database configuration
DATABASE_PATH = DATABASE_DIR / "learning_analytics.db"

# Synthetic data configuration
SYNTHETIC_DATA_CONFIG = {
    "num_students": 100,
    "courses": ["Mathematics", "Physics", "Chemistry", "Biology", "History", "English", "Computer Science", "Machine Learning"],
    "topics": ["Algebra", "Calculus", "Statistics", "Mechanics", "Thermodynamics", "Organic Chemistry", "Genetics", "World War II", "Shakespeare", "Python", "Data Structures", "Algorithms"],
    "score_range": (0, 100),
    "study_hours_range": (0, 20),
    "attendance_range": (0, 100),
    "completion_range": (0, 100),
    "learning_speed_options": ["slow", "medium", "fast"],
    "submission_delay_range": (0, 5)
}

# Agent thresholds
INSIGHT_THRESHOLDS = {
    "high_study_hours": 5,
    "low_attendance": 60,
    "high_score": 85,
    "low_score": 60,
    "risk_score_threshold": 0.7
}

# UI Configuration
UI_CONFIG = {
    "theme": "light",  # or "dark"
    "primary_color": "#1f77b4",
    "background_color": "#ffffff",
    "secondary_background_color": "#f0f2f6",
    "text_color": "#262730",
    "font": "sans-serif"
}

# Export settings
EXPORT_CONFIG = {
    "pdf_page_size": "letter",
    "pdf_margin": [0.5, 0.5, 0.5, 0.5],  # inches
    "chart_width": 800,
    "chart_height": 600
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "app.log",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}