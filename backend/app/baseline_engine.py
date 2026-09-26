"""
Production-Aware Energy & Specific Energy Consumption (SEC) Baseline Engine
Designed for Indian SME Manufacturing (Foundry / Metal Casting Reference)

SEC = Energy Consumption (kWh) / Good Production Output (Tons)

Governing Principles:
1. Never compares energy only with yesterday.
2. Production-aware expected energy baseline dynamically models:
   - production quantity (tons of good castings)
   - product type (Grey Iron FG 260, SG/Ductile Iron EN-GJS-500, Alloy Steel)
   - machine (Induction Melter, Holding Furnace, Screw Compressors, Pumps, Moulding line)
   - shift (Shift A Morning, Shift B Evening Peak, Night Shift Off-Peak)
   - operating conditions (Ambient temp, cold start penalty, holding buffer state)
"""

from typing import Dict, Any, Optional
from .ml_baseline import sec_ml_engine

MACHINE_BASELINES = {
    "furnace_01": {
        "name": "Furnace 01 (Induction Melter 1200kW)",
        "rated_power_kw": 1200.0,
        "base_idle_power_kw": 85.0, # Coil excitation & thermal holding loss
        "specific_kwh_per_ton": {
            "Grey Iron (FG 260)": 570.0,
            "SG / Ductile Iron (EN-GJS-500)": 630.0,
            "Alloy Steel Castings": 680.0
        },
        "shift_adjustment": {
            "Shift A (06:00-14:00)": 1.0,
            "Shift B (14:00-22:00)": 1.02, # Higher ambient & grid voltage fluctuation
            "Night Shift (22:00-06:00)": 0.98 # Favorable coil cooling heat rejection
        },
        "cold_start_penalty_kwh": 350.0,
        "temp_threshold_c": 1450.0,
        "cooling_water_delta_limit_c": 8.5
    },
    "furnace_02": {
        "name": "Furnace 02 (Holding Furnace 450kW)",
        "rated_power_kw": 450.0,
        "base_idle_power_kw": 45.0, # Standby holding power when refractory lining is intact
        "specific_kwh_per_ton": {
            "Grey Iron (FG 260)": 5.1, # Thermal maintenance per ton of held metal
            "SG / Ductile Iron (EN-GJS-500)": 6.2,
            "Alloy Steel Castings": 7.5
        },
        "shift_adjustment": {
            "Shift A (06:00-14:00)": 1.0,
            "Shift B (14:00-22:00)": 1.0,
            "Night Shift (22:00-06:00)": 0.99
        },
        "cold_start_penalty_kwh": 60.0,
        "temp_threshold_c": 1430.0,
        "max_shell_temp_c": 85.0, # Crucible exterior shell limit
        "cooling_water_delta_limit_c": 7.0
    },
    "compressor_01": {
        "name": "Compressor 01 (Atlas Copco Screw 110kW)",
        "rated_power_kw": 110.0,
        "base_idle_power_kw": 22.0, # Unloaded power ~20% of rated
        "loaded_power_kw": 98.0,
        "specific_kwh_per_ton": 22.0, # Base pneumatics per ton of finished casting
        "nominal_pressure_bar": 6.8,
        "max_vibration_mms": 4.5
    },
    "compressor_02": {
        "name": "Compressor 02 (Kaeser Screw 75kW)",
        "rated_power_kw": 75.0,
        "base_idle_power_kw": 12.0, # Unloaded standby baseline
        "loaded_power_kw": 70.0,
        "specific_kwh_per_ton": 9.0, # Trim air allowance
        "nominal_pressure_bar": 6.6,
        "max_vibration_mms": 4.5
    },
    "pump_01": {
        "name": "Pump 01 (Induction Cooling Loop 45kW)",
        "rated_power_kw": 45.0,
        "base_idle_power_kw": 5.0,
        "loaded_power_kw": 38.0,
        "specific_kwh_per_ton": 14.5,
        "max_temp_c": 45.0,
        "max_vibration_mms": 4.0
    },
    "cooling_system": {
        "name": "Cooling Tower & Fans (30kW)",
        "rated_power_kw": 30.0,
        "base_idle_power_kw": 6.0,
        "loaded_power_kw": 26.0,
        "ambient_temp_coeff": 0.45, # Additional kWh/degC when ambient > 30C
        "specific_kwh_per_ton": 11.0
    },
    "casting_line": {
        "name": "Casting Line (DISA Moulding & Sand 160kW)",
        "rated_power_kw": 160.0,
        "base_idle_power_kw": 28.0,
        "loaded_power_kw": 140.0,
        "specific_kwh_per_ton": 42.0,
        "min_air_pressure_bar": 6.0
    },
    "finishing_line": {
        "name": "Finishing Line (Shot Blast & Fettling 90kW)",
        "rated_power_kw": 90.0,
        "base_idle_power_kw": 14.0,
        "loaded_power_kw": 82.0,
        "specific_kwh_per_ton": 31.0,
        "min_air_pressure_bar": 5.8
    }
}

