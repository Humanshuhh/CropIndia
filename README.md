# 🌾 CropIndia: Kisan Sahayak

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**CropIndia: Kisan Sahayak** is an autonomous, AI-powered agronomic advisory and early-warning platform engineered specifically for Indian smallholder farmers. By fusing multimodal computer vision, soil health telemetry, geospatial weather patterns, and vernacular speech synthesis, CropIndia delivers hyper-localized, strictly regenerative, and actionable farming guidance.

---

## 📑 Table of Contents
- [Project Vision](#-project-vision)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [API Endpoints](#-core-api-endpoints)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Project Vision
Smallholder farmers in India face compounding challenges: unpredictable climate patterns, degrading soil health, and a reliance on expensive, synthetic chemical inputs. **Kisan Sahayak** bridges the digital divide by providing an accessible, voice-native, and scientifically grounded platform that promotes **regenerative agriculture**. We empower farmers to diagnose crop diseases instantly, restore soil biology, and make data-driven decisions using tools available in their native dialects.

---

## ✨ Key Features

- 🌿 **Multimodal Leaf Pathology & Diagnostics**: Leverages Google Gemini Vision models to accurately diagnose foliar pathogens, pest infestations, and chlorosis from smartphone photos. Outputs include symptom breakdowns, etiology, and actionable bio-remedies.
- ♻️ **Strictly Regenerative Agronomy**: Prescribes natural biological controls, bio-fungicides, and soil amendments (e.g., *Jeevamrit*, *Trichoderma harzianum*, fermented sour buttermilk, and Neem Seed Kernel Extract) over synthetic chemical inputs.
- 📊 **Soil Health Card Analysis**: Evaluates key soil metrics (Organic Carbon %, pH, texture, N-P-K) against regional agro-climatic baselines to generate customized biological restoration plans and crop rotation strategies.
- 🗣️ **Multilingual & Voice-Native Output**: Generates vernacular advisories with dialect mirroring (Hindi, Bengali, Telugu, Marathi, etc.). Every diagnosis includes a `spoken_summary` optimized for direct Text-to-Speech (TTS) playback.
- 🛰️ **Geospatial & Environmental Telemetry**: Contextualizes diagnostics using GPS coordinates, agro-climatic zone profiles, local weather history (Open-Meteo), and satellite vegetation indices (NDVI/NDWI).
- 🏗️ **CQRS Dual-Data Architecture**: Utilizes Cloud Firestore for sub-second operational state (farmer profiles, active scans) and Google BigQuery for longitudinal agronomic analytics and disease outbreak aggregation.
- 🔒 **Secure Token-Based Authentication**: Implements lightweight, cryptographically secure session authentication using Python’s `secrets` module alongside Firebase Admin SDK integration.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    %% Class Styles
    classDef client fill:#E8F5E9,stroke:#2E7D32,stroke-width:1.5px,color:#1B5E20;
    classDef gateway fill:#E3F2FD,stroke:#1565C0,stroke-width:1.5px,color:#0D47A1;
    classDef backend fill:#FFF8E1,stroke:#F57F17,stroke-width:1.5px,color:#E65100;
    classDef external fill:#F3E5F5,stroke:#7B1FA2,stroke-width:1.5px,color:#4A148C;
    classDef greenZone fill:#E8F8F5,stroke:#00897B,stroke-width:1.5px,color:#004D40;
    classDef blueZone fill:#E1F5FE,stroke:#0288D1,stroke-width:1.5px,color:#01579B;

    %% Client Layer
    subgraph Client["Frontend Client (React 18, Vite, Tailwind)"]
        UI_Diag["Leaf Pathogen Scanner<br/>(DiseaseDiagnosis.tsx)"]:::client
        UI_Soil["Soil Health Engine<br/>(KhetSwasthya.tsx)"]:::client
        UI_Mitra["Kisan Mitra Voice Bot<br/>(Audio Assistant)"]:::client
        UI_Hist["Consultation Timeline<br/>(History.tsx)"]:::client
        UI_Admin["Admin Metrics Portal<br/>(AdminDashboard.tsx)"]:::client
    end

    %% Gateway Layer
    subgraph Gateway["Reverse Proxy and Routing"]
        Proxy["Vite Dev Proxy / Cloud Run Router<br/>/api/v1/ Routes"]:::gateway
    end

    %% Backend Layer
    subgraph Backend["Backend Engine (FastAPI and Uvicorn)"]
        R_Diag["diagnostics.py<br/>POST /api/v1/diagnose"]:::backend
        R_Soil["soil.py<br/>POST /api/v1/soil/evaluate"]:::backend
        R_Weather["weather.py<br/>GET /api/v1/weather/forecast"]:::backend
        R_Hist["history.py<br/>GET /api/v1/history/farmer_id"]:::backend
        R_Voice["voice.py<br/>POST /api/v1/voice/listen"]:::backend
        R_Worker["APScheduler Worker<br/>Daily Farm Telemetry Scan"]:::backend
    end

    %% External Services
    subgraph External["External Services and AI Engines"]
        Gemini["Google Gemini API<br/>(3.8 Flash / 3.7 Flash)<br/>Multimodal Leaf Vision"]:::external
        OpenMeteo["Open-Meteo API<br/>7-Day Weather and Spray Suitability"]:::external
        Sentinel["Sentinel-2 MSI Telemetry<br/>10m NDVI and NDWI Canopy Bands"]:::external
        TTS["Google Text-to-Speech (gTTS)<br/>Regional Voice Advisory"]:::external
    end

    %% Data Layer
    subgraph GreenStore["Green Zone: Operational Store (Firestore)"]
        FS_Diag[("leaf_diagnostics")]:::greenZone
        FS_Soil[("soil_health_records")]:::greenZone
        FS_Warn[("early_warnings")]:::greenZone
        FS_Users[("farmers and admins")]:::greenZone
    end

    subgraph BlueStore["Blue Zone: Analytical Warehouse (BigQuery)"]
        BQ_Weather[("historical_weather")]:::blueZone
        BQ_SHC[("soil_health_cards")]:::blueZone
        BQ_Warn[("early_warning_logs")]:::blueZone
    end

    %% Client -> Gateway
    UI_Diag --> Proxy
    UI_Soil --> Proxy
    UI_Mitra --> Proxy
    UI_Hist --> Proxy
    UI_Admin --> Proxy

    %% Gateway -> Routers
    Proxy --> R_Diag
    Proxy --> R_Soil
    Proxy --> R_Weather
    Proxy --> R_Hist
    Proxy --> R_Voice

    %% Routers -> External
    R_Diag -->|Image Bytes + Context| Gemini
    R_Weather -->|Coordinates| OpenMeteo
    R_Worker -->|Coordinate Bounding Box| Sentinel
    R_Voice -->|Speech Synthesis Request| TTS

    %% Persistence -> Firestore (Green Zone)
    R_Diag -->|save_leaf_diagnostic| FS_Diag
    R_Soil -->|save_soil_record| FS_Soil
    R_Hist -->|get_combined_farmer_history| FS_Diag
    R_Hist -->|get_combined_farmer_history| FS_Soil
    R_Worker -->|Trigger alerts| FS_Warn

    %% Persistence -> BigQuery (Blue Zone)
    R_Worker -.->|Batch load weather logs| BQ_Weather
    R_Soil -.->|Batch load SHC records| BQ_SHC
    R_Worker -.->|Audit warning events| BQ_Warn
```
---

## 💻 Technology Stack

| Category | Technologies |
| :--- | :--- |
| **Backend** | FastAPI, Uvicorn, Pydantic v2, Python `secrets` |
| **AI & Vision** | Google GenAI SDK (`gemini-3.7-flash` / `3.6-flash`), Pillow (PIL) |
| **Databases** | Google Cloud Firestore (Operational), Google BigQuery (Analytical) |
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide React, Web Audio API |
| **External APIs** | Open-Meteo (Historical & Forecast), Satellite NDVI/NDWI feeds |
| **DevOps & Cloud** | Google Cloud Run, Docker, GitHub Actions (CI/CD) |

----------------------------------------------------------------------------------------

```text
CropIndia/
├── backend/
│   ├── agronomy/                 # Automated agro-climatic & background worker tasks
│   │   ├── __init__.py
│   │   └── telemetry_worker.py   # Scheduled Sentinel-2 & weather telemetry scan jobs
│   ├── database/                 # Persistence layer (Firestore Green Zone & BigQuery Blue Zone)
│   │   ├── __init__.py
│   │   ├── bigquery.py           # Google Cloud BigQuery client connection & credentials
│   │   ├── bigquery_crud.py      # BigQuery batch ingestion (weather, bulk SHC, warning audit logs)
│   │   ├── firebase.py           # Firebase Admin SDK & Cloud Firestore initialization
│   │   ├── firestore_crud.py     # Firestore CRUD (farmers, leaf diagnostics, soil records, warnings)
│   │   └── credentials/          # Local service account keys (gitignored)
│   │       └── firebase-key.json
│   ├── ml_engine/                # AI reasoning & agronomic models
│   │   ├── __init__.py
│   │   └── soil_advisor.py       # Regenerative soil health analysis & crop rotation engine
│   ├── routers/                  # Modular FastAPI HTTP route controllers
│   │   ├── __init__.py
│   │   ├── admin.py              # Admin metrics & dashboard analytics
│   │   ├── auth.py               # Farmer & administrative authentication
│   │   ├── diagnostics.py        # Plant leaf vision diagnosis & eco-friendly remedy pipeline
│   │   ├── early_warning.py      # Climate stress, drought, & pathogen outbreak warnings
│   │   ├── farmer_assistant.py   # Kisan Mitra conversational AI assistant
│   │   ├── farmer_profile.py     # Farmer landholding & profile management
│   │   ├── history.py            # Combined foliar scans & soil evaluation history feed
│   │   ├── soil.py               # Soil Health Card evaluation & biological amendment planning
│   │   ├── telemetry.py          # Sentinel-2 MSI surface reflectance (NDVI/NDWI) mapping
│   │   ├── voice.py              # Text-to-speech audio streaming endpoints (gTTS)
│   │   └── weather.py            # Keyless agrometeorological 7-day forecast & spray advisories
│   ├── schemas/                  # Pydantic v2 data models & request/response contracts
│   │   ├── __init__.py
│   │   ├── Farmer_schemas.py
│   │   ├── climate_schemas.py
│   │   ├── diagnosis_schemas.py
│   │   ├── soil_schemas.py
│   │   └── warning_schemas.py
│   ├── services/                 # External service integrations
│   │   ├── __init__.py
│   │   └── weather.py            # Open-Meteo client & spray suitability calculations
│   └── main.py                   # FastAPI application factory, lifespan scheduler, CORS & router mounting
├── frontend/
│   ├── public/                   # Static browser assets & icons
│   ├── src/
│   │   ├── components/           # Reusable UI cards, audio players, error alerts, & layouts
│   │   │   └── common/
│   │   │       ├── ErrorMessage.tsx
│   │   │       └── VoiceReaderButton.tsx
│   │   ├── context/              # Global React state management
│   │   │   ├── LanguageContext.tsx
│   │   │   ├── ResultCacheContext.tsx
│   │   │   └── VoiceContext.tsx
│   │   ├── pages/                # Primary application views
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── DiseaseDiagnosis.tsx
│   │   │   ├── History.tsx       # Unified consultation history timeline
│   │   │   ├── Home.tsx
│   │   │   ├── KhetSwasthya.tsx  # Soil advisory, live Open-Meteo weather & Sentinel-2 cards
│   │   │   └── KisanMitra.tsx
│   │   ├── services/             # Axios/fetch API client adapters
│   │   │   ├── diagnostics.ts
│   │   │   ├── history.ts
│   │   │   └── soil.ts
│   │   ├── types/                # TypeScript interface definitions & data contracts
│   │   │   ├── api.types.ts
│   │   │   └── soil.types.ts
│   │   ├── App.tsx               # Main routing & layout assembly
│   │   └── main.tsx              # React DOM entry point
│   ├── index.html
│   ├── package.json              # Frontend npm dependencies (React 18, Lucide, Tailwind)
│   ├── tsconfig.json             # TypeScript compiler configuration
│   └── vite.config.ts            # Vite bundler configuration & /api reverse-proxy
├── .env.example                  # Template for required environment variables
├── .gitignore                    # Git tracking exclusions (virtual environments, keys, dist)
├── requirements.txt              # Backend Python dependencies (FastAPI, google-genai, gTTS, etc.)
└── README.md                     # Technical architecture, installation guide, & API documentation

```
---

## 🚀 Getting Started

Follow these steps to set up the CropIndia platform locally on your machine.

### Prerequisites

Before you begin, ensure you have the following installed and configured:
- **Python 3.10** or higher ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and **npm** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- A **Google Cloud Project** with the following APIs enabled:
  - [Cloud Firestore API](https://console.cloud.google.com/apis/library/firestore.googleapis.com)
  - [BigQuery API](https://console.cloud.google.com/apis/library/bigquery.googleapis.com)
  - [Gemini API](https://ai.google.dev/)
- A Firebase Service Account key (`firebase-key.json`).

---

### 1. Environment Setup

Create a `.env` file in the **root directory** of the project to store your environment variables. You can copy the contents from `.env.example` and update them:

```bash
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

#### Google Cloud & Firebase Configuration
GOOGLE_CLOUD_PROJECT=cropindia-prod
FIREBASE_KEY_PATH=backend/database/credentials/firebase-key.json
# Alternative for containerized environments:
# FIREBASE_KEY_BASE64=your_base64_encoded_service_account_json

# BigQuery Analytics Settings
BIGQUERY_DATASET_ID=cropindia_analytics
BIGQUERY_DIAGNOSTICS_TABLE=leaf_diagnostics_log
BIGQUERY_SOIL_TABLE=soil_health_log

# Application Security
SECRET_KEY=generate_with_python_secrets_token_hex_32
```


---

### 2. Backend Setup

Open your terminal and run the following commands to set up the Python backend:

```bash
# 1. Clone the repository
git clone [https://github.com/Humanshuhh/CropIndia.git](https://github.com/Humanshuhh/CropIndia.git)
cd CropIndia

# 2. Create and activate a virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate
# On Linux / macOS:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Start the FastAPI development server
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
---
## 3.  Frontend Setup

Open a new terminal window (keep the backend running in the first one) and run the following commands to start the React frontend:

```bash
# 1. Navigate to the frontend directory
cd CropIndia/frontend

# 2. Install Node.js dependencies
npm install

# 3. Start the Vite development server
npm run dev
```
---

## 🔌 Core API Endpoints

The backend exposes a RESTful API designed for seamless integration with the React frontend and mobile clients. All endpoints (except `/health`) require a valid session token in the `Authorization` header.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | **System Health Check.** Verifies server status, Cloud Firestore connectivity, and BigQuery bindings. |
| `POST` | `/api/v1/diagnose` | **Leaf Pathology Diagnostics.** Accepts a multipart image upload, GPS coordinates, and language preference. Returns foliar pathology results, etiology, and bio-remedies. |
| `POST` | `/api/v1/soil/regenerative-plan` | **Soil Health Analysis.** Evaluates uploaded soil health card metrics (N-P-K, pH, Organic Carbon) and outputs a customized biological restoration plan. |
| `POST` | `/api/v1/farmer/query` | **Multimodal Farmer Assistant.** Handles natural text or audio byte queries. Performs dialect matching and returns context-aware agronomic advice. |
| `POST` | `/api/v1/translate-advisory` | **Advisory Translation.** Translates a cached diagnostic or soil advisory to a new target regional language without re-invoking the heavy vision models. |
|`POST`|`/api/v1/auth/signup`| **Farmer Onboarding.** Registers phone, name, and securely hashes PIN/MPIN.
|`POST`|`/api/v1/auth/login`|Secure Unified Login. Validates phone and hashed PIN/MPIN matching.

> 💡 **Interactive Documentation:** Because the backend is built with **FastAPI**, you can explore all endpoints, view request/response schemas, and test the API directly in your browser by visiting the auto-generated Swagger UI at: 
> **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**

---

## 🌐 Digital Public Good & BRICS Alignment
Kisan Sahayak is designed to scale across state borders and emerging economies:

1)Interoperable Data Pipeline: BigQuery schema enables cross-border diagnostic telemetry sharing across agricultural ministries.

2)Modular AI Engine: Easily customizable for localized regional crops across BRICS nations.

3)Low-Bandwidth Optimization: Lightweight API responses and cached translation endpoints ensure reliability in poor rural connectivity zones.



## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

---



