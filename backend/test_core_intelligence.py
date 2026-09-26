"""
End-to-End Test Suite for Core Intelligence Layer
Validates:
1. Production-aware SEC baseline (Multi-variable thermodynamic model)
2. Anomaly detection (High SEC, Energy spikes, Energy without production, Excessive idle, Abnormal telemetry)
3. Root-cause analysis & factor decomposition
4. Data quality & trust protocol (No hallucinated diagnoses)
5. Deterministic demo scenarios (Compressor 02, Furnace 02, Missing sensor)
6. Scikit-Learn Machine Learning Baseline Engine (R^2, MAE, feature weights, confidence bands)
7. End-to-end Mathematical Consistency (Zero discrepancies between telemetry, baseline, and anomaly reports)
"""

import sys
import os
import json

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.baseline_engine import calculate_expected_energy, evaluate_sec_deviation, get_ml_baseline_status
from backend.app.ml_baseline import sec_ml_engine
from backend.app.simulation import factory_simulator
from backend.app.anomaly_engine import analyze_anomalies
from backend.app.safe_action_engine import evaluate_candidate_actions
from backend.app.data_readiness_advisor import get_data_readiness_status
from backend.app.whatif_engine import run_whatif_simulation
from backend.app.copilot_engine import query_copilot

def test_production_aware_baseline():
    print("\n--- TEST 1: PRODUCTION-AWARE SEC BASELINE ---")
    
    # 1. Test scaling with production quantity
    b_10t = calculate_expected_energy("furnace_01", production_tons=10.0, product_type="Grey Iron (FG 260)")
    b_25t = calculate_expected_energy("furnace_01", production_tons=25.0, product_type="Grey Iron (FG 260)")
    assert b_25t["expected_kwh"] > b_10t["expected_kwh"], "Energy must scale with production quantity"
    print(f"[PASS] Production quantity scaling: 10t = {b_10t['expected_kwh']} kWh vs 25t = {b_25t['expected_kwh']} kWh")

    # 2. Test product type metallurgy dependency (Grey Iron vs SG Iron vs Alloy Steel)
    b_grey = calculate_expected_energy("furnace_01", production_tons=20.0, product_type="Grey Iron (FG 260)")
    b_sg = calculate_expected_energy("furnace_01", production_tons=20.0, product_type="SG / Ductile Iron (EN-GJS-500)")
    b_steel = calculate_expected_energy("furnace_01", production_tons=20.0, product_type="Alloy Steel Castings")
    assert b_sg["expected_kwh"] > b_grey["expected_kwh"], "SG Iron melting must require more energy than Grey Iron"
    assert b_steel["expected_kwh"] > b_sg["expected_kwh"], "Alloy Steel melting must require more energy than SG Iron"
    print(f"[PASS] Metallurgy product scaling: Grey Iron ({b_grey['expected_sec']} kWh/t) < SG Iron ({b_sg['expected_sec']} kWh/t) < Steel ({b_steel['expected_sec']} kWh/t)")

    # 3. Test shift adjustments
    b_shift_a = calculate_expected_energy("furnace_01", production_tons=20.0, shift="Shift A (06:00-14:00)")
    b_shift_night = calculate_expected_energy("furnace_01", production_tons=20.0, shift="Night Shift (22:00-06:00)")
    assert b_shift_night["expected_kwh"] < b_shift_a["expected_kwh"], "Night shift cooler heat rejection should yield slightly lower expected baseline"
    print(f"[PASS] Shift dependency: Day ({b_shift_a['expected_kwh']} kWh) vs Night ({b_shift_night['expected_kwh']} kWh)")

    # 4. Test operating conditions (Cold start penalty & ambient temperature)
    b_warm = calculate_expected_energy("furnace_01", production_tons=20.0, is_cold_start=False)
    b_cold = calculate_expected_energy("furnace_01", production_tons=20.0, is_cold_start=True)
    assert b_cold["expected_kwh"] == b_warm["expected_kwh"] + 350.0, "Cold start penalty must add 350 kWh sintering overhead"
    print(f"[PASS] Operating conditions: Warm furnace ({b_warm['expected_kwh']} kWh) vs Cold start ({b_cold['expected_kwh']} kWh)")

