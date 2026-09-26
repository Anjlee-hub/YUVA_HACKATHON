"""
Deterministic Factory Operational Simulation Engine
Models Shakti Foundry — Plant 01 (Peenya, Bengaluru, India)

Supported Scenarios:
1. "compressor_waste": Compressor 02 idle waste (unloaded run during changeovers)
2. "furnace_degradation": Furnace 02 degradation (holding furnace refractory thinning & thermal radiation loss)
3. "missing_sensor": Missing vibration sensor on Compressor 02 / Pump 01 with withheld diagnosis
4. "production_scheduling": Melt rescheduling from peak TOD tariff to off-peak night rate
5. "normal": Optimal baseline operation
"""

import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .baseline_engine import calculate_expected_energy, evaluate_sec_deviation

GRID_CO2_FACTOR_KG_PER_KWH = 0.716

def get_electricity_tariff(hour: int) -> float:
    # BESCOM Industrial TOD tariff structure
    if (6 <= hour < 10) or (18 <= hour < 22):
        return 10.80 # Peak TOD
    elif 22 <= hour or hour < 6:
        return 5.40 # Off-peak TOD incentive
    else:
        return 7.60 # Normal daytime

MACHINES_METADATA = [
    {
        "id": "furnace_01",
        "name": "Furnace 01 (Induction Melter 1200kW)",
        "category": "Primary Melting",
        "rated_power_kw": 1200.0,
        "available_sensors": ["Main Feeder Power Meter", "Coil Cooling Temp", "Lining Thermocouple", "Water Flow Meter"],
        "missing_sensors": ["Acoustic Bath Slag Monitor"]
    },
    {
        "id": "furnace_02",
        "name": "Furnace 02 (Holding Furnace 450kW)",
        "category": "Molten Metal Holding",
        "rated_power_kw": 450.0,
        "available_sensors": ["Sub-meter Power", "Bath Pyrometer", "Cooling Water Delta T", "Shell Thermocouple"],
        "missing_sensors": ["Continuous Thermal Imaging Scanner"]
    },
    {
        "id": "compressor_01",
        "name": "Compressor 01 (Atlas Copco Screw 110kW)",
        "category": "Base Compressed Air",
        "rated_power_kw": 110.0,
        "available_sensors": ["Sub-meter Power", "Air Discharge Pressure", "Dew Point Sensor", "Motor Temp"],
        "missing_sensors": ["Ultrasonic Leakage Matrix"]
    },
    {
        "id": "compressor_02",
        "name": "Compressor 02 (Kaeser Screw 75kW)",
        "category": "Modulating Trim Air",
        "rated_power_kw": 75.0,
        "available_sensors": ["Sub-meter Power", "Discharge Pressure Transducer"],
        "missing_sensors": ["Tri-axial Vibration Accelerometer", "Mass Flow Meter"] # Intentionally missing!
    },
    {
        "id": "pump_01",
        "name": "Pump 01 (Induction Cooling Loop 45kW)",
        "category": "Cooling Circulation",
        "rated_power_kw": 45.0,
        "available_sensors": ["Sub-meter Power", "Inlet Temp", "Outlet Temp"],
        "missing_sensors": ["Ultrasonic Flow Meter", "Differential Pressure Sensor"]
    },
    {
        "id": "cooling_system",
        "name": "Cooling Tower & Fans (30kW)",
        "category": "Heat Rejection",
        "rated_power_kw": 30.0,
        "available_sensors": ["Sub-meter Power", "Sump Water Temp", "Ambient Humidity"],
        "missing_sensors": ["Wet-Bulb Auto-calibrator"]
    },
    {
        "id": "casting_line",
        "name": "Casting Line (DISA Moulding & Sand 160kW)",
        "category": "Moulding & Pouring",
        "rated_power_kw": 160.0,
        "available_sensors": ["Sub-meter Power", "Hydraulic Pressure", "Mould Counter", "Sand Temp"],
        "missing_sensors": []
    },
    {
        "id": "finishing_line",
        "name": "Finishing Line (Shot Blast & Fettling 90kW)",
        "category": "Finishing & Grinding",
        "rated_power_kw": 90.0,
        "available_sensors": ["Sub-meter Power", "Dust Collector DP", "Vibration Sensor"],
        "missing_sensors": []
    }
]

