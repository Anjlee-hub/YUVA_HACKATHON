"""
Production-Safe Action Engine & Manufacturing Constraint Gate
Delegates to decision_engine.py for complete pipeline execution.
Maintains backward compatibility with all existing callers and tests.
"""

from typing import List, Dict, Any, Optional
from .models import ActionEvaluation
from .decision_engine import evaluate_decision_pipeline

def evaluate_candidate_actions(anomaly_id: Optional[str] = None) -> List[ActionEvaluation]:
    """
    Evaluates candidate optimization actions using the constraint gate.
    Returns list of ActionEvaluation instances.
    """
    res = evaluate_decision_pipeline(anomaly_id=anomaly_id)
    return [ActionEvaluation(**a) for a in res["candidate_actions"]]