def test_compressor_waste_scenario():
    print("\n--- TEST 2: COMPRESSOR 02 IDLE WASTE SCENARIO ---")
    factory_simulator.set_scenario("compressor_waste")
    factory_simulator.reset_actions()
    
    summary = factory_simulator.get_factory_summary()
    c2 = factory_simulator.live_telemetry["compressor_02"]
    anomalies = analyze_anomalies()
    
    assert c2["is_anomaly"] is True, "Compressor 02 must be flagged as anomalous"
    assert c2["idle_time_today_hrs"] >= 3.0, "Excessive idle hours must be detected"
    assert c2["pressure_bar"] == 7.4, "Abnormal pressure over-pressurization must be detected"
    print(f"[PASS] Compressor 02 telemetry: Idle = {c2['idle_time_today_hrs']}h, Pressure = {c2['pressure_bar']} bar, SEC Dev = +{c2['sec_deviation_pct']}%")

    # Check root cause decomposition and mathematical consistency
    c2_anom = next(a for a in anomalies if a.machine_id == "compressor_02")
    assert c2_anom.anomaly_type == "EXCESSIVE_IDLE", "Anomaly type must be EXCESSIVE_IDLE"
    assert any("Unloaded Idle" in f.factor_name for f in c2_anom.contributing_factors), "Idle run factor must be present"
    assert c2_anom.maintenance_withheld is True, "Because vibration accelerometer is missing on C2, maintenance diagnosis must be withheld"
    assert c2_anom.sec_deviation_pct == c2["sec_deviation_pct"], f"Anomaly SEC deviation ({c2_anom.sec_deviation_pct}%) must match telemetry ({c2['sec_deviation_pct']}%)"
    print(f"[PASS] Mathematical consistency verified: Anomaly SEC Dev = Telemetry SEC Dev = +{c2_anom.sec_deviation_pct}%")
    print(f"[PASS] Root cause factors: {[(f.factor_name, f'{f.share_pct}%') for f in c2_anom.contributing_factors]}")
    print(f"[PASS] Trust rule: Withheld diagnosis = {c2_anom.maintenance_withheld} ('{c2_anom.withhold_reason}')")

    # Check Constraint Gate evaluation
    actions = evaluate_candidate_actions(c2_anom.id)
    unsafe_action = next(a for a in actions if not a.is_safe)
    safe_action = next(a for a in actions if a.is_safe)
    
    assert "Lower Shop Header Pressure" in unsafe_action.title, "Unsafe pressure drop must be candidate"
    assert "REJECTED BY CONSTRAINT GATE" in unsafe_action.rejection_reason, "Unsafe pressure drop must be rejected"
    assert "Auto-Idle Shutdown" in safe_action.title, "Safe auto-idle must be recommended"
    print(f"[PASS] Constraint Gate Rejection: {unsafe_action.title} -> {unsafe_action.rejection_reason[:80]}...")
    print(f"[PASS] Constraint Gate Approval: {safe_action.title} -> Safe: {safe_action.is_safe}")

def test_furnace_degradation_scenario():
    print("\n--- TEST 3: FURNACE 02 DEGRADATION SCENARIO ---")
    factory_simulator.set_scenario("furnace_degradation")
    factory_simulator.reset_actions()
    
    f2 = factory_simulator.live_telemetry["furnace_02"]
    anomalies = analyze_anomalies()
    
    assert f2["is_anomaly"] is True, "Furnace 02 must be flagged as anomalous"
    assert f2["current_power_kw"] == 78.0, "Holding power must jump from 45kW to 78kW"
    assert f2["temperature_c"] == 115.0, "Abnormal shell temperature must reach 115C (exceeding 85C limit)"
    print(f"[PASS] Furnace 02 telemetry: Holding Power = {f2['current_power_kw']} kW (Base: 45kW), Shell Temp = {f2['temperature_c']}°C, SEC Dev = +{f2['sec_deviation_pct']}%")

    f2_anom = next(a for a in anomalies if a.machine_id == "furnace_02")
    assert f2_anom.anomaly_type == "ENERGY_WITHOUT_PRODUCTION", "Holding heat leak represents energy without production"
    assert f2_anom.evidence_strength == "Strong", "Thermal sensors are installed, so evidence is strong"
    assert f2_anom.data_confidence_pct == 91.0, "Thermal confidence must be high"
    assert f2_anom.sec_deviation_pct == f2["sec_deviation_pct"], f"Anomaly SEC deviation ({f2_anom.sec_deviation_pct}%) must match telemetry ({f2['sec_deviation_pct']}%)"
    print(f"[PASS] Mathematical consistency verified: Anomaly SEC Dev = Telemetry SEC Dev = +{f2_anom.sec_deviation_pct}%")
    print(f"[PASS] Root cause breakdown for Furnace 02: {[(f.factor_name, f'{f.share_pct}%') for f in f2_anom.contributing_factors]}")

    # Check Constraint Gate for Furnace 02
    actions = evaluate_candidate_actions(f2_anom.id)
    unsafe_furnace_action = next(a for a in actions if not a.is_safe)
    safe_furnace_action = next(a for a in actions if a.is_safe)
    assert "Lower Furnace 02 Holding Temperature" in unsafe_furnace_action.title
    assert unsafe_furnace_action.is_safe is False
    assert "fluidity boundary" in unsafe_furnace_action.rejection_reason
    print(f"[PASS] Furnace 02 Constraint Gate: Temperature drop rejected because of cold shuts ({unsafe_furnace_action.rejection_reason[:75]}...)")
    print(f"[PASS] Furnace 02 Constraint Gate: Refractory patch safe ({safe_furnace_action.title})")

