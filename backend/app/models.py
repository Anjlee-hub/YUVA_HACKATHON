from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime

class DataLevel(str, Enum):
    LEVEL_0 = "Level 0: Energy Bill + Operating Hours"
    LEVEL_1 = "Level 1: Main Meter + Production Count + Runtime"
    LEVEL_2 = "Level 2: Sub-meters on Critical Machines"
    LEVEL_3 = "Level 3: IoT Sensors (Temp, Vibration, Pressure)"
    LEVEL_4 = "Level 4: Full SCADA / PLC / Process Telemetry"

class AnomalySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class MachineStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    ANOMALOUS = "ANOMALOUS"
    MAINTENANCE_REQUIRED = "MAINTENANCE_REQUIRED"
    INVESTIGATING = "INVESTIGATING"
    IDLE = "IDLE"

class MachineTelemetry(BaseModel):
    id: str
    name: str
    category: str # "Furnace", "Compressed Air", "Hydraulics & Pumping", "Production Line"
    rated_power_kw: float
    current_power_kw: float
    energy_today_kwh: float
    runtime_today_hrs: float
    idle_time_today_hrs: float
    temperature_c: Optional[float] = None
    vibration_mms: Optional[float] = None
    pressure_bar: Optional[float] = None
    production_units_today: float
    actual_sec: float # kWh / unit or kWh / ton
    expected_sec: float
    sec_deviation_pct: float
    health_score: float # 0 - 100
    status: MachineStatus
    sensors_active: List[str]
    sensors_missing: List[str]
    is_anomaly: bool = False

class DataConfidenceMetric(BaseModel):
    sensor_name: str
    completeness_pct: float
    freshness_pct: float
    consistency_pct: float
    overall_pct: float
    is_available: bool = True
    note: Optional[str] = None

class DataReadinessOverview(BaseModel):
    overall_confidence_pct: float
    current_level: int
    level_name: str
    sensor_metrics: List[DataConfidenceMetric]
    can_diagnose_mechanical: bool
    can_diagnose_thermal: bool
    withheld_diagnoses_count: int
    what_is_available: List[str] = Field(default_factory=list)
    what_is_missing: List[str] = Field(default_factory=list)
    currently_possible_intelligence: List[str] = Field(default_factory=list)
    next_level_unlocks: List[str] = Field(default_factory=list)

class ContributingFactor(BaseModel):
    factor_name: str
    share_pct: float
    impact_description: str
    sensor_evidence: str

class Anomaly(BaseModel):
    id: str
    machine_id: str
    machine_name: str
    title: str
    description: str
    severity: AnomalySeverity
    detected_at: str
    anomaly_type: str = "HIGH_SEC" # "HIGH_SEC", "ENERGY_SPIKE", "ENERGY_WITHOUT_PRODUCTION", "EXCESSIVE_IDLE", "ABNORMAL_TELEMETRY"
    sec_deviation_pct: float
    excess_energy_kwh_per_day: float
    excess_cost_inr_per_month: float
    contributing_factors: List[ContributingFactor]
    evidence_strength: str # "Strong", "Moderate", "Insufficient"
    data_confidence_pct: float = 88.0
    maintenance_withheld: bool = False
    withhold_reason: Optional[str] = None

class ConstraintCheck(BaseModel):
    name: str
    threshold: str
    projected_value: str
    passed: bool
    violation_detail: Optional[str] = None

class WhyThisAction(BaseModel):
    sec_deviation: str
    idle_time: str
    pressure: str
    production: str
    historical_behavior: str

class WhyIsItSafe(BaseModel):
    production_status: str # "PASS" or "FAIL"
    production_detail: str
    quality_status: str    # "PASS" or "FAIL"
    quality_detail: str
    deadline_status: str   # "PASS" or "FAIL"
    deadline_detail: str
    machine_limits_status: str # "PASS" or "FAIL"
    machine_limits_detail: str

class ActionEvaluation(BaseModel):
    id: str
    action_id: Optional[str] = None
    machine_id: Optional[str] = None
    anomaly_id: str
    title: str
    category: str
    description: Optional[str] = None
    proposed_change: str
    required_data: List[str] = Field(default_factory=list)
    energy_savings_pct: float
    expected_energy_kwh_per_day: float = 0.0
    expected_energy_change: Optional[Dict[str, Any]] = None
    monthly_cost_savings_inr: float
    expected_cost_change: Optional[float] = None
    co2_reduction_kg: float
    expected_co2_change: Optional[float] = None
    production_impact_pct: float
    production_impact: Optional[Dict[str, Any]] = None
    quality_impact_pct: float
    quality_impact: Optional[Dict[str, Any]] = None
    deadline_impact_hrs: float
    machine_health_risk: str # "Negligible", "Low", "Moderate", "High"
    risk_level: str = "Low"
    constraints: List[ConstraintCheck]
    is_safe: bool
    status: str = "SAFE_FOR_SIMULATION" # "SAFE_FOR_SIMULATION", "REJECTED", "NEEDS_MORE_DATA", "SIMULATED_NOT_VERIFIED", "APPROVED"
    is_production_safe_savings: bool = False
    rejection_reason: Optional[str] = None
    confidence_score: float = 90.0
    confidence: float = 90.0
    implementation_complexity: str = "Minor Adjustment"
    implementation_time: str = "Instant Config"
    why_this_action: Optional[str] = None
    why_not_alternative: Optional[str] = None
    why_is_it_safe: Optional[WhyIsItSafe] = None
    action_state: str = "CANDIDATE" # "CANDIDATE", "SIMULATED", "APPROVED", "REJECTED"
    predicted_kpis: Optional[Dict[str, Any]] = None

