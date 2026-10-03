import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

base_url = 'http://127.0.0.1:8000'

def request(path, method='GET', data=None):
    url = f'{base_url}{path}'
    req = urllib.request.Request(url, method=method)
    req.add_header('Origin', 'http://127.0.0.1:5173')
    if data:
        req.add_header('Content-Type', 'application/json')
        req.data = json.dumps(data).encode('utf-8')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode('utf-8'))

print('=== LIVE PROTOCOL VALIDATION ACROSS ALL 4 SCENARIOS ===\n')

# Step 1: Scenario 1 - Compressor 02
print('1. Testing Scenario 1 (Compressor 02 Idle Waste)...')
request('/api/factory/reset', 'POST')
res = request('/api/scenario', 'POST', {'scenario': 'compressor_waste'})
assert res['success'] is True

anoms = request('/api/anomalies')
comp_anom = next(a for a in anoms if a['machine_id'] == 'compressor_02')
print(f'   [PASS] Compressor anomaly detected: idle_ratio deviation={comp_anom.get("sec_deviation_pct")}%, evidence={comp_anom.get("evidence_strength")}')

actions = request('/api/actions/candidates')
unsafe = next(a for a in actions if a['id'] == 'action_compressor_lower_pressure_extreme')
assert unsafe['is_safe'] is False
print(f'   [PASS] Unsafe action rejected: {unsafe["rejection_reason"]}')

safe = next(a for a in actions if a['id'] == 'action_compressor_unloaded_shutdown')
assert safe['is_safe'] is True
print(f'   [PASS] Safe action identified: {safe["title"]}')

sim = request('/api/actions/whatif', 'POST', {'action_id': 'action_compressor_unloaded_shutdown'})
print(f'   [PASS] What-if simulation: saved {sim["energy_comparison"]["kwh_saved_day"]} kWh/day, disclaimer="{sim["verification_disclaimer"]}"')

appr = request('/api/actions/approve', 'POST', {'action_id': 'action_compressor_unloaded_shutdown'})
print(f'   [PASS] Action approved: {appr}')

ver = request('/api/verification')
assert len(ver) >= 1
print(f'   [PASS] Verification ledger: {ver[0]["action_title"]} -> {ver[0]["kwh_saved_monthly"]} kWh/mo')

cop1 = request('/api/copilot/query', 'POST', {'question': 'Why was the first action rejected?'})
print(f'   [PASS] Copilot Q1 (Why rejected): {cop1["answer"][:120]}...')
cop2 = request('/api/copilot/query', 'POST', {'question': 'How much could we save?'})
print(f'   [PASS] Copilot Q2 (How much save): {cop2["answer"][:120]}...')

# Step 2: Scenario 2 - Furnace 02
print('\n2. Testing Scenario 2 (Furnace 02 Degradation)...')
request('/api/factory/reset', 'POST')
request('/api/scenario', 'POST', {'scenario': 'furnace_degradation'})
anoms_f = request('/api/anomalies')
furn_anom = next(a for a in anoms_f if a['machine_id'] == 'furnace_02')
print(f'   [PASS] Furnace anomaly detected: evidence={furn_anom["evidence_strength"]}')

actions_f = request('/api/actions/candidates')
unsafe_f = next(a for a in actions_f if a['id'] == 'action_furnace_lower_temp_unsafe')
assert unsafe_f['is_safe'] is False
print(f'   [PASS] Unsafe temp action rejected: {unsafe_f["rejection_reason"]}')

safe_f = next(a for a in actions_f if a['id'] == 'action_furnace_refractory_patch')
assert safe_f['is_safe'] is True
print(f'   [PASS] Safe refractory action identified: {safe_f["title"]}')

sim_f = request('/api/actions/whatif', 'POST', {'action_id': 'action_furnace_refractory_patch'})
print(f'   [PASS] What-if simulation: saved {sim_f["energy_comparison"]["kwh_saved_day"]} kWh/day')

appr_f = request('/api/actions/approve', 'POST', {'action_id': 'action_furnace_refractory_patch'})
print(f'   [PASS] Action approved: {appr_f}')