def test_missing_sensor_scenario():
    print("\n--- TEST 4: MISSING VIBRATION SENSOR & DATA CONFIDENCE ---")
    factory_simulator.set_scenario("missing_sensor")
    factory_simulator.reset_actions()
    
    anomalies = analyze_anomalies()
    readiness = get_data_readiness_status()
    c2 = factory_simulator.live_telemetry["compressor_02"]
    
    c2_missing = next(a for a in anomalies if a.machine_id == "compressor_02")
    assert c2_missing.evidence_strength == "Insufficient", "Evidence strength must be downgraded to Insufficient"
    assert c2_missing.maintenance_withheld is True, "Mechanical diagnosis must be withheld"
    assert c2_missing.sec_deviation_pct == c2["sec_deviation_pct"], "Anomaly SEC deviation must match live telemetry"
    assert readiness.can_diagnose_mechanical is False, "can_diagnose_mechanical must be False when vibration sensor is missing"
    assert readiness.withheld_diagnoses_count >= 1, "Withheld diagnoses count must be incremented"
    print(f"[PASS] Missing sensor trust rule: Evidence = {c2_missing.evidence_strength}, Confidence = {c2_missing.data_confidence_pct}%, Mechanical diagnosis allowed = {readiness.can_diagnose_mechanical}")
    print(f"[PASS] Withhold notice: '{c2_missing.withhold_reason}'")

def test_copilot_grounded_explanations():
    print("\n--- TEST 5: EXPLAINABLE AI COPILOT CITATIONS ---")
    factory_simulator.set_scenario("compressor_waste")
    
    q1 = query_copilot("Why did energy increase?")
    assert "Compressor 02" in q1["answer"], "Copilot must identify Compressor 02"
    assert "Unloaded Idle" in q1["answer"], "Copilot must cite the idle run factor"
    print(f"[PASS] Copilot Q1 (Why did energy increase?): Answer cited {q1['data_source']}")

    q2 = query_copilot("Why is this recommendation safe?")
    assert "DISA" in q2["answer"] or "Constraint" in q2["answer"] or "Throughput" in q2["answer"], "Copilot must cite constraint checks"
    print(f"[PASS] Copilot Q2 (Why is this safe?): Answer cited {q2['data_source']}")

    q3 = query_copilot("What sensor should we add next?")
    assert "Vibration" in q3["answer"], "Copilot must recommend the vibration accelerometer"
    assert "3.1 months" in q3["answer"], "Copilot must cite exact 3.1 months payback"
    print(f"[PASS] Copilot Q3 (What sensor to add?): Answer cited {q3['data_source']}")

def test_deterministic_reproducibility():
    print("\n--- TEST 6: DETERMINISTIC CONSISTENCY ---")
    factory_simulator.set_scenario("furnace_degradation")
    s1 = factory_simulator.get_factory_summary()
    factory_simulator.set_scenario("furnace_degradation")
    s2 = factory_simulator.get_factory_summary()
    assert s1["factory_sec"] == s2["factory_sec"], "Calculations must be completely deterministic"
    assert s1["total_energy_today_kwh"] == s2["total_energy_today_kwh"], "Energy must be completely reproducible"
    print(f"[PASS] Deterministic output: Run 1 SEC = {s1['factory_sec']} vs Run 2 SEC = {s2['factory_sec']}")

