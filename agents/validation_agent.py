from typing import Dict, List
from utils.logger import get_logger

logger = get_logger(__name__)

class ValidationChecklistAgent:
    """
    Validation Checklist Agent responsible for validating the system output quality.
    Checks that each stage of the pipeline has completed successfully.
    """

    def __init__(self):
        """Initialize the Validation Checklist Agent."""
        self.checklist_items = [
            "Data loaded successfully",
            "Missing values handled",
            "Data normalized",
            "Analysis completed",
            "Insights generated",
            "Recommendations generated",
            "Visualizations rendered",
            "Risk predictions completed"
        ]
        self.validation_results = {}
        logger.info("ValidationChecklistAgent initialized")

    def validate_pipeline_stage(self, stage_name: str, status: bool, details: str = None) -> Dict:
        """
        Validate a single pipeline stage.

        Args:
            stage_name (str): Name of the pipeline stage
            status (bool): Whether the stage completed successfully
            details (str, optional): Additional details about the validation

        Returns:
            Dict: Validation result for this stage
        """
        from datetime import datetime
        result = {
            'stage': stage_name,
            'passed': status,
            'details': details or ("Completed successfully" if status else "Failed"),
            'timestamp': datetime.now().isoformat()
        }
        self.validation_results[stage_name] = result
        logger.info(f"Validation stage '{stage_name}': {'PASS' if status else 'FAIL'} - {result['details']}")
        return result

    def validate_data_loading(self, data) -> bool:
        """
        Validate that data has been loaded successfully.

        Args:
            data: The data to validate (DataFrame or similar)

        Returns:
            bool: True if data is valid
        """
        if data is None:
            return self.validate_pipeline_stage(
                "Data loaded successfully",
                False,
                "No data provided"
            )

        if hasattr(data, 'empty') and data.empty:
            return self.validate_pipeline_stage(
                "Data loaded successfully",
                False,
                "Data is empty"
            )

        if hasattr(data, 'shape'):
            return self.validate_pipeline_stage(
                "Data loaded successfully",
                True,
                f"Data loaded with shape {data.shape}"
            )

        return self.validate_pipeline_stage(
            "Data loaded successfully",
            True,
            "Data loaded successfully"
        )

    def validate_missing_values_handled(self, original_data, processed_data) -> bool:
        """
        Validate that missing values have been handled.

        Args:
            original_data: Original data before processing
            processed_data: Data after processing

        Returns:
            bool: True if missing values are handled
        """
        if original_data is None or processed_data is None:
            return self.validate_pipeline_stage(
                "Missing values handled",
                False,
                "Cannot validate: missing original or processed data"
            )

        # Check if we have DataFrames
        if hasattr(original_data, 'isnull') and hasattr(processed_data, 'isnull'):
            original_missing = original_data.isnull().sum().sum()
            processed_missing = processed_data.isnull().sum().sum()

            if processed_missing == 0:
                return self.validate_pipeline_stage(
                    "Missing values handled",
                    True,
                    f"All {original_missing} missing values have been handled"
                )
            else:
                return self.validate_pipeline_stage(
                    "Missing values handled",
                    False,
                    f"{processed_missing} missing values remain unhandled"
                )

        return self.validate_pipeline_stage(
            "Missing values handled",
            True,
            "Assuming missing values handled (validation skipped)"
        )

    def validate_analysis_completed(self, analysis_results) -> bool:
        """
        Validate that analysis has been completed.

        Args:
            analysis_results: Results from analysis agent

        Returns:
            bool: True if analysis is complete
        """
        if not analysis_results:
            return self.validate_pipeline_stage(
                "Analysis completed",
                False,
                "No analysis results provided"
            )

        # Check if we have meaningful results
        has_results = any(bool(v) for v in analysis_results.values() if isinstance(v, dict))
        if has_results:
            return self.validate_pipeline_stage(
                "Analysis completed",
                True,
                f"Analysis completed with {len([k for k, v in analysis_results.items() if v])} stages"
            )
        else:
            return self.validate_pipeline_stage(
                "Analysis completed",
                False,
                "Analysis results are empty or invalid"
            )

    def validate_insights_generated(self, insights) -> bool:
        """
        Validate that insights have been generated.

        Args:
            insights: List of insights

        Returns:
            bool: True if insights are generated
        """
        if not insights:
            return self.validate_pipeline_stage(
                "Insights generated",
                False,
                "No insights generated"
            )

        if len(insights) == 0:
            return self.validate_pipeline_stage(
                "Insights generated",
                False,
                "Insights list is empty"
            )

        return self.validate_pipeline_stage(
            "Insights generated",
            True,
            f"{len(insights)} insights generated"
        )

    def validate_recommendations_generated(self, recommendations) -> bool:
        """
        Validate that recommendations have been generated.

        Args:
            recommendations: List of recommendations

        Returns:
            bool: True if recommendations are generated
        """
        if not recommendations:
            return self.validate_pipeline_stage(
                "Recommendations generated",
                False,
                "No recommendations generated"
            )

        if len(recommendations) == 0:
            return self.validate_pipeline_stage(
                "Recommendations generated",
                False,
                "Recommendations list is empty"
            )

        return self.validate_pipeline_stage(
            "Recommendations generated",
            True,
            f"{len(recommendations)} recommendations generated"
        )

    def validate_visualizations_rendered(self, viz_count: int) -> bool:
        """
        Validate that visualizations have been rendered.

        Args:
            viz_count (int): Number of visualizations rendered

        Returns:
            bool: True if visualizations are rendered
        """
        if viz_count > 0:
            return self.validate_pipeline_stage(
                "Visualizations rendered",
                True,
                f"{viz_count} visualizations rendered"
            )
        else:
            return self.validate_pipeline_stage(
                "Visualizations rendered",
                False,
                "No visualizations rendered"
            )

    def validate_risk_predictions_completed(self, risk_predictions) -> bool:
        """
        Validate that risk predictions have been completed.

        Args:
            risk_predictions: Risk prediction results

        Returns:
            bool: True if risk predictions are completed
        """
        if not risk_predictions:
            return self.validate_pipeline_stage(
                "Risk predictions completed",
                False,
                "No risk predictions generated"
            )

        # Check if we have risk scores or categories
        has_risk_data = (
            isinstance(risk_predictions, dict) and
            ('risk_scores' in risk_predictions or 'high_risk_count' in risk_predictions)
        )

        if has_risk_data:
            return self.validate_pipeline_stage(
                "Risk predictions completed",
                True,
                f"Risk predictions completed for {risk_predictions.get('high_risk_count', 0)} high risk students"
            )
        else:
            return self.validate_pipeline_stage(
                "Risk predictions completed",
                False,
                "Risk predictions are incomplete or invalid"
            )

    def validate_normalization_completed(self, normalized_data) -> bool:
        """
        Validate that data normalization has been completed.

        Args:
            normalized_data: Normalized data

        Returns:
            bool: True if normalization is completed
        """
        if normalized_data is None:
            return self.validate_pipeline_stage(
                "Data normalized",
                False,
                "No normalized data provided"
            )

        # Check if we have normalized columns
        if hasattr(normalized_data, 'columns'):
            normalized_cols = [col for col in normalized_data.columns if col.endswith('_normalized')]
            if len(normalized_cols) > 0:
                return self.validate_pipeline_stage(
                    "Data normalized",
                    True,
                    f"{len(normalized_cols)} features normalized"
                )

        return self.validate_pipeline_stage(
            "Data normalized",
            False,
            "No normalized columns found"
        )

    def run_full_validation(self, validation_data: Dict) -> Dict:
        """
        Run full validation pipeline using provided data.

        Args:
            validation_data (Dict): Dictionary containing all validation inputs:
                - original_data
                - processed_data
                - analysis_results
                - insights
                - recommendations
                - visualizations_count
                - risk_predictions
                - normalized_data

        Returns:
            Dict: Complete validation results
        """
        logger.info("Running full validation pipeline")

        # Reset validation results
        self.validation_results = {}

        # Run all validation checks
        self.validate_data_loading(validation_data.get('original_data'))
        self.validate_missing_values_handled(
            validation_data.get('original_data'),
            validation_data.get('processed_data')
        )
        self.validate_normalization_completed(validation_data.get('normalized_data'))
        self.validate_analysis_completed(validation_data.get('analysis_results'))
        self.validate_insights_generated(validation_data.get('insights'))
        self.validate_recommendations_generated(validation_data.get('recommendations'))
        self.validate_visualizations_rendered(validation_data.get('visualizations_count', 0))
        self.validate_risk_predictions_completed(validation_data.get('risk_predictions'))

        # Calculate overall status
        passed_stages = sum(1 for result in self.validation_results.values() if result['passed'])
        total_stages = len(self.validation_results)
        overall_passed = passed_stages == total_stages

        summary = {
            'overall_passed': overall_passed,
            'passed_stages': passed_stages,
            'total_stages': total_stages,
            'success_rate': (passed_stages / total_stages * 100) if total_stages > 0 else 0,
            'validation_results': self.validation_results
        }

        logger.info(f"Validation complete: {passed_stages}/{total_stages} stages passed ({summary['success_rate']:.1f}%)")
        return summary

    def get_validation_summary(self) -> Dict:
        """
        Get a summary of validation results.

        Returns:
            Dict: Summary of validation results
        """
        if not self.validation_results:
            return {
                'overall_passed': False,
                'passed_stages': 0,
                'total_stages': 0,
                'success_rate': 0,
                'message': "No validation has been run yet"
            }

        passed_stages = sum(1 for result in self.validation_results.values() if result['passed'])
        total_stages = len(self.validation_results)
        overall_passed = passed_stages == total_stages

        return {
            'overall_passed': overall_passed,
            'passed_stages': passed_stages,
            'total_stages': total_stages,
            'success_rate': (passed_stages / total_stages * 100) if total_stages > 0 else 0,
            'validation_results': self.validation_results
        }

    def format_validation_for_display(self) -> str:
        """
        Format validation results for display in the dashboard.

        Returns:
            str: Formatted validation string
        """
        summary = self.get_validation_summary()

        if summary.get('message'):
            return summary['message']

        status_emoji = '🟢' if summary['overall_passed'] else '🔴'
        lines = [
            f"{status_emoji} Pipeline Validation Summary",
            "=" * 40,
            f"Overall Status: {'PASS' if summary['overall_passed'] else 'FAIL'}",
            f"Stages Passed: {summary['passed_stages']}/{summary['total_stages']}",
            f"Success Rate: {summary['success_rate']:.1f}%",
            "",
            "Stage Details:"
        ]

        for stage_name, result in summary['validation_results'].items():
            stage_emoji = '🟢' if result['passed'] else '🔴'
            lines.append(
                f"  {stage_emoji} {stage_name}: {result['details']}"
            )

        return "\n".join(lines)