def calculate_expected_energy(
    machine_id: str,
    production_tons: float,
    product_type: str = "Grey Iron (FG 260)",
    shift: str = "Shift A (06:00-14:00)",
    ambient_temp_c: float = 28.5,
    is_cold_start: bool = False,
    runtime_hrs: float = 8.0,
    operating_condition: str = "Normal",
    use_ml: bool = False
) -> Dict[str, Any]:
    """
    Computes production-aware expected energy (kWh) and expected SEC (kWh/ton).
    When use_ml=True and machine_id == 'furnace_01', uses the trained Scikit-Learn
    Ridge Regression ML Pipeline. Otherwise uses the thermodynamic physics baseline.
    Strictly deterministic: identical inputs yield identical baselines.
    """
    if use_ml and machine_id == "furnace_01":
        return sec_ml_engine.predict_expected_energy(
            production_tons=production_tons,
            product_type=product_type,
            shift=shift,
            ambient_temp_c=ambient_temp_c,
            is_cold_start=is_cold_start,
            runtime_hrs=runtime_hrs
        )

    params = MACHINE_BASELINES.get(machine_id)
    if not params:
        default_sec = 45.0
        exp_kwh = max(10.0, production_tons * default_sec)
        return {
            "expected_kwh": round(exp_kwh, 2),
            "expected_sec": round(exp_kwh / max(0.1, production_tons), 2),
            "methodology": "Linear Fallback Baseline"
        }

    # 1. Primary Melting / Holding Furnaces
    if machine_id in ["furnace_01", "furnace_02"]:
        product_sec = params["specific_kwh_per_ton"].get(product_type, 580.0)
        shift_mult = params["shift_adjustment"].get(shift, 1.0)
        cold_start = params["cold_start_penalty_kwh"] if is_cold_start else 0.0
        
        # Idle thermal holding overhead: depends on runtime minus active melt cycle
        active_melt_hrs = min(runtime_hrs, production_tons * (0.32 if machine_id == "furnace_01" else 0.15))
        idle_holding_hrs = max(0.2, runtime_hrs - active_melt_hrs)
        idle_overhead = params["base_idle_power_kw"] * idle_holding_hrs

        # Ambient weather correction (minor heat loss variance)
        temp_delta = max(0.0, ambient_temp_c - 28.0)
        weather_correction = temp_delta * (1.2 if machine_id == "furnace_01" else 0.6)

        expected_kwh = (production_tons * product_sec * shift_mult) + cold_start + idle_overhead + weather_correction
        expected_sec = expected_kwh / max(0.1, production_tons)

        return {
            "expected_kwh": round(expected_kwh, 2),
            "expected_sec": round(expected_sec, 2),
            "methodology": "Production-Aware Multi-variable Thermodynamic Baseline",
            "components": {
                "process_kwh": round(production_tons * product_sec * shift_mult, 2),
                "idle_holding_kwh": round(idle_overhead, 2),
                "cold_start_kwh": cold_start,
                "weather_overhead_kwh": round(weather_correction, 2)
            }
        }

    # 2. Cooling Tower & Fans
    elif machine_id == "cooling_system":
        temp_delta = max(0.0, ambient_temp_c - 28.0)
        weather_penalty = temp_delta * params["ambient_temp_coeff"] * runtime_hrs
        process_kwh = production_tons * params["specific_kwh_per_ton"]
        idle_kwh = params["base_idle_power_kw"] * max(0.5, runtime_hrs - (production_tons * 0.25))

        expected_kwh = process_kwh + idle_kwh + weather_penalty
        expected_sec = expected_kwh / max(0.1, production_tons)

        return {
            "expected_kwh": round(expected_kwh, 2),
            "expected_sec": round(expected_sec, 2),
            "methodology": "Wet-bulb and Heat-Load Dynamic Baseline",
            "components": {
                "process_kwh": round(process_kwh, 2),
                "weather_penalty_kwh": round(weather_penalty, 2),
                "idle_kwh": round(idle_kwh, 2)
            }
        }

    # 3. Auxiliaries: Compressors, Pumps, Casting & Finishing Lines
    else:
        sec_coeff = params.get("specific_kwh_per_ton", 25.0)
        process_kwh = production_tons * sec_coeff
        
        # Auxiliaries have baseline unloaded idle requirement during shift breaks
        idle_hrs = max(0.4, runtime_hrs - (production_tons * 0.22))
        idle_kwh = params.get("base_idle_power_kw", 10.0) * idle_hrs

        expected_kwh = process_kwh + idle_kwh
        expected_sec = expected_kwh / max(0.1, production_tons)

        return {
            "expected_kwh": round(expected_kwh, 2),
            "expected_sec": round(expected_sec, 2),
            "methodology": "Production-Coupled Variable Auxiliary Baseline",
            "components": {
                "process_kwh": round(process_kwh, 2),
                "idle_kwh": round(idle_kwh, 2)
            }
        }

def evaluate_sec_deviation(
    actual_kwh: float, 
    expected_kwh: float, 
    production_tons: float
) -> Dict[str, Any]:
    """
    Calculates exact mathematical deviation between actual and expected SEC.
    """
    actual_sec = actual_kwh / max(0.01, production_tons)
    expected_sec = expected_kwh / max(0.01, production_tons)
    dev_kwh = actual_kwh - expected_kwh
    dev_pct = ((actual_sec - expected_sec) / max(0.01, expected_sec)) * 100.0

    return {
        "actual_sec": round(actual_sec, 2),
        "expected_sec": round(expected_sec, 2),
        "dev_kwh": round(dev_kwh, 2),
        "dev_pct": round(dev_pct, 1),
        "is_abnormal": dev_pct > 10.0,
        "is_critical": dev_pct > 25.0
    }

def get_ml_baseline_status() -> Dict[str, Any]:
    """Returns training statistics and explainable feature importances of the ML baseline."""
    return {
        "is_trained": sec_ml_engine.is_trained,
        "metrics": sec_ml_engine.metrics,
        "feature_weights": sec_ml_engine.feature_weights
    }

