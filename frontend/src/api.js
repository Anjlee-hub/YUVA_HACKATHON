const API_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) || '/api';

export async function fetchFactoryOverview() {
  const res = await fetch(`${API_BASE}/factory/overview`);
  if (!res.ok) throw new Error('Failed to fetch factory overview');
  return res.json();
}

export async function fetchFactoryMachines() {
  const res = await fetch(`${API_BASE}/factory/machines`);
  if (!res.ok) throw new Error('Failed to fetch machines');
  return res.json();
}

export async function fetchFactoryHistory() {
  const res = await fetch(`${API_BASE}/factory/history`);
  if (!res.ok) throw new Error('Failed to fetch history');
  return res.json();
}

export async function fetchAnomalies() {
  const res = await fetch(`${API_BASE}/anomalies`);
  if (!res.ok) throw new Error('Failed to fetch anomalies');
  return res.json();
}

export async function fetchCandidateActions(anomalyId = null) {
  const url = anomalyId ? `${API_BASE}/actions/candidates?anomaly_id=${anomalyId}` : `${API_BASE}/actions/candidates`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch candidate actions');
  return res.json();
}

export async function postWhatIfSimulation(actionId) {
  const res = await fetch(`${API_BASE}/actions/whatif`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id: actionId })
  });
  if (!res.ok) throw new Error('Failed to run what-if simulation');
  return res.json();
}

export async function approveAction(actionId) {
  const res = await fetch(`${API_BASE}/actions/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id: actionId })
  });
  if (!res.ok) throw new Error('Failed to approve action');
  return res.json();
}

export async function resetSimulationActions() {
  const res = await fetch(`${API_BASE}/actions/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error('Failed to reset actions');
  return res.json();
}

export async function resetDemo() {
  const res = await fetch(`${API_BASE}/factory/reset`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.ok) throw new Error('Failed to reset full demo state');
  return res.json();
}

export async function fetchVerifiedSavings() {
  const res = await fetch(`${API_BASE}/verification`);
  if (!res.ok) throw new Error('Failed to fetch verified savings');
  return res.json();
}

export async function fetchReadiness() {
  const res = await fetch(`${API_BASE}/readiness`);
  if (!res.ok) throw new Error('Failed to fetch readiness');
  return res.json();
}

export async function setProgressiveLevel(level) {
  const res = await fetch(`${API_BASE}/readiness/level`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ level })
  });
  if (!res.ok) throw new Error('Failed to set level');
  return res.json();
}

export async function fetchSensorROI() {
  const res = await fetch(`${API_BASE}/sensor-roi`);
  if (!res.ok) throw new Error('Failed to fetch sensor ROI');
  return res.json();
}

export async function changeScenario(scenario) {
  const res = await fetch(`${API_BASE}/scenario`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scenario })
  });
  if (!res.ok) throw new Error('Failed to set scenario');
  return res.json();
}

export async function queryCopilot(question) {
  const res = await fetch(`${API_BASE}/copilot/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  if (!res.ok) throw new Error('Failed to query copilot');
  return res.json();
}

export async function evaluateDecision(anomalyId = null, machineId = null) {
  const res = await fetch(`${API_BASE}/decision/evaluate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ anomaly_id: anomalyId, machine_id: machineId })
  });
  if (!res.ok) throw new Error('Failed to evaluate decision pipeline');
  return res.json();
}

export async function simulateDecision(actionId) {
  const res = await fetch(`${API_BASE}/decision/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id: actionId })
  });
  if (!res.ok) throw new Error('Failed to simulate decision');
  return res.json();
}

export async function fetchDecisionScenarios() {
  const res = await fetch(`${API_BASE}/decision/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch decision scenarios');
  return res.json();
}

export async function fetchDecisionById(decisionId) {
  const res = await fetch(`${API_BASE}/decision/${decisionId}`);
  if (!res.ok) throw new Error('Failed to fetch decision');
  return res.json();
}

export async function fetchVerificationMatrix(actionId = null) {
  const url = actionId ? `${API_BASE}/verification/matrix?action_id=${actionId}` : `${API_BASE}/verification/matrix`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch verification matrix');
  return res.json();
}

export async function postVerifyAction(actionId) {
  const res = await fetch(`${API_BASE}/verification/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action_id: actionId })
  });
  if (!res.ok) throw new Error('Failed to verify action');
  return res.json();
}


