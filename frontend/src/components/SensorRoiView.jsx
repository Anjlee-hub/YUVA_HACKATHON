import React from 'react';
import { 
  Radar, 
  Sparkles, 
  CheckCircle2, 
  IndianRupee, 
  TrendingUp, 
  ArrowRight, 
  ShieldCheck, 
  Clock, 
  Zap,
  Cpu,
  Layers,
  HelpCircle,
  Award
} from 'lucide-react';

export default function SensorRoiView({ sensorRecommendations }) {
  const topSensor = sensorRecommendations && sensorRecommendations.length > 0 ? sensorRecommendations[0] : null;

  return (
    <div className="space-y-6">
      
      {/* 1. Header & Differentiation Concept */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Radar className="w-5 h-5 text-cyan-400" />
              <h2 className="text-base font-bold text-white">
                Sensor & Data Acquisition ROI Advisor
              </h2>
            </div>
            <p className="text-xs text-gray-400 mt-1 max-w-3xl leading-relaxed">
              <strong className="text-cyan-400">SME Retrofit-First Roadmap:</strong> When the Data Trust layer identifies missing telemetry 
              (e.g., Compressor 02 vibration accelerometer), this advisor ranks potential IoT retrofit sensors by evidence gain, 
              capital outlay, and payback period.
            </p>
          </div>

          <div className="p-3 rounded-lg bg-cyan-950/30 border border-cyan-500/30 text-xs font-mono text-cyan-300">
            <span className="block text-[10px] text-gray-400 uppercase">Transparent Scoring Formula</span>
            <div className="font-bold text-white mt-0.5">
              Score = (Info Value + Opportunity + Evidence Gain) / (Capex Index + Payback)
            </div>
          </div>
        </div>

        {/* Clear Illustrative Disclaimer */}
        <div className="mt-4 pt-3 border-t border-gray-800 flex items-center gap-2 text-xs text-amber-400/90 font-mono">
          <HelpCircle className="w-4 h-4 shrink-0" />
          <span>
            DISCLAIMER: All sensor prices, installation capex, and ROI metrics are ILLUSTRATIVE DEMO ASSUMPTIONS. 
            Do not present as vendor quotations or real market pricing.
          </span>
        </div>
      </div>

      {/* 2. Top Recommended Sensor Banner (NEXT BEST DATA SOURCE) */}
      {topSensor && (
        <div className="p-5 rounded-xl bg-gradient-to-r from-cyan-950/70 via-gray-900 to-emerald-950/70 border border-cyan-500/50 shadow-xl space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono font-bold px-2.5 py-1 rounded bg-cyan-500 text-black flex items-center gap-1">
                <Award className="w-3.5 h-3.5" />
                NEXT BEST DATA SOURCE
              </span>
              <span className="text-xs text-cyan-300 font-semibold font-mono">
                {topSensor.machine_name}
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300">
                Category: {topSensor.sensor_category}
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 font-bold">
                Payback: {topSensor.payback_months} Months
              </span>
            </div>
          </div>

          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              {topSensor.sensor_type}
            </h3>
            <p className="text-xs text-gray-300 mt-1.5 leading-relaxed">
              {topSensor.why_needed}
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
            <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
              <span className="text-gray-500 text-[10px] block">Hardware + Install Capex</span>
              <span className="text-white font-bold text-sm">
                ₹{(topSensor.estimated_capex_inr + topSensor.estimated_installation_inr).toLocaleString()}
              </span>
              <span className="text-[10px] text-gray-500 block">₹{topSensor.estimated_capex_inr.toLocaleString()} hw + ₹{topSensor.estimated_installation_inr.toLocaleString()} inst</span>
            </div>
            <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
              <span className="text-gray-500 text-[10px] block">Annual Opportunity</span>
              <span className="text-emerald-400 font-bold text-sm">
                ₹{topSensor.potential_savings_unlocked_inr_yr.toLocaleString()} / yr
              </span>
              <span className="text-[10px] text-gray-500 block">Prevents catastrophic air end drag</span>
            </div>
            <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
              <span className="text-gray-500 text-[10px] block">Evidence Gain</span>
              <span className="text-cyan-400 font-bold text-sm">
                +{topSensor.evidence_improvement_pct}%
              </span>
              <span className="text-[10px] text-gray-500 block">Unlocks withheld diagnosis</span>
            </div>
            <div className="p-2.5 rounded-lg bg-gray-950/80 border border-gray-800">
              <span className="text-gray-500 text-[10px] block">Transparent Priority Score</span>
              <span className="text-purple-400 font-bold text-sm">
                {topSensor.priority_score} / 10
              </span>
              <span className="text-[10px] text-gray-500 block">Rank #1 overall</span>
            </div>
          </div>

          <div className="pt-2 border-t border-gray-800">
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider block mb-1">
              Capabilities Unlocked for the Factory:
            </span>
            <div className="flex flex-wrap gap-2 text-xs">
              {topSensor.unlocked_capabilities?.map((u, idx) => (
                <span key={idx} className="px-2.5 py-1 rounded bg-gray-800/80 text-gray-300 border border-gray-700/60 flex items-center gap-1.5">
                  <CheckCircle2 className="w-3 h-3 text-cyan-400" />
                  {u}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 3. Ranked Sensor Candidates List */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider px-1">
          Candidate Retrofit Sensor Options (Ranked by Score)
        </h3>

        <div className="space-y-3">
          {sensorRecommendations && sensorRecommendations.map((s) => (
            <div
              key={s.sensor_id}
              className={`p-4 rounded-xl border space-y-3 transition-all ${
                s.is_next_best 
                  ? 'bg-gray-900/90 border-cyan-500/40 shadow-lg' 
                  : 'bg-gray-900/70 border-gray-800 hover:border-gray-700'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 border-b border-gray-800 pb-3">
                <div className="flex items-start gap-3">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold font-mono shrink-0 mt-0.5 ${
                    s.is_next_best ? 'bg-cyan-500 text-black' : 'bg-gray-800 text-gray-400'
                  }`}>
                    {s.recommended_rank}
                  </span>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-gray-400 uppercase font-medium">
                        {s.machine_name}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-gray-800 text-gray-300 border border-gray-700">
                        {s.sensor_category}
                      </span>
                      {s.is_next_best && (
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold">
                          NEXT BEST DATA SOURCE
                        </span>
                      )}
                    </div>
                    <h4 className="text-sm font-bold text-white mt-1">
                      {s.sensor_type}
                    </h4>
                  </div>
                </div>

                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="px-2 py-1 rounded bg-gray-800 text-gray-300">
                    Priority Score: <strong className="text-cyan-400">{s.priority_score}</strong>
                  </span>
                  <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 font-bold border border-emerald-500/30">
                    {s.payback_months} mo payback
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                <div className="p-2 rounded bg-gray-950/60 border border-gray-800/80">
                  <span className="text-gray-500 text-[10px] block">Capex + Install</span>
                  <span className="text-gray-200 font-bold">
                    ₹{(s.estimated_capex_inr + s.estimated_installation_inr).toLocaleString()}
                  </span>
                </div>
                <div className="p-2 rounded bg-gray-950/60 border border-gray-800/80">
                  <span className="text-gray-500 text-[10px] block">Annual Opportunity</span>
                  <span className="text-emerald-400 font-bold">
                    ₹{s.potential_savings_unlocked_inr_yr.toLocaleString()} / yr
                  </span>
                </div>
                <div className="p-2 rounded bg-gray-950/60 border border-gray-800/80">
                  <span className="text-gray-500 text-[10px] block">Evidence Gain</span>
                  <span className="text-cyan-400 font-bold">
                    +{s.evidence_improvement_pct}%
                  </span>
                </div>
                <div className="p-2 rounded bg-gray-950/60 border border-gray-800/80">
                  <span className="text-gray-500 text-[10px] block">Information Value</span>
                  <span className="text-purple-400 font-bold">
                    {s.information_value_score} / 10 ({s.information_gain})
                  </span>
                </div>
              </div>

              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                {s.why_needed}
              </p>

              <div className="flex flex-wrap gap-1.5 pt-1 text-[11px]">
                {s.unlocked_capabilities?.map((c, idx) => (
                  <span key={idx} className="px-2 py-0.5 rounded bg-gray-800/60 text-gray-300 font-mono">
                    • {c}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
