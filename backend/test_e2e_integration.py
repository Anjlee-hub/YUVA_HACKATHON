"""
Comprehensive End-to-End Integration Tests for Shakti Foundry Plant 01 Energy Intelligence Platform.
Validates:
- All 4 Injected Scenarios
- Safe Decision Engine with Constraint Gates & Rejections
- What-if Simulation & Post-Action State Generation
- IPMVP Option B Prototype Savings Verification
- Sensor ROI Advisor & Progressive Intelligence
- AI Copilot Grounded Q&A Across All Scenarios & Missing Data States
- Demo Reset & State Machine Transitions
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_to_baseline():
    """Ensure clean baseline state before each integration test."""
    response = client.post("/api/factory/reset")
    assert response.status_code == 200
    yield
    client.post("/api/factory/reset")


class TestScenario1CompressorWasteE2E:
    def test_full_compressor_lifecycle(self):
        # 1. Switch scenario
        res = client.post("/api/scenario", json={"scenario": "compressor_waste"})
        assert res.status_code == 200
        assert res.json()["success"] is True

        # 2. Verify Anomaly & Root Cause
        res_anom = client.get("/api/anomalies")
        assert res_anom.status_code == 200
        anomalies = res_anom.json()
        assert len(anomalies) >= 1
        comp_anom = next((a for a in anomalies if a["machine_id"] == "compressor_02"), None)
        assert comp_anom is not None
        assert comp_anom["evidence_strength"] in ["Strong", "Moderate"]
        assert comp_anom["sec_deviation_pct"] > 0

        # 3. Verify Decision Engine Candidate Actions & Constraint Gate Rejection
        res_actions = client.get("/api/actions/candidates")
        assert res_actions.status_code == 200
        actions = res_actions.json()
        
        # Unsafe action MUST be rejected by production throughput constraint
        unsafe_action = next((a for a in actions if a["id"] == "action_compressor_lower_pressure_extreme" or a.get("action_id") == "action_compressor_lower_pressure_extreme"), None)
        assert unsafe_action is not None
        assert unsafe_action["is_safe"] is False
        assert unsafe_action["rejection_reason"] is not None

        # Safe action MUST pass constraint gate
        safe_action = next((a for a in actions if a["id"] == "action_compressor_unloaded_shutdown" or a.get("action_id") == "action_compressor_unloaded_shutdown"), None)
        assert safe_action is not None
        assert safe_action["is_safe"] is True

        # 4. What-if Simulation
        res_sim = client.post("/api/actions/whatif", json={"action_id": "action_compressor_unloaded_shutdown"})
        assert res_sim.status_code == 200
        sim_data = res_sim.json()
        assert sim_data["is_production_safe_savings"] is True
        assert "NOT YET VERIFIED" in sim_data["verification_disclaimer"] or "SIMULATED" in sim_data["verification_disclaimer"]

        # 5. Human Approval & Post-Action State Generation
        res_app = client.post("/api/actions/approve", json={"action_id": "action_compressor_unloaded_shutdown"})
        assert res_app.status_code == 200
        assert res_app.json()["success"] is True

        # 6. Savings Verification
        res_ver = client.get("/api/verification")
        assert res_ver.status_code == 200
        records = res_ver.json()
        assert len(records) >= 1
        assert "IPMVP Option B" in records[0]["verification_methodology"]
        assert records[0]["kwh_saved_monthly"] > 0

        # 7. Copilot Q&A
        copilot_queries = [
            "Why did energy increase?",
            "What caused the anomaly?",
            "What action is safe?",
            "How much could we save?",
            "Why was the first action rejected?",
            "Did the intervention work?"
        ]
        for query in copilot_queries:
            res_cop = client.post("/api/copilot/query", json={"question": query})
            assert res_cop.status_code == 200
            ans = res_cop.json()["answer"]
            assert len(ans) > 20
            assert "Error" not in ans


class TestScenario2FurnaceDegradationE2E:
    def test_full_furnace_lifecycle(self):
        # 1. Switch scenario
        res = client.post("/api/scenario", json={"scenario": "furnace_degradation"})
        assert res.status_code == 200

        # 2. Check telemetry deviation
        res_ov = client.get("/api/factory/overview")
        assert res_ov.status_code == 200
        assert res_ov.json()["sec_deviation_pct"] > 0

        # 3. Copilot query before fix explains furnace degradation
        res_cop_before = client.post("/api/copilot/query", json={"question": "Why did energy increase?"})
        assert "furnace" in res_cop_before.json()["answer"].lower() or "holding" in res_cop_before.json()["answer"].lower()

        # 4. Decision Engine: Unsafe action rejected
        res_actions = client.get("/api/actions/candidates")
        actions = res_actions.json()
        unsafe_action = next((a for a in actions if a["id"] == "action_furnace_lower_temp_unsafe" or a.get("action_id") == "action_furnace_lower_temp_unsafe"), None)
        assert unsafe_action is not None
        assert unsafe_action["is_safe"] is False
        assert unsafe_action["rejection_reason"] is not None

        # Safe maintenance action
        safe_action = next((a for a in actions if a["id"] == "action_furnace_refractory_patch" or a.get("action_id") == "action_furnace_refractory_patch"), None)
        assert safe_action is not None
        assert safe_action["is_safe"] is True

        # 5. Simulation & Approval
        res_sim = client.post("/api/actions/whatif", json={"action_id": "action_furnace_refractory_patch"})
        assert res_sim.status_code == 200
        res_app = client.post("/api/actions/approve", json={"action_id": "action_furnace_refractory_patch"})
        assert res_app.status_code == 200

        # 6. Copilot Q&A after fix explains verified intervention
        res_cop = client.post("/api/copilot/query", json={"question": "Did the intervention work?"})
        assert "furnace" in res_cop.json()["answer"].lower() or "verified" in res_cop.json()["answer"].lower() or "saving" in res_cop.json()["answer"].lower()


class TestScenario3TODSchedulingE2E:
    def test_full_tod_lifecycle(self):
        # 1. Switch scenario
        res = client.post("/api/scenario", json={"scenario": "production_scheduling"})
        assert res.status_code == 200

        # 2. Decision Engine
        res_actions = client.get("/api/actions/candidates")
        actions = res_actions.json()
        unsafe_action = next((a for a in actions if a["id"] == "action_tod_emergency_curtailment" or a.get("action_id") == "action_tod_emergency_curtailment"), None)
        assert unsafe_action is not None
        assert unsafe_action["is_safe"] is False
        assert unsafe_action["rejection_reason"] is not None

        safe_action = next((a for a in actions if a["id"] == "action_tod_rescheduling" or a.get("action_id") == "action_tod_rescheduling"), None)
        assert safe_action is not None
        assert safe_action["is_safe"] is True

        # 3. Simulate & Approve
        res_sim = client.post("/api/actions/whatif", json={"action_id": "action_tod_rescheduling"})
        assert res_sim.status_code == 200
        assert res_sim.json()["is_production_safe_savings"] is True

        res_app = client.post("/api/actions/approve", json={"action_id": "action_tod_rescheduling"})
        assert res_app.status_code == 200

        # 4. Copilot
        res_cop = client.post("/api/copilot/query", json={"question": "How much could we save?"})
        assert "₹" in res_cop.json()["answer"] or "inr" in res_cop.json()["answer"].lower() or "cost" in res_cop.json()["answer"].lower()


class TestScenario4MissingSensorE2E:
    def test_missing_sensor_withholding_and_roi(self):
        # 1. Switch scenario
        res = client.post("/api/scenario", json={"scenario": "missing_sensor"})
        assert res.status_code == 200

        # 2. Anomaly shows withheld diagnosis due to missing vibration sensor
        res_anom = client.get("/api/anomalies")
        anomalies = res_anom.json()
        assert len(anomalies) >= 1
        withheld_anom = anomalies[0]
        assert withheld_anom["maintenance_withheld"] is True
        assert withheld_anom["withhold_reason"] is not None
        assert withheld_anom["evidence_strength"] == "Insufficient"

        # 3. Sensor ROI recommends vibration sensor
        res_roi = client.get("/api/sensor-roi")
        assert res_roi.status_code == 200
        roi_data = res_roi.json()
        assert len(roi_data) >= 1
        vib_rec = next((r for r in roi_data if "vibration" in r["sensor_type"].lower()), None)
        assert vib_rec is not None
        assert vib_rec["payback_months"] <= 3.5

        # 4. Copilot Grounding: explains missing data honestly
        res_cop1 = client.post("/api/copilot/query", json={"question": "What caused the anomaly?"})
        assert "withheld" in res_cop1.json()["answer"].lower() or "vibration" in res_cop1.json()["answer"].lower() or "sensor" in res_cop1.json()["answer"].lower()

        res_cop2 = client.post("/api/copilot/query", json={"question": "What data should we collect next?"})
        assert "vibration" in res_cop2.json()["answer"].lower()
        assert "payback" in res_cop2.json()["answer"].lower() or "months" in res_cop2.json()["answer"].lower()


class TestSavingsVerificationE2E:
    def test_verification_matrix_and_honesty(self):
        res = client.get("/api/verification/matrix")
        assert res.status_code == 200
        matrix = res.json()
        assert len(matrix) >= 4

        # Verify safe action structure
        safe_item = next((m for m in matrix if m["action_id"] == "action_compressor_unloaded_shutdown"), None)
        assert safe_item is not None
        assert safe_item["is_production_safe_saving"] is True
        assert safe_item["disclaimer"] == "DEMO — SIMULATED POST-ACTION DATA"

        # Verify unsafe action structure
        unsafe_item = next((m for m in matrix if m["action_id"] == "action_compressor_lower_pressure_extreme"), None)
        assert unsafe_item is not None
        assert unsafe_item["is_production_safe_saving"] is False
        assert unsafe_item["lifecycle_stage"] == "REJECTED"

        # Verify single action verification endpoint
        res_single = client.post("/api/verification/verify", json={"action_id": "action_compressor_unloaded_shutdown"})
        assert res_single.status_code == 200
        single_data = res_single.json()
        assert single_data["is_verified"] is True
        assert single_data["verification_verdict"] == "VERIFIED PRODUCTION-SAFE SAVING"


class TestDemoResetE2E:
    def test_demo_reset_restores_baseline(self):
        # Apply action first
        client.post("/api/scenario", json={"scenario": "compressor_waste"})
        client.post("/api/actions/approve", json={"action_id": "action_compressor_unloaded_shutdown"})
        
        # Verify applied action count >= 1
        ov_before = client.get("/api/factory/overview").json()
        assert len(ov_before["applied_actions"]) >= 1

        # Reset demo
        res_reset = client.post("/api/factory/reset")
        assert res_reset.status_code == 200
        assert res_reset.json()["success"] is True

        # Verify state is clean normal
        ov_after = client.get("/api/factory/overview").json()
        assert ov_after["active_scenario"] == "normal"
        assert len(ov_after["applied_actions"]) == 0