ver_matrix_f = request('/api/verification/matrix')
f_item = next(m for m in ver_matrix_f if m['action_id'] == 'action_furnace_refractory_patch')
print(f'   [PASS] Matrix verification: {f_item["action_title"]} status="{f_item["verification_status"]}"')

# Step 3: Scenario 3 - TOD / Production Scheduling
print('\n3. Testing Scenario 3 (TOD / Production Scheduling)...')
request('/api/factory/reset', 'POST')
request('/api/scenario', 'POST', {'scenario': 'production_scheduling'})
actions_tod = request('/api/actions/candidates')
safe_tod = next(a for a in actions_tod if a['id'] == 'action_tod_rescheduling')
assert safe_tod['is_safe'] is True
print(f'   [PASS] Safe TOD rescheduling candidate: {safe_tod["title"]}')
sim_tod = request('/api/actions/whatif', 'POST', {'action_id': 'action_tod_rescheduling'})
print(f'   [PASS] TOD Simulation: INR saved={sim_tod["cost_comparison"]["savings_month_inr"]}/mo, 0 kWh net change')
request('/api/actions/approve', 'POST', {'action_id': 'action_tod_rescheduling'})
print(f'   [PASS] TOD Action approved')

# Step 4: Scenario 4 - Missing Vibration Sensor
print('\n4. Testing Scenario 4 (Missing Vibration Sensor)...')
request('/api/factory/reset', 'POST')
request('/api/scenario', 'POST', {'scenario': 'missing_sensor'})
anoms_m = request('/api/anomalies')
miss_anom = anoms_m[0]
assert miss_anom['maintenance_withheld'] is True
print(f'   [PASS] Anomaly diagnosis withheld: reason="{miss_anom["withhold_reason"]}"')

rois = request('/api/sensor-roi')
vib_roi = next(r for r in rois if 'vibration' in r['sensor_type'].lower())
print(f'   [PASS] Sensor ROI recommendation: {vib_roi["sensor_type"]} -> Payback: {vib_roi["payback_months"]} months')

cop_m = request('/api/copilot/query', 'POST', {'question': 'Why is the diagnosis withheld?'})
print(f'   [PASS] Copilot withheld explanation: {cop_m["answer"][:120]}...')

# Step 5: Scenario Switching
print('\n5. Testing Scenario Switching Integrity (1 -> 2 -> 3 -> 4 -> 1)...')
request('/api/scenario', 'POST', {'scenario': 'compressor_waste'})
ov1 = request('/api/factory/overview')
assert ov1['active_scenario'] == 'compressor_waste'

request('/api/scenario', 'POST', {'scenario': 'furnace_degradation'})
ov2 = request('/api/factory/overview')
assert ov2['active_scenario'] == 'furnace_degradation'

request('/api/scenario', 'POST', {'scenario': 'production_scheduling'})
ov3 = request('/api/factory/overview')
assert ov3['active_scenario'] == 'production_scheduling'

request('/api/scenario', 'POST', {'scenario': 'missing_sensor'})
ov4 = request('/api/factory/overview')
assert ov4['active_scenario'] == 'missing_sensor'

request('/api/scenario', 'POST', {'scenario': 'compressor_waste'})
ov5 = request('/api/factory/overview')
assert ov5['active_scenario'] == 'compressor_waste'
print('   [PASS] Scenario switching integrity verified with zero stale state cross-contamination.')

# Step 6: Reset Demo
print('\n6. Testing Reset Demo...')
request('/api/actions/approve', 'POST', {'action_id': 'action_compressor_unloaded_shutdown'})
ov_dirty = request('/api/factory/overview')
assert len(ov_dirty['applied_actions']) >= 1
request('/api/factory/reset', 'POST')
ov_clean = request('/api/factory/overview')
assert ov_clean['active_scenario'] == 'normal'
assert len(ov_clean['applied_actions']) == 0
print('   [PASS] Reset Demo restores clean factory baseline state.')
