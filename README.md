# Aero-Optimize ✈️

**Predictive & Prescriptive Airline Operations System**

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.59-FF4B4B.svg)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)

A full-stack data science solution for the aviation industry designed to mitigate the impact of flight delays. This project bridges the gap between **predictive analytics** (forecasting when delays will occur) and **prescriptive optimization** (calculating the mathematically optimal business response). 

The application allows dispatchers to dynamically reassign flight crews during disruptions, balancing operational efficiency with strict FAA regulatory constraints.

---

## 🚀 Live Application
* **Frontend:** [Streamlit Community Cloud](https://aero-optimize.streamlit.app)
* **Backend API:** Hosted on Render

## 🛠️ Tech Stack

* **Machine Learning & OR:** `scikit-learn`, `XGBoost`, `PuLP`, `Pandas`
* **Backend:** FastAPI, Uvicorn
* **Frontend:** Streamlit, PyDeck (Interactive 3D Mapping)
* **Database:** PostgreSQL (Neon), `SQLAlchemy`, `pg8000` (Pure Python driver for cloud stability)
* **Deployment:** Render (Backend API), Streamlit Community Cloud (Frontend)

## ✨ Key Features

1. **Predictive Delay Modeling:** Utilizes a trained XGBoost classifier to predict flight delays based on complex pre-flight conditions, including WMO weather codes, dynamic airport traffic, and historical route delay rates.
2. **Prescriptive Crew Optimization:** Translates disrupted crew schedules into a Mixed-Integer Programming (MIP) problem using PuLP. Automatically calculates the optimal standby crew reassignment to minimize hourly costs without violating FAA maximum working hour constraints.
3. **Interactive 3D Dashboard:** Features a compartmented Streamlit UI with PyDeck integration to render dynamic, interactive 3D arc maps of flight paths based on latitude/longitude queries.
4. **Cloud-Native Database Architecture:** Leverages PostgreSQL with a pure Python `pg8000` driver to prevent C-level memory conflicts during deployment, utilizing SQLAlchemy for robust ORM integration.

## 💻 Local Development Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/aero-optimize.git
cd aero-optimize
```

### 2. Set Up the Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
Install the required packages for both the frontend and backend directly into your virtual environment:
```cmd
venv\Scripts\python.exe -m pip install -r frontend/requirements.txt
venv\Scripts\python.exe -m pip install -r backend/requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the root directory and inside the `frontend/` directory (or use Streamlit Secrets) with your database and API credentials:

```ini
DB_USER="your_db_user"
DB_PASSWORD="your_db_password"
DB_HOST="your_db_host.aws.neon.tech"
DB_PORT="5432"
DB_NAME="your_db_name"
API_URL="http://127.0.0.1:10000/api/check_flight" 
```

### 5. Run the Application

**Start the Backend (FastAPI):**
Open a terminal and run the API server from the `backend` folder:
```cmd
cd backend
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 10000 --reload
```

**Start the Frontend (Streamlit):**
Open a second terminal, ensure you are in the project root, and launch the dashboard:
```cmd
venv\Scripts\python.exe -m streamlit run frontend/app.py
```

## 📂 Project Structure
```text
aero-optimize/
│
├── backend/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── trained_models/         # Contains the serialized XGBoost .joblib models
│   └── requirements.txt        # Backend dependencies
│
├── frontend/
│   ├── app.py                  # Main Streamlit dashboard script
│   ├── database.py             # SQLAlchemy connection logic (using pg8000)
│   └── requirements.txt        # Frontend dependencies (Streamlit, PyDeck, etc.)
│
├── .gitignore
└── README.md
```
