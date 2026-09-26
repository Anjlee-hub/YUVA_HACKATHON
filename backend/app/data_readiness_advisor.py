"""
Data Quality, Readiness Engine & Sensor ROI Advisor
Implements:
1. SME Progressive Data Maturity Model (Level 0 to Level 4)
   - Dynamic capabilities, missing data, and next level unlocks
2. Sensor / Data Acquisition ROI Advisor
   - 5 Standard Retrofit Acquisition Options:
     * Tri-axial Vibration Sensor
     * Digital Pressure Sensor
     * Shell Infrared Pyrometer / Temperature Sensor
     * Machine-Level Digital Sub-Meter
     * Optical PLC / Runtime Signal Sensor
   - Transparent scoring formula:
     Priority Score = (Info Value + Opportunity Unlocked + Evidence Gain) / (Capex Index + Payback)
   - Recommends 'NEXT BEST DATA SOURCE'
3. Strict Data Trust & Evidence-Strength Protocol
   - Withholds mechanical diagnosis when vibration sensors are absent

DISCLAIMER:
All sensor prices and ROI values are ILLUSTRATIVE DEMO ASSUMPTIONS.
Do not present them as vendor quotations or real market prices.
"""

from typing import List, Dict, Any, Optional
from .models import (
    DataReadinessOverview, 
    DataConfidenceMetric, 
    SensorROIRecommendation
)
from .simulation import factory_simulator

