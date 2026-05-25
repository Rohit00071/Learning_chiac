import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def render_score_distribution(df, score_col='quiz_score', title="Score Distribution"):
    """
    Render a histogram of score distribution.

    Args:
        df (pd.DataFrame): DataFrame containing score data
        score_col (str): Column name for scores
        title (str): Chart title
    """
    if df is None or df.empty or score_col not in df.columns:
        st.warning("No data available for score distribution")
        return

    fig = px.histogram(
        df,
        x=score_col,
        nbins=20,
        title=title,
        labels={score_col: 'Score', 'count': 'Number of Students'}
    )
    fig.update_layout(showlegend=False, bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

def render_risk_distribution(risk_counts, title="Risk Distribution"):
    """
    Render a pie chart of risk distribution.

    Args:
        risk_counts (pd.Series): Series with risk categories as index and counts as values
        title (str): Chart title
    """
    if risk_counts is None or len(risk_counts) == 0:
        st.warning("No risk data available")
        return

    fig = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title=title,
        color_discrete_map={'High': '#dc3545', 'Medium': '#ffc107', 'Low': '#28a745'}
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)

def render_correlation_heatmap(correlation_matrix, title="Correlation Heatmap"):
    """
    Render a heatmap of correlation matrix.

    Args:
        correlation_matrix (pd.DataFrame): Correlation matrix
        title (str): Chart title
    """
    if correlation_matrix is None or correlation_matrix.empty:
        st.warning("No correlation data available")
        return

    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        title=title,
        color_continuous_scale='RdBu_r'
    )
    st.plotly_chart(fig, use_container_width=True)

def render_scatter_plot(df, x_col, y_col, color_col=None, title="Scatter Plot"):
    """
    Render a scatter plot.

    Args:
        df (pd.DataFrame): DataFrame containing data
        x_col (str): Column name for x-axis
        y_col (str): Column name for y-axis
        color_col (str, optional): Column name for color encoding
        title (str): Chart title
    """
    if df is None or df.empty:
        st.warning("No data available for scatter plot")
        return

    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Required columns {x_col} or {y_col} not found in data")
        return

    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col if color_col and color_col in df.columns else None,
        title=title,
        labels={x_col: x_col.replace('_', ' ').title(), y_col: y_col.replace('_', ' ').title()}
    )
    st.plotly_chart(fig, use_container_width=True)

def render_bar_chart(df, x_col, y_col, title="Bar Chart", color=None):
    """
    Render a bar chart.

    Args:
        df (pd.DataFrame): DataFrame containing data
        x_col (str): Column name for x-axis
        y_col (str): Column name for y-axis
        title (str): Chart title
        color (str, optional): Color for bars
    """
    if df is None or df.empty:
        st.warning("No data available for bar chart")
        return

    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Required columns {x_col} or {y_col} not found in data")
        return

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[color] if color else None
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def render_line_chart(df, x_col, y_col, title="Line Chart"):
    """
    Render a line chart.

    Args:
        df (pd.DataFrame): DataFrame containing data
        x_col (str): Column name for x-axis
        y_col (str): Column name for y-axis
        title (str): Chart title
    """
    if df is None or df.empty:
        st.warning("No data available for line chart")
        return

    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Required columns {x_col} or {y_col} not found in data")
        return

    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)