"""
Production-Safe Decision Engine & Constraint Gate
Converts detected factory energy anomalies into evaluated candidate interventions.

Core Innovation:
Never optimize energy alone. Energy reduction is worthless if it stalls production lines,
breaches customer delivery deadlines, causes metallurgical casting defects, or risks machine damage.

Pipeline:
Anomaly -> Evidence Check -> Candidate Actions -> Constraint Gate Evaluation -> What-If Simulation -> Safe/Rejected Decision -> Human Approval
"""

from typing import List, Dict, Any, Optional
from .models import (
    ActionEvaluation, 
    ConstraintCheck, 
    WhyIsItSafe, 
    SimulationComparison, 
    WhatIfSimulationResult
)
from .simulation import factory_simulator

def check_sensor_evidence(machine_id: str, required_sensors: List[str]) -> Dict[str, Any]:
    """
    Checks if all required physical sensors are streaming in factory telemetry.
    If required sensors are missing, flags an evidence gap.
    """
    telemetry = factory_simulator.live_telemetry.get(machine_id, {})
    active_sensors = telemetry.get("sensors_active", [])
    missing_sensors = telemetry.get("sensors_missing", [])
    
    missing_required = [s for s in required_sensors if s in missing_sensors or s not in active_sensors]
    has_all_required = len(missing_required) == 0
    
    return {
        "has_all_required": has_all_required,
        "missing_required": missing_required,
        "evidence_confidence": 94.0 if has_all_required else 42.0
    }

