import React from 'react';
import { 
  Zap, 
  Play, 
  Settings2, 
  ShieldCheck, 
  AlertTriangle, 
  Flame, 
  Clock, 
  HelpCircle, 
  RotateCcw,
  Activity,
  CheckCircle2
} from 'lucide-react';

export default function Header({ 
  overview, 
  onScenarioChange, 
  onOpenDemo, 
  onOpenConfig, 
  onResetActions,
  activeScenario 
}) {
  return (
    <header className="sticky top-0 z-40 bg-[#0B1220]/95 backdrop-blur-md border-b border-gray-800 px-4 py-2.5">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-3">
        
        {/* Brand & Factory Context */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-emerald-500 to-cyan-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-sm tracking-wide text-white">YUVA YODHA</span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                Schneider Electric Hackathon Challenge 04
              </span>
              <span className="text-[10px] uppercase tracking-wider font-mono px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                DEMO / SIMULATION
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs text-gray-400">
              <span className="font-medium text-gray-200">Shakti Foundry — Plant 01</span>
              <span>•</span>
              <span>Peenya, Bengaluru</span>
              <span>•</span>
              <span className="flex items-center gap-1 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Digital Twin Online
              </span>
            </div>
          </div>
        </div>

        {/* Central Controls: Demo Scenarios */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="text-xs text-gray-400 font-medium hidden xl:block">
            Injected Scenarios:
          </div>

          <div className="inline-flex rounded-lg bg-gray-900/90 p-0.5 border border-gray-800 text-xs">
            <button
              onClick={() => onScenarioChange('normal')}
              className={`px-2.5 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                activeScenario === 'normal' 
                  ? 'bg-emerald-500 text-black font-semibold shadow' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Baseline normal operations"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              Normal
            </button>

            <button
              onClick={() => onScenarioChange('compressor_waste')}
              className={`px-2.5 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                activeScenario === 'compressor_waste' 
                  ? 'bg-amber-500 text-black font-semibold shadow' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Compressor idling unloaded during changeovers"
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              1. Compressor 02 Idle
            </button>

            <button
              onClick={() => onScenarioChange('furnace_degradation')}
              className={`px-2.5 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                activeScenario === 'furnace_degradation' 
                  ? 'bg-rose-500 text-white font-semibold shadow' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Holding furnace 02 refractory degradation & shell heat loss"
            >
              <Flame className="w-3.5 h-3.5" />
              2. Furnace 02 Degradation
            </button>

            <button
              onClick={() => onScenarioChange('production_scheduling')}
              className={`px-2.5 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                activeScenario === 'production_scheduling' 
                  ? 'bg-purple-500 text-white font-semibold shadow' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Peak TOD tariff melt rescheduling"
            >
              <Clock className="w-3.5 h-3.5" />
              3. TOD Scheduling
            </button>

            <button
              onClick={() => onScenarioChange('missing_sensor')}
              className={`px-2.5 py-1.5 rounded-md flex items-center gap-1.5 transition-all ${
                activeScenario === 'missing_sensor' 
                  ? 'bg-cyan-500 text-black font-semibold shadow' 
                  : 'text-gray-400 hover:text-white'
              }`}
              title="Missing vibration sensor: low sensory evidence & withheld diagnosis"
            >
              <HelpCircle className="w-3.5 h-3.5" />
              4. Missing Vibration Sensor
            </button>
          </div>
        </div>

        {/* Action Buttons: 2-Min Demo, SME Setup, Reset */}
        <div className="flex items-center gap-2">
          {overview?.applied_actions?.length > 0 && (
            <button
              onClick={onResetActions}
              className="px-2.5 py-1.5 text-xs rounded-lg border border-gray-700 bg-gray-800 text-gray-300 hover:bg-gray-700 flex items-center gap-1.5"
              title="Reset simulated action optimizations back to baseline"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              Reset Actions
            </button>
          )}

          <button
            onClick={onOpenDemo}
            className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-black flex items-center gap-1.5 shadow-lg shadow-emerald-500/20 active:scale-95 transition-all"
          >
            <Play className="w-3.5 h-3.5 fill-black" />
            2-Min Guided Demo
          </button>

          <button
            onClick={onOpenConfig}
            className="p-1.5 text-xs rounded-lg border border-gray-700 bg-gray-800/80 text-gray-300 hover:bg-gray-700 hover:text-white"
            title="SME Factory Configuration & Data Sources"
          >
            <Settings2 className="w-4 h-4" />
          </button>
        </div>

      </div>
    </header>
  );
}
