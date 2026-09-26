"""
What-If Scenario Simulation Engine
Evaluates mathematical before-and-after impacts of optimization actions.
Displays Baseline vs Simulated performance across Energy, Cost, CO2, Throughput, and Quality.
Delegates to decision_engine.py for complete simulation protocol.
"""

from typing import Dict, Any, List
from .models import WhatIfSimulationResult, SimulationComparison
from .decision_engine import simulate_decision_action

def run_whatif_simulation(action_id: str) -> WhatIfSimulationResult:
    """Executes high-fidelity before-and-after simulation for a candidate action."""
    res = simulate_decision_action(action_id)
    return WhatIfSimulationResult(**res)
