import React, { useState } from 'react';
import { 
  Settings2, 
  X, 
  Factory, 
  Check, 
  Zap, 
  Boxes, 
  CheckCircle2,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export default function SmeSetupModal({ isOpen, onClose, onApplyConfig }) {
  const [factoryType, setFactoryType] = useState('Foundry & Casting');
  const [plantName, setPlantName] = useState('Shakti Foundry — Plant 01');
  const [location, setLocation] = useState('Peenya, Bengaluru, India');
  const [productionUnit, setProductionUnit] = useState('Metric Tons (Good Castings)');
  const [dailyTarget, setDailyTarget] = useState(25.0);
  const [selectedSensors, setSelectedSensors] = useState({
    main_meter: true,
    production: true,
    runtime: true,
    temp: true,
    pressure: true,
    vibration: false, // Intentionally unchecked to demonstrate retrofit gaps!
    scada: false
  });

  if (!isOpen) return null;

  const toggleSensor = (key) => {
    setSelectedSensors(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSave = () => {
    onApplyConfig({
      factoryType,
      plantName,
      location,
      productionUnit,
      dailyTarget,
      selectedSensors
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
      <div className="bg-[#111827] border border-gray-700 rounded-2xl w-full max-w-xl shadow-2xl p-6 relative">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-400">
              <Factory className="w-4 h-4" />
            </span>
            <span className="text-xs uppercase font-mono tracking-wider font-bold text-white">
              SME Onboarding & Plant Configuration
            </span>
          </div>

          <button 
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Form Body */}
        <div className="mt-4 space-y-4 text-xs">
          
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-gray-400 block mb-1">Factory Sector / Industry:</label>
              <select
                value={factoryType}
                onChange={(e) => setFactoryType(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-cyan-500 font-medium"
              >
                <option value="Foundry & Casting">Foundry & Metal Casting (Ferrous)</option>
                <option value="Forging & Stamping">Forging & Heat Treatment</option>
                <option value="Textile Spinning">Textile Spinning & Dyeing</option>
                <option value="Food Processing">Food & Beverage Processing</option>
                <option value="Plastics & Injection">Plastics & Injection Moulding</option>
              </select>
            </div>

            <div>
              <label className="text-gray-400 block mb-1">Production Counting Unit:</label>
              <select
                value={productionUnit}
                onChange={(e) => setProductionUnit(e.target.value)}
                className="w-full p-2.5 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-cyan-500 font-medium"
              >
                <option value="Metric Tons (Good Castings)">Metric Tons (Good Castings)</option>
                <option value="Kilograms (Finished Output)">Kilograms (Finished Output)</option>
                <option value="Pieces / Components (Good)">Pieces / Components (Good)</option>
                <option value="Batches Completed">Batches Completed</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-gray-400 block mb-1">Facility Name:</label>
              <input
                type="text"
                value={plantName}
                onChange={(e) => setPlantName(e.target.value)}
                className="w-full p-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>

            <div>
              <label className="text-gray-400 block mb-1">Daily Target Volume:</label>
              <input
                type="number"
                value={dailyTarget}
                onChange={(e) => setDailyTarget(parseFloat(e.target.value))}
                className="w-full p-2 rounded-lg bg-gray-900 border border-gray-700 text-white focus:outline-none focus:border-cyan-500 font-mono"
              />
            </div>
          </div>

          {/* Sensor Availability Checklist */}
          <div>
            <label className="text-gray-300 font-bold block mb-2">
              Available Data Sources & Instrumentation on Day 1:
            </label>
            <div className="grid grid-cols-2 gap-2">
              {[
                { id: 'main_meter', label: 'Main Utility Energy Meter' },
                { id: 'production', label: 'Production Weighbridge / Counts' },
                { id: 'runtime', label: 'Machine Runtime Hours' },
                { id: 'temp', label: 'Temperature Sensors (RTDs)' },
                { id: 'pressure', label: 'Pressure Transducers (Air)' },
                { id: 'vibration', label: 'Vibration Accelerometers (IoT)' },
                { id: 'scada', label: 'Full PLC / SCADA Gateway' }
              ].map((item) => (
                <label
                  key={item.id}
                  onClick={() => toggleSensor(item.id)}
                  className={`p-2.5 rounded-lg border flex items-center justify-between cursor-pointer transition-all ${
                    selectedSensors[item.id]
                      ? 'bg-cyan-950/30 border-cyan-500 text-cyan-200'
                      : 'bg-gray-900/60 border-gray-800 text-gray-400'
                  }`}
                >
                  <span className="text-xs">{item.label}</span>
                  <div className={`w-4 h-4 rounded flex items-center justify-center border ${
                    selectedSensors[item.id] ? 'bg-cyan-500 border-cyan-400 text-black' : 'border-gray-700'
                  }`}>
                    {selectedSensors[item.id] && <Check className="w-3 h-3 stroke-[3]" />}
                  </div>
                </label>
              ))}
            </div>
            <p className="text-[11px] text-gray-500 mt-2 italic">
              Notice: The engine works with any subset of sensors without requiring full instrumentation on Day 1.
            </p>
          </div>

        </div>

        {/* Footer */}
        <div className="mt-6 pt-3 border-t border-gray-800 flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-gray-700 bg-gray-800 text-gray-300 text-xs font-semibold"
          >
            Cancel
          </button>

          <button
            onClick={handleSave}
            className="px-5 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-bold text-xs flex items-center gap-1.5 shadow-lg shadow-cyan-500/20 active:scale-95 transition-all"
          >
            <span>Start Energy Intelligence</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>
    </div>
  );
}
