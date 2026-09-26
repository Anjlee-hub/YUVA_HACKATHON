import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Sliders, 
  Sparkles,
  HelpCircle,
  FileSearch,
  BadgeCheck,
  Activity,
  ArrowRight
} from 'lucide-react';

export default function DecisionEngineView({ candidateActions, onLaunchWhatIf }) {
  const [filterType, setFilterType] = useState('ALL'); // 'ALL', 'SAFE', 'REJECTED', 'NEEDS_DATA'

  const filtered = React.useMemo(() => {
    if (!candidateActions) return [];
    if (filterType === 'SAFE') return candidateActions.filter(a => a.is_safe || a.status === 'SAFE_FOR_SIMULATION' || a.status === 'APPROVED');
    if (filterType === 'REJECTED') return candidateActions.filter(a => a.status === 'REJECTED');
    if (filterType === 'NEEDS_DATA') return candidateActions.filter(a => a.status === 'NEEDS_MORE_DATA');
    return candidateActions;
  }, [candidateActions, filterType]);

  const safeCount = candidateActions?.filter(a => a.is_safe || a.status === 'SAFE_FOR_SIMULATION' || a.status === 'APPROVED').length || 0;
  const rejectedCount = candidateActions?.filter(a => a.status === 'REJECTED').length || 0;
  const needsDataCount = candidateActions?.filter(a => a.status === 'NEEDS_MORE_DATA').length || 0;

  return (
    <div className="space-y-6">
      
      {/* 1. Module Header & Core Differentiation */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-white">
                Production-Safe Decision Engine & Constraint Gate
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1 max-w-3xl">
              <strong className="text-emerald-400">Decision-Support Layer:</strong> Converts detected energy waste into certified safe interventions for human approval. Any optimization that violates throughput, product quality, customer deadlines, or machine operating limits is <strong>automatically rejected</strong>.
            </p>
          </div>

          {/* Filter Pills */}
          <div className="inline-flex flex-wrap rounded-lg bg-gray-800 p-0.5 border border-gray-700 text-xs font-medium">
            <button
              onClick={() => setFilterType('ALL')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                filterType === 'ALL' ? 'bg-gray-700 text-white font-semibold' : 'text-gray-400 hover:text-white'
              }`}
            >
              All Actions ({candidateActions?.length || 0})
            </button>
            <button
              onClick={() => setFilterType('SAFE')}
              className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                filterType === 'SAFE' ? 'bg-emerald-500 text-black font-semibold shadow' : 'text-emerald-400 hover:text-white'
              }`}
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Safe For Simulation ({safeCount})
            </button>
            <button
              onClick={() => setFilterType('REJECTED')}
              className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                filterType === 'REJECTED' ? 'bg-rose-500 text-white font-semibold shadow' : 'text-rose-400 hover:text-white'
              }`}
            >
              <XCircle className="w-3.5 h-3.5" />
              Rejected ({rejectedCount})
            </button>
            <button
              onClick={() => setFilterType('NEEDS_DATA')}
              className={`px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                filterType === 'NEEDS_DATA' ? 'bg-amber-500 text-black font-semibold shadow' : 'text-amber-400 hover:text-white'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              Needs More Data ({needsDataCount})
            </button>
          </div>
        </div>
      </div>

      {/* 2. Action Evaluation Cards Grid */}
      <div className="space-y-5">
        {filtered && filtered.map((act) => {
          const isSafe = act.is_safe || act.status === 'SAFE_FOR_SIMULATION' || act.status === 'APPROVED';
          const isNeedsData = act.status === 'NEEDS_MORE_DATA';
          const isRejected = act.status === 'REJECTED';

          return (
            <div
              key={act.id}
              className={`rounded-xl border p-5 transition-all ${
                isSafe 
                  ? 'bg-gray-900/95 border-emerald-500/40 shadow-lg shadow-emerald-950/20' 
                  : isNeedsData
                    ? 'bg-gray-950/90 border-amber-500/40'
                    : 'bg-gray-950/80 border-rose-500/40 opacity-90'
              }`}
            >
              {/* Card Header & Status Indicator */}
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3 border-b border-gray-800 pb-4">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-1.5">
                    <span className="text-xs font-mono uppercase tracking-wider text-cyan-400 font-semibold">
                      {act.category}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800 text-gray-400 border border-gray-700">
                      Complexity: {act.implementation_complexity || act.implementation_time}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800 text-cyan-300 border border-gray-700">
                      Confidence: {act.confidence || act.confidence_score}%
                    </span>
                    {act.is_production_safe_savings && (
                      <span className="text-[10px] font-bold font-mono px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 flex items-center gap-1">
                        <BadgeCheck className="w-3 h-3 text-emerald-400" />
                        PRODUCTION-SAFE SAVINGS QUALIFIED
                      </span>
                    )}
                  </div>
                  <h3 className="text-base font-bold text-white leading-tight">
                    {act.title}
                  </h3>
                  <p className="text-xs text-gray-300 mt-1 max-w-3xl leading-relaxed">
                    {act.proposed_change || act.description}
                  </p>
                </div>

                {/* Primary Decision Status Pill */}
                <div className="flex sm:flex-col items-end gap-2 shrink-0">
                  <span className={`text-xs font-bold font-mono px-3.5 py-1.5 rounded-lg flex items-center gap-1.5 shadow ${
                    isSafe 
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/50' 
                      : isNeedsData
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50'
                        : 'bg-rose-500/20 text-rose-300 border border-rose-500/50'
                  }`}>
                    {isSafe && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                    {isNeedsData && <AlertTriangle className="w-4 h-4 text-amber-400" />}
                    {isRejected && <XCircle className="w-4 h-4 text-rose-400" />}
                    {isSafe ? (act.status === 'APPROVED' ? 'APPROVED & SYNCHRONIZED' : 'SAFE FOR SIMULATION') : (isNeedsData ? 'NEEDS MORE DATA' : 'REJECTED')}
                  </span>

                  {isSafe && (
                    <button
                      onClick={() => onLaunchWhatIf(act.id)}
                      className="px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 transition-all active:scale-95"
                    >
                      <Sliders className="w-3.5 h-3.5" />
                      Run What-If Simulation
                    </button>
                  )}
                </div>
              </div>

              {/* Metrics Bar */}
              <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs font-mono">
                <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Energy Impact</span>
                  <span className="font-bold text-emerald-400 text-sm">
                    {act.energy_savings_pct > 0 ? `-${act.energy_savings_pct}%` : '0.0%'}
                  </span>
                  <span className="text-[10px] text-gray-400 block mt-0.5">
                    {act.expected_energy_kwh_per_day ? `-${act.expected_energy_kwh_per_day} kWh/d` : 'No kWh loss'}
                  </span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Monthly Cost Impact</span>
                  <span className="font-bold text-cyan-400 text-sm">
                    ₹{act.monthly_cost_savings_inr?.toLocaleString() || 0}
                  </span>
                  <span className="text-[10px] text-gray-400 block mt-0.5">₹/month savings</span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">CO2 Reduction</span>
                  <span className="font-bold text-emerald-400 text-sm">
                    {act.co2_reduction_kg > 0 ? `-${act.co2_reduction_kg} kg` : '0 kg'}
                  </span>
                  <span className="text-[10px] text-gray-400 block mt-0.5">Grid emissions</span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Throughput Impact</span>
                  <span className={`font-bold text-sm ${act.production_impact_pct < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {act.production_impact_pct}%
                  </span>
                  <span className="text-[10px] text-gray-400 block mt-0.5">Daily dispatch</span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Quality Tolerance</span>
                  <span className={`font-bold text-sm ${act.quality_impact_pct < 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {act.quality_impact_pct}%
                  </span>
                  <span className="text-[10px] text-gray-400 block mt-0.5">Scrap risk</span>
                </div>

                <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
                  <span className="text-gray-500 text-[10px] block">Machine Risk</span>
                  <span className={`font-bold text-sm ${act.machine_health_risk === 'High' ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {act.machine_health_risk || act.risk_level}
                  </span>
                  <span className="text-[10px] text-gray-400 block mt-0.5">Asset health</span>
                </div>
              </div>

              {/* Explicit Rejection Reason Banner (if unsafe or needs data) */}
              {(!isSafe || isNeedsData) && act.rejection_reason && (
                <div className={`mt-4 p-3 rounded-lg border text-xs space-y-1 ${
                  isNeedsData 
                    ? 'bg-amber-950/30 border-amber-500/40 text-amber-200' 
                    : 'bg-rose-950/40 border-rose-500/40 text-rose-200'
                }`}>
                  <div className={`flex items-center gap-1.5 font-bold ${isNeedsData ? 'text-amber-400' : 'text-rose-400'}`}>
                    {isNeedsData ? <AlertTriangle className="w-4 h-4 shrink-0" /> : <ShieldAlert className="w-4 h-4 shrink-0" />}
                    <span>{isNeedsData ? 'TRUST PROTOCOL WITHHOLDING NOTICE' : 'SAFETY GATE VIOLATION DETAIL'}</span>
                  </div>
                  <p className="leading-relaxed pl-5 font-mono text-[11px]">
                    {act.rejection_reason}
                  </p>
                </div>
              )}

              {/* Manufacturing Constraints Checklist */}
              <div className="mt-4 space-y-2">
                <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block">
                  Deterministic Constraint Gate Checklist:
                </span>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                  {act.constraints?.map((c, idx) => (
                    <div 
                      key={idx} 
                      className={`p-2.5 rounded-lg border flex items-start gap-2.5 ${
                        c.passed 
                          ? 'bg-gray-950/50 border-gray-800' 
                          : isNeedsData
                            ? 'bg-amber-950/20 border-amber-500/40'
                            : 'bg-rose-950/20 border-rose-500/40'
                      }`}
                    >
                      {c.passed ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        isNeedsData ? (
                          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                        ) : (
                          <XCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                        )
                      )}

                      <div className="space-y-0.5 w-full">
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-gray-200">{c.name}</span>
                          <span className={`text-[10px] font-bold font-mono px-1.5 py-0.2 rounded ${
                            c.passed ? 'text-emerald-400' : (isNeedsData ? 'text-amber-400' : 'text-rose-400')
                          }`}>
                            {c.passed ? 'PASSED' : (isNeedsData ? 'EVIDENCE GAP' : 'VIOLATED')}
                          </span>
                        </div>
                        <div className="text-[11px] text-gray-400 font-mono">
                          Threshold: {c.threshold} | Projected: <strong className={c.passed ? 'text-emerald-300' : (isNeedsData ? 'text-amber-300' : 'text-rose-300')}>{c.projected_value}</strong>
                        </div>
                        {c.violation_detail && (
                          <div className={`text-[10px] pt-1 font-sans ${isNeedsData ? 'text-amber-300' : 'text-rose-300'}`}>
                            {c.violation_detail}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* 3. Decision Explanation Panels (Section 6 Requirement) */}
              <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-3 pt-3 border-t border-gray-800 text-xs">
                {/* WHY THIS ACTION? */}
                <div className="p-3 rounded-lg bg-gray-950/60 border border-gray-800 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-cyan-400">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>WHY THIS ACTION?</span>
                  </div>
                  <p className="text-gray-300 leading-relaxed text-[11px]">
                    {act.why_this_action || "Optimizes operating setpoint while respecting process physical boundaries."}
                  </p>
                </div>

                {/* WHY NOT THE ALTERNATIVE? */}
                <div className="p-3 rounded-lg bg-gray-950/60 border border-gray-800 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-amber-400">
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>WHY NOT THE ALTERNATIVE?</span>
                  </div>
                  <p className="text-gray-300 leading-relaxed text-[11px]">
                    {act.why_not_alternative || "Alternative candidate interventions breached physical boundary constraints (pressure collapse, cold shut scrap, or unverified sensor telemetry)."}
                  </p>
                </div>
              </div>

            </div>
          );
        })}
      </div>

    </div>
  );
}
