# FinCortex – Financial Health Scoring & Recommendation Dashboard

**FinCortex** is a financial health analysis platform that helps users understand their financial position through explainable scoring, expense analysis, savings evaluation, and personalised financial recommendations.

The application analyses monthly income, expenses, existing savings, and risk appetite to generate a financial health score and actionable suggestions for better financial planning.

## 🚀 Key Features

- **Financial Health Score:** Calculates a score out of 100 to evaluate the user's financial position.
- **Income & Expense Analysis:** Analyses monthly salary, rent, groceries, transportation, loan EMIs, and other spending.
- **Savings Rate Calculation:** Calculates the percentage of income remaining after monthly expenses.
- **Emergency Fund Analysis:** Evaluates emergency savings, target savings, and emergency runway.
- **Explainable Scoring:** Highlights the financial factors affecting the overall score.
- **Personalised Recommendations:** Generates actionable suggestions based on financial information and risk appetite.
- **Suggested Savings Allocation:** Provides a suggested distribution of monthly surplus.
- **50/30/20 Budget Analysis:** Compares spending patterns against a commonly used budgeting guideline.
- **Financial History:** Allows users to view previous financial assessments.

## 🛠️ Tech Stack

| Component | Technologies |
|---|---|
| Frontend | Next.js, React, JavaScript |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn |
| Data Processing | Pandas, NumPy |
| Database | SQLite |
| API Server | Uvicorn |
| Styling | CSS, Tailwind CSS |

## 🏗️ Project Architecture

FinCortex/
│
├── backend/
│   ├── app/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── explain.py
│   │   ├── features.py
│   │   ├── main.py
│   │   ├── recommendations.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── scoring.py
│   │
│   ├── ml/
│   │   ├── data/
│   │   ├── generate_data.py
│   │   ├── model.pkl
│   │   └── train_model.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── package.json
│   └── .env.local.example
│
└── README.md


## ⚙️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Shreeya-26/FinCortex.git
cd FinCortex
```

### 2. Setup the Backend

Navigate to the backend folder:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

API Documentation:

`http://127.0.0.1:8000/docs`

### 3. Setup the Frontend

Open a second terminal and navigate to the frontend folder:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the Next.js development server:

```bash
npm run dev
```

Frontend URL:

`http://localhost:3000`

### 4. Environment Configuration

Refer to the example environment files:

- `backend/.env.example`
- `frontend/.env.local.example`

Create the corresponding local environment files and configure any required variables before running the application.

## 📊 How It Works

1. The user enters monthly financial details.
2. The application processes income, expenses, savings, and risk appetite.
3. The backend calculates the financial health metrics and score.
4. Financial weaknesses and contributing factors are identified.
5. The recommendation engine generates actionable financial suggestions.
6. Results are displayed through an interactive dashboard.

## 🎯 Project Objective

The objective of FinCortex is to make financial analysis easier to understand by transforming monthly financial data into meaningful insights and practical recommendations.

It focuses on explainability, financial awareness, and better money management.

## ⚠️ Disclaimer

FinCortex is an educational financial analysis tool. Its recommendations are for informational purposes only and do not constitute professional or SEBI-registered investment advice.

## 👩‍💻 Repository

GitHub: https://github.com/Shreeya-26/FinCortex