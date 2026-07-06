# Smart Supply Chain System

An AI-powered logistics and supply chain management platform with **7 role-based panels**, **live map tracking**, and **ML-driven delivery prediction** using Random Forest, Gradient Boosting, and more.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Key Features](#key-features)
4. [User Roles & Panels](#user-roles--panels)
5. [Prerequisites](#prerequisites)
6. [Installation & Setup](#installation--setup)
7. [Running the Project](#running-the-project)
8. [Training ML Models](#training-ml-models)
9. [Project Structure](#project-structure)
10. [Troubleshooting](#troubleshooting)

---

## Project Overview
This system manages end-to-end supply chain operations with:
- Real-time shipment tracking on a live Google Map
- ML models to predict disruptions, disruption severity, and final delivery status
- Role-based access control for 7 different user types
- Analytics and reporting features

---

## Tech Stack
| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Tailwind CSS, Vite, React Query |
| **Backend** | Django 4.2, Django REST Framework (DRF) |
| **Database** | PostgreSQL (Docker) / SQLite (Local Dev) |
| **AI/ML** | Python, Pandas, NumPy, Scikit-learn, Joblib |
| **Live Map** | Google Maps API |
| **Auth** | JWT (JSON Web Tokens) |
| **Deployment** | Docker, Docker Compose, Nginx |

---

## Key Features
1. **Live Shipment Tracking** - Interactive Google Maps to track shipments in real time
2. **ML-Powered Predictions**
   - Disruption Occurrence Prediction (binary classification)
   - Disruption Severity Prediction (multi-class: Low/Medium/High/Critical)
   - Final Delivery Status Prediction (multi-class: On-Time/Delayed/Critically Delayed)
3. **7 Role-Based Dashboards** - Separate interfaces for each user type
4. **Inventory Management** - Track stock levels and warehouse operations
5. **Route Optimization** - Find optimal routes for shipments
6. **Supplier Management** - Manage supplier information and performance
7. **Analytics & Reports** - Visualize KPIs and shipment status trends

---

## User Roles & Panels
| Role | Key Access & Features |
|------|-----------------------|
| **1. Administrator** | Full system access, manage users, view all data, configure settings |
| **2. Warehouse Manager** | Inventory management, warehouse operations, stock tracking |
| **3. Supplier** | Supplier profile, delivery history, order management |
| **4. Transporter** | Shipment assignments, route management, update shipment status |
| **5. Customer** | Track own shipments, view order history, receive notifications |
| **6. Analytics Manager** | View and generate reports, analyze KPIs, export data |
| **7. Support Agent** | Handle customer queries, update shipment issues, manage notifications |

---

## Prerequisites
Make sure the following are installed on your machine:
- **Python** 3.10+ (for local backend)
- **Node.js** 18+ & **npm** 9+ (for frontend)
- **Git** (for version control)
- **Optional (for Docker deployment):** Docker & Docker Compose

---

## Installation & Setup

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd Smart_Supply_Chain_System
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your values:
```bash
# For Windows
copy .env.example .env

# For macOS/Linux
cp .env.example .env
```

#### Edit `.env` file:
- **DJANGO_SECRET_KEY**: Generate a secure secret key (use `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
- **GOOGLE_MAPS_API_KEY**: Your Google Maps API key (required for live map)
- **WEATHER_API_KEY**: Optional, for weather data integration
- Other variables have default values for local dev.

---

## Running the Project

Choose one of the options below:

---

### **Option A: Local Development (Recommended for Group Members)**
No Docker required! Uses SQLite for database.

#### Step 1: Backend Setup
```bash
cd backend

# Create virtual environment (Windows)
python -m venv venv
venv\Scripts\activate

# Create virtual environment (macOS/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Set Django settings module (Windows)
set DJANGO_SETTINGS_MODULE=config.settings.development

# Set Django settings module (macOS/Linux)
export DJANGO_SETTINGS_MODULE=config.settings.development

# Apply migrations
python manage.py migrate

# Create a superuser (for Django admin)
python manage.py createsuperuser

# Start backend server
python manage.py runserver
```
Backend will be available at `http://localhost:8000`

#### Step 2: Frontend Setup
Open a **new terminal window**:
```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend will be available at `http://localhost:3000` (or the port shown in terminal)

---

### **Option B: Docker Compose**
Requires Docker & Docker Compose installed.

```bash
# Build and start all services
docker-compose up --build

# To run in background
docker-compose up -d --build
```

**Create a superuser (once containers are running):**
```bash
docker-compose exec backend python manage.py createsuperuser
```

**Access the app:**
- Frontend: `http://localhost`
- Backend API: `http://localhost/api/v1/`
- Django Admin: `http://localhost/admin/`

---

## Training ML Models
To train and save the ML models (Random Forest, etc.):

```bash
# Make sure you're in project root and backend venv is activated
python train_and_evaluate.py
```

This will:
1. Load the dataset from `data/indian_route_legs.csv`
2. Train 4 models per target
3. Evaluate all models
4. Save **best-performing models** to `backend/ml_models/`
5. Save results to `data/model_results.csv`

---

## Project Structure
```
Smart_Supply_Chain_System/
├── .env                          # Environment variables
├── .env.example                  # Env variable template
├── .gitignore
├── docker-compose.yml            # Docker services config
├── Makefile                      # Convenience commands (Docker)
├── README.md
│
├── backend/                      # Django Backend
│   ├── apps/                     # Django apps
│   │   ├── users/                # User management, auth, roles
│   │   ├── shipments/            # Shipment tracking
│   │   ├── inventory/            # Inventory & warehouse management
│   │   ├── suppliers/            # Supplier management
│   │   ├── routes/               # Route optimization
│   │   ├── analytics/            # Analytics & reporting
│   │   ├── notifications/        # Notifications & alerts
│   │   └── ai_engine/            # ML integration (predictions)
│   ├── config/                   # Project settings
│   │   ├── settings/
│   │   │   ├── base.py           # Base settings (shared)
│   │   │   ├── development.py    # Local dev settings (SQLite)
│   │   │   └── production.py     # Prod settings (PostgreSQL)
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── ml_models/                # Trained ML models (saved here)
│   ├── manage.py
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── frontend/                     # React Frontend
│   ├── src/
│   │   ├── components/           # Reusable UI components
│   │   ├── pages/                # Page components (by feature/role)
│   │   ├── hooks/                # React hooks (React Query)
│   │   ├── services/             # API clients
│   │   ├── store/                # Zustand global state
│   │   ├── types/                # TypeScript type definitions
│   │   ├── utils/                # Helper functions
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── package.json
│
├── data/                         # Datasets & model results
│   ├── indian_route_legs.csv     # Main dataset for ML training
│   └── model_results.csv         # ML model evaluation results
│
├── nginx/                        # Nginx reverse proxy config
│   └── nginx.conf
│
├── train_and_evaluate.py         # ML training script
├── generate_dataset.py           # Dataset generation script
└── generate_indian_routing_dataset.py
```

---

## Troubleshooting

**Port already in use:**
- If 3000 or 8000 are taken, the dev servers will use another port (check terminal)
- For Docker, edit `docker-compose.yml` to change ports

**Backend database errors:**
- For local dev, we use SQLite, so no Postgres setup needed!
- Make sure you applied migrations with `python manage.py migrate`

**Frontend not connecting to backend:**
- Make sure backend server is running
- Check Vite proxy config in `frontend/vite.config.ts`
- Verify `VITE_API_BASE_URL` is set correctly in your `.env`

**ML model not found:**
- Run `python train_and_evaluate.py` to train and save models

---

## Contributors
Add your group members here!

---

## License
[Your License Here]
