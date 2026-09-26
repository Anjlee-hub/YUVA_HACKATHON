import React, { useState } from 'react';
import { 
  AlertOctagon, 
  HelpCircle, 
  ChevronRight, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Percent,
  Search,
  ArrowRight,
  ShieldCheck,
  Info
} from 'lucide-react';

export default function AnomalyRootCauseView({ anomalies, onNavigateToDecision }) {
  const [selectedAnomaly, setSelectedAnomaly] = useState(anomalies && anomalies.length > 0 ? anomalies[0] : null);

  // Update selected if anomalies change
  React.useEffect(() => {
    if (anomalies && anomalies.length > 0) {
      setSelectedAnomaly(anomalies[0]);
    }
  }, [anomalies]);

  if (!anomalies || anomalies.length === 0) {
    return (
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-12 text-center space-y-3">
        <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
        <h3 className="text-base font-bold text-white">No Energy Anomalies Active</h3>
        <p className="text-xs text-gray-400 max-w-md mx-auto">
          All machines are currently operating within the expected production-aware baseline tolerances.
        </p>
        <div className="pt-2">
          <span className="text-xs text-gray-500 font-mono">
            Try injecting an anomaly via the top scenario selector (e.g., Scenario 1: Compressor Idle Waste).
          </span>
        </div>
      </div>
    );
  }

  const current = selectedAnomaly || anomalies[0];

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-rose-400" />
              <h2 className="text-base font-bold text-white">
                Explainable Anomaly Detection & Root-Cause Engine
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Production-aware statistical detection with multi-factor decomposition. Click <strong>"Why?"</strong> to review evidentiary proof and sensor availability.
            </p>
          </div>

          <span className="text-xs font-mono font-bold px-3 py-1.5 rounded-lg bg-rose-500/20 text-rose-300 border border-rose-500/40">
            {anomalies.length} Active Anomaly Flagged
          </span>
        </div>
      </div>

      {/* Main Grid: Anomaly List (Left) + Root-Cause Drilldown (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Anomaly Cards */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
            Detected Deviations
          </h3>

          {anomalies.map((anom) => {
            const isSelected = current && current.id === anom.id;
            return (
              <div
                key={anom.id}
                onClick={() => setSelectedAnomaly(anom)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-rose-950/30 border-rose-500 shadow-lg shadow-rose-950/40'
                    : 'bg-gray-900/80 border-gray-800 hover:border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/40">
                    {anom.severity} SEVERITY
                  </span>
                  <span className="text-[10px] font-mono text-gray-400">
                    {anom.detected_at}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white mt-2 leading-snug">
                  {anom.title}
                </h4>
                <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                  {anom.description}
                </p>

                <div className="mt-3 pt-3 border-t border-gray-800 flex items-center justify-between text-xs font-mono">
                  <div>
                    <span className="text-gray-500 text-[10px] block">SEC Deviation</span>
                    <span className="text-rose-400 font-bold">+{anom.sec_deviation_pct}%</span>
                  </div>
                  <div>
                    <span className="text-gray-500 text-[10px] block">Excess Cost Impact</span>
                    <span className="text-amber-400 font-bold">₹{anom.excess_cost_inr_per_month.toLocaleString()}/mo</span>
                  </div>
                </div>

                {anom.maintenance_withheld && (
                  <div className="mt-2.5 p-1.5 rounded bg-amber-500/10 border border-amber-500/30 text-[11px] text-amber-300 flex items-center gap-1.5">
                    <ShieldAlert className="w-3.5 h-3.5 shrink-0 text-amber-400" />
                    <span>Evidence Incomplete: Diagnosis Withheld</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Right 2 Columns: Root-Cause Decomposition & Evidentiary Proof */}
        {current && (
          <div className="lg:col-span-2 bg-gray-900/80 border border-gray-800 rounded-xl p-5 flex flex-col justify-between space-y-5">
            <div>
              
              {/* Detail Header */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                  <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider">
                    {current.machine_name} Root-Cause Audit
                  </span>
                  <h3 className="text-base font-bold text-white mt-0.5">
                    {current.title}
                  </h3>
                  <div className="mt-1 flex items-center gap-2 text-xs text-gray-400">
                    <span>Evidence Strength: <strong className="text-white">{current.evidence_strength}</strong></span>
                    <span>•</span>
                    <span>Deviation: <strong className="text-rose-400">+{current.sec_deviation_pct}% SEC</strong></span>
                    <span>•</span>
                    <span>Excess Energy: <strong className="text-amber-400">{current.excess_energy_kwh_per_day} kWh/day</strong></span>
                  </div>
                </div>

                <button
                  onClick={() => onNavigateToDecision(current.id)}
                  className="px-3 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs transition-all flex items-center gap-1.5 shrink-0 shadow-lg shadow-emerald-500/20"
                >
                  <span>Evaluate Safe Actions</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* CRITICAL TRUST RULE ALERT (MANDATORY REQUIREMENT) */}
              {current.maintenance_withheld && (
                <div className="my-4 p-4 rounded-xl bg-amber-950/30 border border-amber-500/40 text-xs text-amber-200 space-y-1">
                  <div className="flex items-center gap-2 font-bold text-amber-400">
                    <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>CRITICAL TRUST RULE: Diagnosis Withheld Due to Insufficient Evidence</span>
                  </div>
                  <p className="leading-relaxed text-amber-300/90 pl-6">
                    {current.withhold_reason}
                  </p>
                  <p className="text-[11px] text-amber-400/80 pl-6 italic">
                    Rule: An AI engine must never hallucinate a mechanical failure diagnosis when required physical telemetry (accelerometer/flow) is missing.
                  </p>
                </div>
              )}

              {/* Root Cause Contributing Factors Breakdown (Section 7 Example) */}
              <div className="space-y-3 mt-4">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider">
                    Contributing Factors Breakdown (% Attribution)
                  </h4>
                  <span className="text-[11px] text-gray-500">Multivariate Shapley Decomposition</span>
                </div>

                <div className="space-y-2.5">
                  {current.contributing_factors?.map((f, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-gray-950/60 border border-gray-800 space-y-1.5">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-semibold text-white">{f.factor_name}</span>
                        <span className="font-mono font-bold text-cyan-400">{f.share_pct}%</span>
                      </div>

                      {/* Percentage Bar */}
                      <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
                        <div 
                          className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full rounded-full"
                          style={{ width: `${f.share_pct}%` }}
                        ></div>
                      </div>

                      <p className="text-xs text-gray-400 leading-relaxed mt-1">
                        {f.impact_description}
                      </p>

                      <div className="pt-1 text-[11px] font-mono text-gray-400 flex items-center gap-1.5">
                        <span className="text-gray-500">Sensor Evidence:</span>
                        <span className="text-emerald-400/90">{f.sensor_evidence}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>

            {/* Bottom "Why?" Explanation Callout */}
            <div className="pt-3 border-t border-gray-800 flex items-center justify-between text-xs text-gray-400">
              <span className="flex items-center gap-1.5">
                <Info className="w-3.5 h-3.5 text-cyan-400" />
                Calculated from sub-meter interval power & continuous pressure transducer log
              </span>
              <button
                onClick={() => onNavigateToDecision(current.id)}
                className="text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1"
              >
                Pass to Constraint Gate <ChevronRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
