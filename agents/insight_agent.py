import pandas as pd
from typing import List, Dict
from utils.logger import get_logger
from utils.config import INSIGHT_THRESHOLDS

logger = get_logger(__name__)

class InsightAgent:
    """
    Insight Agent responsible for converting analytics into human-readable insights.
    Generates rule-based insights with priority tagging (High, Medium, Low).
    """

    def __init__(self):
        """Initialize the Insight Agent."""
        self.insights = []
        logger.info("InsightAgent initialized")

    def generate_insights(self, analysis_results: Dict) -> List[Dict]:
        """
        Generate insights from analysis results.

        Args:
            analysis_results (Dict): Results from AnalysisAgent

        Returns:
            List[Dict]: List of insights with text, priority, and category
        """
        self.insights = []  # Reset insights

        if not analysis_results:
            logger.warning("No analysis results provided for insight generation")
            return self.insights

        logger.info("Generating insights from analysis results")

        # Performance insights
        self._generate_performance_insights(analysis_results.get('performance', {}))

        # Clustering insights
        self._generate_clustering_insights(analysis_results.get('clustering', {}))

        # Risk prediction insights
        self._generate_risk_insights(analysis_results.get('risk_prediction', {}))

        # Correlation insights
        self._generate_correlation_insights(analysis_results.get('correlations', {}))

        # Attendance impact insights
        self._generate_attendance_insights(analysis_results.get('attendance_impact', {}))

        logger.info(f"Generated {len(self.insights)} insights")
        return self.insights

    def _generate_performance_insights(self, perf_results):
        """Generate insights from performance analysis."""
        if not perf_results:
            return

        mean_quiz = perf_results.get('mean_quiz_score', 0)
        mean_assignment = perf_results.get('mean_assignment_score', 0)
        weak_pct = perf_results.get('weak_students_percentage', 0)
        top_pct = perf_results.get('top_performers_percentage', 0)

        # Overall performance insight
        if mean_quiz >= 80 and mean_assignment >= 80:
            self.insights.append({
                'text': f"Overall class performance is strong with average quiz score of {mean_quiz:.1f} and assignment score of {mean_assignment:.1f}.",
                'priority': 'Medium',
                'category': 'Performance'
            })
        elif mean_quiz < 60 or mean_assignment < 60:
            self.insights.append({
                'text': f"Overall class performance needs improvement with average quiz score of {mean_quiz:.1f} and assignment score of {mean_assignment:.1f}.",
                'priority': 'High',
                'category': 'Performance'
            })
        else:
            self.insights.append({
                'text': f"Overall class performance is moderate with average quiz score of {mean_quiz:.1f} and assignment score of {mean_assignment:.1f}.",
                'priority': 'Medium',
                'category': 'Performance'
            })

        # Weak students insight
        if weak_pct > 30:
            self.insights.append({
                'text': f"High percentage of students ({weak_pct:.1f}%) are struggling with scores below 60%. Consider intervention strategies.",
                'priority': 'High',
                'category': 'Performance'
            })
        elif weak_pct > 15:
            self.insights.append({
                'text': f"Moderate percentage of students ({weak_pct:.1f}%) need additional support to improve scores.",
                'priority': 'Medium',
                'category': 'Performance'
            })
        else:
            self.insights.append({
                'text': f"Low percentage of students ({weak_pct:.1f}%) are struggling, indicating effective teaching methods.",
                'priority': 'Low',
                'category': 'Performance'
            })

        # Top performers insight
        if top_pct > 30:
            self.insights.append({
                'text': f"Excellent performance by {top_pct:.1f}% of students scoring above 80%. Consider challenging them with advanced material.",
                'priority': 'Medium',
                'category': 'Performance'
            })

        # Course difficulty insights
        course_difficulty = perf_results.get('course_difficulty', {})
        if course_difficulty:
            # Find easiest and hardest courses
            sorted_courses = sorted(course_difficulty.items(), key=lambda x: x[1]['average_score'])
            if sorted_courses:
                hardest_course = sorted_courses[0]
                easiest_course = sorted_courses[-1]

                if hardest_course[1]['average_score'] < 60:
                    self.insights.append({
                        'text': f"'{hardest_course[0]}' is the most challenging course with average score of {hardest_course[1]['average_score']:.1f}. Consider additional support resources.",
                        'priority': 'High',
                        'category': 'Course Difficulty'
                    })

                if easiest_course[1]['average_score'] > 85:
                    self.insights.append({
                        'text': f"'{easiest_course[0]}' has the highest performance with average score of {easiest_course[1]['average_score']:.1f}. Successful teaching practices could be shared.",
                        'priority': 'Medium',
                        'category': 'Course Difficulty'
                    })

    def _generate_clustering_insights(self, cluster_results):
        """Generate insights from clustering analysis."""
        if not cluster_results:
            return

        cluster_stats = cluster_results.get('cluster_statistics', {})
        if not cluster_stats:
            return

        # Find clusters needing attention
        for cluster_id, stats in cluster_stats.items():
            size_pct = stats.get('percentage', 0)
            mean_quiz = stats.get('mean_quiz_score', 0)
            mean_attendance = stats.get('mean_attendance', 0)

            if size_pct > 20:  # Significant cluster
                if mean_quiz < 60 and mean_attendance < 70:
                    self.insights.append({
                        'text': f"Cluster {cluster_id.replace('cluster_', '')} represents {size_pct:.1f}% of students with low quiz scores ({mean_quiz:.1f}) and attendance ({mean_attendance:.1f}%). Targeted intervention needed.",
                        'priority': 'High',
                        'category': 'Segmentation'
                    })
                elif mean_quiz > 80 and mean_attendance > 85:
                    self.insights.append({
                        'text': f"Cluster {cluster_id.replace('cluster_', '')} represents {size_pct:.1f}% of high-performing students with strong quiz scores ({mean_quiz:.1f}) and attendance ({mean_attendance:.1f}).",
                        'priority': 'Medium',
                        'category': 'Segmentation'
                    })

    def _generate_risk_insights(self, risk_results):
        """Generate insights from risk prediction."""
        if not risk_results:
            return

        high_risk_pct = risk_results.get('high_risk_percentage', 0)
        medium_risk_pct = risk_results.get('medium_risk_percentage', 0)

        if high_risk_pct > 20:
            self.insights.append({
                'text': f"High risk alert: {high_risk_pct:.1f}% of students are at high risk of falling behind. Immediate intervention recommended.",
                'priority': 'High',
                'category': 'Risk Prediction'
            })
        elif high_risk_pct > 10:
            self.insights.append({
                'text': f"Moderate risk: {high_risk_pct:.1f}% of students are at high risk. Consider proactive support measures.",
                'priority': 'Medium',
                'category': 'Risk Prediction'
            })

        if medium_risk_pct > 40:
            self.insights.append({
                'text': f"Significant portion ({medium_risk_pct:.1f}%) of students at medium risk. Early intervention could prevent escalation.",
                'priority': 'Medium',
                'category': 'Risk Prediction'
            })

    def _generate_correlation_insights(self, correlations):
        """Generate insights from correlation analysis."""
        if not correlations:
            return

        # Check study hours vs scores
        study_hours_quiz_corr = correlations.get('study_hours', {}).get('quiz_score', 0)
        study_hours_assignment_corr = correlations.get('study_hours', {}).get('assignment_score', 0)

        if abs(study_hours_quiz_corr) > 0.5:
            direction = "positive" if study_hours_quiz_corr > 0 else "negative"
            self.insights.append({
                'text': f"Strong {direction} correlation ({study_hours_quiz_corr:.2f}) between study hours and quiz scores. Encouraging consistent study habits could improve performance.",
                'priority': 'High' if abs(study_hours_quiz_corr) > 0.7 else 'Medium',
                'category': 'Study Habits'
            })

        # Attendance vs scores
        attendance_quiz_corr = correlations.get('attendance_percentage', {}).get('quiz_score', 0)
        if abs(attendance_quiz_corr) > 0.4:
            direction = "positive" if attendance_quiz_corr > 0 else "negative"
            self.insights.append({
                'text': f"Moderate {direction} correlation ({attendance_quiz_corr:.2f}) between attendance and quiz scores. Attendance monitoring could help identify at-risk students early.",
                'priority': 'Medium',
                'category': 'Attendance'
            })

    def _generate_attendance_insights(self, attendance_impact):
        """Generate insights from attendance impact analysis."""
        if not attendance_impact:
            return

        high_att_score = attendance_impact.get('high_attendance_avg_score', 0)
        low_att_score = attendance_impact.get('low_attendance_avg_score', 0)
        difference = attendance_impact.get('difference', 0)

        if difference > 15:
            self.insights.append({
                'text': f"Attendance significantly impacts performance: students with >80% attendance score {high_att_score:.1f} vs <60% attendance scoring {low_att_score:.1f} (difference: {difference:.1f} points).",
                'priority': 'High',
                'category': 'Attendance Impact'
            })
        elif difference > 8:
            self.insights.append({
                'text': f"Attendance shows moderate impact on performance: {difference:.1f} point difference between high and low attendance groups.",
                'priority': 'Medium',
                'category': 'Attendance Impact'
            })

    def get_prioritized_insights(self, priority=None):
        """
        Get insights filtered by priority.

        Args:
            priority (str, optional): Filter by priority level (High, Medium, Low)

        Returns:
            List[Dict]: Filtered insights
        """
        if priority is None:
            return self.insights
        return [insight for insight in self.insights if insight['priority'] == priority]

    def get_insights_by_category(self, category):
        """
        Get insights filtered by category.

        Args:
            category (str): Category to filter by

        Returns:
            List[Dict]: Filtered insights
        """
        return [insight for insight in self.insights if insight['category'] == category]

    def format_insights_for_display(self):
        """
        Format insights for display in the dashboard.

        Returns:
            str: Formatted insights string
        """
        if not self.insights:
            return "No insights generated."

        formatted = []
        for insight in self.insights:
            priority_emoji = {
                'High': '🔴',
                'Medium': '🟡',
                'Low': '🟢'
            }.get(insight['priority'], '⚪')

            formatted.append(
                f"{priority_emoji} **{insight['category']}**: {insight['text']}"
            )

        return "\n\n".join(formatted)