"""
Test Suite for Final Differentiation Layer
Covers:
1. Baseline vs predicted calculation
2. Predicted vs actual comparison
3. kWh savings
4. SEC improvement
5. Cost savings
6. CO2 avoided
7. Production constraint
8. Quality constraint
9. Verified production-safe saving qualification
10. Simulated values clearly separated from verified values
11. Missing sensor detection
12. Sensor ROI calculation
13. Data maturity level
14. Copilot retrieves application values
15. Copilot refuses unsupported numerical claims
16. Copilot explains rejected actions from actual constraints
17. Copilot identifies missing data
18. Complete end-to-end scenario A
19. Complete end-to-end scenario B
20. Complete end-to-end scenario C
"""

import sys
import os
import unittest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.simulation import factory_simulator, GRID_CO2_FACTOR_KG_PER_KWH
from backend.app.anomaly_engine import analyze_anomalies
from backend.app.decision_engine import evaluate_decision_pipeline, simulate_decision_action
from backend.app.verification_engine import (
    get_verified_savings_history, 
    get_action_verification_matrix, 
    verify_single_action,
    ELECTRICITY_TARIFF_INR_PER_KWH
)
from backend.app.data_readiness_advisor import (
    get_data_readiness_status, 
    get_sensor_roi_recommendations,
    PROGRESSIVE_LEVELS
)
from backend.app.copilot_engine import query_copilot
from fastapi.testclient import TestClient
from backend.app.main import app

