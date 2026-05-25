import pandas as pd
import numpy as np
from utils.config import SYNTHETIC_DATA_CONFIG, DATA_DIR
from utils.logger import get_logger

logger = get_logger(__name__)

class SyntheticDataGenerator:
    """
    Generates synthetic learner data for testing and demonstration.
    """

    def __init__(self):
        self.config = SYNTHETIC_DATA_CONFIG

    def generate_student_data(self, num_students=None):
        """
        Generate synthetic learner data.

        Args:
            num_students (int, optional): Number of students to generate.
                                        Defaults to config value.

        Returns:
            pd.DataFrame: DataFrame containing synthetic learner data
        """
        if num_students is None:
            num_students = self.config["num_students"]

        logger.info(f"Generating synthetic data for {num_students} students")

        # Generate data for each field
        student_ids = [f"STU{1000 + i}" for i in range(num_students)]
        first_names = ["Alex", "Sam", "Taylor", "Jordan", "Casey", "Riley", "Quinn", "Avery", "Peyton", "Morgan"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        student_names = [f"{np.random.choice(first_names)} {np.random.choice(last_names)}" for _ in range(num_students)]

        courses = np.random.choice(self.config["courses"], size=num_students)

        # Generate scores with some correlation to study hours
        study_hours = np.random.uniform(
            self.config["study_hours_range"][0],
            self.config["study_hours_range"][1],
            size=num_students
        )

        # Base score influenced by study hours (with noise)
        base_quiz_score = 50 + (study_hours * 2.5) + np.random.normal(0, 10, size=num_students)
        base_quiz_score = np.clip(base_quiz_score, self.config["score_range"][0], self.config["score_range"][1])

        base_assignment_score = 50 + (study_hours * 2.0) + np.random.normal(0, 8, size=num_students)
        base_assignment_score = np.clip(base_assignment_score, self.config["score_range"][0], self.config["score_range"][1])

        quiz_score = np.round(base_quiz_score, 1)
        assignment_score = np.round(base_assignment_score, 1)

        # Attendance and completion percentages
        attendance_percentage = np.random.uniform(
            self.config["attendance_range"][0],
            self.config["attendance_range"][1],
            size=num_students
        )
        attendance_percentage = np.round(attendance_percentage, 1)

        completion_percentage = np.random.uniform(
            self.config["completion_range"][0],
            self.config["completion_range"][1],
            size=num_students
        )
        completion_percentage = np.round(completion_percentage, 1)

        # Weak topics (each student gets 1-3 weak topics)
        weak_topics = []
        for _ in range(num_students):
            num_weak = np.random.randint(1, 4)
            topics = np.random.choice(self.config["topics"], size=num_weak, replace=False)
            weak_topics.append(", ".join(topics))

        # Learning speed
        learning_speed = np.random.choice(
            self.config["learning_speed_options"],
            size=num_students,
            p=[0.2, 0.6, 0.2]  # slow, medium, fast
        )

        # Submission delay days (inversely related to learning speed)
        submission_delay_days = np.random.randint(
            self.config["submission_delay_range"][0],
            self.config["submission_delay_range"][1] + 1,
            size=num_students
        )

        # Adjust submission delay based on learning speed (faster learners submit earlier)
        speed_mapping = {"slow": 1.5, "medium": 1.0, "fast": 0.5}
        submission_delay_days = np.round(submission_delay_days *
                                        np.array([speed_mapping[s] for s in learning_speed])).astype(int)
        submission_delay_days = np.clip(submission_delay_days, 0, 5)

        # Create DataFrame
        data = {
            "student_id": student_ids,
            "student_name": student_names,
            "course": courses,
            "quiz_score": quiz_score,
            "assignment_score": assignment_score,
            "attendance_percentage": attendance_percentage,
            "completion_percentage": completion_percentage,
            "study_hours": np.round(study_hours, 1),
            "weak_topics": weak_topics,
            "learning_speed": learning_speed,
            "submission_delay_days": submission_delay_days
        }

        df = pd.DataFrame(data)
        logger.info(f"Generated synthetic data with shape {df.shape}")
        return df

    def save_to_csv(self, df, filename="synthetic_learner_data.csv"):
        """
        Save synthetic data to CSV file.

        Args:
            df (pd.DataFrame): DataFrame to save
            filename (str): Output filename
        """
        filepath = DATA_DIR / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Synthetic data saved to {filepath}")
        return filepath

# Convenience function
def generate_synthetic_data(num_students=100):
    """
    Generate and return synthetic learner data.

    Args:
        num_students (int): Number of students to generate

    Returns:
        pd.DataFrame: Synthetic learner data
    """
    generator = SyntheticDataGenerator()
    return generator.generate_student_data(num_students)