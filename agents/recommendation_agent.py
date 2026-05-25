import pandas as pd
from typing import List, Dict
from utils.logger import get_logger

logger = get_logger(__name__)

class RecommendationAgent:
    """
    Recommendation Agent responsible for generating personalized recommendations
    for students and courses based on analysis and insights.
    """

    def __init__(self):
        """Initialize the Recommendation Agent."""
        self.recommendations = []
        logger.info("RecommendationAgent initialized")

    def generate_recommendations(self, data: pd.DataFrame, analysis_results: Dict, insights: List[Dict] = None) -> List[Dict]:
        """
        Generate recommendations based on data, analysis, and insights.

        Args:
            data (pd.DataFrame): Learner data with analysis columns (clusters, risk scores, etc.)
            analysis_results (Dict): Results from AnalysisAgent
            insights (List[Dict], optional): Insights from InsightAgent

        Returns:
            List[Dict]: List of recommendations with student_id, text, category, and priority
        """
        self.recommendations = []  # Reset recommendations

        if data is None or data.empty:
            logger.warning("No data provided for recommendation generation")
            return self.recommendations

        logger.info("Generating recommendations")

        # Generate student-specific recommendations
        self._generate_student_recommendations(data, analysis_results)

        # Generate course-level recommendations
        self._generate_course_recommendations(data, analysis_results)

        # Generate general recommendations based on insights
        if insights:
            self._generate_insight_based_recommendations(insights)

        logger.info(f"Generated {len(self.recommendations)} recommendations")
        return self.recommendations

    def _generate_student_recommendations(self, data: pd.DataFrame, analysis_results: Dict):
        """Generate personalized recommendations for individual students."""
        # Check if we have risk scores or clusters
        has_risk = 'risk_score' in data.columns
        has_cluster = 'cluster' in data.columns

        for _, student in data.iterrows():
            student_id = student['student_id']
            student_name = student['student_name']
            course = student['course']
            recommendations_for_student = []

            # Risk-based recommendations
            if has_risk:
                risk_score = student['risk_score']
                risk_category = student.get('risk_category', 'Low')

                if risk_category == 'High':
                    recommendations_for_student.append({
                        'text': f"Immediate intervention recommended: Schedule one-on-one tutoring sessions and develop a personalized learning plan.",
                        'category': 'Mentor Intervention',
                        'priority': 'High'
                    })
                elif risk_category == 'Medium':
                    recommendations_for_student.append({
                        'text': f"Consider additional practice assignments and weekly check-ins to monitor progress.",
                        'category': 'Practice',
                        'priority': 'Medium'
                    })

            # Score-based recommendations
            quiz_score = student['quiz_score']
            assignment_score = student['assignment_score']
            avg_score = (quiz_score + assignment_score) / 2

            if avg_score < 60:
                recommendations_for_student.append({
                    'text': f"Focus on foundational concepts through remedial lessons and practice exercises.",
                    'category': 'Topic Revision',
                    'priority': 'High'
                })
                if quiz_score < assignment_score:
                    recommendations_for_student.append({
                        'text': f"Improve test-taking strategies and time management for quizzes.",
                        'category': 'Practice',
                        'priority': 'Medium'
                    })
                else:
                    recommendations_for_student.append({
                        'text': f"Work on assignment quality and depth of understanding.",
                        'category': 'Practice',
                        'priority': 'Medium'
                    })
            elif avg_score < 75:
                recommendations_for_student.append({
                    'text': f"Engage in regular practice to solidify understanding and aim for consistent improvement.",
                    'category': 'Practice',
                    'priority': 'Medium'
                })

            # Attendance-based recommendations
            attendance = student['attendance_percentage']
            if attendance < 60:
                recommendations_for_student.append({
                    'text': f"Improve attendance to at least 80% to significantly boost learning outcomes.",
                    'category': 'Schedule',
                    'priority': 'High'
                })
            elif attendance < 80:
                recommendations_for_student.append({
                    'text': f"Strive for better attendance consistency to maintain learning momentum.",
                    'category': 'Schedule',
                    'priority': 'Medium'
                })

            # Study hours recommendations
            study_hours = student['study_hours']
            if study_hours < 3:
                recommendations_for_student.append({
                    'text': f"Increase weekly study time to at least 5 hours for better concept retention.",
                    'category': 'Schedule',
                    'priority': 'Medium'
                })
            elif study_hours > 15:
                recommendations_for_student.append({
                    'text': f"Consider balancing study time with adequate rest to prevent burnout.",
                    'category': 'Schedule',
                    'priority': 'Low'
                })

            # Submission delay recommendations
            delay = student['submission_delay_days']
            if delay > 3:
                recommendations_for_student.append({
                    'text': f"Work on time management skills to reduce submission delays and avoid last-minute stress.",
                    'category': 'Schedule',
                    'priority': 'Medium'
                })

            # Add all recommendations for this student
            for rec in recommendations_for_student:
                self.recommendations.append({
                    'student_id': student_id,
                    'student_name': student_name,
                    'course': course,
                    'text': rec['text'],
                    'category': rec['category'],
                    'priority': rec['priority']
                })

    def _generate_course_recommendations(self, data: pd.DataFrame, analysis_results: Dict):
        """Generate recommendations at the course level."""
        if data is None or data.empty:
            return

        # Course performance analysis
        agg_dict = {
            'quiz_score': 'mean',
            'assignment_score': 'mean',
            'attendance_percentage': 'mean',
            'completion_percentage': 'mean',
            'study_hours': 'mean',
        }
        if 'risk_score' in data.columns:
            agg_dict['risk_score'] = 'mean'

        course_stats = data.groupby('course').agg(agg_dict).round(2)

        for course, stats in course_stats.iterrows():
            course_recommendations = []

            # Low course performance
            avg_score = (stats['quiz_score'] + stats['assignment_score']) / 2
            if avg_score < 70:
                course_recommendations.append({
                    'text': f"Review and potentially revise course curriculum or teaching methods for {course}.",
                    'category': 'Curriculum Review',
                    'priority': 'High'
                })

            # Low attendance in course
            if stats['attendance_percentage'] < 70:
                course_recommendations.append({
                    'text': f"Investigate reasons for low attendance in {course} and consider engagement strategies.",
                    'category': 'Engagement',
                    'priority': 'Medium'
                })

            # Low completion in course
            if stats['completion_percentage'] < 70:
                course_recommendations.append({
                    'text': f"Provide additional support and resources to improve completion rates in {course}.",
                    'category': 'Support',
                    'priority': 'Medium'
                })

            # High risk in course
            if 'risk_score' in stats and stats['risk_score'] > 0.5:
                course_recommendations.append({
                    'text': f"Implement early warning system and proactive support for students in {course}.",
                    'category': 'Intervention',
                    'priority': 'High'
                })

            # Add course-level recommendations (apply to all students in course)
            for rec in course_recommendations:
                # Get students in this course
                course_students = data[data['course'] == course]
                for _, student in course_students.iterrows():
                    self.recommendations.append({
                        'student_id': student['student_id'],
                        'student_name': student['student_name'],
                        'course': course,
                        'text': rec['text'],
                        'category': rec['category'],
                        'priority': rec['priority']
                    })

    def _generate_insight_based_recommendations(self, insights: List[Dict]):
        """Generate recommendations based on insights from InsightAgent."""
        for insight in insights:
            insight_text = insight['text']
            category = insight['category']
            priority = insight['priority']

            # Map insight categories to recommendation categories
            recommendation_mapping = {
                'Performance': 'Practice',
                'Segmentation': 'Mentor Intervention',
                'Risk Prediction': 'Mentor Intervention',
                'Study Habits': 'Schedule',
                'Attendance': 'Schedule',
                'Attendance Impact': 'Schedule',
                'Course Difficulty': 'Curriculum Review'
            }

            rec_category = recommendation_mapping.get(category, 'General')

            # Create a general recommendation based on the insight
            self.recommendations.append({
                'student_id': 'GENERAL',
                'student_name': 'All Students',
                'course': 'All Courses',
                'text': f"Based on analysis: {insight_text}",
                'category': rec_category,
                'priority': priority
            })

    def get_student_recommendations(self, student_id: str) -> List[Dict]:
        """
        Get recommendations for a specific student.

        Args:
            student_id (str): Student ID

        Returns:
            List[Dict]: Recommendations for the student
        """
        return [rec for rec in self.recommendations if rec['student_id'] == student_id]

    def get_course_recommendations(self, course: str) -> List[Dict]:
        """
        Get recommendations for a specific course.

        Args:
            course (str): Course name

        Returns:
            List[Dict]: Recommendations for the course
        """
        return [rec for rec in self.recommendations if rec['course'] == course and rec['student_id'] != 'GENERAL']

    def get_general_recommendations(self) -> List[Dict]:
        """
        Get general recommendations applicable to all students.

        Returns:
            List[Dict]: General recommendations
        """
        return [rec for rec in self.recommendations if rec['student_id'] == 'GENERAL']

    def get_prioritized_recommendations(self, priority: str) -> List[Dict]:
        """
        Get recommendations filtered by priority.

        Args:
            priority (str): Priority level (High, Medium, Low)

        Returns:
            List[Dict]: Filtered recommendations
        """
        return [rec for rec in self.recommendations if rec['priority'] == priority]

    def format_recommendations_for_display(self, student_id: str = None) -> str:
        """
        Format recommendations for display in the dashboard.

        Args:
            student_id (str, optional): If provided, show only recommendations for this student

        Returns:
            str: Formatted recommendations string
        """
        if student_id:
            recs = self.get_student_recommendations(student_id)
            title = f"Recommendations for Student {student_id}"
        else:
            recs = self.recommendations
            title = "All Recommendations"

        if not recs:
            return f"{title}\n\nNo recommendations generated."

        formatted = [title, "=" * len(title)]
        for rec in recs:
            priority_emoji = {
                'High': '🔴',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(rec['priority'], '⚪')

            formatted.append(
                f"{priority_emoji} [{rec['category']}] {rec['text']}"
                f"\n   Student: {rec['student_name']} ({rec['student_id']}) | Course: {rec['course']}"
            )

        return "\n\n".join(formatted)