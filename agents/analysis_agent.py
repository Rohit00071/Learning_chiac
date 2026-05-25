import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from utils.logger import get_logger

logger = get_logger(__name__)

class AnalysisAgent:
    """
    Analysis Agent responsible for detecting learning patterns, analyzing student performance,
    and generating statistics including ML-based clustering and prediction.
    """

    def __init__(self):
        """Initialize the Analysis Agent."""
        self.data = None
        self.analysis_results = {}
        logger.info("AnalysisAgent initialized")

    def load_data(self, data):
        """
        Load data for analysis.

        Args:
            data (pd.DataFrame): Learner data
        """
        self.data = data.copy() if data is not None else None
        if self.data is not None:
            logger.info(f"AnalysisAgent loaded data with shape {self.data.shape}")
        else:
            logger.warning("No data provided to AnalysisAgent")

    def analyze_performance(self):
        """
        Analyze student performance statistics.

        Returns:
            dict: Performance analysis results
        """
        if self.data is None or self.data.empty:
            logger.warning("No data available for performance analysis")
            return {}

        logger.info("Performing performance analysis")

        results = {}

        # Basic statistics
        results['mean_quiz_score'] = self.data['quiz_score'].mean()
        results['mean_assignment_score'] = self.data['assignment_score'].mean()
        results['median_quiz_score'] = self.data['quiz_score'].median()
        results['median_assignment_score'] = self.data['assignment_score'].median()
        results['std_quiz_score'] = self.data['quiz_score'].std()
        results['std_assignment_score'] = self.data['assignment_score'].std()

        # Score distributions
        results['quiz_score_distribution'] = {
            'min': self.data['quiz_score'].min(),
            'max': self.data['quiz_score'].max(),
            '25th': self.data['quiz_score'].quantile(0.25),
            '75th': self.data['quiz_score'].quantile(0.75)
        }
        results['assignment_score_distribution'] = {
            'min': self.data['assignment_score'].min(),
            'max': self.data['assignment_score'].max(),
            '25th': self.data['assignment_score'].quantile(0.25),
            '75th': self.data['assignment_score'].quantile(0.75)
        }

        # Attendance and completion stats
        results['mean_attendance'] = self.data['attendance_percentage'].mean()
        results['mean_completion'] = self.data['completion_percentage'].mean()
        results['std_attendance'] = self.data['attendance_percentage'].std()
        results['std_completion'] = self.data['completion_percentage'].std()

        # Study hours statistics
        results['mean_study_hours'] = self.data['study_hours'].mean()
        results['median_study_hours'] = self.data['study_hours'].median()

        # Weak students (bottom 20% by average score)
        self.data['average_score'] = (self.data['quiz_score'] + self.data['assignment_score']) / 2
        weak_threshold = self.data['average_score'].quantile(0.2)
        results['weak_students_count'] = len(self.data[self.data['average_score'] < weak_threshold])
        results['weak_students_percentage'] = (results['weak_students_count'] / len(self.data)) * 100

        # Top performers (top 20% by average score)
        top_threshold = self.data['average_score'].quantile(0.8)
        results['top_performers_count'] = len(self.data[self.data['average_score'] >= top_threshold])
        results['top_performers_percentage'] = (results['top_performers_count'] / len(self.data)) * 100

        # Course difficulty detection (average score per course)
        course_performance = self.data.groupby('course').agg({
            'quiz_score': 'mean',
            'assignment_score': 'mean',
            'average_score': 'mean'
        }).round(2)
        results['course_difficulty'] = course_performance.sort_values('average_score').to_dict('index')

        # Topic weakness analysis
        # Parse weak_topics and count frequency
        all_topics = []
        for topics_str in self.data['weak_topics'].dropna():
            if isinstance(topics_str, str):
                topics = [t.strip() for t in topics_str.split(',')]
                all_topics.extend(topics)

        if all_topics:
            from collections import Counter
            topic_counts = Counter(all_topics)
            results['topic_weakness'] = dict(topic_counts.most_common(10))
        else:
            results['topic_weakness'] = {}

        # Correlation analysis
        numeric_cols = ['quiz_score', 'assignment_score', 'attendance_percentage',
                       'completion_percentage', 'study_hours', 'submission_delay_days']
        available_cols = [col for col in numeric_cols if col in self.data.columns]
        if len(available_cols) >= 2:
            correlation_matrix = self.data[available_cols].corr()
            results['correlations'] = correlation_matrix.round(3).to_dict()
        else:
            results['correlations'] = {}

        # Attendance impact analysis
        if 'attendance_percentage' in self.data.columns and 'average_score' in self.data.columns:
            # Split attendance into high/low groups
            high_attendance = self.data[self.data['attendance_percentage'] >= 80]['average_score'].mean()
            low_attendance = self.data[self.data['attendance_percentage'] < 60]['average_score'].mean()
            results['attendance_impact'] = {
                'high_attendance_avg_score': high_attendance if not np.isnan(high_attendance) else 0,
                'low_attendance_avg_score': low_attendance if not np.isnan(low_attendance) else 0,
                'difference': high_attendance - low_attendance if not (np.isnan(high_attendance) or np.isnan(low_attendance)) else 0
            }

        self.analysis_results['performance'] = results
        logger.info("Performance analysis completed")
        return results

    def perform_clustering(self, n_clusters=3):
        """
        Perform KMeans clustering for learner segmentation.

        Args:
            n_clusters (int): Number of clusters

        Returns:
            dict: Clustering results including cluster assignments and centroids
        """
        if self.data is None or self.data.empty:
            logger.warning("No data available for clustering")
            return {}

        logger.info(f"Performing KMeans clustering with {n_clusters} clusters")

        # Select features for clustering
        feature_columns = ['quiz_score', 'assignment_score', 'attendance_percentage',
                          'completion_percentage', 'study_hours']
        available_features = [col for col in feature_columns if col in self.data.columns]

        if len(available_features) < 2:
            logger.warning("Insufficient features for clustering")
            return {}

        try:
            # Prepare data
            X = self.data[available_features].fillna(self.data[available_features].median())

            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Perform KMeans
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            cluster_labels = kmeans.fit_predict(X_scaled)

            # Add cluster labels to data
            self.data['cluster'] = cluster_labels

            # Calculate cluster statistics
            cluster_stats = {}
            for i in range(n_clusters):
                cluster_data = self.data[self.data['cluster'] == i]
                cluster_stats[f'cluster_{i}'] = {
                    'size': len(cluster_data),
                    'percentage': (len(cluster_data) / len(self.data)) * 100,
                    'mean_quiz_score': cluster_data['quiz_score'].mean(),
                    'mean_assignment_score': cluster_data['assignment_score'].mean(),
                    'mean_attendance': cluster_data['attendance_percentage'].mean(),
                    'mean_completion': cluster_data['completion_percentage'].mean(),
                    'mean_study_hours': cluster_data['study_hours'].mean()
                }

            results = {
                'cluster_labels': cluster_labels.tolist(),
                'cluster_centroids': kmeans.cluster_centers_.tolist(),
                'feature_names': available_features,
                'cluster_statistics': cluster_stats,
                'inertia': kmeans.inertia_
            }

            self.analysis_results['clustering'] = results
            logger.info(f"Clustering completed. Inertia: {kmeans.inertia_:.2f}")
            return results

        except Exception as e:
            logger.error(f"Error during clustering: {e}")
            return {}

    def predict_performance_risk(self):
        """
        Basic prediction model for performance risk using rule-based approach.
        Returns risk scores for each student.

        Returns:
            dict: Risk predictions for students
        """
        if self.data is None or self.data.empty:
            logger.warning("No data available for risk prediction")
            return {}

        logger.info("Predicting performance risk")

        try:
            # Risk factors (weighted)
            risk_scores = []

            for _, student in self.data.iterrows():
                risk = 0.0

                # Low scores increase risk
                avg_score = (student['quiz_score'] + student['assignment_score']) / 2
                if avg_score < 60:
                    risk += 0.3
                elif avg_score < 70:
                    risk += 0.15

                # Low attendance increases risk
                if student['attendance_percentage'] < 60:
                    risk += 0.25
                elif student['attendance_percentage'] < 80:
                    risk += 0.1

                # Low completion increases risk
                if student['completion_percentage'] < 50:
                    risk += 0.2
                elif student['completion_percentage'] < 70:
                    risk += 0.1

                # High submission delay increases risk
                if student['submission_delay_days'] > 3:
                    risk += 0.15
                elif student['submission_delay_days'] > 1:
                    risk += 0.05

                # Low study hours increases risk
                if student['study_hours'] < 3:
                    risk += 0.1

                # Cap risk at 1.0
                risk = min(risk, 1.0)
                risk_scores.append(risk)

            self.data['risk_score'] = risk_scores

            # Categorize risk levels
            risk_categories = []
            for score in risk_scores:
                if score >= 0.7:
                    risk_categories.append('High')
                elif score >= 0.4:
                    risk_categories.append('Medium')
                else:
                    risk_categories.append('Low')

            self.data['risk_category'] = risk_categories

            # Summary statistics
            high_risk_count = sum(1 for cat in risk_categories if cat == 'High')
            medium_risk_count = sum(1 for cat in risk_categories if cat == 'Medium')
            low_risk_count = sum(1 for cat in risk_categories if cat == 'Low')

            results = {
                'risk_scores': risk_scores,
                'risk_categories': risk_categories,
                'high_risk_count': high_risk_count,
                'medium_risk_count': medium_risk_count,
                'low_risk_count': low_risk_count,
                'high_risk_percentage': (high_risk_count / len(self.data)) * 100,
                'medium_risk_percentage': (medium_risk_count / len(self.data)) * 100,
                'low_risk_percentage': (low_risk_count / len(self.data)) * 100,
                'students_at_risk': self.data[self.data['risk_category'] == 'High'][['student_id', 'student_name', 'course']].to_dict('records')
            }

            self.analysis_results['risk_prediction'] = results
            logger.info(f"Risk prediction completed. High risk: {high_risk_count} students")
            return results

        except Exception as e:
            logger.error(f"Error during risk prediction: {e}")
            return {}

    def get_analysis_summary(self):
        """
        Get a summary of all analysis performed.

        Returns:
            dict: Summary of analysis results
        """
        summary = {
            'data_loaded': self.data is not None and not self.data.empty,
            'record_count': len(self.data) if self.data is not None else 0,
            'analysis_performed': list(self.analysis_results.keys())
        }

        # Add key metrics from each analysis
        if 'performance' in self.analysis_results:
            perf = self.analysis_results['performance']
            summary['mean_quiz_score'] = perf.get('mean_quiz_score', 0)
            summary['weak_students_percentage'] = perf.get('weak_students_percentage', 0)
            summary['top_performers_percentage'] = perf.get('top_performers_percentage', 0)

        if 'clustering' in self.analysis_results:
            summary['clusters_identified'] = len(self.analysis_results['clustering'].get('cluster_statistics', {}))

        if 'risk_prediction' in self.analysis_results:
            risk = self.analysis_results['risk_prediction']
            summary['high_risk_percentage'] = risk.get('high_risk_percentage', 0)

        return summary

    def get_data_with_analysis(self):
        """
        Get the data augmented with analysis results (clusters, risk scores, etc.).

        Returns:
            pd.DataFrame: Data with analysis columns added
        """
        return self.data.copy() if self.data is not None else None