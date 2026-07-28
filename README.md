# ⚡ VehicleIQ — Real-Time Vehicle Health Prediction System

> **AI-powered vehicle health prediction system that learns from a user's personal driving behaviour via OBD-II sensor data and predicts component failures before they happen, in plain language.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14+-000000.svg?style=flat&logo=Next.js&logoColor=white)](https://nextjs.org)
[![React Native](https://img.shields.io/badge/React_Native-Expo-61DAFB.svg?style=flat&logo=react&logoColor=white)](https://reactnative.dev)
[![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-1.3+-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.14+-FF6F00.svg?style=flat&logo=tensorflow&logoColor=white)](https://tensorflow.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://docker.com)

---

## 📐 System Architecture Diagram

```mermaid
flowchart TB
    subgraph Layer1 ["1. Telemetry Data Source Layer"]
        OBD["ELM327 Bluetooth OBD-II Dongle"]
        SIM["OBD-II Physics Simulator (4 Scenarios)"]
    end

    subgraph Layer2 ["2. Data Ingestion & Cleaning"]
        READER["BaseOBDReader Abstraction"]
        PIPELINE["Pandas OBDDataPipeline"]
        DB[("SQLite / PostgreSQL DB")]
    end

    subgraph Layer3 ["3. AI/ML Analytics & Explainability Engine"]
        FEAT["OBDFeatureExtractor (Sliding Windows)"]
        STYLE["Driving Style Classifier (Random Forest)"]
        LSTM["Component Health Predictor (LSTM)"]
        SHAP["Explainability Engine (Plain-Language Alerts)"]
    end

    subgraph Layer4 ["4. Application Serving Layer"]
        API["FastAPI REST Backend + JWT Security"]
        WEB["Next.js 14 Web Dashboard"]
        MOBILE["React Native Expo Mobile App"]
        PDF["Printable Mechanic Report Generator"]
    end

    OBD -->|Raw Telemetry| READER
    SIM -->|Simulated Telemetry| READER
    READER --> PIPELINE
    PIPELINE --> DB
    PIPELINE --> FEAT
    FEAT --> STYLE
    FEAT --> LSTM
    STYLE --> SHAP
    LSTM --> SHAP
    SHAP --> API
    API --> WEB
    API --> MOBILE
    API --> PDF
```

---

## ✨ Project Highlights & Features

1. **OBD-II Real-Time Ingestion**: Connects to physical Bluetooth ELM327 dongles or emulates physics-backed telemetry across City, Highway, Sport, and Overheat driving scenarios.
2. **Behavioral Feature Engineering**: Extracts rolling hard braking events, high-RPM frequency ratios, idle time ratios, and thermal stress indices.
3. **Driving Style Classifier**: Random Forest sliding-window classifier categorizing driving styles (`Gentle`, `Moderate`, `Aggressive`) and calculating a 0-100 behavior score.
4. **LSTM Failure Prediction**: Sequential model estimating remaining health percentages (0-100%) for **Brake Pad Wear**, **Engine Stress**, and **Battery/Charging Health**.
5. **Plain-Language Diagnostics**: Converts numerical ML predictions into human-readable alerts with driver recommendations and mechanic summaries.
6. **Next.js Web Dashboard & Mobile App**: Modern dark-mode web dashboard and React Native (Expo) mobile app for live monitoring and mobile push notifications.
7. **Full MLOps Integration**: Docker Compose multi-container setup, Optuna hyperparameter optimization, MLflow experiment tracking, and GitHub Actions CI/CD.

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Telemetry & Ingestion** | Python, `python-OBD`, `pyserial`, Pandas, NumPy |
| **Machine Learning** | Scikit-learn, TensorFlow/Keras (LSTM), Optuna, MLflow, SHAP |
| **Backend API** | FastAPI, Uvicorn, SQLAlchemy, Pydantic V2, PyJWT, Passlib |
| **Web Dashboard** | Next.js 14, React 18, Glassmorphism Vanilla CSS, Lucide Icons |
| **Mobile App** | React Native, Expo SDK, `react-native-ble-plx` |
| **Databases** | SQLite (Dev), PostgreSQL 15 (Prod) |
| **DevOps & Cloud** | Docker, Docker Compose, Render, Vercel, GitHub Actions |

---

## 🚀 Quickstart & Local Setup

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/VehicleIQ.git
cd VehicleIQ

# Create & activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Database & Data Ingestion Test
```bash
# Ingest 30 simulated telemetry frames into local SQLite database
python main.py --mode simulation --scenario city_driving --count 30
```

### 3. Train ML Models & Generate Artifacts
```bash
python train_pipeline.py
```

### 4. Run FastAPI Backend API
```bash
uvicorn backend.app.main:app --reload --port 8000
```
- Interactive API Docs (Swagger UI): `http://localhost:8000/docs`

### 5. Run Next.js Web Dashboard
```bash
cd frontend
npm install
npm run dev
```
- Open `http://localhost:3000` in your browser.

---

## 🐳 Docker Compose Deployment

Spin up the complete multi-container stack (PostgreSQL + FastAPI + Next.js Dashboard):

```bash
docker compose up --build
```

- **Next.js Dashboard**: `http://localhost:3000`
- **FastAPI API**: `http://localhost:8000`
- **PostgreSQL Database**: `localhost:5432`

---

## 🧪 Running Automated Test Suite

```bash
# Run all Phase 1-4 unit and integration test suites
python test_pipeline.py
python test_phase2.py
python test_phase3.py
python test_phase4.py
```

---

## 🌐 Production Cloud Deployment

- **Backend API & PostgreSQL**: Configured for **Render.com** via `render.yaml`.
- **Frontend Dashboard**: Configured for **Vercel** via `vercel.json`.
- **CI/CD Pipeline**: Configured for **GitHub Actions** via `.github/workflows/deploy.yml`.

---

## 📜 License
Developed as a Final-Year Computer Science (AI/ML) Capstone Project. Open source under MIT License.