PROGRESSIVE_LEVELS = [
    {
        "level": 0,
        "name": "Level 0: Utility Bills + Basic Production Data",
        "tagline": "Baseline Energy Accounting",
        "description": "Uses monthly utility electricity bills and manually logged operating hours. Calculates rough monthly SEC.",
        "what_is_available": ["Monthly utility electricity bill (kWh, kVA, Demand charges)", "Monthly dispatch casting tonnage"],
        "what_is_missing": ["Real-time feeder meters", "Machine-level sub-meters", "Operational telemetry", "PLC runtime signals"],
        "currently_possible_intelligence": [
            "Monthly factory-level SEC tracking", 
            "Basic utility tariff peak/off-peak reconciliation"
        ],
        "limitations": [
            "No real-time anomaly alerts", 
            "Cannot pinpoint which machine is wasting energy", 
            "No root-cause evidence"
        ],
        "next_level_unlocks": [
            "Shift-wise SEC tracking", 
            "Real-time peak demand threshold warnings", 
            "Daily regression against production volume"
        ]
    },
    {
        "level": 1,
        "name": "Level 1: Main Energy Meter + Production + Operating Hours",
        "tagline": "Whole-Plant Feeder Telemetry",
        "description": "Digital main feeder smart meter connected with shift-wise production weighbridge and dispatch counts.",
        "what_is_available": ["Digital main feeder meter (Schneider EM6400NG)", "Weighbridge melt heat logs", "Shift operating hours"],
        "what_is_missing": ["Individual furnace / compressor sub-meters", "Physical pressure / temp sensors", "Vibration accelerometers"],
        "currently_possible_intelligence": [
            "Shift-by-shift factory SEC tracking", 
            "Whole-plant peak demand penalties warning", 
            "Daily energy vs production volume regression"
        ],
        "limitations": [
            "Cannot distinguish whether compressor or furnace is causing spike", 
            "No visibility into individual machine idle losses"
        ],
        "next_level_unlocks": [
            "Sub-meter machine energy comparison", 
            "Pinpointing idle unloaded power draw", 
            "Machine-level SEC benchmarking"
        ]
    },
    {
        "level": 2,
        "name": "Level 2: Machine-Level Energy Monitoring",
        "tagline": "Machine-Level SEC Visibility",
        "description": "Retrofit clip-on IoT power meters on Furnace 01, Furnace 02, Compressors, and Pumps.",
        "what_is_available": ["Sub-meters on all 8 main production panels", "Main feeder meter", "Batch tonnage tally"],
        "what_is_missing": ["Continuous pressure transmitters", "Lining thermocouples", "Vibration accelerometers"],
        "currently_possible_intelligence": [
            "Machine energy comparison", 
            "Specific Energy Consumption (SEC) analysis per machine", 
            "Automated energy anomaly detection"
        ],
        "limitations": [
            "Mechanical wear diagnosis NOT reliably possible (withheld by trust protocol)", 
            "Cannot distinguish thermal loss from electrical inefficiencies"
        ],
        "next_level_unlocks": [
            "Vibration-based equipment health analysis", 
            "Stronger root-cause evidence", 
            "Thermal refractory thinning quantification"
        ]
    },
    {
        "level": 3,
        "name": "Level 3: Equipment / Process Telemetry (Temp, Vibration, Pressure, Flow)",
        "tagline": "Operational Digital Twin (Current Factory State)",
        "description": "Thermal thermocouples, discharge pressure transmitters, and selected accelerometers installed across key lines.",
        "what_is_available": [
            "Machine sub-meters (Furnaces, Compressors, Pumps)", 
            "Pneumatic pressure transducer", 
            "Crucible shell & cooling water thermocouples", 
            "Production weighbridge"
        ],
        "what_is_missing": [
            "Compressor 02 vibration accelerometer (in missing sensor scenario)", 
            "Full bi-directional PLC bus integration"
        ],
        "currently_possible_intelligence": [
            "Root-cause decomposition (idle vs pressure vs thermal)", 
            "Production-safe constraint gate evaluation", 
            "IPMVP Option B verified savings"
        ],
        "limitations": [
            "Withholds mechanical diagnosis if vibration sensor is omitted on Compressor 02", 
            "Advisory only — requires human approval for all setpoint changes"
        ],
        "next_level_unlocks": [
            "Bi-directional PLC/SCADA automated recipe tuning", 
            "Real-time dynamic setpoint modulation with closed-loop safety interlocking"
        ]
    },
    {
        "level": 4,
        "name": "Level 4: PLC / SCADA + Process + Quality Integration",
        "tagline": "Advanced Closed-Loop Decision Automation",
        "description": "Full OT gateway integration with machine PLCs, metallography spectrometry, sand properties, and automated advisory.",
        "what_is_available": [
            "Full SCADA / PLC Modbus & Profinet feeds", 
            "Tri-axial vibration on all rotating machinery", 
            "In-line spectrometer molten metal chemistry", 
            "Automated reject tally"
        ],
        "what_is_missing": ["None — full cyber-secure OT layer active"],
        "currently_possible_intelligence": [
            "Predictive metallurgy recipe optimization", 
            "Full mechanical bearing wear diagnosis", 
            "Continuous micro-anomaly prevention"
        ],
        "limitations": [
            "Requires higher capex and ongoing OT cyber-security maintenance"
        ],
        "next_level_unlocks": [
            "Fully automated multi-plant energy grid dispatch"
        ]
    }
]

