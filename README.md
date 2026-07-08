# CareFlow-MCP

**CareFlow-MCP** is an AI-powered NHS-style referral triage and waiting list prioritisation system.  
It helps hospital staff manage referrals by detecting red flags, predicting clinical urgency, estimating DNA missed appointment risk, prioritising waiting lists, supporting clinician review, generating FHIR-style records, PDF reports, audit logs, RAG-based explanations, and SLM summaries.

> This is a synthetic healthcare AI prototype built for learning, demonstration, and portfolio purposes. It is not intended for real clinical diagnosis or real patient decision-making.

---

## Project Overview

Hospitals receive many patient referrals, and staff need to identify which patients require faster attention. CareFlow-MCP supports this workflow by combining:

- Referral text parsing
- Rule-based red-flag detection
- Machine learning triage prediction
- DNA missed appointment prediction
- Waiting list prioritisation
- Human clinician review
- Audit logging
- PDF report generation
- Mock FHIR patient record generation
- RAG assistant for referral explanation
- SLM-based referral summary

The system is designed as a **human-in-the-loop clinical decision-support prototype**, where AI predictions assist staff but final decisions remain with clinicians.

---

## Key Features

### 1. Referral Upload

Staff can upload patient referral details including:

- Patient ID
- Age
- Gender
- Department
- Waiting days
- Referral note

The referral is stored in the backend database and displayed on the dashboard.

---

### 2. Referral Parser

The system extracts important information from referral text, such as:

- Symptoms
- Existing conditions
- Symptom duration

Example extracted symptoms include chest pain, shortness of breath, blood in stool, weight loss, severe headache, weakness, dizziness, fever, cough, and abdominal pain.

---

### 3. Red-Flag Detection

Rule-based red-flag logic detects potentially urgent combinations, such as:

- Chest pain with shortness of breath
- Blood in stool with weight loss in older patients
- Severe headache with weakness or speech difficulty
- Pregnancy with severe abdominal pain

This improves transparency because the red-flag reason is clearly shown.

---

### 4. Machine Learning Triage Prediction

The system predicts referral urgency using ML models.

Urgency classes include:

- Emergency
- Urgent
- Soon
- Routine
- Self-care

The triage model uses synthetic referral data and compares machine learning models such as Logistic Regression and Random Forest.

---

### 5. DNA Missed Appointment Prediction

DNA means **Did Not Attend**.

The system predicts whether a patient may miss an appointment based on features such as:

- Waiting days
- Previous missed appointments
- Appointment time
- Distance band
- Reminder status
- Previous cancellations

The output is shown as:

- Low risk
- Medium risk
- High risk

---

### 6. Waiting List Prioritisation Dashboard

The dashboard ranks referrals using:

- Triage urgency
- Triage risk score
- Red-flag score
- Waiting days
- DNA risk

This helps staff identify which referrals should be reviewed first.

---

### 7. Clinician Review

CareFlow-MCP includes human-in-the-loop review.

A clinician can:

- Approve the AI prediction
- Override urgency
- Request more information
- Add review notes

The referral status is updated after clinician review.

---

### 8. Audit Logs

The system records major actions for accountability, including:

- Referral created
- Referral parsed
- Red flag detected
- Triage predicted
- DNA risk predicted
- Clinician reviewed
- PDF report generated
- FHIR record viewed
- RAG assistant used
- SLM summary generated

---

### 9. PDF Report Generation

The system can generate a PDF referral report containing:

- Patient details
- Referral note
- Extracted symptoms and conditions
- Red-flag assessment
- Triage result
- DNA risk result
- Clinician review
- Safety note

---

### 10. Mock FHIR Patient Record

FHIR stands for **Fast Healthcare Interoperability Resources**.

CareFlow-MCP generates a mock FHIR-style bundle containing:

- Patient resource
- ServiceRequest resource
- Observation resources
- Condition resources

The frontend displays both readable cards and raw JSON.

---

### 11. Model Monitoring Dashboard

The model monitoring page displays:

- Model name
- Accuracy
- Macro F1 score
- Recall scores
- Priority score
- Training rows
- Test rows
- Model comparison results

---

### 12. RAG Referral Assistant

Staff can ask referral-specific questions such as:

- Why is this patient emergency?
- What red flag was detected?
- What is the DNA risk?
- What should staff do next?
- Has a clinician reviewed this referral?

The assistant answers using referral, triage, DNA, and clinician review data.

---

### 13. SLM Referral Summary

The system includes an SLM summary endpoint.

If a local SLM such as Ollama is available, it can generate an AI-style referral summary.  
If not, the system uses a fallback summary engine.

---

## Tech Stack

### Frontend

- React
- Vite
- Bootstrap
- Axios
- React Router

### Backend

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab

### Machine Learning

- Python
- scikit-learn
- pandas
- joblib
- Logistic Regression
- Random Forest

---

## Folder Structure

```text
CareFlow-MCP/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── ml_models/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
│
├── ml/
│   ├── data/
│   ├── scripts/
│   ├── models/
│   └── evaluation/
│
├── docs/
├── README.md
└── .gitignore
