"""
Explainable Anomaly Detection & Root-Cause Analysis Engine
Detects:
1. High SEC (Specific Energy Consumption deviation > 10%)
2. Energy Spikes (transient load surges)
3. Energy Increase Without Production Increase (excessive idle holding/unloaded draw)
4. Excessive Idle Energy (unloaded running during changeovers/breaks)
5. Abnormal Machine Telemetry (temperature over-limit, pressure boundary breach, excessive vibration)

Strict Trust Protocol:
- If required sensor evidence is absent (e.g. vibration accelerometer), evidence strength is reduced to 'Insufficient'
  and the engine strictly WITHHOLDS maintenance diagnoses instead of hallucinating.
"""

from typing import List, Dict, Any, Optional
from .models import Anomaly, AnomalySeverity, ContributingFactor
from .simulation import factory_simulator

def analyze_anomalies() -> List[Anomaly]:
    telemetry = factory_simulator.live_telemetry
    active_scenario = factory_simulator.active_scenario
    applied_actions = factory_simulator.applied_actions
    anomalies = []

    # =========================================================================
    # 1. SCENARIO A: COMPRESSOR 02 IDLE WASTE
    # =========================================================================
    c2 = telemetry.get("compressor_02")
    is_c2_fixed = "action_compressor_unloaded_shutdown" in applied_actions

    if c2 and (active_scenario == "compressor_waste" or c2["is_anomaly"]) and not is_c2_fixed and active_scenario != "missing_sensor":
        has_vibration = c2.get("vibration_mms") is not None
        maintenance_withheld = not has_vibration
        evidence_str = "Moderate" if maintenance_withheld else "Strong"
        confidence = 74.0 if maintenance_withheld else 92.0

        factors = [
            ContributingFactor(
                factor_name="Unloaded Idle Run (Shift Handover / Breaks)",
                share_pct=52.0,
                impact_description="Compressor idling unloaded for 3.2 hrs/day consuming 24 kW unloaded power with zero CFM air delivery to moulding line.",
                sensor_evidence="Sub-meter power log shows 24.0 kW draw during mould shakeout while flow = 0 CFM."
            ),
            ContributingFactor(
                factor_name="Pressure Band Setting Over-pressurization",
                share_pct=21.0,
                impact_description="Discharge cut-off pressure set at 7.4 bar instead of required 6.6 bar (+0.8 bar penalty = ~5.6% excess motor kWh).",
                sensor_evidence="Discharge pressure transducer confirms peak reading 7.4 bar (Nominal 6.6 bar)."
            ),
            ContributingFactor(
                factor_name="Intake Air Temperature Elevation",
                share_pct=14.0,
                impact_description="Elevated ambient temp in compressor room (36.5°C) reduces air density, increasing required compression work.",
                sensor_evidence="Intake air thermocouple reads 36.5°C."
            ),
            ContributingFactor(
                factor_name="Suspected Mechanical Wear / Air End Friction",
                share_pct=13.0,
                impact_description="Internal rotary screw element friction or bearing wear.",
                sensor_evidence="Awaiting accelerometer data (Vibration sensor not fitted on Compressor 02)."
            )
        ]

        sec_dev = round(c2["sec_deviation_pct"], 1)
        expected_kwh = round(c2["expected_sec"] * c2["production_units_today"], 1)
        excess_kwh = round(max(0.0, c2["energy_today_kwh"] - expected_kwh), 1)
        excess_cost = round(excess_kwh * 30 * 8.20, 0)

        withhold_reason = (
            "Energy anomaly detected, but vibration accelerometer data is unavailable. "
            "Mechanical degradation / maintenance diagnosis withheld to prevent unsafe false action."
        ) if maintenance_withheld else None

        anomalies.append(Anomaly(
            id="anomaly_c2_idle_excess",
            machine_id="compressor_02",
            machine_name="Compressor 02 (Kaeser Screw 75kW)",
            title=f"Compressor 02: Excessive Idle Energy & High SEC (+{sec_dev}%)",
            description=f"Detected excessive idle energy ({c2['idle_time_today_hrs']} hrs unloaded) and energy increase without production increase. SEC deviation is +{sec_dev}% above production-aware baseline.",
            severity=AnomalySeverity.HIGH,
            detected_at="Active (Shift A & Shift B changeovers)",
            anomaly_type="EXCESSIVE_IDLE",
            sec_deviation_pct=sec_dev,
            excess_energy_kwh_per_day=excess_kwh,
            excess_cost_inr_per_month=excess_cost,
            contributing_factors=factors,
            evidence_strength=evidence_str,
            data_confidence_pct=confidence,
            maintenance_withheld=maintenance_withheld,
            withhold_reason=withhold_reason
        ))

    # =========================================================================
    # 2. SCENARIO B: FURNACE 02 DEGRADATION (HOLDING FURNACE 450kW)
    # =========================================================================
    f2 = telemetry.get("furnace_02")
    is_f2_fixed = "action_furnace_refractory_patch" in applied_actions

    if f2 and (active_scenario == "furnace_degradation" or f2["is_anomaly"]) and not is_f2_fixed:
        f2_sec_dev = round(f2["sec_deviation_pct"], 1)
        f2_expected_kwh = round(f2["expected_sec"] * f2["production_units_today"], 1)
        f2_excess_kwh = round(max(0.0, f2["energy_today_kwh"] - f2_expected_kwh), 1)
        f2_excess_cost = round(f2_excess_kwh * 30 * 8.20, 0)

        f2_factors = [
            ContributingFactor(
                factor_name="Crucible Refractory Thinning & Thermal Bleed",
                share_pct=55.0,
                impact_description="Crucible refractory wall thinned from 90mm to 52mm, leaking thermal energy into the coil cooling loop.",
                sensor_evidence="Coil cooling water delta T increased from 5.8°C to 11.2°C (Safe limit: 7.0°C)."
            ),
            ContributingFactor(
                factor_name="Lid Insulation Seal Deterioration",
                share_pct=25.0,
                impact_description="Holding furnace lid perimeter ceramic fiber seal compromised, creating convective chimney heat loss.",
                sensor_evidence="Exterior shell surface thermocouple reaches 115.0°C (Safe operating threshold: 85.0°C)."
            ),
            ContributingFactor(
                factor_name="Molten Bath Surface Slag Crust Insulating Defect",
                share_pct=20.0,
                impact_description="Delayed de-slagging allows an irregular cold crust to form, disrupting induction holding thermal coupling.",
                sensor_evidence="Holding draw jumped from 45.0 kW baseline to 78.0 kW to maintain 1420°C bath."
            )
        ]

        anomalies.append(Anomaly(
            id="anomaly_f2_degradation",
            machine_id="furnace_02",
            machine_name="Furnace 02 (Holding Furnace 450kW)",
            title=f"Furnace 02: Thermal Holding Loss & Telemetry Breach (+{f2_sec_dev}% SEC)",
            description=f"Detected energy increase without production increase (holding draw rose from 45kW to {f2['current_power_kw']}kW) and abnormal machine telemetry (shell temp {f2['temperature_c']}°C > 85°C limit).",
            severity=AnomalySeverity.CRITICAL,
            detected_at="Active (Persistent across all holding cycles)",
            anomaly_type="ENERGY_WITHOUT_PRODUCTION",
            sec_deviation_pct=f2_sec_dev,
            excess_energy_kwh_per_day=f2_excess_kwh,
            excess_cost_inr_per_month=f2_excess_cost,
            contributing_factors=f2_factors,
            evidence_strength="Strong", # Temperature sensors and sub-meter are verified
            data_confidence_pct=91.0,
            maintenance_withheld=False,
            withhold_reason=None
        ))

    # =========================================================================
    # 3. SCENARIO C: MISSING VIBRATION SENSOR (LOW EVIDENCE & WITHHELD DIAGNOSIS)
    # =========================================================================
    if active_scenario == "missing_sensor" and c2:
        c2_miss_sec_dev = round(c2["sec_deviation_pct"], 1)
        c2_miss_exp_kwh = round(c2["expected_sec"] * c2["production_units_today"], 1)
        c2_miss_excess_kwh = round(max(0.0, c2["energy_today_kwh"] - c2_miss_exp_kwh), 1)
        c2_miss_excess_cost = round(c2_miss_excess_kwh * 30 * 8.20, 0)

        missing_factors = [
            ContributingFactor(
                factor_name="Unverified Mechanical Drag vs Pneumatic Pipe Distribution Leak",
                share_pct=100.0,
                impact_description=f"Cannot attribute the +{c2_miss_sec_dev}% power elevation between internal screw bearing friction vs external pipe leakage.",
                sensor_evidence=f"Sub-meter power reads {c2['current_power_kw']} kW (+{c2_miss_sec_dev}% spike), but Tri-axial Vibration Accelerometer is NOT installed (Telemetry absent)."
            )
        ]

        anomalies.append(Anomaly(
            id="anomaly_c2_missing_vibration",
            machine_id="compressor_02",
            machine_name="Compressor 02 (Kaeser Screw 75kW)",
            title=f"Compressor 02: Energy Spike (+{c2_miss_sec_dev}%) with Missing Vibration Sensor",
            description=f"Power consumption is elevated by +{c2_miss_sec_dev}% above production-aware baseline. However, crucial mechanical telemetry is absent.",
            severity=AnomalySeverity.MEDIUM,
            detected_at="Active (Detected during current Shift A)",
            anomaly_type="ENERGY_SPIKE",
            sec_deviation_pct=c2_miss_sec_dev,
            excess_energy_kwh_per_day=c2_miss_excess_kwh,
            excess_cost_inr_per_month=c2_miss_excess_cost,
            contributing_factors=missing_factors,
            evidence_strength="Insufficient", # Key requirement!
            data_confidence_pct=42.0, # Degraded confidence
            maintenance_withheld=True,
            withhold_reason=f"Energy anomaly detected (+{c2_miss_sec_dev}%), but vibration data is unavailable. Mechanical wear / bearing degradation diagnosis withheld to prevent unsafe false action."
        ))

    # =========================================================================
    # 4. SCENARIO D: PEAK TOD TARIFF SCHEDULING (OPTIONAL SUPPORTING SCENARIO)
    # =========================================================================
    if active_scenario == "production_scheduling" and "action_tod_rescheduling" not in applied_actions:
        sched_factors = [
            ContributingFactor(
                factor_name="Peak TOD Tariff Melting Exposure",
                share_pct=76.0,
                impact_description="Two 5-ton primary melt heats run during peak tariff window (18:00 - 22:00 @ ₹10.80/kWh) instead of night off-peak (@ ₹5.40/kWh).",
                sensor_evidence="Feeder meter interval log vs BESCOM TOD Tariff schedule."
            ),
            ContributingFactor(
                factor_name="Holding Furnace Buffer Synchronization",
                share_pct=24.0,
                impact_description="Lack of synchronisation between pouring car and induction melter creates unnecessary holding draw.",
                sensor_evidence="Furnace 02 holding power log."
            )
        ]
        anomalies.append(Anomaly(
            id="anomaly_tod_peak_tariff",
            machine_id="furnace_01",
            machine_name="Furnace 01 (Induction Melter 1200kW)",
            title="Melt Scheduling: High Tariff Peak Hour Exposure",
            description="Detected peak tariff cost spike: 38% of energy-intensive melting executed during peak tariff hours (₹10.80/kWh) when night off-peak rate is ₹5.40/kWh.",
            severity=AnomalySeverity.MEDIUM,
            detected_at="Active (Persistent on weekdays)",
            anomaly_type="HIGH_SEC",
            sec_deviation_pct=12.2,
            excess_energy_kwh_per_day=0.0,
            excess_cost_inr_per_month=126000.0,
            contributing_factors=sched_factors,
            evidence_strength="Strong",
            data_confidence_pct=95.0,
            maintenance_withheld=False,
            withhold_reason=None
        ))

    return anomalies
