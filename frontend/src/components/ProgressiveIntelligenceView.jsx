import React from 'react';
import { 
  Layers, 
  CheckCircle2, 
  XCircle, 
  ArrowRight, 
  Sparkles, 
  ShieldCheck, 
  Cpu, 
  FileText, 
  Gauge, 
  Radar, 
  Bot,
  Unlock,
  AlertTriangle
} from 'lucide-react';

export default function ProgressiveIntelligenceView({ readiness, onSetLevel }) {
  const currentLvl = readiness?.status?.current_level ?? 3;
  const levels = readiness?.levels || [];
  const status = readiness?.status;
  const sensors = status?.sensor_metrics || [];

  const currentLevelMeta = levels.find(l => l.level === currentLvl) || levels[currentLvl] || {};

  return (
    <div className="space-y-6">
      
      {/* 1. Header */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Layers className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">
                SME Progressive Data Maturity & Readiness Model (Levels 0 → 4)
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1 max-w-2xl leading-relaxed">
              <strong className="text-white">SME Retrofit-First Roadmap:</strong> Indian foundries and job shops start at Level 0 with utility bills.
              Our engine progressively unlocks advanced intelligence as retrofit sub-meters and IoT sensors are added.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-indigo-950/30 border border-indigo-500/30 text-xs font-mono text-indigo-300">
            <span className="block text-[10px] text-gray-400 uppercase">Current Factory State</span>
            <div className="font-bold text-white mt-0.5">
              Level {currentLvl}: {currentLevelMeta.name || `Level ${currentLvl}`}
            </div>
            <span className="text-[10px] text-emerald-400 block mt-1">
              Sensory Confidence: {status?.overall_confidence_pct}%
            </span>
          </div>
        </div>
      </div>

      {/* 2. Interactive Level Progression Selector */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
          Simulate SME Data Maturity Progression (Levels 0 to 4):
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {levels.map((lvl) => {
            const isSelected = currentLvl === lvl.level;

            return (
              <div
                key={lvl.level}
                onClick={() => onSetLevel(lvl.level)}
                className={`p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${
                  isSelected
                    ? 'bg-indigo-950/40 border-indigo-500 shadow-xl shadow-indigo-950/50 scale-[1.02]'
                    : 'bg-gray-900/80 border-gray-800 hover:border-gray-700'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                      LEVEL {lvl.level}
                    </span>
                    {isSelected && (
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                        CURRENT
                      </span>
                    )}
                  </div>

                  <h4 className="text-xs font-bold text-white">
                    {lvl.tagline}
                  </h4>
                  <p className="text-[11px] text-gray-400 mt-1 line-clamp-3">
                    {lvl.description}
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-gray-800">
                  <button
                    className={`w-full py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isSelected
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    {isSelected ? 'Active Maturity' : `Switch to Level ${lvl.level}`}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 3. 4-Box Dynamic State Breakdown (Available, Missing, Possible, Unlocks) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Box A: What is Available */}
        <div className="p-5 rounded-xl bg-gray-900/90 border border-gray-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4" />
            What Is Currently Available (Level {currentLvl})
          </h4>
          <ul className="space-y-2 text-xs">
            {(status?.what_is_available || currentLevelMeta.what_is_available || []).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-gray-300">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0 mt-1.5"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Box B: What is Missing */}
        <div className="p-5 rounded-xl bg-gray-900/90 border border-gray-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
            <AlertTriangle className="w-4 h-4" />
            What Telemetry Is Missing (Level {currentLvl})
          </h4>
          <ul className="space-y-2 text-xs">
            {(status?.what_is_missing || currentLevelMeta.what_is_missing || []).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-gray-400">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0 mt-1.5"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Box C: What Intelligence Is Currently Possible */}
        <div className="p-5 rounded-xl bg-gray-900/90 border border-gray-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
            <Gauge className="w-4 h-4" />
            Intelligence Currently Possible
          </h4>
          <ul className="space-y-2 text-xs">
            {(status?.currently_possible_intelligence || currentLevelMeta.currently_possible_intelligence || []).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-gray-300">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0 mt-1.5"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
          <div className="pt-2 border-t border-gray-800/80 text-[11px] font-mono text-gray-400">
            Diagnostic Trust Status: {status?.can_diagnose_mechanical ? 'Mechanical wear analysis allowed' : 'Mechanical diagnoses withheld (missing vibration)'}
          </div>
        </div>

        {/* Box D: What Next Level Unlocks */}
        <div className="p-5 rounded-xl bg-gray-900/90 border border-gray-800 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
            <Unlock className="w-4 h-4" />
            What Next Level ({Math.min(currentLvl + 1, 4)}) Unlocks
          </h4>
          <ul className="space-y-2 text-xs">
            {(status?.next_level_unlocks || currentLevelMeta.next_level_unlocks || []).map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 text-purple-200">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-400 shrink-0 mt-1.5"></span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 4. Sensor Completeness & Data Quality Audit */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Factory Sensor Confidence Matrix (Completeness, Freshness, Consistency)
            </h3>
            <p className="text-xs text-gray-400 mt-0.5">
              Scores dynamically evaluate signal loss, communication lag, and data drift.
            </p>
          </div>
          <span className="text-xs font-mono font-bold text-emerald-400">
            Overall Confidence: {status?.overall_confidence_pct}%
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-gray-800 text-gray-400 font-mono text-[11px]">
                <th className="pb-2.5 font-semibold">SENSOR / DATA STREAM</th>
                <th className="pb-2.5 font-semibold text-center">COMPLETENESS</th>
                <th className="pb-2.5 font-semibold text-center">FRESHNESS</th>
                <th className="pb-2.5 font-semibold text-center">CONSISTENCY</th>
                <th className="pb-2.5 font-semibold text-center">OVERALL SCORE</th>
                <th className="pb-2.5 font-semibold">STATUS / AUDIT NOTE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60 font-mono">
              {sensors.map((s, idx) => (
                <tr key={idx} className="hover:bg-gray-800/20">
                  <td className="py-2.5 font-sans font-medium text-white">{s.sensor_name}</td>
                  <td className="py-2.5 text-center text-gray-300">{s.completeness_pct}%</td>
                  <td className="py-2.5 text-center text-gray-300">{s.freshness_pct}%</td>
                  <td className="py-2.5 text-center text-gray-300">{s.consistency_pct}%</td>
                  <td className="py-2.5 text-center font-bold">
                    <span className={`px-2 py-0.5 rounded ${
                      s.overall_pct >= 90 
                        ? 'bg-emerald-500/20 text-emerald-400' 
                        : (s.overall_pct >= 70 ? 'bg-cyan-500/20 text-cyan-400' : 'bg-amber-500/20 text-amber-400')
                    }`}>
                      {s.overall_pct}%
                    </span>
                  </td>
                  <td className="py-2.5 font-sans text-gray-400 text-[11px]">{s.note}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