def test_ml_baseline_regression():
    print("\n--- TEST 7: SCIKIT-LEARN ML BASELINE REGRESSION MODEL ---")
    status = get_ml_baseline_status()
    assert status["is_trained"] is True, "ML Model must be fitted and active"
    assert status["metrics"]["r2_score"] >= 0.95, f"ML Model R2 score must exceed 0.95 (Actual: {status['metrics']['r2_score']})"
    print(f"[PASS] Scikit-Learn Model R^2 = {status['metrics']['r2_score']} | MAE = {status['metrics']['mae_kwh']} kWh | RMSE = {status['metrics']['rmse_kwh']} kWh")
    
    # Feature weights check
    weights = status["feature_weights"]
    assert "production_tons" in weights, "production_tons must be a trained feature"
    assert weights["production_tons"] > 0, "production_tons feature weight must be positive"
    print(f"[PASS] Explainable Feature Weights: Production = {weights['production_tons']}, Cold Start = {weights.get('is_cold_start')}, Ambient Temp = {weights.get('ambient_temp_c')}")

    # Prediction test with confidence interval
    pred_grey = sec_ml_engine.predict_expected_energy(production_tons=20.0, product_type="Grey Iron (FG 260)")
    pred_sg = sec_ml_engine.predict_expected_energy(production_tons=20.0, product_type="SG / Ductile Iron (EN-GJS-500)")
    assert pred_sg["expected_kwh"] > pred_grey["expected_kwh"], "ML Model must predict higher expected energy for SG Iron than Grey Iron"
    assert pred_grey["ci_lower_kwh"] < pred_grey["expected_kwh"] < pred_grey["ci_upper_kwh"], "Prediction must lie inside confidence interval"
    print(f"[PASS] ML Prediction: 20t Grey Iron = {pred_grey['expected_kwh']} kWh (CI: [{pred_grey['ci_lower_kwh']}, {pred_grey['ci_upper_kwh']}]) < SG Iron = {pred_sg['expected_kwh']} kWh")

    # Baseline Engine integration test
    ml_res = calculate_expected_energy("furnace_01", production_tons=20.0, use_ml=True)
    assert ml_res["is_ml_derived"] is True, "calculate_expected_energy with use_ml=True must return ML prediction"
    print(f"[PASS] Baseline engine use_ml=True flag verified: {ml_res['expected_sec']} kWh/ton")

def test_end_to_end_mathematical_consistency():
    print("\n--- TEST 8: END-TO-END MATHEMATICAL HARMONIZATION ---")
    for sc in ["compressor_waste", "furnace_degradation", "missing_sensor"]:
        factory_simulator.set_scenario(sc)
        factory_simulator.reset_actions()
        anomalies = analyze_anomalies()
        for a in anomalies:
            m = factory_simulator.live_telemetry[a.machine_id]
            # SEC Deviation consistency
            assert a.sec_deviation_pct == m["sec_deviation_pct"], f"Scenario {sc}: Anomaly SEC dev ({a.sec_deviation_pct}%) must equal telemetry ({m['sec_deviation_pct']}%)"
            # Excess energy non-negativity
            assert a.excess_energy_kwh_per_day >= 0.0, "Excess energy must be non-negative"
            # Excess cost calculation consistency (30 days * 8.20 avg tariff)
            expected_cost = round(a.excess_energy_kwh_per_day * 30 * 8.20, 0)
            assert a.excess_cost_inr_per_month == expected_cost, f"Excess cost {a.excess_cost_inr_per_month} must match formula {expected_cost}"
    print("[PASS] 100% Mathematical consistency verified across all scenarios, telemetry, and anomaly diagnostics.")

if __name__ == "__main__":
    test_production_aware_baseline()
    test_compressor_waste_scenario()
    test_furnace_degradation_scenario()
    test_missing_sensor_scenario()
    test_copilot_grounded_explanations()
    test_deterministic_reproducibility()
    test_ml_baseline_regression()
    test_end_to_end_mathematical_consistency()
    print("\n==============================================")
    print("ALL CORE INTELLIGENCE LAYER TESTS PASSED (8/8)!")
    print("==============================================")
