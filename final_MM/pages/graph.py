from flask import Blueprint, session, jsonify
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import os
import numpy as np

graph_bp = Blueprint('graph', __name__)

@graph_bp.route('/')
def get_graph():
    try:
        # Get analysis results from session
        results = session.get('analysis_results', [])
        if not results:
            return jsonify({
                'error': 'No analysis results found. Please analyze a file first.'
            })
        
        df = pd.DataFrame(results)
        
        # Calculate sentiment counts for each model
        svm_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        lr_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        bert_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for item in results:
            svm_counts[item['svm_sentiment']] += 1
            lr_counts[item['lr_sentiment']] += 1
            bert_counts[item['bert_sentiment']] += 1

        # Create SVM sentiment bar chart
        fig_svm = go.Figure(data=[
            go.Bar(
                x=['Positive', 'Neutral', 'Negative'],
                y=[svm_counts['positive'], svm_counts['neutral'], svm_counts['negative']],
                marker_color=['#28a745', '#ffc107', '#dc3545'],
                text=[svm_counts['positive'], svm_counts['neutral'], svm_counts['negative']],
                textposition='auto',
            )
        ])
        fig_svm.update_layout(
            title='SVM Sentiment Analysis',
            xaxis_title='Sentiment',
            yaxis_title='Count',
            template='plotly_white',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )

        # Create Logistic Regression sentiment bar chart
        fig_lr = go.Figure(data=[
            go.Bar(
                x=['Positive', 'Neutral', 'Negative'],
                y=[lr_counts['positive'], lr_counts['neutral'], lr_counts['negative']],
                marker_color=['#28a745', '#ffc107', '#dc3545'],
                text=[lr_counts['positive'], lr_counts['neutral'], lr_counts['negative']],
                textposition='auto',
            )
        ])
        fig_lr.update_layout(
            title='Logistic Regression Sentiment Analysis',
            xaxis_title='Sentiment',
            yaxis_title='Count',
            template='plotly_white',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )

        # Create BERT sentiment bar chart
        fig_bert = go.Figure(data=[
            go.Bar(
                x=['Positive', 'Neutral', 'Negative'],
                y=[bert_counts['positive'], bert_counts['neutral'], bert_counts['negative']],
                marker_color=['#28a745', '#ffc107', '#dc3545'],
                text=[bert_counts['positive'], bert_counts['neutral'], bert_counts['negative']],
                textposition='auto',
            )
        ])
        fig_bert.update_layout(
            title='BERT Sentiment Analysis',
            xaxis_title='Sentiment',
            yaxis_title='Count',
            template='plotly_white',
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#333')
        )

        return jsonify({
            'svm_chart': json.loads(json.dumps(fig_svm, cls=PlotlyJSONEncoder)),
            'lr_chart': json.loads(json.dumps(fig_lr, cls=PlotlyJSONEncoder)),
            'bert_chart': json.loads(json.dumps(fig_bert, cls=PlotlyJSONEncoder))
        })

    except Exception as e:
        return jsonify({
            'error': f'Error generating graphs: {str(e)}'
        })

def generate_recommendations(sentiment_data):
    """Generate personalized recommendations based on sentiment analysis results."""
    positive = sentiment_data.get("positive", 0)
    negative = sentiment_data.get("negative", 0)
    neutral = sentiment_data.get("neutral", 0)
    total = positive + negative + neutral

    if total == 0:
        return ["No data available for analysis."]

    recommendations = []

    # Content strategy recommendations
    if negative > positive:
        recommendations.append("The analysis shows a higher level of negative sentiment. Consider focusing on more positive topics or activities.")
    elif positive > neutral:
        recommendations.append("The content shows strong positive sentiment. This is great for engagement and audience connection.")
    elif neutral > positive and negative:
        recommendations.append("Most content has a neutral tone. Consider exploring topics that generate stronger emotional responses.")

    # Model performance insights
    if sentiment_data.get("model_agreement", {}).get("all_agree", 0) / total > 0.7:
        recommendations.append("High model agreement indicates reliable sentiment analysis results.")
    elif sentiment_data.get("model_agreement", {}).get("all_agree", 0) / total < 0.3:
        recommendations.append("Low model agreement suggests complex sentiment patterns. Consider manual review of key content.")

    return recommendations