def evaluate_decision_pipeline(
    anomaly_id: Optional[str] = None, 
    machine_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the complete Decision Engine Pipeline:
    1. Reads active scenario and telemetry.
    2. Runs evidence checks on required data.
    3. Generates candidate interventions.
    4. Evaluates constraint gate (pressure, throughput, quality, machine limits, deadlines).
    5. Determines Production-Safe Savings qualification.
    6. Constructs grounded explanations (WHY THIS ACTION? / WHY NOT THE ALTERNATIVE?).
    """
    telemetry = factory_simulator.live_telemetry
    active_scenario = factory_simulator.active_scenario
    applied_actions = factory_simulator.applied_actions
    
    c2 = telemetry.get("compressor_02", {})
    f2 = telemetry.get("furnace_02", {})
    f1 = telemetry.get("furnace_01", {})
    
    candidates: List[ActionEvaluation] = []
    
    # -------------------------------------------------------------------------
    # SCENARIO A: COMPRESSOR 02 IDLE WASTE
    # -------------------------------------------------------------------------
    if active_scenario == "compressor_waste" or (c2 and c2.get("is_anomaly") and active_scenario != "missing_sensor"):
        is_c2_fixed = "action_compressor_unloaded_shutdown" in applied_actions
        
        # Candidate 1: Lower Header Pressure to 5.2 bar (UNSAFE OPTIMIZATION)
        c1_constraints = [
            ConstraintCheck(
                name="DISA Moulding Machine Min Pneumatic Pressure",
                threshold="≥ 6.0 bar",
                projected_value="5.2 bar",
                passed=False,
                violation_detail="VIOLATION: DISA automatic moulding line pneumatic squeeze cylinders stall below 6.0 bar, causing soft moulds, sand blowouts, and severe dimensional defects."
            ),
            ConstraintCheck(
                name="Shot Blast Finishing Velocity",
                threshold="≥ 5.8 bar",
                projected_value="5.2 bar",
                passed=False,
                violation_detail="VIOLATION: Shot blast nozzle abrasive velocity degrades, causing cleaning rejects and slowing finishing cycle."
            ),
            ConstraintCheck(
                name="Daily Casting Delivery Deadline",
                threshold="0 hrs delay",
                projected_value="+2.5 hrs delay",
                passed=False,
                violation_detail="VIOLATION: Production slowdown breaches customer dispatch window for Mahindra auto parts order."
            )
        ]
        
        candidates.append(ActionEvaluation(
            id="action_compressor_lower_pressure_extreme",
            action_id="action_compressor_lower_pressure_extreme",
            machine_id="compressor_02",
            anomaly_id="anomaly_c2_idle_excess",
            title="Candidate Action 1: Lower Shop Header Pressure to 5.2 bar",
            category="Pneumatic Setpoint Reduction",
            description="Drastically decrease compressor discharge cut-off pressure from 7.4 bar down to 5.2 bar to save motor compression kW.",
            proposed_change="Drastically decrease compressor discharge cut-off pressure from 7.4 bar down to 5.2 bar to save motor compression kW.",
            required_data=["Sub-meter Power", "Discharge Pressure Transducer"],
            energy_savings_pct=8.4,
            expected_energy_kwh_per_day=70.0,
            expected_energy_change={"kwh_per_day": 70.0, "pct": 8.4},
            monthly_cost_savings_inr=14800.0,
            expected_cost_change=14800.0,
            co2_reduction_kg=960.0,
            expected_co2_change=960.0,
            production_impact_pct=-12.5,
            production_impact={"throughput_loss_pct": 12.5, "status": "BREACH"},
            quality_impact_pct=-8.0,
            quality_impact={"scrap_surge_pct": 8.0, "status": "BREACH"},
            deadline_impact_hrs=2.5,
            machine_health_risk="Low",
            risk_level="High",
            constraints=c1_constraints,
            is_safe=False,
            status="REJECTED",
            is_production_safe_savings=False,
            rejection_reason="REJECTED BY CONSTRAINT GATE: Projected pressure (5.2 bar) falls below minimum process requirement (≥ 6.0 bar for DISA moulding). Causes 12.5% throughput collapse and casting surface defects.",
            confidence_score=94.0,
            confidence=94.0,
            implementation_complexity="Instant Config",
            implementation_time="Instant Config (15 mins)",
            why_this_action="Compressor power scales with discharge pressure, but dropping pressure to 5.2 bar impairs pneumatic actuators across the shop floor.",
            why_not_alternative="Reducing pressure to 5.2 bar was rejected because the moulding process requires a minimum pressure of 6.0 bar. Squeeze cylinders stall below 6.0 bar, causing scrap parts.",
            action_state="REJECTED"
        ))

        # Candidate 2: 90-sec Auto-Idle Shutdown & Tighten Pressure Band to 6.6 bar (SAFE RECOMMENDATION)
        c2_evidence = check_sensor_evidence("compressor_02", ["Sub-meter Power", "Discharge Pressure Transducer"])
        c2_constraints = [
            ConstraintCheck(
                name="Pneumatic Squeeze Pressure Buffer",
                threshold="≥ 6.0 bar",
                projected_value="6.6 bar (Safe buffer +0.6 bar)",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Motor Starts/Hour Thermal Limit",
                threshold="≤ 6 starts/hr",
                projected_value="3.2 starts/hr",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Moulding Line Throughput Retained",
                threshold="100% throughput",
                projected_value="100.0%",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Casting Dimensional Quality Spec",
                threshold="Zero defect impact",
                projected_value="No defect risk",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Customer Dispatch Schedule",
                threshold="0 hrs delay",
                projected_value="0.0 hrs delay",
                passed=True,
                violation_detail=None
            )
        ]
        
        c2_all_passed = all(c.passed for c in c2_constraints)
        c2_is_safe = c2_all_passed and c2_evidence["has_all_required"]
        c2_status = "APPROVED" if is_c2_fixed else ("SAFE_FOR_SIMULATION" if c2_is_safe else "REJECTED")

        candidates.append(ActionEvaluation(
            id="action_compressor_unloaded_shutdown",
            action_id="action_compressor_unloaded_shutdown",
            machine_id="compressor_02",
            anomaly_id="anomaly_c2_idle_excess",
            title="Candidate Action 2: 90-sec Auto-Idle Shutdown & Tighten Pressure Band to 6.6 bar",
            category="Operational Sequence Optimization",
            description="Reprogram Compressor 02 PLC: transition to standby if unloaded > 90 seconds (during mold shakeout/shift breaks) and trim cut-off from 7.4 to 6.6 bar.",
            proposed_change="Reprogram Compressor 02 PLC: transition to standby if unloaded > 90 seconds (during mold shakeout/shift breaks) and trim cut-off from 7.4 to 6.6 bar.",
            required_data=["Sub-meter Power", "Discharge Pressure Transducer"],
            energy_savings_pct=25.1,
            expected_energy_kwh_per_day=84.2,
            expected_energy_change={"kwh_per_day": 84.2, "pct": 25.1},
            monthly_cost_savings_inr=20700.0,
            expected_cost_change=20700.0,
            co2_reduction_kg=1810.0,
            expected_co2_change=1810.0,
            production_impact_pct=0.0,
            production_impact={"throughput_loss_pct": 0.0, "status": "PASS"},
            quality_impact_pct=0.0,
            quality_impact={"scrap_surge_pct": 0.0, "status": "PASS"},
            deadline_impact_hrs=0.0,
            machine_health_risk="Negligible",
            risk_level="Low",
            constraints=c2_constraints,
            is_safe=c2_is_safe,
            status=c2_status,
            is_production_safe_savings=c2_is_safe,
            rejection_reason=None,
            confidence_score=c2_evidence["evidence_confidence"],
            confidence=c2_evidence["evidence_confidence"],
            implementation_complexity="Minor Adjustment",
            implementation_time="Minor Adjustment (1 hour)",
            why_this_action="Compressor 02 is consuming 24 kW during unloaded periods (3.2 hrs/day idle). The proposed 90-second auto-idle shutdown reduces idle energy by 84.2 kWh/day while maintaining the required 6.6 bar process pressure above the 6.0 bar minimum threshold.",
            why_not_alternative="Reducing pressure to 5.2 bar was rejected because the moulding process requires a minimum pressure of 6.0 bar. Auto-idle shutdown saves energy by eliminating no-load run without starving air receivers.",
            why_is_it_safe=WhyIsItSafe(
                production_status="PASS",
                production_detail="100% throughput retained (120 moulds/hour nominal)",
                quality_status="PASS",
                quality_detail="Zero casting defect risk; line header maintains 6.6 bar",
                deadline_status="PASS",
                deadline_detail="Zero dispatch delay",
                machine_limits_status="PASS",
                machine_limits_detail="3.2 motor starts/hr well below 6.0 thermal limit"
            ),
            action_state="APPROVED" if is_c2_fixed else "CANDIDATE"
        ))

    # -------------------------------------------------------------------------
    # SCENARIO B: FURNACE 02 DEGRADATION
    # -------------------------------------------------------------------------
    if active_scenario == "furnace_degradation" or (f2 and f2.get("is_anomaly")):
        is_f2_fixed = "action_furnace_refractory_patch" in applied_actions

        # Candidate 3: Lower Furnace 02 Holding Temperature to 1350°C (UNSAFE OPTIMIZATION)
        f3_constraints = [
            ConstraintCheck(
                name="Liquid Metal Fluidity & Pouring Window",
                threshold="≥ 1410°C at ladle nozzle for thin-wall SG Iron",
                projected_value="1350°C (Sub-liquidus)",
                passed=False,
                violation_detail="VIOLATION: Molten iron liquidus fluidity drops below metallurgical specification. High risk of cold shuts, misruns, and micro-porosity in automotive castings."
            ),
            ConstraintCheck(
                name="Ladle Transport Temperature Drop Allowance",
                threshold="Holding bath > 1415°C",
                projected_value="1350°C",
                passed=False,
                violation_detail="VIOLATION: Metal cools by 40°C during crane transfer to moulding carousel, skulling the ladle lip."
            ),
            ConstraintCheck(
                name="ISO 9001 Metallurgy Quality Assurance",
                threshold="Scrap rate < 2.0%",
                projected_value="Scrap rate 16.2%",
                passed=False,
                violation_detail="VIOLATION: Expected scrap rate surges by +14.2%."
            )
        ]

        candidates.append(ActionEvaluation(
            id="action_furnace_lower_temp_unsafe",
            action_id="action_furnace_lower_temp_unsafe",
            machine_id="furnace_02",
            anomaly_id="anomaly_f2_degradation",
            title="Candidate Action 3: Lower Furnace 02 Holding Temperature to 1350°C",
            category="Thermal Setpoint Reduction",
            description="Lower molten iron holding bath temperature from 1420°C down to 1350°C to reduce electrical holding kilowatt losses.",
            proposed_change="Lower molten iron holding bath temperature from 1420°C down to 1350°C to reduce electrical holding kilowatt losses.",
            required_data=["Sub-meter Power", "Bath Pyrometer"],
            energy_savings_pct=6.8,
            expected_energy_kwh_per_day=42.0,
            expected_energy_change={"kwh_per_day": 42.0, "pct": 6.8},
            monthly_cost_savings_inr=32000.0,
            expected_cost_change=32000.0,
            co2_reduction_kg=2600.0,
            expected_co2_change=2600.0,
            production_impact_pct=-6.0,
            production_impact={"throughput_loss_pct": 6.0, "status": "BREACH"},
            quality_impact_pct=-14.2,
            quality_impact={"scrap_surge_pct": 14.2, "status": "BREACH"},
            deadline_impact_hrs=1.5,
            machine_health_risk="Low",
            risk_level="High",
            constraints=f3_constraints,
            is_safe=False,
            status="REJECTED",
            is_production_safe_savings=False,
            rejection_reason="REJECTED BY CONSTRAINT GATE: Projected holding temperature (1350°C) falls below metallurgical fluidity boundary (≥ 1410°C required). Causes 14.2% scrap surge due to cold-shuts and freezes pouring nozzles.",
            confidence_score=98.0,
            confidence=98.0,
            implementation_complexity="Instant Config",
            implementation_time="Instant Config (5 mins)",
            why_this_action="Thermodynamic radiation loss is proportional to T^4, so reducing bath temp saves holding kWh, but freezes the pouring stream.",
            why_not_alternative="Lowering holding temperature to 1350°C was rejected because the metallurgical specification requires ≥ 1410°C at the pouring nozzle. Sub-liquidus iron creates cold-shuts, scrap castings, and ladle freeze-ups.",
            action_state="REJECTED"
        ))

        # Candidate 4: Scheduled Refractory Dry-Vibe Patch & Lid Perimeter Seal (SAFE RECOMMENDATION)
        f4_evidence = check_sensor_evidence("furnace_02", ["Sub-meter Power", "Shell Thermocouple", "Cooling Water Delta T"])
        f4_constraints = [
            ConstraintCheck(
                name="Crucible Shell Surface Temperature",
                threshold="< 85.0°C",
                projected_value="70.0°C (Safe thermal barrier restored)",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Coil Cooling Water Delta T",
                threshold="< 7.0°C rise",
                projected_value="5.8°C rise (Optimal)",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Pouring Bath Superheat Maintained",
                threshold="1415°C - 1425°C",
                projected_value="1420°C (Certified)",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Production Throughput Retained",
                threshold="≥ 24.5 tons/day",
                projected_value="24.5 tons/day (100%)",
                passed=True,
                violation_detail=None
            )
        ]

        f4_all_passed = all(c.passed for c in f4_constraints)
        f4_is_safe = f4_all_passed and f4_evidence["has_all_required"]
        f4_status = "APPROVED" if is_f2_fixed else ("SAFE_FOR_SIMULATION" if f4_is_safe else "REJECTED")

        candidates.append(ActionEvaluation(
            id="action_furnace_refractory_patch",
            action_id="action_furnace_refractory_patch",
            machine_id="furnace_02",
            anomaly_id="anomaly_f2_degradation",
            title="Candidate Action 4: Scheduled Refractory Dry-Vibe Patch & Lid Perimeter Seal Restoration",
            category="Thermal Maintenance SOP",
            description="Execute a 2-hour dry-vibe refractory patch on crucible hot-face and replace lid ceramic fiber rope seal during planned Sunday maintenance.",
            proposed_change="Execute a 2-hour dry-vibe refractory patch on crucible hot-face and replace lid ceramic fiber rope seal during planned Sunday maintenance.",
            required_data=["Sub-meter Power", "Shell Thermocouple", "Cooling Water Delta T"],
            energy_savings_pct=41.0,
            expected_energy_kwh_per_day=264.0,
            expected_energy_change={"kwh_per_day": 264.0, "pct": 41.0},
            monthly_cost_savings_inr=65000.0,
            expected_cost_change=65000.0,
            co2_reduction_kg=5660.0,
            expected_co2_change=5660.0,
            production_impact_pct=0.0,
            production_impact={"throughput_loss_pct": 0.0, "status": "PASS"},
            quality_impact_pct=0.2,
            quality_impact={"scrap_reduction_pct": 0.2, "status": "PASS"},
            deadline_impact_hrs=0.0,
            machine_health_risk="Negligible",
            risk_level="Low",
            constraints=f4_constraints,
            is_safe=f4_is_safe,
            status=f4_status,
            is_production_safe_savings=f4_is_safe,
            rejection_reason=None,
            confidence_score=f4_evidence["evidence_confidence"],
            confidence=f4_evidence["evidence_confidence"],
            implementation_complexity="SOP Maintenance",
            implementation_time="Planned Maintenance Window (2 hours)",
            why_this_action="Furnace 02 holding draw jumped from 45 kW to 78 kW (+73%) and shell temp reached 115°C due to refractory thinning. Scheduled dry-vibe patching restores thermal resistance, saving 264 kWh/day while keeping tapping bath at 1420°C.",
            why_not_alternative="Lowering holding temperature to 1350°C was rejected because it causes catastrophic casting misruns. Restoring the refractory lining fixes thermal losses at the physical source without sacrificing metallurgical quality.",
            why_is_it_safe=WhyIsItSafe(
                production_status="PASS",
                production_detail="24.5 tons/day throughput fully retained",
                quality_status="PASS",
                quality_detail="Pouring superheat maintained at 1420°C",
                deadline_status="PASS",
                deadline_detail="Executed during planned Sunday maintenance window",
                machine_limits_status="PASS",
                machine_limits_detail="Shell temp drops from 115°C to 70°C, cooling water delta drops from 11.2°C to 5.8°C"
            ),
            action_state="APPROVED" if is_f2_fixed else "CANDIDATE"
        ))

    # -------------------------------------------------------------------------
    # SCENARIO C: MISSING VIBRATION SENSOR (EVIDENCE GAP / TRUST PROTOCOL)
    # -------------------------------------------------------------------------
    if active_scenario == "missing_sensor":
        missing_evidence = check_sensor_evidence("compressor_02", ["Sub-meter Power", "Tri-axial Vibration Accelerometer"])
        
        c6_constraints = [
            ConstraintCheck(
                name="Tri-axial Vibration Sensor Telemetry Availability",
                threshold="Sensor stream online & calibrated",
                projected_value="SENSOR NOT INSTALLED (Missing)",
                passed=False,
                violation_detail="EVIDENCE GAP: Tri-axial vibration accelerometer is not installed on Compressor 02 air-end. Telemetry stream is absent."
            ),
            ConstraintCheck(
                name="Data Confidence & Trust Protocol Gate",
                threshold="≥ 75.0% confidence for invasive mechanical overhaul",
                projected_value="42.0% (Confidence Degraded)",
                passed=False,
                violation_detail="TRUST PROTOCOL: System strictly withholds invasive mechanical overhaul diagnosis when mechanical telemetry is absent to prevent false actions."
            )
        ]

        candidates.append(ActionEvaluation(
            id="action_compressor_bearing_overhaul_unsupported",
            action_id="action_compressor_bearing_overhaul_unsupported",
            machine_id="compressor_02",
            anomaly_id="anomaly_c2_missing_vibration",
            title="Candidate Action 6: Mechanical Air-End Bearing Overhaul & Rotor Rebuild",
            category="Mechanical Overhaul",
            description="Initiate emergency machine shutdown to dismantle compressor air-end and replace bearings based on suspected internal mechanical drag.",
            proposed_change="Initiate emergency machine shutdown to dismantle compressor air-end and replace bearings based on suspected internal mechanical drag.",
            required_data=["Sub-meter Power", "Tri-axial Vibration Accelerometer"],
            energy_savings_pct=19.2,
            expected_energy_kwh_per_day=62.0,
            expected_energy_change={"kwh_per_day": 62.0, "pct": 19.2},
            monthly_cost_savings_inr=15200.0,
            expected_cost_change=15200.0,
            co2_reduction_kg=1330.0,
            expected_co2_change=1330.0,
            production_impact_pct=-15.0,
            production_impact={"throughput_loss_pct": 15.0, "status": "BREACH"},
            quality_impact_pct=0.0,
            quality_impact={"scrap_surge_pct": 0.0, "status": "PASS"},
            deadline_impact_hrs=8.0,
            machine_health_risk="Moderate",
            risk_level="Medium",
            constraints=c6_constraints,
            is_safe=False,
            status="NEEDS_MORE_DATA",
            is_production_safe_savings=False,
            rejection_reason="WITHHELD BY TRUST PROTOCOL (NEEDS MORE DATA): Required vibration accelerometer is NOT installed on Compressor 02. Invasive mechanical tear-down withheld to prevent false maintenance action.",
            confidence_score=42.0,
            confidence=42.0,
            implementation_complexity="SOP Maintenance",
            implementation_time="8 hours emergency plant downtime",
            why_this_action="Elevated power (+28.1%) detected, but mechanical telemetry is missing. The system withholds diagnosis and recommends installing a ₹18.5k vibration accelerometer (Rank #1 ROI) before performing teardown.",
            why_not_alternative="Action held in 'NEEDS MORE DATA' state. We do not approve unverified mechanical maintenance because the energy increase could be caused by external pipe leaks rather than bearing wear.",
            action_state="REJECTED"
        ))

    # -------------------------------------------------------------------------
    # SCENARIO D: PEAK TOD TARIFF SCHEDULING
    # -------------------------------------------------------------------------
    if active_scenario == "production_scheduling" or len(candidates) == 0:
        is_sched_fixed = "action_tod_rescheduling" in applied_actions

        tod_constraints = [
            ConstraintCheck(
                name="Factory Shift Manning (Karnataka Factories Act)",
                threshold="Shift supervisor certified for night melting",
                projected_value="Certified crew available in Shift C",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Holding Furnace Molten Buffer Capacity",
                threshold="≤ 8.0 tons buffer",
                projected_value="6.5 tons buffer",
                passed=True,
                violation_detail=None
            ),
            ConstraintCheck(
                name="Daily Pouring Schedule Alignment",
                threshold="Pouring line starts at 07:30 ready",
                projected_value="Hot metal available at 07:00",
                passed=True,
                violation_detail=None
            )
        ]

        # Candidate 5B: Emergency Peak Shedding by Shutting Off Pouring Line Conveyor (UNSAFE OPTIMIZATION)
        tod_unsafe_constraints = [
            ConstraintCheck(
                name="DISA Moulding Line Continuous Feed",
                threshold="0% Line Starvation",
                projected_value="-25.0% Throughput Collapse",
                passed=False,
                violation_detail="VIOLATION: Halting primary melting during peak hours without buffer starves the moulding line, halting pouring operations."
            ),
            ConstraintCheck(
                name="Mahindra Automotive Delivery Dispatch SLA",
                threshold="0 hrs delay",
                projected_value="+4.0 hrs dispatch breach",
                passed=False,
                violation_detail="VIOLATION: Delays 24.5-ton casting dispatch past the customer delivery window, triggering contractual delivery penalty."
            ),
            ConstraintCheck(
                name="Molten Iron Liquidus Superheat in Transfer Ladles",
                threshold="≥ 1410°C",
                projected_value="1375°C (Ladle lip freezing)",
                passed=False,
                violation_detail="VIOLATION: Metal cools in crane transfer ladles below liquidus temperature, causing severe cold-shuts and ladle skulling."
            )
        ]

        candidates.append(ActionEvaluation(
            id="action_tod_emergency_curtailment",
            action_id="action_tod_emergency_curtailment",
            machine_id="furnace_01",
            anomaly_id="anomaly_tod_peak_tariff",
            title="Candidate Action 5B: Peak Shift Melting Curtailment Without Holding Buffer",
            category="Emergency Peak Shedding",
            description="Completely shut down Furnace 01 during peak tariff hours (18:00 - 22:00) without pre-melting molten buffer.",
            proposed_change="Completely shut down Furnace 01 during peak tariff hours (18:00 - 22:00) without pre-melting molten buffer.",
            required_data=["Main Feeder Power Meter", "Weighbridge Batch Log"],
            energy_savings_pct=14.0,
            expected_energy_kwh_per_day=420.0,
            expected_energy_change={"kwh_per_day": 420.0, "pct": 14.0},
            monthly_cost_savings_inr=-48000.0, # Negative due to delivery penalties
            expected_cost_change=-48000.0,
            co2_reduction_kg=3600.0,
            expected_co2_change=3600.0,
            production_impact_pct=-25.0,
            production_impact={"throughput_loss_pct": 25.0, "status": "BREACH"},
            quality_impact_pct=-18.5,
            quality_impact={"scrap_surge_pct": 18.5, "status": "BREACH"},
            deadline_impact_hrs=4.0,
            machine_health_risk="High",
            risk_level="High",
            constraints=tod_unsafe_constraints,
            is_safe=False,
            status="REJECTED",
            is_production_safe_savings=False,
            rejection_reason="REJECTED BY CONSTRAINT GATE: Shutting down primary induction melting without buffer starves the moulding line (-25.0% throughput), delays dispatch by +4.0 hrs, and freezes transfer ladles below 1410°C.",
            confidence_score=96.0,
            confidence=96.0,
            implementation_complexity="Instant Config",
            implementation_time="Instant Shutdown",
            why_this_action="Peak power curtailment avoids the ₹10.80/kWh rate, but starving the line collapses daily production output.",
            why_not_alternative="Emergency peak shedding without buffer was rejected because it causes +4.0 hrs delivery delay and severe ladle skulling. Shifting pre-melting to night off-peak (03:00 - 06:00) achieves tariff savings without production loss.",
            action_state="REJECTED"
        ))

        candidates.append(ActionEvaluation(
            id="action_tod_rescheduling",
            action_id="action_tod_rescheduling",
            machine_id="furnace_01",
            anomaly_id="anomaly_tod_peak_tariff",
            title="Candidate Action 5: Shift Primary Heat Pre-Melting to Night Off-Peak Slot (03:00 - 06:00)",
            category="Energy-Aware Production Scheduling",
            description="Realign furnace batch start: execute first 2 heats between 03:00 - 06:00 (Night TOD tariff ₹5.40/kWh) and store in holding furnace, avoiding peak ₹10.80/kWh rate.",
            proposed_change="Realign furnace batch start: execute first 2 heats between 03:00 - 06:00 (Night TOD tariff ₹5.40/kWh) and store in holding furnace, avoiding peak ₹10.80/kWh rate.",
            required_data=["Main Feeder Power Meter", "BESCOM TOD Tariff Schedule"],
            energy_savings_pct=0.0,
            expected_energy_kwh_per_day=0.0,
            expected_energy_change={"kwh_per_day": 0.0, "pct": 0.0},
            monthly_cost_savings_inr=126000.0,
            expected_cost_change=126000.0,
            co2_reduction_kg=0.0,
            expected_co2_change=0.0,
            production_impact_pct=0.0,
            production_impact={"throughput_loss_pct": 0.0, "status": "PASS"},
            quality_impact_pct=0.0,
            quality_impact={"scrap_surge_pct": 0.0, "status": "PASS"},
            deadline_impact_hrs=0.0,
            machine_health_risk="Negligible",
            risk_level="Low",
            constraints=tod_constraints,
            is_safe=True,
            status="APPROVED" if is_sched_fixed else "SAFE_FOR_SIMULATION",
            is_production_safe_savings=True,
            rejection_reason=None,
            confidence_score=97.0,
            confidence=97.0,
            implementation_complexity="SOP Change",
            implementation_time="SOP Shift Schedule Change (0 Capex)",
            why_this_action="Electricity tariff drops by 50% from ₹10.80/kWh during peak hours to ₹5.40/kWh during night off-peak. Pre-melting the initial 6.5-ton charge between 03:00 - 06:00 saves ₹126,000/month with zero change in net kWh or pouring times.",
            why_not_alternative="Alternative daytime melting exposes the plant to the ₹10.80/kWh peak TOD tariff bracket. Off-peak scheduling captures tariff incentives without changing total tonnage or cycle duration.",
            why_is_it_safe=WhyIsItSafe(
                production_status="PASS",
                production_detail="Hot metal ready at 07:00, 30 mins before moulding start",
                quality_status="PASS",
                quality_detail="Zero metallurgical impact; holding furnace buffer maintained",
                deadline_status="PASS",
                deadline_detail="Daily dispatch schedule unchanged",
                machine_limits_status="PASS",
                machine_limits_detail="Holding capacity buffer 6.5t safely below 8.0t limit"
            ),
            action_state="APPROVED" if is_sched_fixed else "CANDIDATE"
        ))

    # Filter by anomaly_id or machine_id if requested
    if anomaly_id:
        filtered = [a for a in candidates if a.anomaly_id == anomaly_id]
        if filtered:
            candidates = filtered
    elif machine_id:
        filtered = [a for a in candidates if a.machine_id == machine_id]
        if filtered:
            candidates = filtered

    safe_count = len([a for a in candidates if a.is_safe])
    rejected_count = len([a for a in candidates if a.status == "REJECTED"])
    needs_data_count = len([a for a in candidates if a.status == "NEEDS_MORE_DATA"])

    return {
        "active_scenario": active_scenario,
        "candidate_actions": [a.model_dump() for a in candidates],
        "summary": {
            "total_candidates": len(candidates),
            "safe_for_simulation": safe_count,
            "rejected_by_constraints": rejected_count,
            "needs_more_data": needs_data_count,
            "production_safe_savings_unlocked_inr_month": sum(
                a.monthly_cost_savings_inr for a in candidates if a.is_production_safe_savings
            )
        }
    }

def simulate_decision_action(action_id: str) -> Dict[str, Any]:
    """
    Executes a high-fidelity What-If Simulation for a candidate action.
    Returns BEFORE (CURRENT BASELINE) vs AFTER (SIMULATED PREDICTION).
    Clearly flagged with 'WHAT-IF SIMULATION — NOT YET VERIFIED' protocol.
    """
    summary = factory_simulator.get_factory_summary()
    telemetry = factory_simulator.live_telemetry

    # Action 2: Compressor 02 Auto-Idle Shutdown
    if action_id == "action_compressor_unloaded_shutdown":
        c2 = telemetry.get("compressor_02", {})
        baseline_kwh = c2.get("energy_today_kwh", 336.0)
        simulated_kwh = round(baseline_kwh - 84.2, 1)
        kwh_saved = round(baseline_kwh - simulated_kwh, 1)
        pct_energy = round(-(kwh_saved / baseline_kwh) * 100, 1)

        baseline_cost_month = round(baseline_kwh * 30 * 8.20, 0)
        simulated_cost_month = round(simulated_kwh * 30 * 8.20, 0)
        savings_cost_month = round(baseline_cost_month - simulated_cost_month, 0)

        baseline_co2 = round(baseline_kwh * 30 * 0.716, 0)
        simulated_co2 = round(simulated_kwh * 30 * 0.716, 0)
        reduction_co2 = round(baseline_co2 - simulated_co2, 0)

        metrics = [
            SimulationComparison(
                metric="Compressor 02 Daily Energy",
                unit="kWh/day",
                baseline=baseline_kwh,
                simulated=simulated_kwh,
                pct_change=pct_energy,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Compressor 02 Specific Energy Consumption",
                unit="kWh/ton",
                baseline=round(baseline_kwh / 24.5, 2),
                simulated=round(simulated_kwh / 24.5, 2),
                pct_change=pct_energy,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Plant Overall Specific Energy Consumption (SEC)",
                unit="kWh/ton",
                baseline=summary["factory_sec"],
                simulated=round(summary["factory_sec"] - (kwh_saved / 24.5), 1),
                pct_change=round(-((kwh_saved / 24.5) / summary["factory_sec"]) * 100, 1),
                is_favorable=True
            ),
            SimulationComparison(
                metric="Compressor 02 Monthly Power Cost",
                unit="₹/month",
                baseline=baseline_cost_month,
                simulated=simulated_cost_month,
                pct_change=pct_energy,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Monthly CO2 Emissions",
                unit="kg CO2/month",
                baseline=baseline_co2,
                simulated=simulated_co2,
                pct_change=pct_energy,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Moulding Line Pneumatic Throughput",
                unit="Moulds/hour",
                baseline=120.0,
                simulated=120.0,
                pct_change=0.0,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Casting Quality Pass Rate",
                unit="%",
                baseline=97.4,
                simulated=97.4,
                pct_change=0.0,
                is_favorable=True
            )
        ]

        return {
            "action_id": action_id,
            "action_title": "Candidate Action 2: 90-sec Auto-Idle Shutdown & Tighten Pressure Band to 6.6 bar",
            "machine_id": "compressor_02",
            "machine_name": "Compressor 02 (Kaeser Screw 75kW)",
            "status": "SIMULATED_NOT_VERIFIED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": True,
            "energy_comparison": {
                "current_kwh_day": baseline_kwh,
                "predicted_kwh_day": simulated_kwh,
                "kwh_saved_day": kwh_saved,
                "pct_change": pct_energy
            },
            "cost_comparison": {
                "current_cost_month_inr": baseline_cost_month,
                "predicted_cost_month_inr": simulated_cost_month,
                "savings_month_inr": savings_cost_month,
                "pct_change": pct_energy
            },
            "co2_comparison": {
                "current_emissions_kg_month": baseline_co2,
                "predicted_emissions_kg_month": simulated_co2,
                "reduction_kg_month": reduction_co2,
                "pct_change": pct_energy
            },
            "production_comparison": {
                "current_throughput": "120 moulds/hr (24.5 tons/day)",
                "predicted_throughput": "120 moulds/hr (24.5 tons/day)",
                "change_pct": 0.0,
                "throughput_retained": True
            },
            "quality_comparison": {
                "current_status": "97.4% Pass Rate (ISO 9001)",
                "predicted_status": "97.4% Pass Rate (Zero Defect Surge)",
                "status": "PASS"
            },
            "risk_level": "Negligible",
            "confidence_pct": 96.0,
            "payback_period_days": 0,
            "production_throughput_retained": True,
            "quality_tolerance_satisfied": True,
            "recommendation_verdict": "RECOMMENDED SAFE",
            "why_this_action": "Compressor 02 is consuming 24 kW during unloaded periods (3.2 hrs/day idle). The proposed 90-second auto-idle shutdown reduces idle energy by 84.2 kWh/day while maintaining the required 6.6 bar process pressure above the 6.0 bar minimum threshold.",
            "why_not_alternative": "Reducing pressure to 5.2 bar was rejected because the moulding process requires a minimum pressure of 6.0 bar.",
            "metrics": [m.model_dump() for m in metrics]
        }

    # Action 4: Furnace 02 Refractory Patch & Lid Seal Restoration
    elif action_id == "action_furnace_refractory_patch":
        f2 = telemetry.get("furnace_02", {})
        baseline_kwh = f2.get("energy_today_kwh", 624.0)
        simulated_kwh = round(baseline_kwh - 264.0, 1)
        kwh_saved = round(baseline_kwh - simulated_kwh, 1)
        pct_energy = round(-(kwh_saved / baseline_kwh) * 100, 1)

        baseline_cost_month = round(baseline_kwh * 30 * 8.20, 0)
        simulated_cost_month = round(simulated_kwh * 30 * 8.20, 0)
        savings_cost_month = round(baseline_cost_month - simulated_cost_month, 0)

        baseline_co2 = round(baseline_kwh * 30 * 0.716, 0)
        simulated_co2 = round(simulated_kwh * 30 * 0.716, 0)
        reduction_co2 = round(baseline_co2 - simulated_co2, 0)

        metrics = [
            SimulationComparison(
                metric="Furnace 02 Molten Holding Power",
                unit="kW",
                baseline=78.0,
                simulated=46.0,
                pct_change=-41.0,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Furnace 02 Specific Energy Consumption",
                unit="kWh/ton",
                baseline=round(baseline_kwh / 24.5, 2),
                simulated=round(simulated_kwh / 24.5, 2),
                pct_change=pct_energy,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Plant Overall Specific Energy Consumption (SEC)",
                unit="kWh/ton",
                baseline=summary["factory_sec"],
                simulated=round(summary["factory_sec"] - (kwh_saved / 24.5), 1),
                pct_change=round(-((kwh_saved / 24.5) / summary["factory_sec"]) * 100, 1),
                is_favorable=True
            ),
            SimulationComparison(
                metric="Furnace 02 Monthly Power Cost",
                unit="₹/month",
                baseline=baseline_cost_month,
                simulated=simulated_cost_month,
                pct_change=pct_energy,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Crucible Shell Surface Temperature",
                unit="°C",
                baseline=115.0,
                simulated=70.0,
                pct_change=-39.1,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Good Castings Daily Output",
                unit="Tons/day",
                baseline=24.5,
                simulated=24.5,
                pct_change=0.0,
                is_favorable=True
            )
        ]

        return {
            "action_id": action_id,
            "action_title": "Candidate Action 4: Scheduled Refractory Dry-Vibe Patch & Lid Perimeter Seal Restoration",
            "machine_id": "furnace_02",
            "machine_name": "Furnace 02 (Holding Furnace 450kW)",
            "status": "SIMULATED_NOT_VERIFIED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": True,
            "energy_comparison": {
                "current_kwh_day": baseline_kwh,
                "predicted_kwh_day": simulated_kwh,
                "kwh_saved_day": kwh_saved,
                "pct_change": pct_energy
            },
            "cost_comparison": {
                "current_cost_month_inr": baseline_cost_month,
                "predicted_cost_month_inr": simulated_cost_month,
                "savings_month_inr": savings_cost_month,
                "pct_change": pct_energy
            },
            "co2_comparison": {
                "current_emissions_kg_month": baseline_co2,
                "predicted_emissions_kg_month": simulated_co2,
                "reduction_kg_month": reduction_co2,
                "pct_change": pct_energy
            },
            "production_comparison": {
                "current_throughput": "24.5 tons/day",
                "predicted_throughput": "24.5 tons/day",
                "change_pct": 0.0,
                "throughput_retained": True
            },
            "quality_comparison": {
                "current_status": "Bath superheat 1420°C maintained",
                "predicted_status": "Bath superheat 1420°C maintained (Optimal fluidity)",
                "status": "PASS"
            },
            "risk_level": "Negligible",
            "confidence_pct": 97.0,
            "payback_period_days": 8,
            "production_throughput_retained": True,
            "quality_tolerance_satisfied": True,
            "recommendation_verdict": "RECOMMENDED SAFE",
            "why_this_action": "Furnace 02 holding draw jumped from 45 kW to 78 kW (+73%) and shell temp reached 115°C due to refractory thinning. Scheduled dry-vibe patching restores thermal resistance, saving 264 kWh/day while keeping tapping bath at 1420°C.",
            "why_not_alternative": "Lowering holding temperature to 1350°C was rejected because it causes catastrophic casting misruns. Restoring the refractory lining fixes thermal losses at the physical source without sacrificing metallurgical quality.",
            "metrics": [m.model_dump() for m in metrics]
        }

    # Action 5: Peak TOD Tariff Rescheduling
    elif action_id == "action_tod_rescheduling":
        baseline_cost_month = 1240000.0
        simulated_cost_month = 1114000.0
        savings_cost_month = 126000.0

        metrics = [
            SimulationComparison(
                metric="TOD Shift Power Cost Blend",
                unit="₹/kWh",
                baseline=8.20,
                simulated=6.85,
                pct_change=-16.5,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Monthly Foundry Electricity Bill",
                unit="₹/month",
                baseline=baseline_cost_month,
                simulated=simulated_cost_month,
                pct_change=-10.2,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Total Monthly kWh Consumption",
                unit="kWh/month",
                baseline=151000.0,
                simulated=151000.0,
                pct_change=0.0,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Casting Delivery Lead Time",
                unit="Hours",
                baseline=24.0,
                simulated=24.0,
                pct_change=0.0,
                is_favorable=True
            )
        ]

        return {
            "action_id": action_id,
            "action_title": "Candidate Action 5: Shift Primary Heat Pre-Melting to Night Off-Peak Slot",
            "machine_id": "furnace_01",
            "machine_name": "Furnace 01 & 02 Melt System",
            "status": "SIMULATED_NOT_VERIFIED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": True,
            "energy_comparison": {
                "current_kwh_day": 14350.0,
                "predicted_kwh_day": 14350.0,
                "kwh_saved_day": 0.0,
                "pct_change": 0.0
            },
            "cost_comparison": {
                "current_cost_month_inr": baseline_cost_month,
                "predicted_cost_month_inr": simulated_cost_month,
                "savings_month_inr": savings_cost_month,
                "pct_change": -10.2
            },
            "co2_comparison": {
                "current_emissions_kg_month": 108116.0,
                "predicted_emissions_kg_month": 108116.0,
                "reduction_kg_month": 0.0,
                "pct_change": 0.0
            },
            "production_comparison": {
                "current_throughput": "24.5 tons/day",
                "predicted_throughput": "24.5 tons/day",
                "change_pct": 0.0,
                "throughput_retained": True
            },
            "quality_comparison": {
                "current_status": "Shift A pouring starts on schedule",
                "predicted_status": "Shift A pouring starts on schedule",
                "status": "PASS"
            },
            "risk_level": "Negligible",
            "confidence_pct": 97.0,
            "payback_period_days": 0,
            "production_throughput_retained": True,
            "quality_tolerance_satisfied": True,
            "recommendation_verdict": "RECOMMENDED SAFE",
            "why_this_action": "Electricity tariff drops by 50% from ₹10.80/kWh during peak hours to ₹5.40/kWh during night off-peak. Pre-melting the initial 6.5-ton charge between 03:00 - 06:00 saves ₹126,000/month with zero change in net kWh or pouring times.",
            "why_not_alternative": "Alternative daytime melting exposes the plant to the ₹10.80/kWh peak TOD tariff bracket.",
            "metrics": [m.model_dump() for m in metrics]
        }

    # Action 1: Compressor 02 Extreme Pressure Drop (UNSAFE CANDIDATE)
    elif action_id in ["action_compressor_lower_pressure_extreme", "action_compressor_reduce_pressure"]:
        c2 = telemetry.get("compressor_02", {})
        baseline_kwh = c2.get("energy_today_kwh", 336.0)
        simulated_kwh = round(baseline_kwh - 70.0, 1)

        metrics = [
            SimulationComparison(
                metric="Compressor 02 Daily Energy",
                unit="kWh/day",
                baseline=baseline_kwh,
                simulated=simulated_kwh,
                pct_change=-8.4,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Moulding Line Pneumatic Squeeze Pressure",
                unit="bar",
                baseline=7.4,
                simulated=5.2,
                pct_change=-29.7,
                is_favorable=False
            ),
            SimulationComparison(
                metric="Moulding Line Pneumatic Throughput",
                unit="Moulds/hour",
                baseline=120.0,
                simulated=105.0,
                pct_change=-12.5,
                is_favorable=False
            ),
            SimulationComparison(
                metric="Casting Scrap Rate Surge",
                unit="%",
                baseline=1.2,
                simulated=9.2,
                pct_change=666.7,
                is_favorable=False
            ),
            SimulationComparison(
                metric="Daily Net Financial Balance (Energy Saved - Scrap Losses)",
                unit="₹/day",
                baseline=0.0,
                simulated=-4730.0,
                pct_change=-100.0,
                is_favorable=False
            )
        ]

        return {
            "action_id": action_id,
            "action_title": "Candidate Action 1: Lower Shop Header Pressure to 5.2 bar (UNSAFE CANDIDATE)",
            "machine_id": "compressor_02",
            "machine_name": "Compressor 02 (Kaeser Screw 75kW)",
            "status": "SIMULATED_REJECTED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": False,
            "energy_comparison": {
                "current_kwh_day": baseline_kwh,
                "predicted_kwh_day": simulated_kwh,
                "kwh_saved_day": 70.0,
                "pct_change": -8.4
            },
            "cost_comparison": {
                "current_cost_month_inr": round(baseline_kwh * 30 * 8.20, 0),
                "predicted_cost_month_inr": round(simulated_kwh * 30 * 8.20, 0),
                "savings_month_inr": -142000.0, # Negative due to scrap penalty
                "pct_change": -8.4
            },
            "co2_comparison": {
                "current_emissions_kg_month": round(baseline_kwh * 30 * 0.716, 0),
                "predicted_emissions_kg_month": round(simulated_kwh * 30 * 0.716, 0),
                "reduction_kg_month": 960.0,
                "pct_change": -8.4
            },
            "production_comparison": {
                "current_throughput": "120 moulds/hr (24.5 tons/day)",
                "predicted_throughput": "105 moulds/hr (21.4 tons/day)",
                "change_pct": -12.5,
                "throughput_retained": False
            },
            "quality_comparison": {
                "current_status": "97.4% Pass Rate",
                "predicted_status": "89.4% Pass Rate (Scrap surge: soft moulds)",
                "status": "BREACH"
            },
            "risk_level": "High",
            "confidence_pct": 94.0,
            "payback_period_days": 0,
            "production_throughput_retained": False,
            "quality_tolerance_satisfied": False,
            "recommendation_verdict": "REJECTED BY CONSTRAINT GATE (Violates DISA Moulding Pressure min 6.0 bar)",
            "why_this_action": "Compressor power scales with discharge pressure, but dropping pressure to 5.2 bar impairs pneumatic actuators across the shop floor.",
            "why_not_alternative": "Reducing pressure to 5.2 bar was rejected because the moulding process requires a minimum pressure of 6.0 bar. Squeeze cylinders stall below 6.0 bar, causing scrap parts.",
            "metrics": [m.model_dump() for m in metrics]
        }

    # Action 3: Lower Furnace 02 Holding Temperature to 1350°C (UNSAFE CANDIDATE)
    elif action_id == "action_furnace_lower_temp_unsafe":
        f2 = telemetry.get("furnace_02", {})
        baseline_kwh = f2.get("energy_today_kwh", 624.0)
        simulated_kwh = round(baseline_kwh - 42.0, 1)

        metrics = [
            SimulationComparison(
                metric="Furnace 02 Molten Holding Power",
                unit="kW",
                baseline=78.0,
                simulated=72.7,
                pct_change=-6.8,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Ladle Lip Pouring Temperature",
                unit="°C",
                baseline=1420.0,
                simulated=1350.0,
                pct_change=-4.9,
                is_favorable=False
            ),
            SimulationComparison(
                metric="Casting Metallurgical Scrap Rate",
                unit="%",
                baseline=1.2,
                simulated=15.4,
                pct_change=1183.3,
                is_favorable=False
            ),
            SimulationComparison(
                metric="Daily Net Financial Balance",
                unit="₹/day",
                baseline=0.0,
                simulated=-9800.0,
                pct_change=-100.0,
                is_favorable=False
            )
        ]

        return {
            "action_id": action_id,
            "action_title": "Candidate Action 3: Lower Furnace 02 Holding Temperature to 1350°C (UNSAFE CANDIDATE)",
            "machine_id": "furnace_02",
            "machine_name": "Furnace 02 (Holding Furnace 450kW)",
            "status": "SIMULATED_REJECTED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": False,
            "energy_comparison": {
                "current_kwh_day": baseline_kwh,
                "predicted_kwh_day": simulated_kwh,
                "kwh_saved_day": 42.0,
                "pct_change": -6.8
            },
            "cost_comparison": {
                "current_cost_month_inr": round(baseline_kwh * 30 * 8.20, 0),
                "predicted_cost_month_inr": round(simulated_kwh * 30 * 8.20, 0),
                "savings_month_inr": -185000.0, # Negative due to cold-shut scrap
                "pct_change": -6.8
            },
            "co2_comparison": {
                "current_emissions_kg_month": round(baseline_kwh * 30 * 0.716, 0),
                "predicted_emissions_kg_month": round(simulated_kwh * 30 * 0.716, 0),
                "reduction_kg_month": 2600.0,
                "pct_change": -6.8
            },
            "production_comparison": {
                "current_throughput": "24.5 tons/day",
                "predicted_throughput": "23.0 tons/day",
                "change_pct": -6.0,
                "throughput_retained": False
            },
            "quality_comparison": {
                "current_status": "97.4% Pass Rate",
                "predicted_status": "83.2% Pass Rate (Cold-shut scrap surge)",
                "status": "BREACH"
            },
            "risk_level": "High",
            "confidence_pct": 98.0,
            "payback_period_days": 0,
            "production_throughput_retained": False,
            "quality_tolerance_satisfied": False,
            "recommendation_verdict": "REJECTED BY CONSTRAINT GATE (Sub-liquidus iron creates casting misruns)",
            "why_this_action": "Thermodynamic radiation loss is proportional to T^4, so reducing bath temp saves holding kWh, but freezes the pouring stream.",
            "why_not_alternative": "Lowering holding temperature to 1350°C was rejected because the metallurgical specification requires ≥ 1410°C at the pouring nozzle.",
            "metrics": [m.model_dump() for m in metrics]
        }

    # Action 5B: TOD Peak Melting Curtailment Without Buffer (UNSAFE CANDIDATE)
    elif action_id == "action_tod_emergency_curtailment":
        metrics = [
            SimulationComparison(
                metric="Peak Hours kWh Draw (18:00 - 22:00)",
                unit="kWh",
                baseline=420.0,
                simulated=0.0,
                pct_change=-100.0,
                is_favorable=True
            ),
            SimulationComparison(
                metric="Daily Casting Throughput",
                unit="Tons/day",
                baseline=24.5,
                simulated=18.4,
                pct_change=-25.0,
                is_favorable=False
            ),
            SimulationComparison(
                metric="Customer Dispatch Lead Time Delay",
                unit="Hours",
                baseline=0.0,
                simulated=4.0,
                pct_change=100.0,
                is_favorable=False
            )
        ]

        return {
            "action_id": action_id,
            "action_title": "Candidate Action 5B: Peak Shift Melting Curtailment Without Holding Buffer (UNSAFE CANDIDATE)",
            "machine_id": "furnace_01",
            "machine_name": "Furnace 01 Primary Melter",
            "status": "SIMULATED_REJECTED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": False,
            "energy_comparison": {"current_kwh_day": 14350.0, "predicted_kwh_day": 13930.0, "kwh_saved_day": 420.0, "pct_change": -2.9},
            "cost_comparison": {"current_cost_month_inr": 1240000.0, "predicted_cost_month_inr": 1288000.0, "savings_month_inr": -48000.0, "pct_change": 3.9},
            "co2_comparison": {"current_emissions_kg_month": 108116.0, "predicted_emissions_kg_month": 104950.0, "reduction_kg_month": 3166.0, "pct_change": -2.9},
            "production_comparison": {"current_throughput": "24.5 tons/day", "predicted_throughput": "18.4 tons/day", "change_pct": -25.0, "throughput_retained": False},
            "quality_comparison": {"current_status": "97.4% Pass Rate", "predicted_status": "78.9% Pass Rate (Ladle skulling)", "status": "BREACH"},
            "risk_level": "High",
            "confidence_pct": 96.0,
            "payback_period_days": 0,
            "production_throughput_retained": False,
            "quality_tolerance_satisfied": False,
            "recommendation_verdict": "REJECTED BY CONSTRAINT GATE (Causes 25% throughput loss and 4 hr delivery delay)",
            "why_this_action": "Peak power curtailment avoids the ₹10.80/kWh rate, but starving the line collapses daily production output.",
            "why_not_alternative": "Emergency peak shedding without buffer was rejected because it causes +4.0 hrs delivery delay and severe ladle skulling.",
            "metrics": [m.model_dump() for m in metrics]
        }

    # Action 6: Mechanical Overhaul Withheld Due to Missing Sensor
    elif action_id == "action_compressor_bearing_overhaul_unsupported":
        return {
            "action_id": action_id,
            "action_title": "Candidate Action 6: Mechanical Air-End Bearing Overhaul (WITHHELD)",
            "machine_id": "compressor_02",
            "machine_name": "Compressor 02 (Kaeser Screw 75kW)",
            "status": "SIMULATED_WITHHELD",
            "is_verified": False,
            "verification_disclaimer": "DIAGNOSIS WITHHELD — MISSING VIBRATION TELEMETRY",
            "is_production_safe_savings": False,
            "energy_comparison": {"current_kwh_day": 336.0, "predicted_kwh_day": 274.0, "kwh_saved_day": 62.0, "pct_change": -18.5},
            "cost_comparison": {"current_cost_month_inr": 82656.0, "predicted_cost_month_inr": 67456.0, "savings_month_inr": 15200.0, "pct_change": -18.5},
            "co2_comparison": {"current_emissions_kg_month": 7217.0, "predicted_emissions_kg_month": 5887.0, "reduction_kg_month": 1330.0, "pct_change": -18.5},
            "production_comparison": {"current_throughput": "24.5 tons/day", "predicted_throughput": "0.0 tons/day (8 hr outage)", "change_pct": -100.0, "throughput_retained": False},
            "quality_comparison": {"current_status": "Evidence Incomplete", "predicted_status": "Diagnosis Withheld", "status": "WITHHELD"},
            "risk_level": "Medium",
            "confidence_pct": 42.0,
            "payback_period_days": 180,
            "production_throughput_retained": False,
            "quality_tolerance_satisfied": False,
            "recommendation_verdict": "WITHHELD UNDER DATA TRUST PROTOCOL (Install vibration sensor first)",
            "why_this_action": "Elevated power (+19.2%) detected, but mechanical telemetry is missing. The system withholds diagnosis and recommends installing a ₹22k vibration accelerometer before performing teardown.",
            "why_not_alternative": "Action held in 'NEEDS MORE DATA' state to prevent false maintenance actions.",
            "metrics": []
        }

    else:
        # Fallback evaluation
        return {
            "action_id": action_id,
            "action_title": "General Operational Tuning",
            "machine_id": "generic_machine",
            "machine_name": "Target Asset",
            "status": "SIMULATED_NOT_VERIFIED",
            "is_verified": False,
            "verification_disclaimer": "WHAT-IF SIMULATION - NOT YET VERIFIED",
            "is_production_safe_savings": False,
            "energy_comparison": {"current_kwh_day": 100.0, "predicted_kwh_day": 95.0, "kwh_saved_day": 5.0, "pct_change": -5.0},
            "cost_comparison": {"current_cost_month_inr": 10000.0, "predicted_cost_month_inr": 9500.0, "savings_month_inr": 500.0, "pct_change": -5.0},
            "co2_comparison": {"current_emissions_kg_month": 800.0, "predicted_emissions_kg_month": 760.0, "reduction_kg_month": 40.0, "pct_change": -5.0},
            "production_comparison": {"current_throughput": "Nominal", "predicted_throughput": "Nominal", "change_pct": 0.0, "throughput_retained": True},
            "quality_comparison": {"current_status": "Optimal", "predicted_status": "Optimal", "status": "PASS"},
            "risk_level": "Low",
            "confidence_pct": 85.0,
            "payback_period_days": 15,
            "production_throughput_retained": True,
            "quality_tolerance_satisfied": True,
            "recommendation_verdict": "REVIEW REQUIRED",
            "why_this_action": "Generic tuning action.",
            "why_not_alternative": "N/A",
            "metrics": []
        }

def get_decision_scenarios() -> List[Dict[str, Any]]:
    """Returns available demonstration scenarios with decision engine context."""
    return [
        {
            "id": "compressor_waste",
            "name": "Scenario A: Compressor 02 Idle Energy Waste",
            "machine_id": "compressor_02",
            "anomaly_type": "EXCESSIVE_IDLE",
            "description": "Compressor idling unloaded for 3.2 hrs/day consuming 24 kW unloaded power.",
            "key_constraint": "DISA Moulding min pressure ≥ 6.0 bar",
            "safe_action": "Candidate Action 2: 90-sec Auto-Idle Shutdown & Tighten Pressure Band to 6.6 bar",
            "rejected_action": "Candidate Action 1: Lower Shop Header Pressure to 5.2 bar (Stalls Squeeze Cylinders)"
        },
        {
            "id": "furnace_degradation",
            "name": "Scenario B: Furnace 02 Holding Degradation",
            "machine_id": "furnace_02",
            "anomaly_type": "ENERGY_WITHOUT_PRODUCTION",
            "description": "Holding power rose from 45 kW to 78 kW due to refractory thinning; shell temp 115°C.",
            "key_constraint": "Metallurgical fluidity boundary ≥ 1410°C (Cold-shut prevention)",
            "safe_action": "Candidate Action 4: Scheduled Refractory Dry-Vibe Patch & Lid Perimeter Seal Restoration",
            "rejected_action": "Candidate Action 3: Lower Furnace 02 Holding Temperature to 1350°C (Sub-liquidus scrap)"
        },
        {
            "id": "missing_sensor",
            "name": "Scenario C: Missing Vibration Data (Evidence Gap)",
            "machine_id": "compressor_02",
            "anomaly_type": "ENERGY_SPIKE",
            "description": "Compressor power spike (+28.1%) detected, but vibration accelerometer is not installed.",
            "key_constraint": "Trust Protocol Evidence Gate (No unsupported maintenance teardowns)",
            "safe_action": None,
            "status": "NEEDS_MORE_DATA",
            "withheld_action": "Candidate Action 6: Mechanical Air-End Bearing Overhaul (Diagnosis withheld until sensor fitted)"
        },
        {
            "id": "production_scheduling",
            "name": "Scenario D: Peak TOD Tariff Melt Scheduling",
            "machine_id": "furnace_01",
            "anomaly_type": "HIGH_SEC",
            "description": "Exploits BESCOM ₹5.40/kWh night off-peak tariff vs ₹10.80/kWh peak rate.",
            "key_constraint": "Holding buffer capacity ≤ 8.0 tons",
            "safe_action": "Candidate Action 5: Shift Primary Heat Pre-Melting to Night Off-Peak Slot (03:00 - 06:00)",
            "rejected_action": "Candidate Action 5B: Daytime Melting Curtailment Without Buffer (Starves Moulding Line & Delays Dispatch)"
        }
    ]

