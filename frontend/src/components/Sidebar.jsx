import React from 'react';
import { 
  LayoutDashboard, 
  Cpu, 
  LineChart, 
  AlertOctagon, 
  ShieldCheck, 
  Sliders, 
  Award, 
  Radar, 
  Layers, 
  Bot, 
  Gauge,
  Sparkles
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, anomaliesCount, verifiedCount, safeActionsCount }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, section: 'Core' },
    { id: 'digital_twin', label: 'Factory Digital Twin', icon: Cpu, section: 'Factory' },
    { id: 'sec_baseline', label: 'SEC Baseline Engine', icon: LineChart, section: 'Energy' },
    { 
      id: 'anomalies', 
      label: 'Anomaly & Root Cause', 
      icon: AlertOctagon, 
      badge: anomaliesCount > 0 ? anomaliesCount : null,
      badgeColor: 'bg-rose-500 text-white',
      section: 'Energy' 
    },
    { 
      id: 'decision_engine', 
      label: 'Production-Safe Engine', 
      icon: ShieldCheck, 
      highlight: true,
      badge: safeActionsCount > 0 ? `${safeActionsCount} Safe` : null,
      badgeColor: 'bg-emerald-500 text-black',
      section: 'Intelligence' 
    },
    { id: 'what_if', label: 'What-If Simulation', icon: Sliders, section: 'Intelligence' },
    { 
      id: 'verification', 
      label: 'Savings & Verification', 
      icon: Award, 
      section: 'Measurement' 
    },
    { id: 'sensor_roi', label: 'Digitalization ROI Advisor', icon: Radar, section: 'Upgrade' },
    { id: 'progressive_levels', label: 'Progressive Intelligence', icon: Layers, section: 'Retrofit' },
    { id: 'copilot', label: 'AI Energy Copilot', icon: Bot, isAi: true, section: 'Interface' },
  ];

  return (
    <aside className="w-64 bg-[#0B1220] border-r border-gray-800 flex flex-col shrink-0">
      
      {/* Constraint Gate Status Widget */}
      <div className="p-3 border-b border-gray-800/80 bg-gray-900/40">
        <div className="flex items-center justify-between text-xs mb-1.5">
          <span className="text-gray-400 font-medium">Safety Constraint Gate</span>
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
            ACTIVE
          </span>
        </div>
        <p className="text-[11px] text-gray-500 leading-tight">
          Guarantees zero throughput sacrifice or metallurgical quality compromise.
        </p>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? item.highlight 
                    ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                    : 'bg-gray-800 text-white border border-gray-700'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? (item.highlight ? 'text-emerald-400' : 'text-cyan-400') : 'text-gray-400'}`} />
                <span className={item.highlight && isActive ? 'font-semibold' : ''}>{item.label}</span>
              </div>

              {item.badge && (
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}

              {item.isAi && (
                <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-1">
                  <Sparkles className="w-2.5 h-2.5" />
                  Ask
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-3 border-t border-gray-800 text-[11px] bg-gray-900/30">
        <div className="flex items-center justify-between text-gray-400 mb-1">
          <span>Retrofit Level:</span>
          <span className="font-semibold text-cyan-400">Level 3 (Sensory)</span>
        </div>
        <div className="flex items-center justify-between text-gray-400">
          <span>Data Confidence:</span>
          <span className="font-semibold text-emerald-400">88%</span>
        </div>
      </div>
    </aside>
  );
}
