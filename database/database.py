import sqlite3
import pandas as pd
from pathlib import Path
from utils.config import DATABASE_PATH
from utils.logger import get_logger

logger = get_logger(__name__)

class LearningDatabase:
    """
    Handles SQLite database operations for learner data and system snapshots.
    """

    def __init__(self, db_path=None):
        """
        Initialize the database connection.

        Args:
            db_path (Path, optional): Path to SQLite database file.
                                    Defaults to config value.
        """
        self.db_path = db_path or DATABASE_PATH
        self.connection = None
        self.cursor = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            # Learner data table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS learner_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT UNIQUE,
                    student_name TEXT,
                    course TEXT,
                    quiz_score REAL,
                    assignment_score REAL,
                    attendance_percentage REAL,
                    completion_percentage REAL,
                    study_hours REAL,
                    weak_topics TEXT,
                    learning_speed TEXT,
                    submission_delay_days INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Analysis snapshots table (for change tracking)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snapshot_data TEXT,  -- JSON string of analysis results
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insights table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    insight_text TEXT,
                    priority TEXT,  -- High, Medium, Low
                    category TEXT,  -- e.g., Performance, Attendance, etc.
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Recommendations table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT,
                    recommendation_text TEXT,
                    category TEXT,  -- e.g., Practice, Mentor, Schedule, Revision
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            self.connection.commit()
            logger.info("Database tables created or verified")
        except sqlite3.Error as e:
            logger.error(f"Table creation error: {e}")
            raise

    def load_learner_data(self):
        """
        Load learner data from database.

        Returns:
            pd.DataFrame: Learner data
        """
        try:
            query = "SELECT * FROM learner_data"
            df = pd.read_sql_query(query, self.connection)
            logger.info(f"Loaded {len(df)} learner records from database")
            return df
        except Exception as e:
            logger.error(f"Error loading learner data: {e}")
            return pd.DataFrame()

    def save_learner_data(self, df):
        """
        Save learner data to database (replaces existing data).

        Args:
            df (pd.DataFrame): Learner data to save
        """
        try:
            # Clear existing data
            self.cursor.execute("DELETE FROM learner_data")
            # Insert new data
            df.to_sql('learner_data', self.connection, if_exists='append', index=False)
            self.connection.commit()
            logger.info(f"Saved {len(df)} learner records to database")
        except Exception as e:
            logger.error(f"Error saving learner data: {e}")
            self.connection.rollback()
            raise

    def append_learner_data(self, df):
        """
        Append new learner data to database.

        Args:
            df (pd.DataFrame): Learner data to append
        """
        try:
            df.to_sql('learner_data', self.connection, if_exists='append', index=False)
            self.connection.commit()
            logger.info(f"Appended {len(df)} learner records to database")
        except Exception as e:
            logger.error(f"Error appending learner data: {e}")
            self.connection.rollback()
            raise

    def save_analysis_snapshot(self, snapshot_data):
        """
        Save analysis snapshot for change tracking.

        Args:
            snapshot_data (dict): Analysis results to save
        """
        try:
            import json
            snapshot_json = json.dumps(snapshot_data)
            self.cursor.execute(
                "INSERT INTO analysis_snapshots (snapshot_data) VALUES (?)",
                (snapshot_json,)
            )
            self.connection.commit()
            logger.info("Analysis snapshot saved")
        except Exception as e:
            logger.error(f"Error saving analysis snapshot: {e}")
            self.connection.rollback()

    def get_latest_analysis_snapshot(self):
        """
        Retrieve the most recent analysis snapshot.

        Returns:
            dict: Analysis snapshot data or None if not found
        """
        try:
            self.cursor.execute(
                "SELECT snapshot_data FROM analysis_snapshots ORDER BY timestamp DESC LIMIT 1"
            )
            row = self.cursor.fetchone()
            if row:
                import json
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Error retrieving analysis snapshot: {e}")
            return None

    def save_insight(self, insight_text, priority, category):
        """
        Save an insight to the database.

        Args:
            insight_text (str): The insight text
            priority (str): Priority level (High, Medium, Low)
            category (str): Insight category
        """
        try:
            self.cursor.execute(
                "INSERT INTO insights (insight_text, priority, category) VALUES (?, ?, ?)",
                (insight_text, priority, category)
            )
            self.connection.commit()
            logger.info(f"Insight saved: {insight_text[:50]}...")
        except Exception as e:
            logger.error(f"Error saving insight: {e}")
            self.connection.rollback()

    def get_insights(self, limit=50):
        """
        Retrieve insights from database.

        Args:
            limit (int): Maximum number of insights to retrieve

        Returns:
            list: List of insight dictionaries
        """
        try:
            self.cursor.execute(
                "SELECT insight_text, priority, category, timestamp FROM insights ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = self.cursor.fetchall()
            insights = []
            for row in rows:
                insights.append({
                    "text": row[0],
                    "priority": row[1],
                    "category": row[2],
                    "timestamp": row[3]
                })
            return insights
        except Exception as e:
            logger.error(f"Error retrieving insights: {e}")
            return []

    def save_recommendation(self, student_id, recommendation_text, category):
        """
        Save a recommendation to the database.

        Args:
            student_id (str): Student ID
            recommendation_text (str): Recommendation text
            category (str): Recommendation category
        """
        try:
            self.cursor.execute(
                "INSERT INTO recommendations (student_id, recommendation_text, category) VALUES (?, ?, ?)",
                (student_id, recommendation_text, category)
            )
            self.connection.commit()
            logger.info(f"Recommendation saved for student {student_id}")
        except Exception as e:
            logger.error(f"Error saving recommendation: {e}")
            self.connection.rollback()

    def get_recommendations(self, student_id=None, limit=100):
        """
        Retrieve recommendations from database.

        Args:
            student_id (str, optional): Filter by student ID
            limit (int): Maximum number of recommendations to retrieve

        Returns:
            list: List of recommendation dictionaries
        """
        try:
            if student_id:
                self.cursor.execute(
                    "SELECT student_id, recommendation_text, category, timestamp FROM recommendations WHERE student_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (student_id, limit)
                )
            else:
                self.cursor.execute(
                    "SELECT student_id, recommendation_text, category, timestamp FROM recommendations ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            rows = self.cursor.fetchall()
            recommendations = []
            for row in rows:
                recommendations.append({
                    "student_id": row[0],
                    "text": row[1],
                    "category": row[2],
                    "timestamp": row[3]
                })
            return recommendations
        except Exception as e:
            logger.error(f"Error retrieving recommendations: {e}")
            return []

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()