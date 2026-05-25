import pandas as pd
import json
from typing import Dict, List, Any
from utils.logger import get_logger
from database.database import LearningDatabase

logger = get_logger(__name__)

class ChangeDiffViewerAgent:
    """
    Change Diff Viewer Agent responsible for tracking differences between
    previous and current insights, highlighting changes and trends.
    """

    def __init__(self, db_path=None):
        """
        Initialize the Change Diff Viewer Agent.

        Args:
            db_path (Path, optional): Path to SQLite database.
        """
        self.db = LearningDatabase(db_path)
        self.current_insights = []
        self.previous_insights = []
        self.diff_results = {}
        logger.info("ChangeDiffViewerAgent initialized")

    def load_current_insights(self, insights: List[Dict]):
        """
        Load current insights for comparison.

        Args:
            insights (List[Dict]): Current insights from InsightAgent
        """
        self.current_insights = insights.copy() if insights else []
        logger.info(f"Loaded {len(self.current_insights)} current insights")

    def load_previous_insights(self):
        """
        Load previous insights from database snapshot.
        """
        try:
            snapshot = self.db.get_latest_analysis_snapshot()
            if snapshot and 'insights' in snapshot:
                self.previous_insights = snapshot['insights']
                logger.info(f"Loaded {len(self.previous_insights)} previous insights from database")
            else:
                self.previous_insights = []
                logger.info("No previous insights found in database")
        except Exception as e:
            logger.error(f"Error loading previous insights: {e}")
            self.previous_insights = []

    def get_latest_analysis_snapshot(self):
        """
        Get the latest analysis snapshot from the database.

        Returns:
            dict: The latest snapshot or None
        """
        try:
            return self.db.get_latest_analysis_snapshot()
        except Exception as e:
            logger.error(f"Error getting latest analysis snapshot: {e}")
            return None

    def save_current_snapshot(self, analysis_results: Dict):
        """
        Save current analysis results as snapshot for future comparison.

        Args:
            analysis_results (Dict): Current analysis results
        """
        try:
            # Prepare snapshot data
            snapshot_data = {
                'insights': self.current_insights,
                'analysis_results': analysis_results,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            self.db.save_analysis_snapshot(snapshot_data)
            logger.info("Current analysis snapshot saved to database")
        except Exception as e:
            logger.error(f"Error saving analysis snapshot: {e}")

    def compute_insight_differences(self) -> Dict:
        """
        Compute differences between current and previous insights.

        Returns:
            Dict: Differences including additions, removals, and modifications
        """
        if not self.current_insights and not self.previous_insights:
            logger.warning("No insights to compare")
            return {
                'added': [],
                'removed': [],
                'modified': [],
                'unchanged': [],
                'total_current': 0,
                'total_previous': 0
            }

        # Convert insights to comparable format (text + category)
        def insight_key(insight):
            return (insight.get('text', ''), insight.get('category', ''))

        current_set = {insight_key(ins): ins for ins in self.current_insights}
        previous_set = {insight_key(ins): ins for ins in self.previous_insights}

        # Find added insights (in current but not in previous)
        added_keys = current_set.keys() - previous_set.keys()
        added = [current_set[key] for key in added_keys]

        # Find removed insights (in previous but not in current)
        removed_keys = previous_set.keys() - current_set.keys()
        removed = [previous_set[key] for key in removed_keys]

        # Find common insights
        common_keys = current_set.keys() & previous_set.keys()
        unchanged = []
        modified = []

        for key in common_keys:
            current_insight = current_set[key]
            previous_insight = previous_set[key]

            # Check if priority changed (most likely change)
            if current_insight.get('priority') != previous_insight.get('priority'):
                modified.append({
                    'insight': current_insight.get('text', ''),
                    'category': current_insight.get('category', ''),
                    'change_type': 'priority_shift',
                    'old_priority': previous_insight.get('priority'),
                    'new_priority': current_insight.get('priority'),
                    'description': f"Priority shifted from {previous_insight.get('priority')} to {current_insight.get('priority')}"
                })
            else:
                unchanged.append(current_insight)

        self.diff_results = {
            'added': added,
            'removed': removed,
            'modified': modified,
            'unchanged': unchanged,
            'total_current': len(self.current_insights),
            'total_previous': len(self.previous_insights)
        }

        logger.info(f"Insight diff computed: {len(added)} added, {len(removed)} removed, {len(modified)} modified, {len(unchanged)} unchanged")
        return self.diff_results

    def compute_recommendation_differences(self, current_recommendations: List[Dict], previous_recommendations: List[Dict] = None) -> Dict:
        """
        Compute differences between current and previous recommendations.

        Args:
            current_recommendations (List[Dict]): Current recommendations
            previous_recommendations (List[Dict], optional): Previous recommendations (if None, load from db)

        Returns:
            Dict: Differences in recommendations
        """
        if previous_recommendations is None:
            # Load previous recommendations from database
            try:
                # We don't have a direct method, but we could store them in snapshots
                # For now, we'll return empty diff
                logger.warning("Previous recommendations not available for diff")
                return {
                    'added': [],
                    'removed': [],
                    'modified': [],
                    'total_current': len(current_recommendations) if current_recommendations else 0,
                    'total_previous': 0
                }
            except Exception as e:
                logger.error(f"Error loading previous recommendations: {e}")
                return {
                    'added': [],
                    'removed': [],
                    'modified': [],
                    'total_current': len(current_recommendations) if current_recommendations else 0,
                    'total_previous': 0
                }

        # Simple implementation - compare counts and categories
        current_count = len(current_recommendations) if current_recommendations else 0
        previous_count = len(previous_recommendations) if previous_recommendations else 0

        return {
            'added': [],  # Simplified
            'removed': [],  # Simplified
            'modified': [],  # Simplified
            'total_current': current_count,
            'total_previous': previous_count,
            'count_change': current_count - previous_count
        }

    def get_insight_trends(self) -> Dict:
        """
        Analyze trends in insights over time.

        Returns:
            Dict: Trend analysis
        """
        if not self.current_insights:
            return {'trend': 'no_data'}

        # Count insights by priority
        current_priority_counts = {}
        for insight in self.current_insights:
            priority = insight.get('priority', 'Unknown')
            current_priority_counts[priority] = current_priority_counts.get(priority, 0) + 1

        # Count previous insights by priority if available
        previous_priority_counts = {}
        if self.previous_insights:
            for insight in self.previous_insights:
                priority = insight.get('priority', 'Unknown')
                previous_priority_counts[priority] = previous_priority_counts.get(priority, 0) + 1

        # Calculate changes
        priority_changes = {}
        all_priorities = set(current_priority_counts.keys()) | set(previous_priority_counts.keys())
        for priority in all_priorities:
            current = current_priority_counts.get(priority, 0)
            previous = previous_priority_counts.get(priority, 0)
            change = current - previous
            if change != 0:
                priority_changes[priority] = change

        # Determine overall trend
        high_change = priority_changes.get('High', 0)
        medium_change = priority_changes.get('Medium', 0)
        low_change = priority_changes.get('Low', 0)

        if high_change > 0:
            trend = 'increasing_concern'
        elif high_change < 0:
            trend = 'improving_situation'
        elif medium_change > 0:
            trend = 'moderate_changes'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'current_priority_distribution': current_priority_counts,
            'previous_priority_distribution': previous_priority_counts,
            'priority_changes': priority_changes,
            'high_insight_change': high_change,
            'medium_insight_change': medium_change,
            'low_insight_change': low_change
        }

    def format_diff_for_display(self) -> str:
        """
        Format the difference results for display in the dashboard.

        Returns:
            str: Formatted diff string
        """
        if not self.diff_results:
            return "No difference analysis available. Load insights first."

        lines = [
            "Insight Change Analysis",
            "=" * 25,
            f"Current Insights: {self.diff_results['total_current']}",
            f"Previous Insights: {self.diff_results['total_previous']}",
            f"Net Change: {self.diff_results['total_current'] - self.diff_results['total_previous']:+d}",
            "",
            "Changes Detected:"
        ]

        # Added insights
        if self.diff_results['added']:
            lines.append("\n🟢 NEW INSIGHTS:")
            for insight in self.diff_results['added'][:5]:  # Limit to 5
                lines.append(f"  • {insight.get('text', '')} [{insight.get('category', '')}]")
                if insight.get('priority'):
                    lines.append(f"    Priority: {insight['priority']}")

        # Removed insights
        if self.diff_results['removed']:
            lines.append("\n🔴 REMOVED INSIGHTS:")
            for insight in self.diff_results['removed'][:5]:  # Limit to 5
                lines.append(f"  • {insight.get('text', '')} [{insight.get('category', '')}]")
                if insight.get('priority'):
                    lines.append(f"    Priority: {insight['priority']}")

        # Modified insights
        if self.diff_results['modified']:
            lines.append("\n🟡 MODIFIED INSIGHTS (Priority Changes):")
            for mod in self.diff_results['modified'][:5]:  # Limit to 5
                lines.append(
                    f"  • {mod['insight']} [{mod['category']}]"
                    f"\n    Priority: {mod['old_priority']} → {mod['new_priority']} ({mod['description']})"
                )

        # If no changes
        if not (self.diff_results['added'] or self.diff_results['removed'] or self.diff_results['modified']):
            lines.append("\n✅ NO SIGNIFICANT CHANGES DETECTED")
            lines.append("Insights remain consistent with previous analysis.")

        # Add trend analysis
        trends = self.get_insight_trends()
        lines.extend([
            "",
            "Trend Analysis:",
            f"Overall Trend: {trends['trend'].replace('_', ' ').title()}"
        ])

        return "\n".join(lines)

    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for the diff viewer.

        Returns:
            Dict: Summary statistics
        """
        if not self.diff_results:
            return {}

        return {
            'total_current': self.diff_results['total_current'],
            'total_previous': self.diff_results['total_previous'],
            'added_count': len(self.diff_results['added']),
            'removed_count': len(self.diff_results['removed']),
            'modified_count': len(self.diff_results['modified']),
            'unchanged_count': len(self.diff_results['unchanged']),
            'net_change': self.diff_results['total_current'] - self.diff_results['total_previous']
        }

    def close(self):
        """Close database connection."""
        self.db.close()