def get_data_readiness_status() -> DataReadinessOverview:
    """
    Dynamically audits factory sensory data completeness, freshness, and consistency.
    Enforces strict Data Trust rule: withholds unsupported mechanical diagnosis.
    """
    lvl = factory_simulator.data_level
    scenario = factory_simulator.active_scenario
    
    # In missing sensor scenario or lower tiers, vibration is unavailable on key machines
    is_vibration_active = (lvl >= 4) and (scenario != "missing_sensor")
    vib_completeness = 88.0 if is_vibration_active else 0.0
    vib_freshness = 90.0 if is_vibration_active else 0.0
    vib_consistency = 86.0 if is_vibration_active else 0.0
    vib_overall = 88.0 if is_vibration_active else 0.0

    sensors = [
        DataConfidenceMetric(
            sensor_name="Schneider EM6400NG Main Feeder Meter",
            completeness_pct=99.4,
            freshness_pct=99.8,
            consistency_pct=98.5,
            overall_pct=99.2,
            is_available=True,
            note="Continuous 1-second Modbus RS485 digital telemetry"
        ),
        DataConfidenceMetric(
            sensor_name="Machine Sub-meters (Furnaces & Compressors)",
            completeness_pct=97.8,
            freshness_pct=98.2,
            consistency_pct=96.0,
            overall_pct=97.3,
            is_available=lvl >= 2,
            note="IoT CT-clamp meters on 6 main distribution panels"
        ),
        DataConfidenceMetric(
            sensor_name="Production Weighbridge & Batch Counters",
            completeness_pct=95.0,
            freshness_pct=94.5,
            consistency_pct=93.2,
            overall_pct=94.2,
            is_available=lvl >= 1,
            note="Weighed melt heats and good casting tally"
        ),
        DataConfidenceMetric(
            sensor_name="Temperature Sensors (Cooling Water & Coil)",
            completeness_pct=92.1,
            freshness_pct=91.0,
            consistency_pct=89.5,
            overall_pct=90.8,
            is_available=lvl >= 3,
            note="RTD PT100 sensors on cooling loop & shell thermocouples"
        ),
        DataConfidenceMetric(
            sensor_name="Pneumatic Pressure Transmitters (Compressor Room)",
            completeness_pct=88.5,
            freshness_pct=89.0,
            consistency_pct=87.2,
            overall_pct=88.2,
            is_available=lvl >= 3,
            note="4-20mA pressure transducer on main air receiver"
        ),
        DataConfidenceMetric(
            sensor_name="Vibration Accelerometers (IoT Tri-axial)",
            completeness_pct=vib_completeness,
            freshness_pct=vib_freshness,
            consistency_pct=vib_consistency,
            overall_pct=vib_overall,
            is_available=is_vibration_active,
            note="Missing on Compressor 02; Telemetry absent in Missing Sensor scenario"
        ),
        DataConfidenceMetric(
            sensor_name="Maintenance & Breakdowns Digital Log",
            completeness_pct=64.0,
            freshness_pct=62.0,
            consistency_pct=58.0,
            overall_pct=61.3,
            is_available=True,
            note="Shift operator manual mobile app entries"
        )
    ]

    active_scores = [s.overall_pct for s in sensors if s.is_available]
    overall_conf = round(sum(active_scores) / len(active_scores), 1) if active_scores else 50.0

    can_diagnose_mechanical = is_vibration_active
    can_diagnose_thermal = (lvl >= 3)
    withheld_count = 1 if not can_diagnose_mechanical else 0

    curr_lvl_meta = PROGRESSIVE_LEVELS[lvl]

    return DataReadinessOverview(
        overall_confidence_pct=overall_conf,
        current_level=lvl,
        level_name=curr_lvl_meta["name"],
        sensor_metrics=sensors,
        can_diagnose_mechanical=can_diagnose_mechanical,
        can_diagnose_thermal=can_diagnose_thermal,
        withheld_diagnoses_count=withheld_count,
        what_is_available=curr_lvl_meta["what_is_available"],
        what_is_missing=curr_lvl_meta["what_is_missing"],
        currently_possible_intelligence=curr_lvl_meta["currently_possible_intelligence"],
        next_level_unlocks=curr_lvl_meta["next_level_unlocks"]
    )

