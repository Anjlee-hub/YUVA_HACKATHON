import React, { useState, useEffect } from 'react';
import { 
  Award, 
  ShieldCheck, 
  CheckCircle2, 
  AlertCircle, 
  TrendingDown, 
  Leaf, 
  IndianRupee, 
  Zap,
  HelpCircle,
  FileCheck,
  ArrowRight,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import { fetchVerificationMatrix, postVerifyAction } from '../api';

export default function SavingsVerificationView({ verifiedRecords, onActionApproved }) {
  const [activeTab, setActiveTab] = useState('matrix'); // 'matrix' | 'historical'
  const [matrixData, setMatrixData] = useState([]);
  const [selectedActionId, setSelectedActionId] = useState('action_compressor_unloaded_shutdown');
  const [loading, setLoading] = useState(false);
  const [verifyMessage, setVerifyMessage] = useState(null);

  useEffect(() => {
    loadMatrix();
  }, [selectedActionId]);

  const loadMatrix = async () => {
    try {
      setLoading(true);
      const data = await fetchVerificationMatrix();
      setMatrixData(data);
    } catch (err) {
      console.error("Failed to load verification matrix:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyNow = async (actionId) => {
    try {
      setLoading(true);
      const res = await postVerifyAction(actionId);
      setVerifyMessage(res);
      await loadMatrix();
      if (onActionApproved) onActionApproved();
    } catch (err) {
      console.error("Verification failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const totKwh = verifiedRecords?.reduce((acc, r) => acc + r.kwh_saved_monthly, 0) || 0;
  const totInr = verifiedRecords?.reduce((acc, r) => acc + r.inr_saved_monthly, 0) || 0;
  const totCo2 = verifiedRecords?.reduce((acc, r) => acc + r.co2_avoided_kg_monthly, 0) || 0;

  const currentItem = matrixData.find(m => m.action_id === selectedActionId) || matrixData[0];

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Measurement & Verification (M&V) Protocol */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Award className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-white">
                Savings Verification & IPMVP Option B Audit Trail
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1 max-w-3xl leading-relaxed">
              <strong className="text-white">Strict Trust Protocol:</strong> We never call predicted savings "verified". 
              Only interventions confirmed by post-action sub-meter telemetry while maintaining throughput and metallurgical quality qualify as 
              <span className="text-emerald-400 font-semibold"> Verified Production-Safe Savings</span>.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <span className="px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-semibold font-mono">
              M&V Framework: IPMVP Option B — Prototype
            </span>
          </div>
        </div>

        {/* Complete Savings Lifecycle Stepper */}
        <div className="mt-5 pt-4 border-t border-gray-800">
          <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block mb-2">
            Complete Savings Lifecycle:
          </span>
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <div className="px-2.5 py-1 rounded bg-gray-800 text-gray-300 font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              1. BASELINE
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-gray-600" />
            <div className="px-2.5 py-1 rounded bg-blue-900/40 text-blue-300 border border-blue-500/30 font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-blue-400"></span>
              2. PREDICTED (What-If)
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-gray-600" />
            <div className="px-2.5 py-1 rounded bg-indigo-900/40 text-indigo-300 border border-indigo-500/30 font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
              3. APPROVED (Human Gate)
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-gray-600" />
            <div className="px-2.5 py-1 rounded bg-purple-900/40 text-purple-300 border border-purple-500/30 font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-purple-400"></span>
              4. SIMULATED ACTUAL (Post-Action)
            </div>
            <ArrowRight className="w-3.5 h-3.5 text-gray-600" />
            <div className="px-2.5 py-1 rounded bg-emerald-900/40 text-emerald-300 border border-emerald-500/30 font-semibold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              5. VERIFIED (M&V Protocol)
            </div>
          </div>
        </div>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-gray-400 block">Audited Monthly Plant Savings</span>
            <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
              ₹{totInr.toLocaleString()}
            </div>
            <span className="text-[11px] text-gray-500 font-mono">₹{(totInr * 12).toLocaleString()} / year</span>
          </div>
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
            <IndianRupee className="w-6 h-6" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-gray-400 block">Verified Monthly Electrical Energy Saved</span>
            <div className="text-2xl font-bold font-mono text-cyan-400 mt-1">
              {totKwh.toLocaleString()}
            </div>
            <span className="text-[11px] text-gray-500 font-mono">kWh / month sub-metered</span>
          </div>
          <div className="p-3 rounded-lg bg-cyan-500/10 text-cyan-400">
            <Zap className="w-6 h-6" />
          </div>
        </div>

        <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 flex items-center justify-between">
          <div>
            <span className="text-xs text-gray-400 block">Scope 2 Carbon Emissions Avoided</span>
            <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">
              {(totCo2 / 1000).toFixed(1)}t
            </div>
            <span className="text-[11px] text-gray-500 font-mono">Metric Tons CO2e / month</span>
          </div>
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Leaf className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-3 border-b border-gray-800 pb-2">
        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'matrix'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              : 'text-gray-400 hover:text-white bg-gray-900/40'
          }`}
        >
          Predicted vs Actual Comparison Matrix
        </button>
        <button
          onClick={() => setActiveTab('historical')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
            activeTab === 'historical'
              ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
              : 'text-gray-400 hover:text-white bg-gray-900/40'
          }`}
        >
          Auditable M&V Historical Ledger ({verifiedRecords?.length || 0})
        </button>
      </div>

      {/* TAB 1: PREDICTED VS ACTUAL MATRIX */}
      {activeTab === 'matrix' && (
        <div className="space-y-5">
          {/* Action Selector */}
          <div className="flex flex-wrap items-center justify-between gap-3 bg-gray-900/70 p-3 rounded-xl border border-gray-800">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-400 font-semibold">Select Intervention for Verification Audit:</span>
              <div className="flex flex-wrap gap-2">
                {matrixData.map(m => (
                  <button
                    key={m.action_id}
                    onClick={() => setSelectedActionId(m.action_id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                      selectedActionId === m.action_id
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 font-bold'
                        : 'bg-gray-800/80 text-gray-400 hover:text-white'
                    }`}
                  >
                    {m.action_id === 'action_compressor_unloaded_shutdown' ? 'Compressor 02 (Safe)' : 
                     m.action_id === 'action_furnace_refractory_patch' ? 'Furnace 02 (Safe)' : 
                     'Compressor 02 (Unsafe Rejection Demo)'}
                  </button>
                ))}
              </div>
            </div>

            <div className="text-[11px] font-mono text-amber-400/90 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20">
              DEMO — SIMULATED POST-ACTION DATA
            </div>
          </div>

          {currentItem && (
            <div className="space-y-4 bg-gray-900/90 border border-gray-800 rounded-xl p-5">
              {/* Card Header & Status */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-cyan-400 uppercase font-semibold">
                      {currentItem.machine_name}
                    </span>
                    <span className="text-[11px] font-mono text-gray-400">
                      • Lifecycle Stage: <strong className="text-white">{currentItem.lifecycle_stage}</strong>
                    </span>
                  </div>
                  <h3 className="text-base font-bold text-white">
                    {currentItem.action_title}
                  </h3>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <span className={`text-xs font-mono px-3 py-1.5 rounded font-bold border ${
                    currentItem.is_production_safe_saving
                      ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                      : 'bg-red-500/20 text-red-400 border-red-500/40'
                  }`}>
                    {currentItem.verification_status}
                  </span>
                </div>
              </div>

              {/* Constraint Checks Audit Bar */}
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-[11px] font-mono">
                <div className={`p-2 rounded border flex items-center gap-1.5 ${
                  currentItem.energy_reduction_positive ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-red-950/20 border-red-500/30 text-red-300'
                }`}>
                  {currentItem.energy_reduction_positive ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <XCircle className="w-3.5 h-3.5 text-red-400" />}
                  <span>Energy Saved &gt; 0</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-1.5 ${
                  currentItem.production_maintained ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-red-950/20 border-red-500/30 text-red-300'
                }`}>
                  {currentItem.production_maintained ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <XCircle className="w-3.5 h-3.5 text-red-400" />}
                  <span>Throughput 100% Retained</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-1.5 ${
                  currentItem.quality_maintained ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-red-950/20 border-red-500/30 text-red-300'
                }`}>
                  {currentItem.quality_maintained ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <XCircle className="w-3.5 h-3.5 text-red-400" />}
                  <span>Quality Standard Met</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-1.5 ${
                  currentItem.machine_limits_maintained ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-red-950/20 border-red-500/30 text-red-300'
                }`}>
                  {currentItem.machine_limits_maintained ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <XCircle className="w-3.5 h-3.5 text-red-400" />}
                  <span>Machine Limits Safe</span>
                </div>

                <div className={`p-2 rounded border flex items-center gap-1.5 ${
                  currentItem.evidence_sufficient ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300' : 'bg-red-950/20 border-red-500/30 text-red-300'
                }`}>
                  {currentItem.evidence_sufficient ? <CheckCircle className="w-3.5 h-3.5 text-emerald-400" /> : <XCircle className="w-3.5 h-3.5 text-red-400" />}
                  <span>Sensory Evidence Valid</span>
                </div>
              </div>

              {/* 6 Core Rows Comparison Table */}
              <div className="overflow-x-auto rounded-lg border border-gray-800">
                <table className="w-full text-left text-xs font-mono">
                  <thead className="bg-gray-950/80 text-gray-400 border-b border-gray-800">
                    <tr>
                      <th className="py-2.5 px-3">Metric Parameter</th>
                      <th className="py-2.5 px-3">Unit</th>
                      <th className="py-2.5 px-3 text-right">BEFORE (Baseline)</th>
                      <th className="py-2.5 px-3 text-right">PREDICTED (What-If)</th>
                      <th className="py-2.5 px-3 text-right text-emerald-400">ACTUAL (Simulated Live)</th>
                      <th className="py-2.5 px-3 text-right">Prediction Error</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800/60 bg-gray-900/50">
                    {currentItem.rows.map((row, idx) => (
                      <tr key={idx} className="hover:bg-gray-800/30 transition-colors">
                        <td className="py-2.5 px-3 text-gray-200 font-sans font-medium">{row.metric}</td>
                        <td className="py-2.5 px-3 text-gray-500">{row.unit}</td>
                        <td className="py-2.5 px-3 text-right text-gray-300 font-bold">{row.before.toLocaleString()}</td>
                        <td className="py-2.5 px-3 text-right text-blue-300 font-bold">{row.predicted.toLocaleString()}</td>
                        <td className={`py-2.5 px-3 text-right font-bold ${
                          currentItem.is_production_safe_saving ? 'text-emerald-400' : 'text-red-400'
                        }`}>
                          {row.actual.toLocaleString()}
                        </td>
                        <td className="py-2.5 px-3 text-right">
                          <span className={`px-1.5 py-0.5 rounded text-[11px] ${
                            Math.abs(row.variance_pct) <= 5.0 ? 'bg-emerald-500/10 text-emerald-400' : 'bg-amber-500/10 text-amber-400'
                          }`}>
                            {row.variance_pct > 0 ? `+${row.variance_pct}%` : `${row.variance_pct}%`}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* 4 Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 rounded-lg bg-gray-950/70 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block uppercase">Prediction Error</span>
                  <span className="text-base font-bold font-mono text-cyan-400">
                    {currentItem.prediction_error_pct}%
                  </span>
                  <span className="text-[10px] text-gray-400 block font-mono">Predicted vs Simulated</span>
                </div>

                <div className="p-3 rounded-lg bg-gray-950/70 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block uppercase">Actual Energy Saved</span>
                  <span className="text-base font-bold font-mono text-emerald-400">
                    {currentItem.actual_kwh_saved.toLocaleString()} kWh/day
                  </span>
                  <span className="text-[10px] text-gray-400 block font-mono">SEC Δ: {currentItem.actual_sec_improvement_pct}%</span>
                </div>

                <div className="p-3 rounded-lg bg-gray-950/70 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block uppercase">Actual Monthly Savings</span>
                  <span className="text-base font-bold font-mono text-emerald-400">
                    ₹{currentItem.actual_cost_saved_inr.toLocaleString()}
                  </span>
                  <span className="text-[10px] text-gray-400 block font-mono">₹{(currentItem.actual_cost_saved_inr * 12).toLocaleString()} / yr</span>
                </div>

                <div className="p-3 rounded-lg bg-gray-950/70 border border-gray-800">
                  <span className="text-[10px] text-gray-500 block uppercase">Actual CO2 Avoided</span>
                  <span className="text-base font-bold font-mono text-emerald-400">
                    {currentItem.actual_co2_avoided_kg.toLocaleString()} kg/mo
                  </span>
                  <span className="text-[10px] text-gray-400 block font-mono">{(currentItem.actual_co2_avoided_kg / 1000).toFixed(1)} MT CO2e</span>
                </div>
              </div>

              {/* Variance Analysis & Disclaimers */}
              <div className="p-3.5 rounded-lg bg-gray-950/80 border border-gray-800 text-xs space-y-2">
                <div className="flex items-center gap-1.5 text-gray-300 font-semibold">
                  <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Auditable Variance & Operational Reconciliation:</span>
                </div>
                <p className="text-gray-300 leading-relaxed font-sans">
                  {currentItem.variance_explanation}
                </p>
                <div className="pt-2 border-t border-gray-800/80 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-[11px] text-gray-500 font-mono">
                  <span>Methodology: {currentItem.verification_methodology}</span>
                  <span className="text-gray-400">{currentItem.real_deployment_note}</span>
                </div>
              </div>

              {/* Action Button: Verify Live */}
              {currentItem.is_production_safe_saving && currentItem.lifecycle_stage !== 'VERIFIED' && (
                <div className="pt-2 flex justify-end">
                  <button
                    onClick={() => handleVerifyNow(currentItem.action_id)}
                    disabled={loading}
                    className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-gray-950 font-bold text-xs flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/10"
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Confirm & Certify M&V Verification</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* TAB 2: AUDITABLE HISTORICAL LEDGER */}
      {activeTab === 'historical' && (
        <div className="space-y-4">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
            Post-Implementation Verified Action Records ({verifiedRecords?.length || 0})
          </h3>

          {verifiedRecords && verifiedRecords.map((rec) => (
            <div 
              key={rec.id}
              className="p-5 rounded-xl bg-gray-900/90 border border-gray-800 space-y-4"
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-gray-800 pb-3">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-emerald-400 uppercase font-semibold">
                      {rec.machine_name}
                    </span>
                    <span className="text-[10px] text-gray-400 font-mono">
                      • Implemented: {rec.implemented_date}
                    </span>
                  </div>
                  <h4 className="text-sm font-bold text-white leading-tight">
                    {rec.action_title}
                  </h4>
                </div>

                <span className="text-[10px] font-mono px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold shrink-0">
                  VERIFIED PRODUCTION-SAFE SAVING
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded-lg bg-gray-950/60 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Predicted SEC Delta</span>
                  <span className="text-gray-300 font-bold text-sm">
                    {rec.predicted_sec_improvement_pct}%
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-emerald-950/20 border border-emerald-500/30">
                  <span className="text-emerald-400 text-[10px] block">Actual Verified Delta</span>
                  <span className="text-emerald-400 font-bold text-sm">
                    {rec.actual_sec_improvement_pct}%
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/60 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Monthly kWh Saved</span>
                  <span className="text-cyan-400 font-bold text-sm">
                    {rec.kwh_saved_monthly.toLocaleString()}
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/60 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Monthly ₹ Saved</span>
                  <span className="text-emerald-400 font-bold text-sm">
                    ₹{rec.inr_saved_monthly.toLocaleString()}
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/60 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Throughput Impact</span>
                  <span className="text-emerald-400 font-bold text-sm">
                    {rec.production_impact_pct}% (Zero Loss)
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/60 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Quality Rejection</span>
                  <span className="text-emerald-400 font-bold text-sm">
                    {rec.quality_impact_pct}% (Zero Loss)
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-gray-950/70 border border-gray-800 text-xs space-y-1">
                <div className="flex items-center gap-1.5 text-gray-400 font-semibold">
                  <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Auditable Discrepancy & Variance Analysis:</span>
                </div>
                <p className="text-gray-300 leading-relaxed font-sans text-xs">
                  {rec.variance_explanation}
                </p>
                <div className="pt-1 text-[11px] font-mono text-gray-500">
                  Methodology: {rec.verification_methodology}
                </div>
              </div>

            </div>
          ))}
        </div>
      )}

    </div>
  );
}
