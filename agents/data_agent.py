import pandas as pd
import numpy as np
from pathlib import Path
from utils.logger import get_logger
from utils.synthetic_data_generator import generate_synthetic_data
from database.database import LearningDatabase

logger = get_logger(__name__)

class DataAgent:
    """
    Data Agent responsible for loading, cleaning, normalizing, and storing learner data.
    Also generates synthetic data when no file is uploaded.
    """

    def __init__(self, db_path=None):
        """
        Initialize the Data Agent.

        Args:
            db_path (Path, optional): Path to SQLite database.
        """
        self.db = LearningDatabase(db_path)
        self.data = None
        self.processed_data = None
        logger.info("DataAgent initialized")

    def load_csv(self, file_path):
        """
        Load learner data from CSV file.

        Args:
            file_path (str or Path): Path to CSV file

        Returns:
            pd.DataFrame: Loaded data
        """
        try:
            self.data = pd.read_csv(file_path)
            logger.info(f"Loaded CSV data from {file_path} with shape {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading CSV file {file_path}: {e}")
            raise

    def load_from_database(self):
        """
        Load learner data from database.

        Returns:
            pd.DataFrame: Learner data from database
        """
        try:
            self.data = self.db.load_learner_data()
            logger.info(f"Loaded data from database with shape {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Error loading data from database: {e}")
            raise

    def generate_synthetic_data(self, num_students=100):
        """
        Generate synthetic learner data.

        Args:
            num_students (int): Number of students to generate

        Returns:
            pd.DataFrame: Synthetic learner data
        """
        try:
            self.data = generate_synthetic_data(num_students)
            logger.info(f"Generated synthetic data with shape {self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"Error generating synthetic data: {e}")
            raise

    def validate_data(self, df=None):
        """
        Validate learner data for required fields and data types.

        Args:
            df (pd.DataFrame, optional): Data to validate. If None, uses self.data

        Returns:
            tuple: (is_valid, errors_list)
        """
        if df is None:
            df = self.data

        if df is None or df.empty:
            return False, ["No data provided"]

        required_columns = [
            'student_id', 'student_name', 'course', 'quiz_score', 'assignment_score',
            'attendance_percentage', 'completion_percentage', 'study_hours',
            'weak_topics', 'learning_speed', 'submission_delay_days'
        ]

        errors = []

        # Check for missing columns
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {missing_cols}")

        # Check data types and ranges if no missing columns
        if not missing_cols:
            # Check score ranges
            if not df['quiz_score'].between(0, 100).all():
                errors.append("quiz_score must be between 0 and 100")
            if not df['assignment_score'].between(0, 100).all():
                errors.append("assignment_score must be between 0 and 100")

            # Check percentage ranges
            if not df['attendance_percentage'].between(0, 100).all():
                errors.append("attendance_percentage must be between 0 and 100")
            if not df['completion_percentage'].between(0, 100).all():
                errors.append("completion_percentage must be between 0 and 100")

            # Check study hours (reasonable range)
            if not df['study_hours'].between(0, 24).all():
                errors.append("study_hours should be between 0 and 24")

            # Check submission delay
            if not df['submission_delay_days'].between(0, 30).all():
                errors.append("submission_delay_days should be between 0 and 30")

            # Check learning_speed values
            valid_speeds = ['slow', 'medium', 'fast']
            if not df['learning_speed'].isin(valid_speeds).all():
                errors.append(f"learning_speed must be one of {valid_speeds}")

        is_valid = len(errors) == 0
        return is_valid, errors

    def clean_data(self, df=None):
        """
        Clean learner data by handling missing values and outliers.

        Args:
            df (pd.DataFrame, optional): Data to clean. If None, uses self.data

        Returns:
            pd.DataFrame: Cleaned data
        """
        if df is None:
            df = self.data.copy()
        else:
            df = df.copy()

        if df is None or df.empty:
            logger.warning("No data to clean")
            return df

        logger.info(f"Cleaning data with shape {df.shape}")

        # Handle missing values
        numeric_columns = ['quiz_score', 'assignment_score', 'attendance_percentage',
                          'completion_percentage', 'study_hours', 'submission_delay_days']

        for col in numeric_columns:
            if col in df.columns:
                # Fill missing values with median for numeric columns
                df[col] = df[col].fillna(df[col].median())

        # Fill missing categorical values
        categorical_columns = ['student_name', 'course', 'weak_topics', 'learning_speed']
        for col in categorical_columns:
            if col in df.columns:
                # Fill with mode or default value
                if df[col].notna().any():
                    df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else "Unknown")
                else:
                    df[col] = df[col].fillna("Unknown")

        # Handle outliers for scores (cap at 1st and 99th percentiles)
        score_columns = ['quiz_score', 'assignment_score']
        for col in score_columns:
            if col in df.columns:
                lower_bound = df[col].quantile(0.01)
                upper_bound = df[col].quantile(0.99)
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)

        # Ensure percentages are within bounds
        percentage_columns = ['attendance_percentage', 'completion_percentage']
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].clip(0, 100)

        # Ensure study hours are non-negative
        if 'study_hours' in df.columns:
            df['study_hours'] = df['study_hours'].clip(lower=0)

        # Ensure submission delay is non-negative
        if 'submission_delay_days' in df.columns:
            df['submission_delay_days'] = df['submission_delay_days'].clip(lower=0)

        self.processed_data = df
        logger.info(f"Data cleaning completed. Shape: {df.shape}")
        return df

    def normalize_data(self, df=None):
        """
        Normalize numeric fields to 0-1 scale for analysis.

        Args:
            df (pd.DataFrame, optional): Data to normalize. If None, uses processed data

        Returns:
            pd.DataFrame: Normalized data
        """
        if df is None:
            df = self.processed_data.copy() if self.processed_data is not None else self.data.copy()
        else:
            df = df.copy()

        if df is None or df.empty:
            logger.warning("No data to normalize")
            return df

        logger.info("Normalizing numeric fields")

        # Columns to normalize
        normalize_columns = ['quiz_score', 'assignment_score', 'attendance_percentage',
                           'completion_percentage', 'study_hours']

        for col in normalize_columns:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                if max_val > min_val:  # Avoid division by zero
                    df[f'{col}_normalized'] = (df[col] - min_val) / (max_val - min_val)
                else:
                    df[f'{col}_normalized'] = 0.0  # All values are the same

        logger.info("Normalization completed")
        return df

    def save_to_database(self, df=None):
        """
        Save processed data to database.

        Args:
            df (pd.DataFrame, optional): Data to save. If None, uses processed data
        """
        if df is None:
            df = self.processed_data

        if df is not None and not df.empty:
            try:
                # Select only the original columns (excluding normalized ones)
                original_columns = [col for col in df.columns if not col.endswith('_normalized')]
                save_df = df[original_columns].copy() if original_columns else df.copy()
                self.db.save_learner_data(save_df)
                logger.info("Data saved to database")
            except Exception as e:
                logger.error(f"Error saving data to database: {e}")
                raise
        else:
            logger.warning("No data to save to database")

    def get_data(self):
        """
        Get the current processed data.

        Returns:
            pd.DataFrame: Current data
        """
        return self.processed_data if self.processed_data is not None else self.data

    def close(self):
        """Close database connection."""
        self.db.close()