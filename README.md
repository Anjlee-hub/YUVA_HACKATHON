# Schneider Electric Yuva Yodha Energy Tech Hackathon — Challenge 04
## Production-Safe Energy Intelligence for Indian SME Manufacturing
**Factory Model:** Shakti Foundry — Plant 01, Peenya Industrial Area, Bengaluru, India

### Quick Start Instructions

#### 1. Backend Server (FastAPI + Python Analytics Engine)
```bash
# From workspace root
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
API Documentation available at: `http://127.0.0.1:8000/docs`

#### 2. Frontend Application (React + Vite + Tailwind CSS)
```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5173
```
Open web prototype in your browser at: `http://127.0.0.1:5173`

---

### Core Innovation: The Production-Safe Decision Loop
```
Factory Telemetry (Sub-meters & Sensors)
  → Data Quality & Confidence Engine
  → Production-Aware SEC Baseline (kWh / Good Cast Ton)
  → Statistical Anomaly Detection
  → Explainable Root-Cause Decomposition (Shapley factors)
  → Candidate Optimization Actions Generated
  → Manufacturing Constraint Gate (Throughput, Quality, Delivery, Equipment Health)
  → Unsafe Actions Filtered & REJECTED with Audit Detail
  → What-If Multi-Metric Simulation (Before vs After)
  → Human Operator Approval
  → Live Factory State Synchronized
  → IPMVP Option B Verified Savings Audit
  → Digitalization & Sensor ROI Advisor (What to install next)
```

---

### Features & Differentiators

1. **Retrofit-First Architecture:** Designed for brownfield Indian SME factories with heterogeneous/incomplete instrumentation.
2. **Progressive Intelligence (Levels 0 → 4):** Proves SMEs don't need to replace legacy machinery on Day 1.
3. **Production-Aware Baseline:** Computes $SEC = \text{Energy} / \text{Good Output}$ factoring in alloy grade (FG 260 vs SG Iron), shift timing, and ambient weather. Never compares energy only with yesterday.
4. **Critical Trust Rule:** When sensory evidence is incomplete (e.g., vibration sensor absent on Compressor 02), the system explicitly **withholds mechanical diagnosis** rather than hallucinating.
5. **Production-Safe Constraint Gate:** Rejects optimizations that compromise casting quality or line speed (e.g., dropping header pressure below DISA squeeze minimum or dropping melt superheat temperature).
6. **What-If Simulation:** Displays Baseline vs Simulated metrics with human approval controls.
7. **IPMVP Option B Verified Savings:** Reconciles predicted vs actual verified savings with auditable variance explanations.
8. **Digitalization ROI Advisor:** Recommends the #1 highest ROI sensor to buy next with capital cost and payback period in months.
9. **Explainable AI Copilot:** Grounded purely in shopfloor telemetry and constraint models without numerical hallucinations.
10. **2-Minute Interactive Guided Tour:** Built-in step-by-step walkthrough covering the entire end-to-end loop.
