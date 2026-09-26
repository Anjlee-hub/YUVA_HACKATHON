import React, { useState } from 'react';
import { 
  Cpu, 
  Activity, 
  Flame, 
  Wind, 
  Droplets, 
  Fan, 
  Boxes, 
  Hammer, 
  AlertTriangle, 
  CheckCircle2, 
  X,
  TrendingUp,
  Clock,
  Gauge,
  HelpCircle,
  ShieldCheck
} from 'lucide-react';

const MACHINE_ICONS = {
  furnace_01: Flame,
  furnace_02: Flame,
  compressor_01: Wind,
  compressor_02: Wind,
  pump_01: Droplets,
  cooling_system: Fan,
  casting_line: Boxes,
  finishing_line: Hammer
};

export default function DigitalTwin({ machines, onSelectAnomalyMachine }) {
  const [selectedMachine, setSelectedMachine] = useState(null);

  return (
    <div className="space-y-6">
      
      {/* Header Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-gray-900/60 border border-gray-800 p-4 rounded-xl">
        <div>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">
              Operational Digital Twin (Shakti Foundry Plant 01)
            </h2>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Lightweight operational state model for 8 primary foundry units. Click any machine to inspect active telemetry, thermodynamic balance, and missing IoT instrumentation.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-gray-800 border border-gray-700 text-gray-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span> 7 Operational
          </span>
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-rose-950/40 border border-rose-500/40 text-rose-300">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span> Active Anomalies
          </span>
        </div>
      </div>

      {/* 8 Machine Operational Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {machines && machines.map((m) => {
          const Icon = MACHINE_ICONS[m.id] || Cpu;
          const isAnomaly = m.is_anomaly;

          return (
            <div
              key={m.id}
              onClick={() => setSelectedMachine(m)}
              className={`p-4 rounded-xl border transition-all cursor-pointer glass-card-hover flex flex-col justify-between ${
                isAnomaly
                  ? 'bg-rose-950/20 border-rose-500/50 hover:border-rose-400 shadow-lg shadow-rose-950/30'
                  : 'bg-gray-900/80 border-gray-800 hover:border-gray-700'
              }`}
            >
              <div>
                {/* Card Header */}
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-2.5">
                    <div className={`p-2 rounded-lg ${
                      isAnomaly ? 'bg-rose-500/20 text-rose-400' : 'bg-gray-800 text-cyan-400'
                    }`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <span className="text-[10px] uppercase font-mono tracking-wider text-gray-400">
                        {m.category}
                      </span>
                      <h3 className="text-sm font-bold text-white leading-tight">
                        {m.name.split('(')[0]}
                      </h3>
                    </div>
                  </div>

                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    isAnomaly 
                      ? 'bg-rose-500 text-white animate-pulse' 
                      : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  }`}>
                    {isAnomaly ? 'ANOMALY' : 'OPTIMAL'}
                  </span>
                </div>

                {/* Machine Primary Telemetry */}
                <div className="mt-4 grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-gray-950/60 border border-gray-800/80">
                    <span className="text-gray-500 text-[10px] block">Current Power</span>
                    <span className="text-white font-bold text-sm">{m.current_power_kw}</span>
                    <span className="text-gray-400 text-[10px] ml-1">kW</span>
                  </div>

                  <div className="p-2 rounded bg-gray-950/60 border border-gray-800/80">
                    <span className="text-gray-500 text-[10px] block">Specific Energy</span>
                    <span className={`font-bold text-sm ${isAnomaly ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {m.actual_sec}
                    </span>
                    <span className="text-gray-400 text-[10px] ml-1">
                      {m.category.includes('Melting') ? 'kWh/t' : 'kWh'}
                    </span>
                  </div>
                </div>

                {/* Dynamic Telemetry Specs */}
                <div className="mt-3 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between text-gray-400">
                    <span>Runtime / Idle:</span>
                    <span className="font-mono text-gray-200">
                      {m.runtime_today_hrs}h / <span className={m.idle_time_today_hrs > 2.0 ? 'text-amber-400 font-bold' : ''}>{m.idle_time_today_hrs}h</span>
                    </span>
                  </div>

                  {m.temperature_c !== null && (
                    <div className="flex items-center justify-between text-gray-400">
                      <span>Temperature:</span>
                      <span className="font-mono text-gray-200">{m.temperature_c} °C</span>
                    </div>
                  )}

                  {m.pressure_bar !== null && (
                    <div className="flex items-center justify-between text-gray-400">
                      <span>Pressure:</span>
                      <span className="font-mono text-gray-200">{m.pressure_bar} bar</span>
                    </div>
                  )}

                  {m.vibration_mms !== null ? (
                    <div className="flex items-center justify-between text-gray-400">
                      <span>Vibration:</span>
                      <span className="font-mono text-gray-200">{m.vibration_mms} mm/s</span>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between text-amber-400/90 text-[11px]">
                      <span>Vibration:</span>
                      <span className="font-mono italic text-[10px]">Sensor Missing</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Card Footer: Health & Missing Sensors */}
              <div className="mt-4 pt-3 border-t border-gray-800/80 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="text-gray-500 text-[11px]">Health:</span>
                  <span className={`font-mono font-bold ${
                    m.health_score < 75 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {m.health_score}%
                  </span>
                </div>

                {m.sensors_missing?.length > 0 ? (
                  <span className="text-[10px] text-amber-300 font-medium bg-amber-500/10 px-1.5 py-0.5 rounded border border-amber-500/20">
                    {m.sensors_missing.length} unmonitored
                  </span>
                ) : (
                  <span className="text-[10px] text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3 h-3" /> Fully Instrumented
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Detailed Machine Modal */}
      {selectedMachine && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in">
          <div className="bg-[#111827] border border-gray-700 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto shadow-2xl p-6">
            
            <div className="flex items-start justify-between border-b border-gray-800 pb-4">
              <div>
                <span className="text-xs font-mono uppercase tracking-wider text-cyan-400">
                  {selectedMachine.category} Digital Twin Telemetry
                </span>
                <h3 className="text-lg font-bold text-white mt-0.5">
                  {selectedMachine.name}
                </h3>
              </div>
              <button 
                onClick={() => setSelectedMachine(null)}
                className="p-1 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="mt-4 space-y-4">
              
              {/* Telemetry Matrix */}
              <div className="grid grid-cols-3 gap-3 font-mono text-xs">
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                  <span className="text-gray-400 text-[10px] block">Current Power</span>
                  <span className="text-lg font-bold text-white">{selectedMachine.current_power_kw} kW</span>
                  <span className="text-gray-500 text-[10px] block mt-1">Rated: {selectedMachine.rated_power_kw} kW</span>
                </div>
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                  <span className="text-gray-400 text-[10px] block">Energy Consumed Today</span>
                  <span className="text-lg font-bold text-white">{selectedMachine.energy_today_kwh} kWh</span>
                  <span className="text-gray-500 text-[10px] block mt-1">Runtime: {selectedMachine.runtime_today_hrs} hrs</span>
                </div>
                <div className="p-3 rounded-lg bg-gray-900 border border-gray-800">
                  <span className="text-gray-400 text-[10px] block">Idle Unloaded Time</span>
                  <span className={`text-lg font-bold ${selectedMachine.idle_time_today_hrs > 2.0 ? 'text-amber-400' : 'text-gray-300'}`}>
                    {selectedMachine.idle_time_today_hrs} hrs
                  </span>
                  <span className="text-gray-500 text-[10px] block mt-1">Idle power ~20-25%</span>
                </div>
              </div>

              {/* SEC Comparison */}
              <div className="p-4 rounded-xl bg-gray-900 border border-gray-800">
                <h4 className="text-xs font-semibold text-gray-300 mb-2">Production-Aware SEC Evaluation</h4>
                <div className="flex items-center justify-between text-xs font-mono">
                  <div>
                    <span className="text-gray-400 text-[11px]">Actual SEC:</span>
                    <span className={`ml-2 text-sm font-bold ${selectedMachine.is_anomaly ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {selectedMachine.actual_sec}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400 text-[11px]">Expected Baseline:</span>
                    <span className="ml-2 text-sm font-bold text-gray-300">
                      {selectedMachine.expected_sec}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-400 text-[11px]">Deviation:</span>
                    <span className={`ml-2 text-sm font-bold ${selectedMachine.is_anomaly ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {selectedMachine.sec_deviation_pct > 0 ? `+${selectedMachine.sec_deviation_pct}%` : `${selectedMachine.sec_deviation_pct}%`}
                    </span>
                  </div>
                </div>
              </div>

              {/* Sensory Readiness: Active vs Missing */}
              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-gray-900 border border-gray-800">
                  <span className="text-emerald-400 font-semibold block mb-2">Active Sensors</span>
                  <ul className="space-y-1 text-gray-300">
                    {selectedMachine.sensors_active?.map((s, idx) => (
                      <li key={idx} className="flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="p-3 rounded-xl bg-gray-900 border border-gray-800">
                  <span className="text-amber-400 font-semibold block mb-2">Missing Retrofit Opportunities</span>
                  {selectedMachine.sensors_missing?.length > 0 ? (
                    <ul className="space-y-1 text-gray-300">
                      {selectedMachine.sensors_missing.map((s, idx) => (
                        <li key={idx} className="flex items-center gap-1.5 text-amber-300/90">
                          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                          <span>{s}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-400 text-xs italic">All key physical telemetry installed.</p>
                  )}
                </div>
              </div>

              {selectedMachine.is_anomaly && (
                <div className="p-3 rounded-xl bg-rose-950/30 border border-rose-500/40 text-xs text-rose-300 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
                    <span>This machine has an active SEC anomaly. Inspect root cause decomposition.</span>
                  </div>
                  <button
                    onClick={() => {
                      setSelectedMachine(null);
                      onSelectAnomalyMachine(selectedMachine.id);
                    }}
                    className="px-3 py-1 rounded bg-rose-500 hover:bg-rose-400 text-black font-semibold"
                  >
                    View Root Cause
                  </button>
                </div>
              )}

            </div>
          </div>
        </div>
      )}

    </div>
  );
}
