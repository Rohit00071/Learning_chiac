# AI Learning Analytics Dashboard

A production-quality, multi-agent AI analytics dashboard for analyzing learner/student data and providing actionable insights.

## Features

- **Multi-Agent Architecture**: Six specialized AI agents working together
- **Data Intelligence**: Load, clean, and analyze learner data
- **Pattern Detection**: Machine learning for student segmentation and risk prediction
- **Actionable Insights**: Rule-based and LLM-generated insights with priority tagging
- **Personalized Recommendations**: Student-specific and course-level suggestions
- **Validation System**: Quality checklist for output verification
- **Change Tracking**: Diff viewer to see insight evolution over time
- **Modern UI**: Professional Streamlit dashboard with interactive visualizations
- **Export Capabilities**: PDF reports and CSV downloads
- **Synthetic Data Generator**: For testing and demonstration

## Project Structure

```
AI Learning Analytics Dashboard/
│
├── agents/
│   ├── data_agent.py
│   ├── analysis_agent.py
│   ├── insight_agent.py
│   ├── recommendation_agent.py
│   ├── validation_agent.py
│   └── diff_viewer_agent.py
│
├── dashboard/
│   ├── app.py
│   ├── pages/
│   │   ├── home.py
│   │   ├── data_upload.py
│   │   ├── analytics.py
│   │   ├── insights.py
│   │   ├── recommendations.py
│   │   ├── validation_report.py
│   │   └── change_diff_viewer.py
│   └── components/
│       ├── kpi_card.py
│       └── chart_components.py
│
├── database/
│   └── database.py
│
├── data/
│   └── sample_learner_data.csv
│
├── reports/
│
├── utils/
│   ├── synthetic_data_generator.py
│   ├── config.py
│   └── logger.py
│
├── requirements.txt
└── README.md
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run dashboard/app.py
   ```

## Usage

1. **Home Dashboard**: Overview of key metrics and system status
2. **Data Upload**: Upload CSV learner data or use synthetic data generator
3. **Analytics**: View performance statistics, clustering results, and visualizations
4. **Insights**: Read actionable insights about learning patterns
5. **Recommendations**: Get personalized suggestions for students and courses
6. **Validation Report**: Check system output quality via checklist
7. **Change Diff Viewer**: Track how insights evolve with more data

## Core Agents

1. **Data Agent**: Handles data loading, cleaning, normalization, and storage
2. **Analysis Agent**: Detects patterns, performs statistical analysis, and runs ML models
3. **Insight Agent**: Converts analytics into human-readable insights with priority tagging
4. **Recommendation Agent**: Generates personalized and course-level recommendations
5. **Validation Checklist Agent**: Validates system output quality at each stage
6. **Change Diff Viewer Agent**: Tracks differences between previous and current insights

## Data Fields

- student_id
- student_name
- course
- quiz_score
- assignment_score
- attendance_percentage
- completion_percentage
- study_hours
- weak_topics
- learning_speed
- submission_delay_days

## Demo Requirements

The application demonstrates:
1. Initial insights using small dataset
2. Improved insights after adding more learner data
3. Better recommendations with larger datasets
4. Change Diff Viewer showing insight evolution

## Configuration

Modify `utils/config.py` to adjust:
- Database paths
- Synthetic data parameters
- Agent thresholds
- UI theme settings

## Extensibility

- Add new agents by inheriting from base agent classes
- Extend synthetic data generator for additional fields
- Integrate with external data sources via Data Agent
- Enhance Insight Agent with advanced LLM prompts

## License

MIT License - feel free to use and modify for educational or commercial purposes.