class FactorySimulator:
    def __init__(self):
        self.active_scenario = "normal"
        self.applied_actions = set()
        self.data_level = 3 # Levels 0 to 4
        self.live_telemetry = {}
        self.generate_initial_state()

    def set_scenario(self, scenario_name: str):
        self.active_scenario = scenario_name
        self.generate_initial_state()

    def set_data_level(self, level: int):
        self.data_level = level
        self.generate_initial_state()

    def apply_action(self, action_id: str):
        self.applied_actions.add(action_id)
        self.generate_initial_state()

    def reset_actions(self):
        self.applied_actions.clear()
        self.generate_initial_state()

    def generate_initial_state(self):
        """
        Generates deterministic operational state reflecting the active scenario and applied actions.
        Produces consistent, demo-friendly results for reproducible evaluation.
        """
        base_production = 24.5 # Tons per day of good ductile & grey iron castings
        telemetry = {}

        is_compressor_action_applied = "action_compressor_unloaded_shutdown" in self.applied_actions
        is_furnace_action_applied = "action_furnace_refractory_patch" in self.applied_actions
        is_scheduling_applied = "action_tod_rescheduling" in self.applied_actions

        for meta in MACHINES_METADATA:
            m_id = meta["id"]
            rated = meta["rated_power_kw"]
            
            # Default deterministic baseline state
            runtime_hrs = 7.5
            idle_hrs = 0.5
            power_kw = rated * 0.72
            temp_c = 42.0
            vib_mms = 1.8
            pressure_bar = 6.8
            prod_tons = base_production
            is_anomaly = False
            health = 96.0

            # -------------------------------------------------------------
            # SCENARIO 1: COMPRESSOR 02 IDLE WASTE
            # -------------------------------------------------------------
            if m_id == "compressor_02":
                if self.active_scenario == "compressor_waste" and not is_compressor_action_applied:
                    # In idle waste: compressor stays unloaded during changeovers (3.2 hrs idle!), consuming 24 kW while doing 0 work
                    idle_hrs = 3.2
                    runtime_hrs = 4.8
                    power_kw = 54.0 # High average because of unloaded draw
                    energy_kwh = (power_kw * 4.8) + (24.0 * idle_hrs) # 259.2 + 76.8 = 336 kWh
                    pressure_bar = 7.4 # Abnormal over-pressurization
                    temp_c = 48.0
                    vib_mms = None # Missing vibration sensor on Compressor 02!
                    health = 68.0
                    is_anomaly = True
                elif is_compressor_action_applied:
                    # After safe auto-idle shutdown fix applied!
                    idle_hrs = 0.4
                    runtime_hrs = 5.2
                    power_kw = 44.0
                    energy_kwh = (power_kw * 5.2) + (5.0 * idle_hrs) # ~230.8 kWh
                    pressure_bar = 6.6
                    temp_c = 41.5
                    vib_mms = None
                    health = 94.0
                    is_anomaly = False
                elif self.active_scenario == "missing_sensor":
                    # Missing sensor scenario: power is elevated +19.2%, vibration missing
                    idle_hrs = 2.1
                    runtime_hrs = 5.5
                    power_kw = 51.0
                    energy_kwh = (power_kw * 5.5) + (20.0 * idle_hrs)
                    pressure_bar = 7.1
                    temp_c = 45.0
                    vib_mms = None # Crucial: None!
                    health = 74.0
                    is_anomaly = True
                else:
                    # Normal Compressor 02
                    idle_hrs = 1.0
                    runtime_hrs = 6.2
                    power_kw = 46.0
                    energy_kwh = (power_kw * 6.2) + (16.0 * idle_hrs)
                    pressure_bar = 6.6
                    temp_c = 41.0
                    vib_mms = None
                    health = 95.0
                    is_anomaly = False

                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            # -------------------------------------------------------------
            # SCENARIO 2: FURNACE 02 DEGRADATION (HOLDING FURNACE)
            # -------------------------------------------------------------
            elif m_id == "furnace_02":
                if self.active_scenario == "furnace_degradation" and not is_furnace_action_applied:
                    # Holding furnace lining thinning causes thermal radiation loss; holding power jumps from 45 kW to 78 kW
                    runtime_hrs = 8.0
                    idle_hrs = 2.5
                    power_kw = 78.0 # Normal holding power is 45 kW -> +73% idle holding power!
                    energy_kwh = (power_kw * runtime_hrs) # 624 kWh
                    temp_c = 115.0 # Shell surface temperature spikes to 115C (limit 85C)!
                    vib_mms = 1.2
                    pressure_bar = None
                    health = 58.0
                    is_anomaly = True
                elif is_furnace_action_applied:
                    # After refractory dry-vibe patch & lid seal applied!
                    runtime_hrs = 7.8
                    idle_hrs = 0.8
                    power_kw = 46.0
                    energy_kwh = (power_kw * runtime_hrs)
                    temp_c = 72.0
                    vib_mms = 1.1
                    pressure_bar = None
                    health = 95.0
                    is_anomaly = False
                else:
                    # Normal Furnace 02
                    runtime_hrs = 7.6
                    idle_hrs = 0.8
                    power_kw = 48.0
                    energy_kwh = (power_kw * runtime_hrs)
                    temp_c = 68.0
                    vib_mms = 1.1
                    pressure_bar = None
                    health = 96.0
                    is_anomaly = False

                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            # -------------------------------------------------------------
            # FURNACE 01 (PRIMARY INDUCTION MELTER)
            # -------------------------------------------------------------
            elif m_id == "furnace_01":
                runtime_hrs = 7.8
                idle_hrs = 0.8
                power_kw = 995.0
                energy_kwh = 14350.0 # ~585 kWh/ton for Grey Iron FG 260
                temp_c = 1425.0 # Bath tapping temperature
                vib_mms = 1.9
                pressure_bar = None
                health = 95.0
                is_anomaly = False

                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            # -------------------------------------------------------------
            # OTHER AUXILIARIES (Compressor 01, Pump 01, Cooling, Lines)
            # -------------------------------------------------------------
            elif m_id == "compressor_01":
                runtime_hrs = 7.6
                idle_hrs = 0.4
                power_kw = 92.0
                energy_kwh = (power_kw * runtime_hrs) + (22.0 * idle_hrs)
                pressure_bar = 7.0
                vib_mms = 2.1
                temp_c = 52.0
                health = 95.0
                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            elif m_id == "pump_01":
                runtime_hrs = 7.8
                idle_hrs = 0.2
                power_kw = 36.0
                energy_kwh = (power_kw * runtime_hrs) + (5.0 * idle_hrs)
                temp_c = 34.0
                vib_mms = 1.8
                pressure_bar = 2.8
                health = 96.0
                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            elif m_id == "cooling_system":
                runtime_hrs = 7.8
                idle_hrs = 0.2
                power_kw = 24.0
                energy_kwh = (power_kw * runtime_hrs) + (6.0 * idle_hrs)
                temp_c = 29.5
                vib_mms = 1.4
                pressure_bar = None
                health = 95.0
                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            elif m_id == "casting_line":
                runtime_hrs = 7.2
                idle_hrs = 0.8
                power_kw = 135.0
                energy_kwh = (power_kw * runtime_hrs)
                temp_c = 38.0
                vib_mms = 2.4
                pressure_bar = 6.4
                health = 94.0
                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            else: # finishing_line
                runtime_hrs = 6.8
                idle_hrs = 1.2
                power_kw = 78.0
                energy_kwh = (power_kw * runtime_hrs)
                temp_c = 32.0
                vib_mms = 2.6
                pressure_bar = 6.2
                health = 94.0
                expected_dict = calculate_expected_energy(m_id, prod_tons)
                dev = evaluate_sec_deviation(energy_kwh, expected_dict["expected_kwh"], prod_tons)

            # Progressive Data Level Sensory Gate
            if self.data_level < 3:
                # Sensors like vibration, temp not yet installed on lower levels
                if self.data_level in [0, 1]:
                    vib_mms = None
                    temp_c = None
                    pressure_bar = None
                elif self.data_level == 2:
                    vib_mms = None

            telemetry[m_id] = {
                "id": m_id,
                "name": meta["name"],
                "category": meta["category"],
                "rated_power_kw": rated,
                "current_power_kw": round(power_kw, 1),
                "energy_today_kwh": round(energy_kwh, 1),
                "runtime_today_hrs": round(runtime_hrs, 1),
                "idle_time_today_hrs": round(idle_hrs, 1),
                "temperature_c": round(temp_c, 1) if temp_c is not None else None,
                "vibration_mms": round(vib_mms, 2) if vib_mms is not None else None,
                "pressure_bar": round(pressure_bar, 1) if pressure_bar is not None else None,
                "production_units_today": prod_tons,
                "actual_sec": dev["actual_sec"],
                "expected_sec": dev["expected_sec"],
                "sec_deviation_pct": dev["dev_pct"],
                "health_score": round(health, 1),
                "status": "ANOMALOUS" if is_anomaly else "OPTIMAL",
                "sensors_active": meta["available_sensors"],
                "sensors_missing": meta["missing_sensors"],
                "is_anomaly": is_anomaly
            }

        self.live_telemetry = telemetry

    def get_factory_summary(self) -> Dict[str, Any]:
        self.generate_initial_state()
        tot_power = sum(m["current_power_kw"] for m in self.live_telemetry.values())
        tot_energy = sum(m["energy_today_kwh"] for m in self.live_telemetry.values())
        tot_prod = 24.5 # Tons of good casting output
        avg_sec = tot_energy / tot_prod
        expected_tot_sec = 695.0 # Baseline benchmark for medium ductile/grey iron foundry
        sec_dev_pct = round(((avg_sec - expected_tot_sec) / expected_tot_sec) * 100.0, 1)
        
        # Calculate cost based on TOD tariff blend (~₹8.20/kWh avg)
        avg_tariff = 8.20
        if "action_tod_rescheduling" in self.applied_actions:
            avg_tariff = 6.85 # Shifted melting to off-peak night
        cost_today = tot_energy * avg_tariff
        co2_today = tot_energy * GRID_CO2_FACTOR_KG_PER_KWH

        active_anomalies = [m for m in self.live_telemetry.values() if m["is_anomaly"]]

        # Verified savings accumulated
        verified_inr_month = 0.0
        if "action_compressor_unloaded_shutdown" in self.applied_actions:
            verified_inr_month += 38400.0
        if "action_furnace_refractory_patch" in self.applied_actions:
            verified_inr_month += 72000.0 # Furnace 02 holding refractory savings
        if "action_tod_rescheduling" in self.applied_actions:
            verified_inr_month += 126000.0

        return {
            "factory_name": "Shakti Foundry — Plant 01",
            "location": "Peenya Industrial Area, Bengaluru, India",
            "industry": "Foundry & Casting (Ferrous / Ductile Iron)",
            "production_unit": "Metric Tons (Good Castings)",
            "total_power_kw": round(tot_power, 1),
            "total_energy_today_kwh": round(tot_energy, 1),
            "factory_sec": round(avg_sec, 1),
            "factory_sec_baseline": expected_tot_sec,
            "sec_deviation_pct": sec_dev_pct,
            "energy_cost_today_inr": round(cost_today, 0),
            "co2_emissions_today_kg": round(co2_today, 1),
            "production_today_units": tot_prod,
            "quality_pass_rate_pct": 97.4,
            "active_anomalies_count": len(active_anomalies),
            "verified_savings_monthly_inr": verified_inr_month,
            "data_confidence_pct": 88.0 if self.data_level >= 3 else (72.0 if self.data_level == 2 else 54.0),
            "current_intelligence_level": self.data_level,
            "active_scenario": self.active_scenario,
            "applied_actions": list(self.applied_actions)
        }

    def generate_30day_history(self) -> List[Dict[str, Any]]:
        """Generates deterministic 30 days of hourly energy and SEC data with clear injection of anomalies."""
        records = []
        base_time = datetime.now() - timedelta(days=30)

        for day in range(30):
            current_day_time = base_time + timedelta(days=day)
            is_anomaly_day = (day >= 24) # Anomaly developed in last 6 days
            
            for hour in range(24):
                ts = current_day_time + timedelta(hours=hour)
                tariff = get_electricity_tariff(hour)
                
                # Foundry production cycle (2 shifts: 06:00 to 22:00, maintenance 22:00 to 06:00)
                is_prod_shift = 6 <= hour < 22
                prod_tons_hr = 1.5 if is_prod_shift else 0.2
                
                # Deterministic base energy calculation
                base_kwh = prod_tons_hr * 620.0 + (30.0 if is_prod_shift else 15.0)
                
                # Anomaly injection for Compressor 02 or Furnace 02
                if is_anomaly_day:
                    if self.active_scenario == "compressor_waste" and is_prod_shift:
                        base_kwh += 35.0 # idle compressor energy waste
                    elif self.active_scenario == "furnace_degradation":
                        base_kwh += 42.0 # Furnace 02 holding thermal heat leakage
                
                sec = base_kwh / max(0.1, prod_tons_hr)
                expected_sec = 690.0
                
                records.append({
                    "timestamp": ts.strftime("%Y-%m-%d %H:%M"),
                    "date": ts.strftime("%Y-%m-%d"),
                    "hour": hour,
                    "production_tons": round(prod_tons_hr, 2),
                    "energy_kwh": round(base_kwh, 1),
                    "sec": round(sec, 1),
                    "expected_sec": expected_sec,
                    "sec_deviation_pct": round(((sec - expected_sec) / expected_sec) * 100.0, 1),
                    "cost_inr": round(base_kwh * tariff, 1),
                    "co2_kg": round(base_kwh * GRID_CO2_FACTOR_KG_PER_KWH, 1),
                    "is_simulated": True
                })
        return records

factory_simulator = FactorySimulator()
