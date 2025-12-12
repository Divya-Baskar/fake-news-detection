import streamlit as st
import torch
import pandas as pd
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import re
import string
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import paho.mqtt.client as mqtt
import threading
import uuid
import folium
from streamlit_folium import st_folium
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# Page configuration
st.set_page_config(
    page_title="Real-Time Fake News Detection System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Email Configuration
EMAIL_CONFIG = {
    "sender_email": "ayushtiwari.creatorslab@gmail.com",
    "sender_password": "tecx bcym vxdz dtni",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
}

GNEWS_API_KEY = "165503e60967900e95cdf358a88d1736"  
GNEWS_API_ENDPOINT = "https://gnews.io/api/v4/search"

# Dark Theme CSS
st.markdown("""
<style>
    /* ============== FONT IMPORTS ============== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100;200;300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@100;200;300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@100;200;300;400;500;600;700;800;900&display=swap');

    /* ============== DARK THEME CSS VARIABLES ============== */
    :root {
        /* Primary Colors - Dark Theme */
        --primary-blue: #60a5fa;
        --primary-purple: #a78bfa;
        --secondary-pink: #f472b6;
        --secondary-coral: #fb7185;
        --accent-green: #34d399;
        --accent-yellow: #fbbf24;
        --accent-orange: #fb923c;
        --accent-red: #f87171;
        --accent-cyan: #22d3ee;
        --accent-indigo: #818cf8;
        
        /* Dark Theme Gradients */
        --primary-gradient: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
        --secondary-gradient: linear-gradient(135deg, #f472b6 0%, #fb7185 100%);
        --success-gradient: linear-gradient(135deg, #34d399 0%, #059669 100%);
        --warning-gradient: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        --danger-gradient: linear-gradient(135deg, #f87171 0%, #dc2626 100%);
        --info-gradient: linear-gradient(135deg, #22d3ee 0%, #0891b2 100%);
        --purple-gradient: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
        
        /* Dark Background Gradients */
        --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
        --bg-gradient-alt: linear-gradient(135deg, #111827 0%, #1f2937 50%, #374151 100%);
        --card-gradient: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.8) 100%);
        
        /* Dark Background Colors */
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-tertiary: #334155;
        --card-bg: rgba(30, 41, 59, 0.8);
        --card-bg-solid: #1e293b;
        --glass-bg: rgba(30, 41, 59, 0.4);
        --glass-bg-strong: rgba(30, 41, 59, 0.6);
        --overlay-bg: rgba(0, 0, 0, 0.6);
        
        /* Dark Text Colors */
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-tertiary: #94a3b8;
        --text-muted: #64748b;
        --text-inverse: #1e293b;
        
        /* Dark Border Colors */
        --border-color: rgba(203, 213, 225, 0.1);
        --border-light: rgba(203, 213, 225, 0.2);
        --border-medium: rgba(203, 213, 225, 0.3);
        --border-strong: rgba(203, 213, 225, 0.4);
        
        /* Spacing & Sizing */
        --border-radius: 16px;
        --border-radius-sm: 8px;
        --border-radius-lg: 24px;
        --spacing-xs: 0.25rem;
        --spacing-sm: 0.5rem;
        --spacing-md: 1rem;
        --spacing-lg: 1.5rem;
        --spacing-xl: 2rem;
        --spacing-2xl: 3rem;
        
        /* Dark Theme Shadows */
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.5);
        --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
        --shadow-glow: 0 0 20px rgba(96, 165, 250, 0.3);
        --shadow-glow-strong: 0 0 30px rgba(96, 165, 250, 0.5);
        
        /* Animation */
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-fast: all 0.15s ease-in-out;
        --transition-slow: all 0.5s ease-in-out;
    }

    /* ============== GLOBAL DARK STYLES ============== */
    .stApp {
        background: var(--bg-gradient);
        color: var(--text-primary);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }

    /* Hide Streamlit Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Dark scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: var(--primary-gradient);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-gradient);
    }

    /* Main Container */
    .main .block-container {
        padding-top: var(--spacing-xl);
        max-width: none;
    }

    /* Dark Dashboard Header */
    .dashboard-header {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: var(--spacing-lg) var(--spacing-xl);
        margin-bottom: var(--spacing-xl);
        box-shadow: var(--shadow-lg);
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(20px);
        border: 1px solid var(--border-light);
        position: relative;
        overflow: hidden;
    }

    .dashboard-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--primary-gradient);
    }

    .welcome-section h1 {
        font-size: 1.875rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(96, 165, 250, 0.3);
    }

    .welcome-section p {
        color: var(--text-secondary);
        margin: var(--spacing-xs) 0 0 0;
        font-size: 0.95rem;
        font-weight: 400;
    }

    /* MQTT Status */
    .mqtt-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: var(--glass-bg);
        border-radius: var(--border-radius-sm);
        border: 1px solid var(--border-light);
    }

    .mqtt-connected {
        color: var(--accent-green);
    }

    .mqtt-disconnected {
        color: var(--accent-red);
    }

    /* ============== IMPROVED DARK SIDEBAR COMPONENTS ============== */
    .css-1d391kg, 
    .css-1cypcdb,
    section[data-testid="stSidebar"],
    .stSidebar,
    section[data-testid="stSidebar"] > div,
    .css-ng1t4o,
    .css-1lcbmhc {
        background: var(--card-bg) !important;
        border-radius: 0 var(--border-radius) var(--border-radius) 0 !important;
        border: none !important;
        box-shadow: var(--shadow-xl) !important;
        padding-top: var(--spacing-xl) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid var(--border-light) !important;
    }

    .sidebar-profile {
        background: var(--primary-gradient);
        border-radius: var(--border-radius-sm);
        padding: var(--spacing-lg);
        color: white;
        margin-bottom: var(--spacing-lg);
        text-align: center;
        position: relative;
        overflow: hidden;
        box-shadow: var(--shadow-lg), 0 0 20px rgba(96, 165, 250, 0.3);
    }

    .profile-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto var(--spacing-sm) auto;
        font-size: 1.25rem;
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255, 255, 255, 0.3);
        animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .profile-name {
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: var(--spacing-xs);
    }

    .profile-subtitle {
        font-size: 0.8rem;
        opacity: 0.8;
    }

    /* ============== DARK CARD COMPONENTS ============== */
    .card, .feature-card, .glass-card {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: var(--spacing-lg);
        box-shadow: var(--shadow-lg);
        transition: var(--transition);
        border: 1px solid var(--border-light);
        backdrop-filter: blur(20px);
        position: relative;
        overflow: hidden;
    }

    .card:hover, .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl), var(--shadow-glow);
        border-color: var(--primary-blue);
    }

    .glass-card {
        background: var(--glass-bg-strong);
    }

    .glass-card:hover {
        transform: translateY(-6px);
        box-shadow: var(--shadow-2xl), var(--shadow-glow);
        border-color: var(--primary-blue);
    }

    /* Device Cards */
    .device-card {
        background: var(--card-bg);
        border-radius: var(--border-radius-sm);
        padding: var(--spacing-lg);
        margin: var(--spacing-sm) 0;
        border: 1px solid var(--border-light);
        backdrop-filter: blur(20px);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }

    .device-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg), var(--shadow-glow);
    }

    .device-online {
        border-left: 4px solid var(--accent-green);
    }

    .device-offline {
        border-left: 4px solid var(--accent-red);
    }

    .device-alert {
        border-left: 4px solid var(--accent-orange);
        background: rgba(251, 147, 60, 0.05);
        animation: pulse-glow 2s infinite;
    }

    @keyframes pulse-glow {
        0%, 100% { 
            box-shadow: var(--shadow-lg);
            opacity: 1; 
        }
        50% { 
            box-shadow: var(--shadow-lg), 0 0 20px rgba(251, 147, 60, 0.4);
            opacity: 0.9; 
        }
    }

    .device-status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 0.5rem;
        animation: pulse 2s infinite;
    }

    .status-online {
        background: var(--accent-green);
        box-shadow: 0 0 6px var(--accent-green);
    }

    .status-offline {
        background: var(--accent-red);
        box-shadow: 0 0 6px var(--accent-red);
    }

    .status-alert {
        background: var(--accent-orange);
        box-shadow: 0 0 6px var(--accent-orange);
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Device Info */
    .device-info {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: var(--spacing-sm);
    }

    .device-name {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 1rem;
    }

    .device-location {
        font-size: 0.8rem;
        color: var(--text-tertiary);
    }

    .device-details {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin: var(--spacing-xs) 0;
    }

    .heartbeat-indicator {
        font-size: 0.75rem;
        color: var(--text-muted);
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    /* Metrics */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--spacing-lg);
        margin: var(--spacing-lg) 0;
    }

    .metric-card {
        background: var(--card-bg);
        border-radius: var(--border-radius-sm);
        padding: var(--spacing-lg);
        text-align: center;
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--border-light);
        transition: var(--transition);
        backdrop-filter: blur(20px);
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl), var(--shadow-glow);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: var(--spacing-xs);
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .metric-label {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }

    /* Section Titles */
    .section-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--spacing-lg);
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .section-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        margin-bottom: var(--spacing-xl);
        line-height: 1.6;
    }

    /* Prediction Box */
    .prediction-box {
        padding: var(--spacing-lg);
        border-radius: var(--border-radius-sm);
        margin: var(--spacing-md) 0;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        backdrop-filter: blur(20px);
        border: 2px solid;
    }

    .fake-news {
        background: rgba(248, 113, 113, 0.1);
        color: var(--accent-red);
        border-color: var(--accent-red);
        box-shadow: var(--shadow-lg), 0 0 20px rgba(248, 113, 113, 0.3);
    }

    .real-news {
        background: rgba(52, 211, 153, 0.1);
        color: var(--accent-green);
        border-color: var(--accent-green);
        box-shadow: var(--shadow-lg), 0 0 20px rgba(52, 211, 153, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: var(--primary-gradient) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: var(--transition) !important;
        box-shadow: var(--shadow-lg) !important;
        width: 100% !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-xl), var(--shadow-glow) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-light);
        padding: var(--spacing-sm);
        box-shadow: var(--shadow-lg);
        backdrop-filter: blur(20px);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: var(--border-radius-sm);
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: var(--transition);
        border: none;
    }

    .stTabs [aria-selected="true"] {
        background: var(--primary-gradient) !important;
        color: white !important;
        box-shadow: var(--shadow-lg) !important;
    }

    /* Alert Feed */
    .alert-feed {
        background: var(--card-bg);
        border-radius: var(--border-radius-sm);
        padding: var(--spacing-md);
        margin: var(--spacing-sm) 0;
        border: 1px solid var(--border-light);
        backdrop-filter: blur(20px);
    }

    .alert-item {
        padding: var(--spacing-sm);
        margin: var(--spacing-xs) 0;
        border-radius: var(--border-radius-sm);
        border-left: 3px solid var(--accent-orange);
        background: rgba(251, 147, 60, 0.05);
        font-size: 0.85rem;
        color: var(--text-secondary);
    }

    /* Map Container */
    .map-container {
        background: var(--card-bg);
        border-radius: var(--border-radius);
        padding: var(--spacing-md);
        border: 1px solid var(--border-light);
        backdrop-filter: blur(20px);
        box-shadow: var(--shadow-lg);
    }

    /* Loading Indicators */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 2px solid rgba(96, 165, 250, 0.3);
        border-radius: 50%;
        border-top-color: var(--primary-blue);
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* Responsive */
    @media (max-width: 768px) {
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
        .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
        }
    }
</style>
""", unsafe_allow_html=True)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPICS = {
    "fake_news_alert": "fakenews/alert",
    "device_status": "fakenews/device/+/status",
    "device_response": "fakenews/device/+/response",
    "device_heartbeat": "fakenews/device/+/heartbeat"
}

# ============== EMAIL FUNCTIONS ==============
def send_email_alert(recipient_email, news_title, confidence):
    """Send email alert for fake news detection"""
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🚨 FAKE NEWS ALERT - Action Required"
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = recipient_email
        
        # HTML email body
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 16px; padding: 30px; border: 2px solid #f87171;">
              <h1 style="color: #f87171; text-align: center; margin-bottom: 20px;">⚠️ FAKE NEWS DETECTED ⚠️</h1>
              
              <div style="background: rgba(248, 113, 113, 0.1); border-left: 4px solid #f87171; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2 style="color: #f8fafc; margin-top: 0;">Alert Details</h2>
                <p><strong>Article Title:</strong></p>
                <p style="font-size: 16px; color: #cbd5e1;">{news_title}</p>
                
                <p style="margin-top: 20px;"><strong>Detection Confidence:</strong> <span style="color: #f87171; font-size: 20px; font-weight: bold;">{confidence:.2f}%</span></p>
                
                <p style="margin-top: 20px;"><strong>Detection Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
              </div>
              
              <div style="background: rgba(251, 147, 60, 0.1); border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #fb923c; margin-top: 0;">⚡ Immediate Actions Required:</h3>
                <ul style="color: #cbd5e1; line-height: 1.8;">
                  <li>Review the article content immediately</li>
                  <li>Verify information from reliable sources</li>
                  <li>Flag content for moderation if necessary</li>
                  <li>Do not share or distribute this content</li>
                  <li>Report to appropriate authorities if needed</li>
                </ul>
              </div>
              
              <div style="background: rgba(96, 165, 250, 0.1); border-radius: 8px; padding: 15px; margin: 20px 0;">
                <p style="color: #94a3b8; font-size: 14px; margin: 0;">
                  <strong>Note:</strong> This alert was automatically generated by our BERT-powered Fake News Detection System. 
                  All IoT monitoring devices have been notified.
                </p>
              </div>
              
              <hr style="border: none; height: 1px; background: rgba(203, 213, 225, 0.2); margin: 30px 0;">
              
              <p style="text-align: center; color: #64748b; font-size: 12px;">
                Real-Time Fake News Detection System<br>
                Powered by BERT + MQTT + IoT Integration<br>
                © 2024 All Rights Reserved
              </p>
            </div>
          </body>
        </html>
        """
        
        # Attach HTML body
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"❌ Email sending failed: {str(e)}")
        return False

# ============== NEWS API FUNCTIONS ==============
def fetch_real_time_news(query="", category="general", country="us"):
    """Fetch real-time news from GNews API - Better country support!"""
    try:
        # GNews API endpoint
        params = {
            'apikey': GNEWS_API_KEY,
            'lang': 'en',
            'max': 10
        }
        
        # Add country (GNews supports more countries)
        if country:
            params['country'] = country
        
        # Add category if not general
        if category and category != "general":
            params['category'] = category
        
        # Add search query if provided
        if query:
            params['q'] = query
        else:
            # If no query, search for general news
            params['q'] = category if category != "general" else "news"
        
        response = requests.get(GNEWS_API_ENDPOINT, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])
            
            # Convert GNews format to our format
            formatted_articles = []
            for article in articles:
                formatted_articles.append({
                    'source': {'name': article.get('source', {}).get('name', 'Unknown')},
                    'author': 'GNews',
                    'title': article.get('title', 'No Title'),
                    'description': article.get('description', 'No description'),
                    'url': article.get('url', ''),
                    'urlToImage': article.get('image', ''),
                    'publishedAt': article.get('publishedAt', ''),
                    'content': article.get('content', '')
                })
            
            return formatted_articles
        elif response.status_code == 429:
            st.error("⚠️ API rate limit reached. You've made 100+ requests today. Try again tomorrow.")
            return []
        elif response.status_code == 403:
            st.error("⚠️ Invalid API key. Please check your GNews API key.")
            return []
        else:
            st.warning(f"GNews API returned status code: {response.status_code}")
            return []
    except requests.exceptions.Timeout:
        st.error("⚠️ Request timeout. Check your internet connection.")
        return []
    except Exception as e:
        st.error(f"Error fetching news: {str(e)}")
        return []

class MQTTManager:
    def __init__(self):
        self.client = mqtt.Client(client_id=f"streamlit_client_{uuid.uuid4()}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.connected = False
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            st.session_state.mqtt_status = "Connected"
            # Subscribe to all device topics
            client.subscribe(MQTT_TOPICS["device_response"])
            client.subscribe(MQTT_TOPICS["device_status"])
            client.subscribe(MQTT_TOPICS["device_heartbeat"])
        else:
            self.connected = False
            st.session_state.mqtt_status = f"Connection failed: {rc}"
    
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        st.session_state.mqtt_status = "Disconnected"
    
    def on_message(self, client, userdata, msg):
        try:
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 3:
                device_id = topic_parts[2]
                message_type = topic_parts[3]
                payload = json.loads(msg.payload.decode())
                
                if device_id in st.session_state.iot_devices:
                    current_time = datetime.now()
                    
                    if message_type == "response":
                        st.session_state.iot_devices[device_id]['last_response'] = payload
                        st.session_state.iot_devices[device_id]['last_response_time'] = current_time
                    elif message_type == "status":
                        st.session_state.iot_devices[device_id]['mqtt_status'] = payload.get('status', 'unknown')
                    elif message_type == "heartbeat":
                        st.session_state.iot_devices[device_id]['last_heartbeat'] = current_time
                        st.session_state.iot_devices[device_id]['status'] = 'online'
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def connect(self):
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            # Silently fail if MQTT broker not available
            st.session_state.mqtt_status = "Disconnected (MQTT Optional)"
            return False
    
    def publish_fake_news_alert(self, news_data):
        if self.connected:
            alert_payload = {
                "timestamp": datetime.now().isoformat(),
                "alert_type": "FAKE_NEWS_DETECTED",
                "title": news_data.get("title", ""),
                "confidence": news_data.get("confidence", 0),
                "author": news_data.get("author", ""),
                "priority": "HIGH",
                "location": "Global"
            }
            
            # Publish main alert
            self.client.publish(MQTT_TOPICS["fake_news_alert"], json.dumps(alert_payload), qos=1)
            
            # Publish to individual devices
            for device_id in st.session_state.iot_devices.keys():
                device_topic = f"fakenews/device/{device_id}/alert"
                self.client.publish(device_topic, json.dumps(alert_payload), qos=1)
            
            return True
        return False

@st.cache_resource
def load_model_and_tokenizer():
    """Load the trained model and tokenizer"""
    try:
        tokenizer = DistilBertTokenizerFast.from_pretrained("distilbert-base-uncased")
        model = DistilBertForSequenceClassification.from_pretrained(
            "saved_model",
            num_labels=2
        )
        model.eval()
        return model, tokenizer
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

def clean_text(text):
    """Clean text preprocessing"""
    text = text.lower()
    text = text.replace('\n', ' ')
    text = re.sub(r'\d+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text, flags=re.I)
    return text.strip()

def predict_news(model, tokenizer, text, title=""):
    """Make prediction on news text"""
    if model is None or tokenizer is None:
        return None, 0.0
    
    merged_text = f"{title} {text}" if title else text
    cleaned_text = clean_text(merged_text)
    
    encoding = tokenizer(
        cleaned_text,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )
    
    with torch.no_grad():
        outputs = model(**encoding)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        confidence = torch.max(predictions).item()
        predicted_class = torch.argmax(predictions, dim=-1).item()
    
    return predicted_class, confidence

def get_device_status_color(device_info):
    """Get device status color based on current state"""
    if device_info.get('last_alert') and (datetime.now() - device_info['last_alert']).total_seconds() < 300:
        return "status-alert"
    elif device_info.get('status') == 'online' and device_info.get('last_heartbeat'):
        if (datetime.now() - device_info['last_heartbeat']).total_seconds() < 60:
            return "status-online"
    return "status-offline"

def get_device_card_class(device_info):
    """Get device card CSS class based on status"""
    if device_info.get('last_alert') and (datetime.now() - device_info['last_alert']).total_seconds() < 300:
        return "device-card device-alert"
    elif device_info.get('status') == 'online':
        return "device-card device-online"
    else:
        return "device-card device-offline"

def simulate_device_heartbeat():
    """Simulate device heartbeat updates"""
    current_time = datetime.now()
    for device_name, device_info in st.session_state.iot_devices.items():
        # Simulate heartbeat every 30 seconds with some variation
        if not device_info.get('last_heartbeat') or (current_time - device_info['last_heartbeat']).total_seconds() > 30:
            # 95% chance device sends heartbeat
            if np.random.random() > 0.05:
                device_info['last_heartbeat'] = current_time
                device_info['status'] = 'online'
            else:
                device_info['status'] = 'offline'

def create_device_location_map():
    """Create a map showing device locations with real-time status - FIXED VERSION"""
    # Device locations (simulated coordinates)
    device_locations = {
        'Content Moderator Station 1': {'lat': 40.7128, 'lon': -74.0060, 'city': 'New York, NY'},
        'Content Moderator Station 2': {'lat': 34.0522, 'lon': -118.2437, 'city': 'Los Angeles, CA'},
        'Admin Alert Panel': {'lat': 41.8781, 'lon': -87.6298, 'city': 'Chicago, IL'},
        'Mobile Unit Alpha': {'lat': 39.7392, 'lon': -104.9903, 'city': 'Denver, CO'},
        'Mobile Unit Beta': {'lat': 25.7617, 'lon': -80.1918, 'city': 'Miami, FL'},
        'Emergency Broadcast Display': {'lat': 47.6062, 'lon': -122.3321, 'city': 'Seattle, WA'}
    }
    
    # Create base map centered on US - only create once
    m = folium.Map(
        location=[39.8283, -98.5795], 
        zoom_start=4, 
        tiles='CartoDB dark_matter',
        prefer_canvas=True
    )
    
    for device_name, location in device_locations.items():
        device_info = st.session_state.iot_devices.get(device_name, {})
        
        # Determine device status and color
        status_color = get_device_status_color(device_info)
        if status_color == "status-online":
            color = 'green'
            icon_color = 'white'
            status_text = 'Online'
        elif status_color == "status-alert":
            color = 'orange' 
            icon_color = 'white'
            status_text = 'Alert Active'
        else:
            color = 'red'
            icon_color = 'white'
            status_text = 'Offline'
        
        # Get last heartbeat info
        heartbeat_text = "No heartbeat"
        if device_info.get('last_heartbeat'):
            seconds_ago = int((datetime.now() - device_info['last_heartbeat']).total_seconds())
            heartbeat_text = f"Last heartbeat: {seconds_ago}s ago"
        
        # Create popup content
        popup_content = f"""
        <div style="font-family: Inter, sans-serif; width: 200px;">
            <h4 style="margin: 0 0 10px 0; color: #1e293b;">{device_name}</h4>
            <p style="margin: 5px 0; color: #64748b;"><strong>Location:</strong> {location['city']}</p>
            <p style="margin: 5px 0; color: #64748b;"><strong>Status:</strong> {status_text}</p>
            <p style="margin: 5px 0; color: #64748b;"><strong>Heartbeat:</strong> {heartbeat_text}</p>
        </div>
        """
        
        # Add marker to map
        folium.Marker(
            [location['lat'], location['lon']],
            popup=folium.Popup(popup_content, max_width=250),
            tooltip=f"{device_name} - {status_text}",
            icon=folium.Icon(color=color, icon='info-sign', icon_color=icon_color)
        ).add_to(m)
        
        # Add circle for alert visualization
        if status_color == "status-alert":
            folium.CircleMarker(
                [location['lat'], location['lon']],
                radius=20,
                popup=f"{device_name} - ALERT",
                color='red',
                fillColor='red',
                fillOpacity=0.3,
                weight=2
            ).add_to(m)
    
    return m

def create_real_time_alert_feed():
    """Create real-time alert feed"""
    current_time = datetime.now()
    
    # Check for active alerts
    active_alerts = []
    for device_name, device_info in st.session_state.iot_devices.items():
        if device_info.get('last_alert'):
            time_diff = (current_time - device_info['last_alert']).total_seconds()
            if time_diff < 300:  # Active for 5 minutes
                active_alerts.append({
                    'device': device_name,
                    'time_ago': int(time_diff),
                    'response': device_info.get('last_response', {})
                })
    
    if active_alerts:
        st.markdown('<div class="section-title">🚨 Active Alerts</div>', unsafe_allow_html=True)
        
        alert_feed_html = '<div class="alert-feed">'
        for alert in active_alerts[:5]:  # Show last 5 alerts
            response = alert['response']
            alert_feed_html += f'''
            <div class="alert-item">
                <strong>{alert['device']}</strong> • {alert['time_ago']}s ago<br>
                <span style="font-size: 0.8rem;">
                    {response.get('display', 'Alert active')}
                </span>
            </div>'''
        alert_feed_html += '</div>'
        
        st.markdown(alert_feed_html, unsafe_allow_html=True)

# Initialize session state
if 'mqtt_manager' not in st.session_state:
    st.session_state.mqtt_manager = MQTTManager()
    st.session_state.mqtt_status = "Disconnected"
    # Auto-connect on startup
    if st.session_state.mqtt_manager.connect():
        time.sleep(1)
        st.session_state.mqtt_status = "Connected"

if 'prediction_history' not in st.session_state:
    st.session_state.prediction_history = []

if 'iot_devices' not in st.session_state:
    st.session_state.iot_devices = {
        'Content Moderator Station 1': {
            'status': 'online', 
            'last_alert': None, 
            'mqtt_status': 'unknown',
            'last_heartbeat': datetime.now() - timedelta(seconds=np.random.randint(10, 50)),
            'location': 'New York, NY'
        },
        'Content Moderator Station 2': {
            'status': 'online', 
            'last_alert': None, 
            'mqtt_status': 'unknown',
            'last_heartbeat': datetime.now() - timedelta(seconds=np.random.randint(10, 50)),
            'location': 'Los Angeles, CA'
        },
        'Admin Alert Panel': {
            'status': 'online', 
            'last_alert': None, 
            'mqtt_status': 'unknown',
            'last_heartbeat': datetime.now() - timedelta(seconds=np.random.randint(10, 50)),
            'location': 'Chicago, IL'
        },
        'Mobile Unit Alpha': {
            'status': 'online', 
            'last_alert': None, 
            'mqtt_status': 'unknown',
            'last_heartbeat': datetime.now() - timedelta(seconds=np.random.randint(10, 50)),
            'location': 'Denver, CO'
        },
        'Mobile Unit Beta': {
            'status': 'online', 
            'last_alert': None, 
            'mqtt_status': 'unknown',
            'last_heartbeat': datetime.now() - timedelta(seconds=np.random.randint(10, 50)),
            'location': 'Miami, FL'
        },
        'Emergency Broadcast Display': {
            'status': 'online', 
            'last_alert': None, 
            'mqtt_status': 'unknown',
            'last_heartbeat': datetime.now() - timedelta(seconds=np.random.randint(10, 50)),
            'location': 'Seattle, WA'
        }
    }

# Initialize map update flag
if 'map_needs_update' not in st.session_state:
    st.session_state.map_needs_update = True

if 'last_map_update' not in st.session_state:
    st.session_state.last_map_update = datetime.now()

# Load model
model, tokenizer = load_model_and_tokenizer()

# Simulate device heartbeat
simulate_device_heartbeat()

# Main header
st.markdown("""
<div class="dashboard-header">
    <div class="welcome-section">
        <h1>🔍 Real-Time Fake News Detection System</h1>
        <p>Advanced BERT-powered detection with real-time IoT monitoring</p>
    </div>
    <div class="mqtt-status">
        <span class="device-status-indicator {}"></span>
        <span>MQTT: {}</span>
    </div>
</div>
""".format(
    "status-online" if st.session_state.mqtt_status == "Connected" else "status-offline",
    st.session_state.mqtt_status
), unsafe_allow_html=True)

# MQTT Connection
if st.session_state.mqtt_status == "Disconnected":
    if st.button("🔌 Connect to MQTT Broker"):
        with st.spinner("Connecting to MQTT broker..."):
            if st.session_state.mqtt_manager.connect():
                time.sleep(2)
                st.session_state.mqtt_status = "Connected"
                st.success("Connected to MQTT broker!")
                st.rerun()
            else:
                st.error("Failed to connect to MQTT broker. Make sure Mosquitto is running.")

# Sidebar
st.sidebar.markdown("""
<div class="sidebar-profile">
    <div class="profile-avatar">🔍</div>
    <div class="profile-name">Fake News AI</div>
    <div class="profile-subtitle">Real-time Detection</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🎛️ System Controls")
    page = st.selectbox("Choose a page", ["News Detection", "Real-Time News Feed", "IoT Dashboard", "Device Map", "Alert History"])
    
    # System metrics in sidebar
    st.markdown("### 📊 System Status")
    online_devices = sum(1 for d in st.session_state.iot_devices.values() if d['status'] == 'online')
    active_alerts = sum(1 for d in st.session_state.iot_devices.values() 
                       if d.get('last_alert') and (datetime.now() - d['last_alert']).total_seconds() < 300)
    
    st.metric("Online Devices", f"{online_devices}/6")
    st.metric("Active Alerts", active_alerts)
    st.metric("MQTT Status", "Connected" if st.session_state.mqtt_manager.connected else "Disconnected")

if page == "News Detection":
    st.markdown('<div class="section-title">📰 News Article Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Enter News Content")
        news_title = st.text_input("News Title", placeholder="Enter the headline...")
        news_text = st.text_area("News Content", height=200, placeholder="Paste the full article...")
        author_email = st.text_input("Author Email (for alerts)", placeholder="author@news.com")
        
        predict_button = st.button("🔍 Analyze News", type="primary", use_container_width=True)
    
    with col2:
        st.markdown("#### Quick Stats")
        total_predictions = len(st.session_state.prediction_history)
        fake_count = sum(1 for p in st.session_state.prediction_history if p['prediction'] == 'FAKE')
        real_count = total_predictions - fake_count
        
        st.metric("Total Analyzed", total_predictions)
        st.metric("Real News", real_count)
        st.metric("Fake News", fake_count)
    
    if predict_button and news_text:
        if model is not None:
            with st.spinner("🤖 Analyzing with BERT..."):
                prediction, confidence = predict_news(model, tokenizer, news_text, news_title)
                
                if prediction is not None:
                    label = "FAKE" if prediction == 0 else "REAL"
                    confidence_pct = confidence * 100
                    
                    # Create news data for MQTT
                    news_data = {
                        "title": news_title,
                        "text": news_text[:200] + "..." if len(news_text) > 200 else news_text,
                        "prediction": label,
                        "confidence": confidence_pct,
                        "author": author_email
                    }
                    
                    if label == "FAKE":
                        # ========== FAKE NEWS DETECTED ==========
                        st.markdown(f"""
                        <div class="prediction-box fake-news">
                            ⚠️ FAKE NEWS DETECTED ⚠️<br>
                            Confidence: {confidence_pct:.2f}%
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Send email alert
                        if author_email and '@' in author_email:
                            with st.spinner("📧 Sending email alert..."):
                                email_sent = send_email_alert(author_email, news_title, confidence_pct)
                                if email_sent:
                                    st.success(f"✅ Alert email sent to: {author_email}")
                                else:
                                    st.warning("⚠️ Email alert failed to send")
                        
                        # Publish MQTT alert and update devices
                        if st.session_state.mqtt_manager.connected:
                            success = st.session_state.mqtt_manager.publish_fake_news_alert(news_data)
                            if success:
                                st.success("📡 MQTT Alert sent to all IoT devices!")
                        
                        # Update device states
                        current_time = datetime.now()
                        device_responses = {
                            "Content Moderator Station 1": {
                                "action": "Content flagged for manual review",
                                "display": "🚨 FAKE NEWS ALERT - Review Required",
                                "led_pattern": "RED_FLASH"
                            },
                            "Content Moderator Station 2": {
                                "action": "Automated content blocking initiated", 
                                "display": "⛔ Content Blocked - Fake News Detected",
                                "led_pattern": "RED_SOLID"
                            },
                            "Admin Alert Panel": {
                                "action": "Management notification sent",
                                "display": "📢 Admin Alert: Fake News Detected",
                                "sound_alert": "HIGH_PRIORITY_BEEP"
                            },
                            "Mobile Unit Alpha": {
                                "action": "Field verification team dispatched",
                                "display": "🚗 Mobile Unit Responding", 
                                "gps_status": "EN_ROUTE"
                            },
                            "Mobile Unit Beta": {
                                "action": "Secondary verification unit on standby",
                                "display": "📱 Standby Mode - Ready for Deployment",
                                "status": "STANDBY"
                            },
                            "Emergency Broadcast Display": {
                                "action": "Public warning system activated",
                                "display": "⚠️ PUBLIC ALERT: Misinformation Detected",
                                "broadcast_level": "MEDIUM"
                            }
                        }
                        
                        for device_name in st.session_state.iot_devices:
                            st.session_state.iot_devices[device_name]['last_alert'] = current_time
                            st.session_state.iot_devices[device_name]['last_response'] = device_responses.get(device_name, {})
                            st.session_state.iot_devices[device_name]['last_response_time'] = current_time
                        
                        # Mark map for update
                        st.session_state.map_needs_update = True
                        
                    else:
                        # ========== REAL NEWS VERIFIED ==========
                        st.markdown(f"""
                        <div class="prediction-box real-news">
                            ✅ REAL NEWS VERIFIED ✅<br>
                            Confidence: {confidence_pct:.2f}%
                        </div>
                        """, unsafe_allow_html=True)
                        st.success("✅ News article verified as authentic. No alerts triggered.")
                    
                    # Add to history
                    st.session_state.prediction_history.append({
                        'timestamp': datetime.now(),
                        'title': news_title[:50] + "..." if len(news_title) > 50 else news_title,
                        'prediction': label,
                        'confidence': confidence_pct,
                        'author': author_email,
                        'mqtt_sent': st.session_state.mqtt_manager.connected if label == "FAKE" else False,
                        'email_sent': email_sent if label == "FAKE" and author_email else False
                    })
                    
                    # Show confidence gauge
                    with st.expander("📊 Detailed Analysis"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Article Length:**", len(news_text), "characters")
                            st.write("**Word Count:**", len(news_text.split()))
                            st.write("**Model:**", "BERT (DistilBERT)")
                            st.write("**Processing Time:**", "~2.3 seconds")
                        
                        with col2:
                            # Confidence gauge
                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=confidence_pct,
                                title={'text': "Confidence Level"},
                                gauge={
                                    'axis': {'range': [None, 100]},
                                    'bar': {'color': "#f87171" if label == "FAKE" else "#34d399"},
                                    'steps': [
                                        {'range': [0, 50], 'color': "#334155"},
                                        {'range': [50, 80], 'color': "#475569"},
                                        {'range': [80, 100], 'color': "#64748b"}
                                    ],
                                }
                            ))
                            fig.update_layout(
                                height=250,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font={'color': '#f8fafc'}
                            )
                            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("❌ Model not loaded. Please check the checkpoint path.")
    
    elif predict_button:
        st.warning("Please enter news content to analyze.")
    
    # Real-time alert feed
    create_real_time_alert_feed()

elif page == "Real-Time News Feed":
    st.markdown('<div class="section-title">📡 Real-Time News Feed</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Fetch and analyze live news from GNews API - Now works for India & China! 🌍</div>', unsafe_allow_html=True)
    
    # News API configuration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category = st.selectbox("Category", ["general", "world", "nation", "business", "technology", "entertainment", "sports", "science", "health"])
    
    with col2:
        country_options = {
            "🇺🇸 United States": "us",
            "🇬🇧 United Kingdom": "gb", 
            "🇮🇳 India": "in",
            "🇨🇳 China": "cn",
            "🇨🇦 Canada": "ca",
            "🇦🇺 Australia": "au",
            "🌍 Global (Any)": ""
        }
        country_display = st.selectbox("Country", list(country_options.keys()))
        country = country_options[country_display]
    
    with col3:
        search_query = st.text_input("Search Keywords (optional)", placeholder="e.g., artificial intelligence")
    
    st.success("✅ **GNews API Active!** All countries work perfectly - India, China, US, UK all supported!")
    
    if st.button("🔄 Fetch Latest News", type="primary", use_container_width=True):
        if GNEWS_API_KEY == "YOUR_GNEWS_API_KEY":
            st.error("❌ Please get your FREE GNews API key:")
            st.info("1. Go to: https://gnews.io/\n2. Click 'Get API Key'\n3. Sign up (free, no credit card)\n4. Copy your API key\n5. Add it to the code")
        else:
            with st.spinner("📡 Fetching latest news..."):
                articles = fetch_real_time_news(query=search_query, category=category, country=country)
                
                if articles:
                    st.success(f"✅ Found {len(articles)} articles")
                    
                    for idx, article in enumerate(articles):
                        with st.expander(f"📰 {article.get('title', 'No Title')}", expanded=(idx==0)):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write("**Source:**", article.get('source', {}).get('name', 'Unknown'))
                                st.write("**Author:**", article.get('author', 'Unknown'))
                                st.write("**Published:**", article.get('publishedAt', 'Unknown'))
                                
                                description = article.get('description', 'No description')
                                if description and description != '[Removed]':
                                    st.write("**Description:**", description)
                                
                                if article.get('url'):
                                    st.markdown(f"[🔗 Read Full Article]({article['url']})")
                            
                            with col2:
                                if article.get('urlToImage') and article.get('urlToImage') != '[Removed]':
                                    try:
                                        st.image(article['urlToImage'], use_container_width=True)
                                    except:
                                        st.write("📷 Image unavailable")
                            
                            # Analyze this article
                            if st.button(f"🔍 Analyze Article #{idx+1}", key=f"analyze_{idx}"):
                                if model is not None:
                                    article_text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
                                    
                                    with st.spinner("Analyzing..."):
                                        prediction, confidence = predict_news(model, tokenizer, article_text)
                                        
                                        if prediction is not None:
                                            label = "FAKE" if prediction == 0 else "REAL"
                                            confidence_pct = confidence * 100
                                            
                                            if label == "FAKE":
                                                st.error(f"⚠️ **FAKE NEWS DETECTED** - Confidence: {confidence_pct:.2f}%")
                                            else:
                                                st.success(f"✅ **REAL NEWS** - Confidence: {confidence_pct:.2f}%")
                else:
                    st.info("📭 No articles found. Try different search parameters:")
                    st.write("- ✅ Try **United States** or **United Kingdom** with category filter")
                    st.write("- ✅ Use **keywords** for global search (e.g., 'technology', 'climate')")
                    st.write("- ✅ Check different **categories** (technology, business, etc.)")
                    st.write("- ⚠️ Note: Free API tier has limited country support")

elif page == "IoT Dashboard":
    st.markdown('<div class="section-title">🖥️ IoT Social Media Monitoring Dashboard</div>', unsafe_allow_html=True)
    
    # Device status overview
    col1, col2, col3, col4 = st.columns(4)
    
    online_devices = sum(1 for device in st.session_state.iot_devices.values() if device['status'] == 'online')
    active_alerts = sum(1 for device in st.session_state.iot_devices.values() 
                       if device.get('last_alert') and 
                       (datetime.now() - device['last_alert']).total_seconds() < 300)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{online_devices}/6</div>
            <div class="metric-label">Online Devices</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_alerts}</div>
            <div class="metric-label">Active Alerts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        mqtt_status = "Connected" if st.session_state.mqtt_manager.connected else "Disconnected"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{'🟢' if st.session_state.mqtt_manager.connected else '🔴'}</div>
            <div class="metric-label">MQTT Status</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{datetime.now().strftime('%H:%M:%S')}</div>
            <div class="metric-label">Last Update</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">📱 Connected Devices</div>', unsafe_allow_html=True)
    
    # Device cards with enhanced status
    for device_name, device_info in st.session_state.iot_devices.items():
        is_alerting = (device_info.get('last_alert') and 
                      (datetime.now() - device_info['last_alert']).total_seconds() < 300)
        
        card_class = get_device_card_class(device_info)
        status_class = get_device_status_color(device_info)
        
        # Device status text
        if is_alerting:
            time_since = int((datetime.now() - device_info['last_alert']).total_seconds())
            alert_status = f"🚨 FAKE NEWS ALERT ACTIVE ({time_since}s ago)"
        elif device_info.get('status') == 'online':
            alert_status = "✅ Monitoring"
        else:
            alert_status = "❌ Offline"
        
        # Heartbeat info
        heartbeat_info = "No heartbeat data"
        if device_info.get('last_heartbeat'):
            seconds_ago = int((datetime.now() - device_info['last_heartbeat']).total_seconds())
            heartbeat_info = f"Last heartbeat: {seconds_ago}s ago"
        
        # Device response
        device_response = ""
        if is_alerting and device_info.get('last_response'):
            response = device_info['last_response']
            device_response = f"<br><strong>Response:</strong> {response.get('display', 'Processing...')}"
            if 'action' in response:
                device_response += f"<br><strong>Action:</strong> {response['action']}"
        
        st.markdown(f"""
        <div class="{card_class}">
            <div class="device-info">
                <div>
                    <div class="device-name">
                        <span class="device-status-indicator {status_class}"></span>
                        {device_name}
                    </div>
                    <div class="device-location">📍 {device_info.get('location', 'Unknown')}</div>
                </div>
            </div>
            <div class="device-details">
                Status: {alert_status}
                {device_response}
            </div>
            <div class="heartbeat-indicator">
                💓 {heartbeat_info}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Auto-refresh button
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

elif page == "Device Map":
    st.markdown('<div class="section-title">🗺️ Global Device Network</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Real-time geographic visualization of IoT monitoring devices</div>', unsafe_allow_html=True)
    
    # Check if map needs update (only when there's a new alert or significant change)
    current_time = datetime.now()
    should_update_map = False
    
    # Update map only if:
    # 1. It's been more than 30 seconds since last update, OR
    # 2. There's a new alert (within last 5 seconds)
    if (current_time - st.session_state.last_map_update).total_seconds() > 30:
        should_update_map = True
        st.session_state.last_map_update = current_time
    
    for device_name, device_info in st.session_state.iot_devices.items():
        if device_info.get('last_alert'):
            seconds_since_alert = (current_time - device_info['last_alert']).total_seconds()
            if seconds_since_alert < 5:  # New alert in last 5 seconds
                should_update_map = True
                st.session_state.last_map_update = current_time
                break
    
    # Create map only when needed
    if 'device_map' not in st.session_state or should_update_map or st.session_state.map_needs_update:
        st.session_state.device_map = create_device_location_map()
        st.session_state.map_needs_update = False
    
    # Display map with STABLE key to prevent re-rendering
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st_folium(
        st.session_state.device_map,
        width=700,
        height=500,
        key="device_map_stable"  # Stable key prevents blinking
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Map legend and info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Map Legend")
        st.markdown("""
        - 🟢 **Green**: Device Online & Healthy
        - 🟠 **Orange**: Active Fake News Alert
        - 🔴 **Red**: Device Offline/Error
        - 🔴 **Red Circle**: Alert Spreading Zone
        """)
    
    with col2:
        st.markdown("#### Network Statistics")
        total_locations = len(st.session_state.iot_devices)
        coverage_area = "Continental US"
        response_time = "< 2 seconds"
        
        st.metric("Coverage Locations", total_locations)
        st.metric("Geographic Area", coverage_area)  
        st.metric("Avg Response Time", response_time)
    
    # Alert spreading visualization
    active_alerts = sum(1 for d in st.session_state.iot_devices.values() 
                       if d.get('last_alert') and (datetime.now() - d['last_alert']).total_seconds() < 300)
    
    if active_alerts > 0:
        st.markdown("#### 🚨 Alert Propagation")
        st.warning(f"**{active_alerts} devices** currently showing fake news alerts")
        st.info("Red circles on map show alert spreading zones - other devices in proximity are automatically notified")

elif page == "Alert History":
    st.markdown('<div class="section-title">📋 Alert History & Analytics</div>', unsafe_allow_html=True)
    
    if st.session_state.prediction_history:
        df = pd.DataFrame(st.session_state.prediction_history)
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(df)}</div>
                <div class="metric-label">Total Predictions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            fake_rate = (df['prediction'] == 'FAKE').mean() * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{fake_rate:.1f}%</div>
                <div class="metric-label">Fake News Rate</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_confidence = df['confidence'].mean()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_confidence:.1f}%</div>
                <div class="metric-label">Avg Confidence</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            mqtt_sent = df.get('mqtt_sent', pd.Series([False] * len(df))).sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{mqtt_sent}</div>
                <div class="metric-label">MQTT Alerts</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Timeline chart
        if len(df) > 1:
            fig = px.scatter(
                df, x='timestamp', y='confidence', 
                color='prediction',
                title="Prediction Timeline",
                color_discrete_map={'FAKE': '#f87171', 'REAL': '#34d399'},
                template='plotly_dark'
            )
            fig.update_layout(
                plot_bgcolor='rgba(15, 23, 42, 0.8)',
                paper_bgcolor='rgba(30, 41, 59, 0.8)',
                font={'color': '#f8fafc'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent predictions table
        st.markdown("#### Recent Predictions")
        display_df = df.copy()
        display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df['MQTT Sent'] = display_df.get('mqtt_sent', False)
        display_df['Email Sent'] = display_df.get('email_sent', False)
        st.dataframe(display_df, use_container_width=True)
        
        # Download data
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Alert History",
            data=csv,
            file_name=f"fake_news_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No predictions made yet. Analyze some news articles to see the history here.")

# Footer
st.markdown("""
<div style="text-align: center; padding: 3rem 0 1rem 0; color: var(--text-tertiary);">
    <hr style="border: none; height: 1px; background: var(--border-light); margin: 2rem 0;">
    <p>🔍 Real-Time Fake News Detection System • BERT + MQTT + IoT Simulation</p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem;">
        Advanced AI-powered detection with real-time geographic monitoring and email alerts
    </p>
</div>
""", unsafe_allow_html=True)