def get_sensor_roi_recommendations() -> List[SensorROIRecommendation]:
    """
    Ranks potential retrofit IoT sensors for the SME based on the 5 standard acquisition options:
    1. Tri-axial Vibration Sensor
    2. Digital Pressure Sensor
    3. Shell Infrared Pyrometer / Temperature Sensor
    4. Additional Energy Sub-meter
    5. Optical PLC / Runtime Signal Sensor

    Scoring Formula:
    Priority Score = (Info Value [1-10] + Opportunity Score [1-10] + Evidence Gain [%/10]) /
                     ((Capex + Install) / 10000 + Payback Months)
    Transparently recommends 'NEXT BEST DATA SOURCE'.
    """
    scenario = factory_simulator.active_scenario

    candidates = [
        {
            "sensor_id": "roi_c2_vibration",
            "machine_id": "compressor_02",
            "machine_name": "Compressor 02 (Kaeser Screw 75kW)",
            "sensor_type": "Tri-axial Wireless Vibration & Bearing Temperature Sensor (Magnetic Mount)",
            "sensor_category": "Tri-axial Vibration Sensor",
            "information_gain": "Critical",
            "information_value_score": 9.5,
            "opportunity_score": 9.5,
            "estimated_capex_inr": 18500.0,
            "estimated_installation_inr": 3500.0,
            "potential_savings_unlocked_inr_yr": 84000.0,
            "payback_months": 3.1,
            "evidence_improvement_pct": 45.0,
            "unlocked_capabilities": [
                "Eliminates withheld maintenance diagnoses on Compressor 02",
                "Detects bearing degradation before air-end seizure (prevents ₹3.2L replacement)",
                "Differentiates between internal mechanical drag vs external pipe leaks"
            ],
            "why_needed": "Compressor 02 currently has unexplained energy deviations where mechanical diagnosis is withheld due to missing vibration accelerometer."
        },
        {
            "sensor_id": "roi_receiver_pressure",
            "machine_id": "compressor_01",
            "machine_name": "Compressed Air Header & Distribution Ring",
            "sensor_type": "Digital High-Precision Gauge Pressure Transmitter (0-16 bar, 4-20mA)",
            "sensor_category": "Pressure Sensor",
            "information_gain": "High",
            "information_value_score": 7.5,
            "opportunity_score": 7.5,
            "estimated_capex_inr": 14000.0,
            "estimated_installation_inr": 2500.0,
            "potential_savings_unlocked_inr_yr": 68000.0,
            "payback_months": 2.9,
            "evidence_improvement_pct": 30.0,
            "unlocked_capabilities": [
                "Precise pneumatic pressure threshold monitoring for DISA moulding lines",
                "Direct detection of line drop vs compressor unloading",
                "Prevents excessive compressor over-pressurization above 7.0 bar"
            ],
            "why_needed": "Pneumatic lines experience pressure spikes. Digital transmitter verifies pressure stays within safe 6.0-6.8 bar operating window."
        },
        {
            "sensor_id": "roi_furnace_infrared_pyrometer",
            "machine_id": "furnace_02",
            "machine_name": "Furnace 02 (Holding Furnace 450kW)",
            "sensor_type": "Non-Contact Infrared Crucible Shell Surface Pyrometer Array",
            "sensor_category": "Temperature Sensor",
            "information_gain": "High",
            "information_value_score": 8.5,
            "opportunity_score": 9.0,
            "estimated_capex_inr": 34000.0,
            "estimated_installation_inr": 5000.0,
            "potential_savings_unlocked_inr_yr": 112000.0,
            "payback_months": 4.2,
            "evidence_improvement_pct": 38.0,
            "unlocked_capabilities": [
                "Real-time refractory lining degradation hotspot detection",
                "Optimizes dry-vibe patching intervals before thermal radiation escalates",
                "Prevents continuous 30-40 kW radiation heat leakage through thinned shell"
            ],
            "why_needed": "Holding furnace operates 24/7. Continuous shell thermal array warns before surface temperature breaches 85°C safety limit."
        },
        {
            "sensor_id": "roi_submeter_auxiliaries",
            "machine_id": "pump_01",
            "machine_name": "Pumps & Cooling Towers Auxiliary Panel",
            "sensor_type": "IoT 3-Phase Multi-Function Energy Sub-Meter with Split-Core CTs",
            "sensor_category": "Additional Energy Sub-meter",
            "information_gain": "Medium",
            "information_value_score": 7.5,
            "opportunity_score": 7.0,
            "estimated_capex_inr": 16000.0,
            "estimated_installation_inr": 3000.0,
            "potential_savings_unlocked_inr_yr": 48000.0,
            "payback_months": 4.8,
            "evidence_improvement_pct": 25.0,
            "unlocked_capabilities": [
                "Dedicated sub-meter isolation for cooling tower fan modulation",
                "Continuous power factor and harmonic distortion monitoring",
                "Enables IPMVP Option B sub-meter verification on water circuit"
            ],
            "why_needed": "Cooling circuits represent 6-8% of total plant kWh. Non-invasive split-core sub-meter enables zero-downtime retrofit."
        },
        {
            "sensor_id": "roi_plc_runtime_signal",
            "machine_id": "casting_line",
            "machine_name": "DISA Moulding Line & Sand Plant PLC",
            "sensor_type": "Optically Isolated Digital I/O State & Mould Cycle Pulse Collector",
            "sensor_category": "PLC / Runtime Signal",
            "information_gain": "Medium",
            "information_value_score": 7.0,
            "opportunity_score": 7.5,
            "estimated_capex_inr": 12000.0,
            "estimated_installation_inr": 2000.0,
            "potential_savings_unlocked_inr_yr": 42000.0,
            "payback_months": 4.0,
            "evidence_improvement_pct": 22.0,
            "unlocked_capabilities": [
                "Direct correlation of mould cycle rate with compressor pneumatic air consumption",
                "Detects idle standby periods without relying on manual operator logs",
                "Zero risk to PLC code (passive optically isolated tap)"
            ],
            "why_needed": "Correlates air and power consumption directly with machine operational states to eliminate false idle alarms."
        }
    ]

    # Calculate transparent priority score for each candidate
    scored_candidates = []
    for c in candidates:
        tot_cost = c["estimated_capex_inr"] + c["estimated_installation_inr"]
        cost_index = tot_cost / 10000.0 # e.g. 2.2 for 22k
        info_val = c["information_value_score"]
        opp_score = c["opportunity_score"]
        evid_score = c["evidence_improvement_pct"] / 10.0 # e.g. 4.2 for 42%
        
        # Transparent Priority Score
        # Higher numerator (value, opportunity, evidence) / lower denominator (cost index + payback months)
        priority_score = round((info_val + opp_score + evid_score) / (cost_index + c["payback_months"]), 2)
        
        c["priority_score"] = priority_score
        scored_candidates.append(c)

    # Sort descending by priority score
    scored_candidates.sort(key=lambda x: x["priority_score"], reverse=True)

    recommendations = []
    for idx, c in enumerate(scored_candidates):
        is_next = (idx == 0) # Top ranked is recommended NEXT BEST DATA SOURCE
        recommendations.append(SensorROIRecommendation(
            sensor_id=c["sensor_id"],
            machine_id=c["machine_id"],
            machine_name=c["machine_name"],
            sensor_type=c["sensor_type"],
            sensor_category=c["sensor_category"],
            information_gain=c["information_gain"],
            information_value_score=c["information_value_score"],
            estimated_capex_inr=c["estimated_capex_inr"],
            estimated_installation_inr=c["estimated_installation_inr"],
            potential_savings_unlocked_inr_yr=c["potential_savings_unlocked_inr_yr"],
            payback_months=c["payback_months"],
            evidence_improvement_pct=c["evidence_improvement_pct"],
            priority_score=c["priority_score"],
            is_next_best=is_next,
            unlocked_capabilities=c["unlocked_capabilities"],
            why_needed=c["why_needed"],
            recommended_rank=idx + 1,
            illustrative_disclaimer="All sensor prices and ROI values are ILLUSTRATIVE DEMO ASSUMPTIONS."
        ))

    return recommendations