class SimulationComparison(BaseModel):
    metric: str
    unit: str
    baseline: float
    simulated: float
    pct_change: float
    is_favorable: bool

class WhatIfSimulationResult(BaseModel):
    action_id: str
    action_title: str
    machine_name: str
    metrics: List[SimulationComparison]
    production_throughput_retained: bool = True
    quality_tolerance_satisfied: bool = True
    recommendation_verdict: str = "RECOMMENDED SAFE"
    payback_period_days: int = 0
    is_verified: bool = False
    verification_disclaimer: str = "WHAT-IF SIMULATION - NOT YET VERIFIED"
    is_production_safe_savings: bool = True
    energy_comparison: Optional[Dict[str, Any]] = None
    cost_comparison: Optional[Dict[str, Any]] = None
    co2_comparison: Optional[Dict[str, Any]] = None
    production_comparison: Optional[Dict[str, Any]] = None
    quality_comparison: Optional[Dict[str, Any]] = None
    why_this_action: Optional[str] = None
    why_not_alternative: Optional[str] = None

class VerifiedSavingsRecord(BaseModel):
    id: str
    action_title: str
    machine_name: str
    implemented_date: str
    predicted_sec_improvement_pct: float
    actual_sec_improvement_pct: float
    kwh_saved_monthly: float
    inr_saved_monthly: float
    co2_avoided_kg_monthly: float
    production_impact_pct: float
    quality_impact_pct: float
    variance_explanation: str
    verification_methodology: str # "IPMVP Option B (Machine Sub-meter Isolation)"

class MetricComparisonRow(BaseModel):
    metric: str
    unit: str
    before: float
    predicted: float
    actual: float
    variance_pct: float

class PredictedVsActualVerification(BaseModel):
    action_id: str
    action_title: str
    machine_name: str
    lifecycle_stage: str # "BASELINE", "PREDICTED", "APPROVED", "SIMULATED_ACTUAL", "VERIFIED"
    verification_status: str # "VERIFIED PRODUCTION-SAFE SAVING", "SIMULATED ACTUAL - PENDING VERIFICATION", "REJECTED - CONSTRAINT VIOLATION"
    is_production_safe_saving: bool
    disclaimer: str = "DEMO — SIMULATED POST-ACTION DATA"
    real_deployment_note: str = "In real deployment, verification requires actual sub-meter measurements under IPMVP Option B with baseline normalization."
    rows: List[MetricComparisonRow]
    prediction_error_pct: float
    actual_kwh_saved: float
    actual_sec_improvement_pct: float
    actual_cost_saved_inr: float
    actual_co2_avoided_kg: float
    production_maintained: bool
    quality_maintained: bool
    machine_limits_maintained: bool
    energy_reduction_positive: bool
    risk_acceptable: bool
    evidence_sufficient: bool
    variance_explanation: str
    verification_methodology: str

class SensorROIRecommendation(BaseModel):
    sensor_id: str
    machine_id: str
    machine_name: str
    sensor_type: str
    sensor_category: str = "Specialized Sensor" # "Tri-axial Vibration Sensor", "Pressure Sensor", "Temperature Sensor", "PLC / Runtime Signal", "Additional Energy Sub-meter"
    information_gain: str # "High", "Medium", "Critical"
    information_value_score: float = 8.5 # 1 - 10
    estimated_capex_inr: float
    estimated_installation_inr: float
    potential_savings_unlocked_inr_yr: float
    payback_months: float
    evidence_improvement_pct: float = 35.0
    priority_score: float = 8.5
    is_next_best: bool = False
    unlocked_capabilities: List[str]
    why_needed: str
    recommended_rank: int
    illustrative_disclaimer: str = "All sensor prices and ROI values are ILLUSTRATIVE DEMO ASSUMPTIONS."

class FactoryOverview(BaseModel):
    factory_name: str
    location: str
    industry: str
    production_unit: str
    total_power_kw: float
    total_energy_today_kwh: float
    factory_sec: float
    factory_sec_baseline: float
    sec_deviation_pct: float
    energy_cost_today_inr: float
    co2_emissions_today_kg: float
    production_today_units: float
    quality_pass_rate_pct: float
    active_anomalies_count: int
    verified_savings_monthly_inr: float
    data_confidence_pct: float
    current_intelligence_level: int

