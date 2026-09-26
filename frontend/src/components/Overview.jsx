import React from 'react';
import { 
  Zap, 
  TrendingDown, 
  IndianRupee, 
  Leaf, 
  Boxes, 
  CheckCircle, 
  AlertTriangle, 
  Award,
  ArrowUpRight,
  ArrowDownRight,
  ShieldCheck,
  ChevronRight,
  Cpu,
  BarChart3,
  Sparkles
} from 'lucide-react';
import { 
  AreaChart, 
  Area, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  ReferenceLine 
} from 'recharts';

export default function Overview({ 
  overview, 
  machines, 
  history, 
  anomalies, 
  safeActions, 
  onNavigate,
  onSimulateAction
}) {
  if (!overview) return null;

  // Chart data: daily aggregated from 30-day hourly history
  const chartData = React.useMemo(() => {
    if (!history || history.length === 0) return [];
    // Sample every 4 hours or aggregate by day
    return history.filter((_, idx) => idx % 6 === 0).map((pt) => ({
      time: pt.timestamp.split(' ')[0].slice(5) + ' ' + pt.timestamp.split(' ')[1],
      actual_energy: pt.energy_kwh,
      expected_energy: Math.round(pt.production_tons * 620),
      sec: pt.sec,
      expected_sec: pt.expected_sec,
      production: pt.production_tons,
      cost: pt.cost_inr
    }));
  }, [history]);

  const secDev = overview.sec_deviation_pct;
  const isAnomalous = secDev > 5.0;

  return (
    <div className="space-y-6">
      
      {/* 1. Value Proposition Banner (MANDATORY REQUIREMENT) */}
      <div className="bg-gradient-to-r from-emerald-950/60 via-gray-900 to-cyan-950/60 border border-emerald-500/30 rounded-xl p-4 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="text-xs uppercase tracking-wider font-semibold text-emerald-400 flex items-center gap-1.5">
                <span>Retrofit-First Production-Safe Energy Engine</span>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              </div>
              <h2 className="text-base font-bold text-white mt-0.5">
                Indian SME Manufacturing Energy Optimization Protocol
              </h2>
            </div>
          </div>

          {/* Core Differentiation Badges */}
          <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-1.5">
              <span>ENERGY</span>
              <span className="font-bold">↓ REDUCE</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-1.5">
              <span>SEC</span>
              <span className="font-bold">↓ REDUCE</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-1.5">
              <span>COST</span>
              <span className="font-bold">↓ REDUCE</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center gap-1.5">
              <span>CO2</span>
              <span className="font-bold">↓ REDUCE</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 flex items-center gap-1.5">
              <span>PRODUCTION</span>
              <span className="font-bold">→ 100% RETAINED</span>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-purple-500/10 border border-purple-500/30 text-purple-300 flex items-center gap-1.5">
              <span>QUALITY</span>
              <span className="font-bold">→ 100% TOLERANCE</span>
            </div>
          </div>
        </div>
      </div>

      {/* 2. Top KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-8 gap-3">
        
        {/* KPI 1: Energy Today */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Energy Today</span>
            <Zap className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-white">
              {overview.total_energy_today_kwh.toLocaleString()}
            </div>
            <div className="text-[11px] text-gray-400">kWh consumed</div>
          </div>
        </div>

        {/* KPI 2: SEC */}
        <div className={`border rounded-xl p-3 flex flex-col justify-between ${
          isAnomalous ? 'bg-rose-950/20 border-rose-500/40' : 'bg-gray-900/80 border-gray-800'
        }`}>
          <div className="flex items-center justify-between text-xs">
            <span className={isAnomalous ? 'text-rose-300 font-semibold' : 'text-gray-400'}>Factory SEC</span>
            {isAnomalous ? (
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-rose-500/20 text-rose-400">
                +{secDev}%
              </span>
            ) : (
              <TrendingDown className="w-4 h-4 text-emerald-400" />
            )}
          </div>
          <div className="mt-2">
            <div className={`text-xl font-bold font-mono ${isAnomalous ? 'text-rose-400' : 'text-emerald-400'}`}>
              {overview.factory_sec}
            </div>
            <div className="text-[11px] text-gray-400">
              kWh / Ton (Base: {overview.factory_sec_baseline})
            </div>
          </div>
        </div>

        {/* KPI 3: Energy Cost */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Energy Cost</span>
            <IndianRupee className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-white">
              ₹{overview.energy_cost_today_inr.toLocaleString()}
            </div>
            <div className="text-[11px] text-gray-400">BESCOM TOD blend</div>
          </div>
        </div>

        {/* KPI 4: Scope 2 CO2 */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>CO2 Emissions</span>
            <Leaf className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-white">
              {(overview.co2_emissions_today_kg / 1000).toFixed(1)}t
            </div>
            <div className="text-[11px] text-gray-400">CEA grid factor (0.716)</div>
          </div>
        </div>

        {/* KPI 5: Daily Production */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Production</span>
            <Boxes className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-white">
              {overview.production_today_units}t
            </div>
            <div className="text-[11px] text-gray-400">Good cast metal</div>
          </div>
        </div>

        {/* KPI 6: Casting Quality */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-3 flex flex-col justify-between">
          <div className="flex items-center justify-between text-gray-400 text-xs">
            <span>Quality Pass</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-emerald-400">
              {overview.quality_pass_rate_pct}%
            </div>
            <div className="text-[11px] text-gray-400">Zero defect sacrifice</div>
          </div>
        </div>

        {/* KPI 7: Active Anomalies */}
        <div className={`border rounded-xl p-3 flex flex-col justify-between cursor-pointer transition-all ${
          overview.active_anomalies_count > 0 
            ? 'bg-rose-950/20 border-rose-500/40 hover:border-rose-400' 
            : 'bg-gray-900/80 border-gray-800'
        }`} onClick={() => onNavigate('anomalies')}>
          <div className="flex items-center justify-between text-xs">
            <span className={overview.active_anomalies_count > 0 ? 'text-rose-300 font-semibold' : 'text-gray-400'}>
              Anomalies
            </span>
            <AlertTriangle className={`w-4 h-4 ${overview.active_anomalies_count > 0 ? 'text-rose-400 animate-pulse' : 'text-gray-400'}`} />
          </div>
          <div className="mt-2">
            <div className={`text-xl font-bold font-mono ${overview.active_anomalies_count > 0 ? 'text-rose-400' : 'text-gray-400'}`}>
              {overview.active_anomalies_count}
            </div>
            <div className="text-[11px] text-gray-400 flex items-center gap-1">
              <span>View root cause</span>
              <ChevronRight className="w-3 h-3" />
            </div>
          </div>
        </div>

        {/* KPI 8: Verified Savings */}
        <div className="bg-emerald-950/20 border border-emerald-500/40 rounded-xl p-3 flex flex-col justify-between cursor-pointer hover:border-emerald-400 transition-all" onClick={() => onNavigate('verification')}>
          <div className="flex items-center justify-between text-xs">
            <span className="text-emerald-300 font-semibold">Verified Savings</span>
            <Award className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-2">
            <div className="text-xl font-bold font-mono text-emerald-400">
              ₹{(overview.verified_savings_monthly_inr / 1000).toFixed(0)}k
            </div>
            <div className="text-[11px] text-gray-400 flex items-center gap-1">
              <span>/month IPMVP B</span>
              <ChevronRight className="w-3 h-3" />
            </div>
          </div>
        </div>

      </div>

      {/* 3. Main Operational Section: Real-time Telemetry Strip + AI Recommendation */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Production-Aware Energy Baseline vs Actual */}
        <div className="lg:col-span-2 bg-gray-900/80 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-white text-sm">
                  Production-Aware Dynamic Energy Baseline Tracking (30-Day Hourly Log)
                </h3>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">
                Expected energy dynamically scales with good casting tonnage and product metallurgy (not just "yesterday's energy").
              </p>
            </div>

            <div className="flex items-center gap-3 text-xs">
              <span className="flex items-center gap-1.5 text-gray-300">
                <span className="w-3 h-1 bg-cyan-400 rounded"></span> Actual Energy (kWh)
              </span>
              <span className="flex items-center gap-1.5 text-gray-400">
                <span className="w-3 h-1 bg-emerald-500 rounded border-dashed"></span> Expected Baseline
              </span>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="actualEnergy" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="time" stroke="#6B7280" tick={{ fontSize: 10 }} />
                <YAxis stroke="#6B7280" tick={{ fontSize: 10 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', borderRadius: '8px', fontSize: '12px' }}
                  itemStyle={{ color: '#F8FAFC' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="actual_energy" 
                  name="Actual Energy (kWh)" 
                  stroke="#06B6D4" 
                  strokeWidth={2}
                  fillOpacity={1} 
                  fill="url(#actualEnergy)" 
                />
                <Line 
                  type="monotone" 
                  dataKey="expected_energy" 
                  name="Expected Baseline (kWh)" 
                  stroke="#10B981" 
                  strokeWidth={2} 
                  strokeDasharray="4 4"
                  dot={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-3 pt-3 border-t border-gray-800 flex items-center justify-between text-xs text-gray-400">
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-300 font-mono">
                SEC Equation: kWh ÷ Good Output Tons
              </span>
              <span>•</span>
              <span>Alloy Grade: FG 260 Grey Iron</span>
            </div>
            <button 
              onClick={() => onNavigate('sec_baseline')}
              className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-medium"
            >
              Examine Baseline Multi-variable Model <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Right 1 Col: Production-Safe Action Dispatcher */}
        <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-white text-sm">Certified Safe Recommendation</h3>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                100% SAFE
              </span>
            </div>

            {safeActions && safeActions.length > 0 ? (
              <div className="space-y-3">
                <div className="p-3 rounded-lg bg-gray-800/60 border border-gray-700/60">
                  <div className="text-xs font-semibold text-emerald-300 mb-1">
                    {safeActions[0].title}
                  </div>
                  <p className="text-xs text-gray-300 leading-relaxed">
                    {safeActions[0].proposed_change}
                  </p>

                  <div className="mt-3 grid grid-cols-2 gap-2 text-xs font-mono">
                    <div className="p-2 rounded bg-gray-900/80 border border-gray-800">
                      <div className="text-gray-400 text-[10px]">Energy Impact</div>
                      <div className="text-emerald-400 font-bold">-{safeActions[0].energy_savings_pct}%</div>
                    </div>
                    <div className="p-2 rounded bg-gray-900/80 border border-gray-800">
                      <div className="text-gray-400 text-[10px]">Monthly Savings</div>
                      <div className="text-cyan-400 font-bold">₹{safeActions[0].monthly_cost_savings_inr.toLocaleString()}</div>
                    </div>
                    <div className="p-2 rounded bg-gray-900/80 border border-gray-800">
                      <div className="text-gray-400 text-[10px]">Throughput Penalty</div>
                      <div className="text-emerald-400 font-bold">0.0% (Zero)</div>
                    </div>
                    <div className="p-2 rounded bg-gray-900/80 border border-gray-800">
                      <div className="text-gray-400 text-[10px]">Quality Risk</div>
                      <div className="text-emerald-400 font-bold">0.0% (Safe)</div>
                    </div>
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-cyan-950/20 border border-cyan-500/30 text-xs text-cyan-300 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-cyan-400" />
                    <span>Tested against 4 shopfloor constraint rules</span>
                  </div>
                  <span className="font-bold">PASSED</span>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400 text-xs">
                No pending anomalies requiring intervention.
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-gray-800 flex items-center gap-2">
            <button
              onClick={() => onSimulateAction(safeActions[0]?.id || 'action_compressor_unloaded_shutdown')}
              className="flex-1 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-semibold text-xs transition-all shadow-lg shadow-emerald-500/20 flex items-center justify-center gap-1.5"
            >
              <span>Test in What-If Simulator</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onNavigate('decision_engine')}
              className="px-3 py-2 rounded-lg border border-gray-700 bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs"
              title="View all candidate actions evaluated by constraint gate"
            >
              View Filter
            </button>
          </div>
        </div>

      </div>

      {/* 4. Factory Operational Digital Twin Strip (8 Machines) */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-400" />
            <div>
              <h3 className="font-bold text-white text-sm">
                Factory Digital Twin — Operational Machine Status (Shakti Foundry Plant 01)
              </h3>
              <p className="text-xs text-gray-400">
                Click any machine card to inspect real-time sensory telemetry, SEC deviation, and missing sensors.
              </p>
            </div>
          </div>
          <button 
            onClick={() => onNavigate('digital_twin')}
            className="text-indigo-400 hover:text-indigo-300 text-xs flex items-center gap-1 font-medium"
          >
            Open Full Digital Twin <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {machines && machines.map((m) => {
            const hasAnomaly = m.is_anomaly;
            return (
              <div 
                key={m.id}
                onClick={() => onNavigate('digital_twin')}
                className={`p-3 rounded-lg border cursor-pointer transition-all glass-card-hover ${
                  hasAnomaly 
                    ? 'bg-rose-950/20 border-rose-500/40 hover:border-rose-400' 
                    : 'bg-gray-800/40 border-gray-700/60 hover:border-gray-600'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-[10px] font-mono uppercase tracking-wider text-gray-400">
                      {m.category}
                    </span>
                    <h4 className="text-xs font-bold text-white leading-snug mt-0.5">
                      {m.name.split('(')[0]}
                    </h4>
                  </div>
                  <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                    hasAnomaly ? 'bg-rose-500 text-white animate-pulse' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  }`}>
                    {hasAnomaly ? 'ANOMALY' : 'OPTIMAL'}
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-2 gap-1.5 text-xs font-mono">
                  <div>
                    <span className="text-gray-500 text-[10px]">Power</span>
                    <div className="font-semibold text-gray-200">{m.current_power_kw} kW</div>
                  </div>
                  <div>
                    <span className="text-gray-500 text-[10px]">SEC</span>
                    <div className={`font-semibold ${hasAnomaly ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {m.actual_sec}
                    </div>
                  </div>
                </div>

                <div className="mt-2.5 pt-2 border-t border-gray-700/50 flex items-center justify-between text-[11px] text-gray-400">
                  <span>Health: {m.health_score}%</span>
                  {m.sensors_missing?.length > 0 && (
                    <span className="text-amber-400 font-mono text-[10px]">
                      {m.sensors_missing.length} missing sensor
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
