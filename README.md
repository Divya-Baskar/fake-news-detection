# fake-news-detection
Real-Time Fake News Detection System integrating DistilBERT (AI) &amp; MQTT (IoT). Detects misinformation with 94.3% accuracy and broadcasts instant alerts to distributed IoT devices in &lt;0.35s. Features a live Streamlit dashboard, geospatial mapping, and active moderator notification.

# 🛡️ AI-IoT Integrated Fake News Defense System

![DistilBERT](https://img.shields.io/badge/Model-DistilBERT-blue)
![MQTT](https://img.shields.io/badge/Protocol-MQTT-orange)
![Latency](https://img.shields.io/badge/Latency-%3C0.35s-success)
![Accuracy](https://img.shields.io/badge/Accuracy-94.3%25-green)

## ⚡ Executive Summary
This project is an **active defense system** against misinformation, bridging the gap between Natural Language Processing (NLP) and the Internet of Things (IoT). 

Unlike passive classifiers, this system analyzes news streams in real-time using **DistilBERT** and broadcasts "Red Alerts" to distributed IoT nodes via the **MQTT protocol**. The system achieves sub-second latency, ensuring misinformation is flagged before it spreads.

## 📊 Key Performance Metrics
| Metric | Value | Description |
| :--- | :--- | :--- |
| **Model Accuracy** | **94.3%** | Fine-tuned DistilBERT on fake news datasets. |
| **System Latency** | **<0.35s** | Time taken from input → Model → IoT Alert. |
| **Communication** | **MQTT** | Lightweight pub/sub protocol for instant broadcasting. |

## 🏗️ System Architecture
The data flows through three distinct layers:
1.  **Ingestion Layer:** Streamlit Interface / Live News Feed.
2.  **Processing Layer:** DistilBERT Transformer Model (Semantic Analysis).
3.  **Action Layer:** MQTT Broker triggers IoT Devices & Geospatial Dashboard.

## 🌟 Key Features
* **🧠 Advanced NLP:** Utilizes `DistilBERT` for deep semantic understanding of news content (superior to standard LSTM/RNN).
* **📡 IoT Integration:** Uses **MQTT** to publish alerts to subscribed topics. Physical IoT devices (simulated or real) receive distinct signals (Red LED for Fake, Green for Real).
* **🗺️ Geospatial Tracking:** Plots the origin of news sources on a live map to identify "misinformation hotspots."
* **⚡ Low Latency:** Optimized pipeline ensures alerts are generated in under 350 milliseconds.
* **🔔 Automated Notification:** Active moderator notification system for flagged high-risk content.

## 🛠️ Tech Stack
* **AI/ML:** PyTorch, Hugging Face Transformers (DistilBERT), Scikit-learn.
* **IoT/Networking:** Paho-MQTT, Mosquitto Broker.
* **Web/UI:** Streamlit, PyDeck (for maps).
* **Language:** Python 3.9+

## ⚙️ Installation & Setup

### 1. Clone the Repo
```bash
git clone [https://github.com/YOUR_USERNAME/fake-news-iot-defense.git](https://github.com/YOUR_USERNAME/fake-news-iot-defense.git)
