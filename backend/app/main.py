import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import asyncio
import json

from .database import init_db
from .baseline_engine import get_ml_baseline_status
from .simulation import factory_simulator
from .anomaly_engine import analyze_anomalies
from .safe_action_engine import evaluate_candidate_actions
from .whatif_engine import run_whatif_simulation
from .decision_engine import (
    evaluate_decision_pipeline,
    simulate_decision_action,
    get_decision_scenarios
)
from .verification_engine import (
    get_verified_savings_history,
    get_action_verification_matrix,
    verify_single_action
)
from .data_readiness_advisor import (
    get_data_readiness_status,
    get_sensor_roi_recommendations,
    PROGRESSIVE_LEVELS
)
from .copilot_engine import query_copilot

# Initialize database
init_db()

app = FastAPI(
    title="Schneider Electric Yuva Yodha - Production-Safe Energy Intelligence API",
    description="Backend API for Retrofit-First Energy Decision Engine in Indian SME Manufacturing (Shakti Foundry Plant 01)",
    version="1.0.0"
)

# CORS middleware for local Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScenarioRequest(BaseModel):
    scenario: str # "normal", "compressor_waste", "furnace_degradation", "production_scheduling", "missing_sensor"

class LevelRequest(BaseModel):
    level: int # 0 to 4

class ActionRequest(BaseModel):
    action_id: str

class DecisionEvaluateRequest(BaseModel):
    anomaly_id: Optional[str] = None
    machine_id: Optional[str] = None

class CopilotQueryRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Schneider Electric Yuva Yodha Energy Tech Hackathon — Challenge 04",
        "factory": "Shakti Foundry — Plant 01, Bengaluru, India",
        "environment": "DEMO/SIMULATION"
    }

@app.get("/api/factory/overview")
def get_factory_overview():
    return factory_simulator.get_factory_summary()

@app.get("/api/factory/machines")
def get_factory_machines():
    return list(factory_simulator.live_telemetry.values())

@app.get("/api/factory/history")
def get_factory_history():
    return factory_simulator.generate_30day_history()

@app.get("/api/baseline/ml-model")
def get_baseline_ml_model():
    return get_ml_baseline_status()

@app.get("/api/anomalies")
def get_anomalies():
    return analyze_anomalies()

# =============================================================================
# DECISION ENGINE & CONSTRAINT GATE ENDPOINTS
# =============================================================================

@app.post("/api/decision/evaluate")
def post_decision_evaluate(payload: Optional[DecisionEvaluateRequest] = None):
    anom_id = payload.anomaly_id if payload else None
    m_id = payload.machine_id if payload else None
    return evaluate_decision_pipeline(anomaly_id=anom_id, machine_id=m_id)

@app.post("/api/decision/simulate")
def post_decision_simulate(payload: ActionRequest):
    return simulate_decision_action(payload.action_id)

@app.get("/api/decision/scenarios")
def get_decision_scenarios_route():
    return get_decision_scenarios()

@app.get("/api/decision/{decision_id}")
def get_decision_by_id_route(decision_id: str):
    res = evaluate_decision_pipeline()
    matched = next((a for a in res["candidate_actions"] if a["id"] == decision_id or a.get("action_id") == decision_id), None)
    if not matched:
        raise HTTPException(status_code=404, detail=f"Decision action '{decision_id}' not found")
    sim = simulate_decision_action(decision_id)
    return {
        "evaluation": matched,
        "simulation": sim
    }

@app.get("/api/actions/candidates")
def get_candidate_actions(anomaly_id: Optional[str] = None):
    return evaluate_candidate_actions(anomaly_id)

@app.post("/api/actions/whatif")
def post_whatif(payload: ActionRequest):
    return run_whatif_simulation(payload.action_id)

@app.post("/api/actions/approve")
def approve_action(payload: ActionRequest):
    factory_simulator.apply_action(payload.action_id)
    return {
        "success": True,
        "action_id": payload.action_id,
        "message": "Action successfully approved and simulated into live factory state.",
        "new_summary": factory_simulator.get_factory_summary()
    }

@app.post("/api/actions/reset")
def reset_actions():
    factory_simulator.reset_actions()
    return {
        "success": True,
        "message": "Factory state reset to initial scenario baseline.",
        "new_summary": factory_simulator.get_factory_summary()
    }

@app.get("/api/verification")
def get_verification():
    return get_verified_savings_history()

@app.get("/api/verification/matrix")
def get_verification_matrix(action_id: Optional[str] = None):
    return get_action_verification_matrix(action_id)

@app.post("/api/verification/verify")
def post_verify_action(payload: ActionRequest):
    return verify_single_action(payload.action_id)

@app.get("/api/readiness")
def get_readiness():
    return {
        "status": get_data_readiness_status(),
        "levels": PROGRESSIVE_LEVELS
    }

@app.post("/api/readiness/level")
def set_data_level(payload: LevelRequest):
    if not (0 <= payload.level <= 4):
        raise HTTPException(status_code=400, detail="Level must be between 0 and 4")
    factory_simulator.set_data_level(payload.level)
    return {
        "success": True,
        "new_level": payload.level,
        "readiness": get_data_readiness_status()
    }

@app.get("/api/sensor-roi")
def get_sensor_roi():
    return get_sensor_roi_recommendations()

@app.post("/api/scenario")
def set_scenario(payload: ScenarioRequest):
    factory_simulator.set_scenario(payload.scenario)
    return {
        "success": True,
        "active_scenario": payload.scenario,
        "summary": factory_simulator.get_factory_summary()
    }

@app.post("/api/copilot/query")
def copilot_chat(payload: CopilotQueryRequest):
    return query_copilot(payload.question)

# Real-time WebSocket connection for live telemetry ticks
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            summary = factory_simulator.get_factory_summary()
            machines = list(factory_simulator.live_telemetry.values())
            await websocket.send_text(json.dumps({
                "type": "TELEMETRY_TICK",
                "summary": summary,
                "machines": machines
            }))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