class TestDifferentiationLayer(unittest.TestCase):

    def setUp(self):
        factory_simulator.reset_actions()
        factory_simulator.set_scenario("normal")
        factory_simulator.set_data_level(3)
        self.client = TestClient(app)

    def tearDown(self):
        factory_simulator.reset_actions()
        factory_simulator.set_scenario("normal")
        factory_simulator.set_data_level(3)

    # 1. Baseline vs predicted calculation
    def test_01_baseline_vs_predicted_calculation(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        self.assertTrue(len(matrix) > 0)
        c2 = matrix[0]
        energy_row = next(r for r in c2.rows if r.metric == "Daily Energy")
        self.assertEqual(energy_row.before, 336.0)
        self.assertEqual(energy_row.predicted, 228.0)
        expected_pred_saved = energy_row.before - energy_row.predicted
        self.assertEqual(expected_pred_saved, 108.0)

    # 2. Predicted vs actual comparison
    def test_02_predicted_vs_actual_comparison(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        c2 = matrix[0]
        self.assertEqual(len(c2.rows), 6) # Energy, SEC, Cost, CO2, Production, Quality
        energy_row = c2.rows[0]
        self.assertEqual(energy_row.actual, 230.8)
        self.assertTrue(c2.prediction_error_pct > 0.0)
        self.assertLess(c2.prediction_error_pct, 5.0) # Error under 5%

    # 3. kWh savings calculation
    def test_03_kwh_savings(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        c2 = matrix[0]
        # actual saved = 336.0 - 230.8 = 105.2
        self.assertAlmostEqual(c2.actual_kwh_saved, 105.2, places=1)

        matrix_f2 = get_action_verification_matrix("action_furnace_refractory_patch")
        f2 = matrix_f2[0]
        # actual saved = 624.0 - 368.0 = 256.0
        self.assertAlmostEqual(f2.actual_kwh_saved, 256.0, places=1)

    # 4. SEC improvement
    def test_04_sec_improvement(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        c2 = matrix[0]
        self.assertAlmostEqual(c2.actual_sec_improvement_pct, 31.3, places=1)

    # 5. Cost savings
    def test_05_cost_savings(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        c2 = matrix[0]
        # 105.2 kWh/day * 8.2 INR/kWh * 30 days = 25,879.2 INR
        expected_monthly_cost = round(105.2 * ELECTRICITY_TARIFF_INR_PER_KWH * 30, 0)
        self.assertEqual(c2.actual_cost_saved_inr, expected_monthly_cost)

    # 6. CO2 avoided
    def test_06_co2_avoided(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        c2 = matrix[0]
        # 105.2 * 0.716 * 30 = 2,259.7 -> 2260 kg CO2/month
        expected_co2 = round(105.2 * GRID_CO2_FACTOR_KG_PER_KWH * 30, 0)
        self.assertEqual(c2.actual_co2_avoided_kg, expected_co2)

    # 7. Production constraint
    def test_07_production_constraint(self):
        matrix = get_action_verification_matrix()
        safe_c2 = next(m for m in matrix if m.action_id == "action_compressor_unloaded_shutdown")
        unsafe_c2 = next(m for m in matrix if m.action_id == "action_compressor_reduce_pressure")
        self.assertTrue(safe_c2.production_maintained)
        self.assertFalse(unsafe_c2.production_maintained)

    # 8. Quality constraint
    def test_08_quality_constraint(self):
        matrix = get_action_verification_matrix()
        safe_f2 = next(m for m in matrix if m.action_id == "action_furnace_refractory_patch")
        unsafe_c2 = next(m for m in matrix if m.action_id == "action_compressor_reduce_pressure")
        self.assertTrue(safe_f2.quality_maintained)
        self.assertFalse(unsafe_c2.quality_maintained)

    # 9. Verified production-safe saving qualification
    def test_09_verified_production_safe_saving_qualification(self):
        v_res_safe = verify_single_action("action_compressor_unloaded_shutdown")
        self.assertTrue(v_res_safe["is_verified"])
        self.assertEqual(v_res_safe["verification_verdict"], "VERIFIED PRODUCTION-SAFE SAVING")
        self.assertTrue(v_res_safe["criteria_audit"]["production_throughput_maintained"])
        self.assertTrue(v_res_safe["criteria_audit"]["quality_tolerance_maintained"])

        v_res_unsafe = verify_single_action("action_compressor_reduce_pressure")
        self.assertFalse(v_res_unsafe["is_verified"])
        self.assertEqual(v_res_unsafe["verification_verdict"], "REJECTED - NOT PRODUCTION-SAFE")

    # 10. Simulated values clearly separated from verified values
    def test_10_simulated_values_clearly_separated_from_verified(self):
        matrix = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        c2 = matrix[0]
        self.assertIn("SIMULATED", c2.disclaimer)
        self.assertIn("IPMVP Option B", c2.real_deployment_note)
        # By default before human live approval, lifecycle stage is PREDICTED
        self.assertEqual(c2.lifecycle_stage, "PREDICTED")
        
        # After human approval in simulator
        factory_simulator.apply_action("action_compressor_unloaded_shutdown")
        matrix_after = get_action_verification_matrix("action_compressor_unloaded_shutdown")
        self.assertEqual(matrix_after[0].lifecycle_stage, "VERIFIED")

    # 11. Missing sensor detection
    def test_11_missing_sensor_detection(self):
        factory_simulator.set_scenario("missing_sensor")
        readiness = get_data_readiness_status()
        self.assertFalse(readiness.can_diagnose_mechanical)
        self.assertEqual(readiness.withheld_diagnoses_count, 1)

    # 12. Sensor ROI calculation
    def test_12_sensor_roi_calculation(self):
        rois = get_sensor_roi_recommendations()
        self.assertEqual(len(rois), 5)
        top = rois[0]
        self.assertEqual(top.sensor_id, "roi_c2_vibration")
        self.assertTrue(top.is_next_best)
        self.assertEqual(top.payback_months, 3.1)
        self.assertEqual(top.estimated_capex_inr, 18500.0)
        self.assertIn("ILLUSTRATIVE DEMO ASSUMPTIONS", top.illustrative_disclaimer)

    # 13. Data maturity level
    def test_13_data_maturity_level(self):
        self.assertEqual(len(PROGRESSIVE_LEVELS), 5)
        factory_simulator.set_data_level(2)
        r2 = get_data_readiness_status()
        self.assertEqual(r2.current_level, 2)
        self.assertIn("Machine energy comparison", r2.currently_possible_intelligence)
        self.assertIn("Vibration-based equipment health analysis", r2.next_level_unlocks)

    # 14. Copilot retrieves application values
    def test_14_copilot_retrieves_application_values(self):
        factory_simulator.set_scenario("compressor_waste")
        res = query_copilot("Why did energy increase?")
        summary = factory_simulator.get_factory_summary()
        self.assertIn(str(summary["factory_sec"]), res["answer"])
        self.assertIn("Compressor 02", res["answer"])

    # 15. Copilot refuses unsupported numerical claims
    def test_15_copilot_refuses_unsupported_numerical_claims(self):
        factory_simulator.set_scenario("missing_sensor")
        res = query_copilot("Can you give bearing wear vibration diagnosis for Compressor 02?")
        self.assertIn("Insufficient Data to Answer Reliably", res["answer"])
        self.assertIn("vibration accelerometer", res["answer"].lower())

    # 16. Copilot explains rejected actions from actual constraints
    def test_16_copilot_explains_rejected_actions(self):
        factory_simulator.set_scenario("compressor_waste")
        res = query_copilot("Why was an action rejected?")
        self.assertIn("5.2 bar", res["answer"])
        self.assertIn("6.0 bar", res["answer"])
        self.assertIn("DISA", res["answer"])

    # 17. Copilot identifies missing data
    def test_17_copilot_identifies_missing_data(self):
        factory_simulator.set_scenario("missing_sensor")
        res = query_copilot("What data should we collect next?")
        self.assertIn("Tri-axial", res["answer"])
        self.assertIn("3.1 months", res["answer"])

    # 18. Complete end-to-end scenario A
    def test_18_complete_end_to_end_scenario_a(self):
        # DETECT
        factory_simulator.set_scenario("compressor_waste")
        anomalies = analyze_anomalies()
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].machine_id, "compressor_02")
        
        # ACTIONS & CONSTRAINT GATE
        pipeline = evaluate_decision_pipeline()
        rej = [a for a in pipeline["candidate_actions"] if not a["is_safe"]]
        safe = [a for a in pipeline["candidate_actions"] if a["is_safe"]]
        self.assertTrue(any("5.2 bar" in a["title"] for a in rej))
        self.assertTrue(any("90-sec" in a["title"] for a in safe))

        # WHAT-IF SIMULATION
        safe_action = safe[0]
        sim_res = simulate_decision_action(safe_action["action_id"])
        self.assertIn("WHAT-IF SIMULATION - NOT YET VERIFIED", sim_res["verification_disclaimer"])
        self.assertTrue(sim_res["is_production_safe_savings"])

        # HUMAN APPROVAL
        factory_simulator.apply_action(safe_action["action_id"])

        # SIMULATED ACTUAL & VERIFICATION
        v_check = verify_single_action(safe_action["action_id"])
        self.assertTrue(v_check["is_verified"])
        self.assertEqual(v_check["verification_verdict"], "VERIFIED PRODUCTION-SAFE SAVING")

        # EXPLAIN VIA COPILOT
        copilot_res = query_copilot("Did the intervention work?")
        self.assertIn("VERIFIED PRODUCTION-SAFE SAVING", copilot_res["answer"])
        self.assertIn("105.2", copilot_res["answer"])

    # 19. Complete end-to-end scenario B
    def test_19_complete_end_to_end_scenario_b(self):
        factory_simulator.set_scenario("furnace_degradation")
        anomalies = analyze_anomalies()
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0].machine_id, "furnace_02")

        pipeline = evaluate_decision_pipeline()
        safe = [a for a in pipeline["candidate_actions"] if a["is_safe"]]
        self.assertTrue(any("Refractory" in a["title"] for a in safe))

        factory_simulator.apply_action("action_furnace_refractory_patch")
        v_check = verify_single_action("action_furnace_refractory_patch")
        self.assertTrue(v_check["is_verified"])
        self.assertAlmostEqual(v_check["post_action_savings"]["kwh_saved_daily"], 256.0, places=1)

    # 20. Complete end-to-end scenario C
    def test_20_complete_end_to_end_scenario_c(self):
        factory_simulator.set_scenario("missing_sensor")
        readiness = get_data_readiness_status()
        self.assertFalse(readiness.can_diagnose_mechanical)

        rois = get_sensor_roi_recommendations()
        self.assertEqual(rois[0].sensor_id, "roi_c2_vibration")
        self.assertEqual(rois[0].recommended_rank, 1)

        # Copilot grounds in sensor ROI
        c_res = query_copilot("What data should we collect next?")
        self.assertIn("Vibration", c_res["answer"])
        self.assertIn("84,000", c_res["answer"])

if __name__ == '__main__':
    unittest.main()
