# Quick Launch Guide

## Prerequisites
- Python 3.11+
- pip package manager

## Installation

1. Clone or copy this project to your local machine
2. Navigate to the project directory:
   ```bash
   cd "AI Learning Analytics Dashboard"
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

```bash
streamlit run dashboard/app.py
```

## Features Demonstration

### Initial Insights with Small Dataset
1. Use the sidebar to load the sample data (`data/sample_learner_data.csv`) or generate synthetic data (20-50 students)
2. Click "Run Full Analysis"
3. Navigate through the tabs to see:
   - Home Dashboard: Overview metrics
   - Analytics: Performance statistics and clustering
   - Insights: Generated insights with priority tags
   - Recommendations: Personalized suggestions
   - Validation Report: Pipeline quality check
   - Change Diff Viewer: (Will show limited changes with single dataset)

### Improved Insights with More Data
1. Generate additional synthetic data (e.g., 150 students) using the sidebar
2. Click "Run Full Analysis" again
3. Observe:
   - More stable clustering results
   - Different insight priorities in the Insights tab
   - Changes visible in the Change Diff Viewer tab
   - Updated recommendations based on larger dataset

### Change Diff Viewer Demonstration
1. Run analysis with Dataset A (small)
2. Click "Save as Baseline" in the Change Diff Viewer tab
3. Run analysis with Dataset B (larger or different characteristics)
4. View the differences in the Change Diff Viewer tab showing:
   - New insights that emerged
   - Insights that disappeared
   - Insights that changed in priority

## Key Features Implemented

✅ Multi-Agent AI Architecture (6 specialized agents)
✅ Data loading, cleaning, and normalization
✅ Performance analysis with statistics
✅ Machine learning clustering (KMeans) for student segmentation
✅ Risk prediction modeling
✅ Rule-based insight generation with priority tagging
✅ Personalized recommendation generation
✅ Pipeline validation system
✅ Change tracking and diff visualization
✅ Modern Streamlit dashboard with interactive visualizations
✅ Synthetic data generator for testing
✅ Export capabilities (via agents - extendable)
✅ Session state persistence
✅ Error handling and logging
✅ Configuration file support

## Agent Responsibilities

1. **Data Agent**: Loads, cleans, normalizes, stores data; generates synthetic data
2. **Analysis Agent**: Performs statistical analysis, clustering, risk prediction
3. **Insight Agent**: Converts analytics to human-readable insights with priorities
4. **Recommendation Agent**: Creates personalized and course-level recommendations
5. **Validation Checklist Agent**: Validates each stage of the pipeline
6. **Change Diff Viewer Agent**: Tracks evolution of insights over time

## Technology Stack

- Frontend: Streamlit
- Backend: Python 3.11+
- Libraries: pandas, numpy, scikit-learn, plotly, matplotlib
- Database: SQLite for persistence
- Optional: OpenAI, LangChain, CrewAI for LLM-enhanced features

## Extending the System

- Add new data sources by modifying the Data Agent
- Enhance insights with LLM integration in the Insight Agent
- Add new recommendation types in the Recommendation Agent
- Extend validation rules in the Validation Checklist Agent
- Add new visualization types in the dashboard components

## Notes

- The first run may take a moment as dependencies are loaded
- Synthetic data generation creates realistic learner data with correlations
- All agent state is preserved in session during browser session
- Database persists data between runs (stored in database/learning_analytics.db)