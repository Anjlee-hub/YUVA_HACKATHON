"""
Production-Safe Decision Engine & What-If Simulation Test Suite
Validates:
1. Safe action approval
2. Unsafe action rejection
3. Minimum pressure constraint
4. Production throughput constraint
5. Quality constraint
6. Machine operating limit
7. Missing sensor data
8. Insufficient evidence / Trust Protocol
9. What-if energy calculation
10. Cost calculation
11. CO2 calculation
12. Production-safe savings qualification
13. Deterministic scenario results
14. API response validation
"""

import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.main import app
from backend.app.simulation import factory_simulator
from backend.app.decision_engine import evaluate_decision_pipeline, simulate_decision_action, get_decision_scenarios

class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)
        factory_simulator.reset_actions()

    # 1. Safe Action Approval
    def test_01_safe_action_approval(self):
        factory_simulator.set_scenario("compressor_waste")
        res = evaluate_decision_pipeline()
        safe_action = next((a for a in res["candidate_actions"] if a["id"] == "action_compressor_unloaded_shutdown"), None)
        self.assertIsNotNone(safe_action)
        self.assertTrue(safe_action["is_safe"])
        self.assertEqual(safe_action["status"], "SAFE_FOR_SIMULATION")
        self.assertIsNone(safe_action["rejection_reason"])
        print("\n[PASS] Test 1: Safe action approval verified.")

    # 2. Unsafe Action Rejection
    def test_02_unsafe_action_rejection(self):
        factory_simulator.set_scenario("compressor_waste")
        res = evaluate_decision_pipeline()
        unsafe = next((a for a in res["candidate_actions"] if a["id"] == "action_compressor_lower_pressure_extreme"), None)
        self.assertIsNotNone(unsafe)
        self.assertFalse(unsafe["is_safe"])
        self.assertEqual(unsafe["status"], "REJECTED")
        self.assertIn("REJECTED BY CONSTRAINT GATE", unsafe["rejection_reason"])
        print("[PASS] Test 2: Unsafe action rejection verified.")

    # 3. Minimum Pressure Constraint
    def test_03_minimum_pressure_constraint(self):
        factory_simulator.set_scenario("compressor_waste")
        res = evaluate_decision_pipeline()
        unsafe = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_lower_pressure_extreme")
        pressure_constraint = next(c for c in unsafe["constraints"] if "Pneumatic Pressure" in c["name"])
        self.assertFalse(pressure_constraint["passed"])
        self.assertEqual(pressure_constraint["threshold"], "≥ 6.0 bar")
        self.assertEqual(pressure_constraint["projected_value"], "5.2 bar")
        self.assertIn("stall below 6.0 bar", pressure_constraint["violation_detail"])
        print("[PASS] Test 3: Minimum pressure constraint (5.2 bar < 6.0 bar) rejection verified.")

    # 4. Production Throughput Constraint
    def test_04_production_throughput_constraint(self):
        factory_simulator.set_scenario("compressor_waste")
        res = evaluate_decision_pipeline()
        unsafe = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_lower_pressure_extreme")
        self.assertEqual(unsafe["production_impact_pct"], -12.5)
        self.assertLess(unsafe["production_impact_pct"], 0.0)
        print("[PASS] Test 4: Production throughput constraint violation (-12.5%) verified.")

    # 5. Quality Constraint
    def test_05_quality_constraint(self):
        factory_simulator.set_scenario("furnace_degradation")
        res = evaluate_decision_pipeline()
        unsafe_temp = next(a for a in res["candidate_actions"] if a["id"] == "action_furnace_lower_temp_unsafe")
        fluidity_check = next(c for c in unsafe_temp["constraints"] if "Fluidity" in c["name"])
        self.assertFalse(fluidity_check["passed"])
        self.assertEqual(fluidity_check["projected_value"], "1350°C (Sub-liquidus)")
        self.assertEqual(unsafe_temp["quality_impact_pct"], -14.2)
        print("[PASS] Test 5: Quality constraint (sub-liquidus cold shut scrap -14.2%) verified.")

    # 6. Machine Operating Limit
    def test_06_machine_operating_limit(self):
        factory_simulator.set_scenario("compressor_waste")
        res = evaluate_decision_pipeline()
        safe_action = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_unloaded_shutdown")
        motor_start_limit = next(c for c in safe_action["constraints"] if "Motor Starts" in c["name"])
        self.assertTrue(motor_start_limit["passed"])
        self.assertEqual(motor_start_limit["threshold"], "≤ 6 starts/hr")
        self.assertEqual(motor_start_limit["projected_value"], "3.2 starts/hr")
        print("[PASS] Test 6: Machine operating limit (3.2 starts/hr <= 6 starts/hr) verified.")

    # 7. Missing Sensor Data
    def test_07_missing_sensor_data(self):
        factory_simulator.set_scenario("missing_sensor")
        res = evaluate_decision_pipeline()
        c6 = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_bearing_overhaul_unsupported")
        self.assertEqual(c6["status"], "NEEDS_MORE_DATA")
        vib_sensor = next(c for c in c6["constraints"] if "Vibration" in c["name"])
        self.assertFalse(vib_sensor["passed"])
        self.assertEqual(vib_sensor["projected_value"], "SENSOR NOT INSTALLED (Missing)")
        print("[PASS] Test 7: Missing sensor data detection verified.")

    # 8. Insufficient Evidence / Trust Protocol
    def test_08_insufficient_evidence(self):
        factory_simulator.set_scenario("missing_sensor")
        res = evaluate_decision_pipeline()
        c6 = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_bearing_overhaul_unsupported")
        self.assertFalse(c6["is_safe"])
        self.assertEqual(c6["confidence_score"], 42.0)
        self.assertIn("WITHHELD BY TRUST PROTOCOL", c6["rejection_reason"])
        print("[PASS] Test 8: Insufficient evidence Trust Protocol withholding verified.")

    # 9. What-If Energy Calculation
    def test_09_whatif_energy_calculation(self):
        factory_simulator.set_scenario("compressor_waste")
        sim = simulate_decision_action("action_compressor_unloaded_shutdown")
        energy = sim["energy_comparison"]
        self.assertEqual(energy["current_kwh_day"], 336.0)
        self.assertEqual(energy["predicted_kwh_day"], 251.8)
        self.assertEqual(energy["kwh_saved_day"], 84.2)
        self.assertEqual(energy["pct_change"], -25.1)
        self.assertEqual(sim["verification_disclaimer"], "WHAT-IF SIMULATION - NOT YET VERIFIED")
        print("[PASS] Test 9: What-if energy calculation (336 -> 251.8 kWh, saved 84.2 kWh) verified.")

    # 10. Cost Calculation
    def test_10_cost_calculation(self):
        factory_simulator.set_scenario("compressor_waste")
        sim = simulate_decision_action("action_compressor_unloaded_shutdown")
        cost = sim["cost_comparison"]
        expected_saved = round(84.2 * 30 * 8.20, 0)
        self.assertAlmostEqual(cost["savings_month_inr"], expected_saved, delta=2.0)
        print(f"[PASS] Test 10: Cost calculation (INR {cost['savings_month_inr']}/month) verified.")

    # 11. CO2 Calculation
    def test_11_co2_calculation(self):
        factory_simulator.set_scenario("compressor_waste")
        sim = simulate_decision_action("action_compressor_unloaded_shutdown")
        co2 = sim["co2_comparison"]
        expected_co2_saved = round(84.2 * 30 * 0.716, 0)
        self.assertAlmostEqual(co2["reduction_kg_month"], expected_co2_saved, delta=2.0)
        print(f"[PASS] Test 11: CO2 calculation ({co2['reduction_kg_month']} kg CO2/month) verified.")

    # 12. Production-Safe Savings Qualification
    def test_12_production_safe_savings_qualification(self):
        factory_simulator.set_scenario("compressor_waste")
        res = evaluate_decision_pipeline()
        safe_action = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_unloaded_shutdown")
        unsafe_action = next(a for a in res["candidate_actions"] if a["id"] == "action_compressor_lower_pressure_extreme")
        self.assertTrue(safe_action["is_production_safe_savings"])
        self.assertFalse(unsafe_action["is_production_safe_savings"])
        print("[PASS] Test 12: Production-Safe Savings qualification criteria verified.")

    # 13. Deterministic Scenario Results
    def test_13_deterministic_scenario_results(self):
        scenarios = get_decision_scenarios()
        self.assertEqual(len(scenarios), 4)
        r1 = evaluate_decision_pipeline()
        r2 = evaluate_decision_pipeline()
        self.assertEqual(r1["summary"], r2["summary"])
        print("[PASS] Test 13: Deterministic scenario results verified.")

    # 14. API Response Validation
    def test_14_api_response_validation(self):
        # POST /api/decision/evaluate
        res_eval = self.client.post("/api/decision/evaluate", json={})
        self.assertEqual(res_eval.status_code, 200)
        eval_data = res_eval.json()
        self.assertIn("candidate_actions", eval_data)
        self.assertIn("summary", eval_data)

        # POST /api/decision/simulate
        res_sim = self.client.post("/api/decision/simulate", json={"action_id": "action_compressor_unloaded_shutdown"})
        self.assertEqual(res_sim.status_code, 200)
        sim_data = res_sim.json()
        self.assertEqual(sim_data["verification_disclaimer"], "WHAT-IF SIMULATION - NOT YET VERIFIED")
        self.assertEqual(sim_data["status"], "SIMULATED_NOT_VERIFIED")

        # GET /api/decision/scenarios
        res_scen = self.client.get("/api/decision/scenarios")
        self.assertEqual(res_scen.status_code, 200)
        self.assertEqual(len(res_scen.json()), 4)

        # GET /api/decision/{id}
        res_one = self.client.get("/api/decision/action_compressor_unloaded_shutdown")
        self.assertEqual(res_one.status_code, 200)
        one_data = res_one.json()
        self.assertIn("evaluation", one_data)
        self.assertIn("simulation", one_data)
        print("[PASS] Test 14: API response validation for all 4 decision endpoints verified.")

if __name__ == "__main__":
    unittest.main()
