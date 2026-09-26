import React, { useState } from 'react';
import { 
  Play, 
  CheckCircle2, 
  ArrowRight, 
  ArrowLeft, 
  X, 
  ShieldCheck, 
  AlertTriangle, 
  Sliders, 
  Award, 
  Sparkles,
  Zap,
  RotateCcw
} from 'lucide-react';

export default function GuidedDemoModal({ 
  isOpen, 
  onClose, 
  onScenarioChange, 
  onNavigateTab, 
  onSimulateAction, 
  onApproveAction 
}) {
  const [currentStep, setCurrentStep] = useState(1);

  if (!isOpen) return null;

  const steps = [
    {
      step: 1,
      title: "Step 1: Baseline Normal Operations",
      description: "Shakti Foundry Plant 01 is running Grey Cast Iron (FG 260) with standard 695 kWh/ton SEC. Sub-meters and weighbridge are streaming normally.",
      actionLabel: "Inject Compressor Anomaly →",
      onExecute: () => {
        onScenarioChange('normal');
        onNavigateTab('overview');
      }
    },
    {
      step: 2,
      title: "Step 2: Anomaly Emerges (Compressor 02)",
      description: "Compressor 02 starts idling unloaded during mold shakeout and shift changeovers. Specific Energy Consumption surges +26.8% above production-aware baseline.",
      actionLabel: "Inspect Anomaly Root Cause →",
      onExecute: () => {
        onScenarioChange('compressor_waste');
        onNavigateTab('anomalies');
      }
    },
    {
      step: 3,
      title: "Step 3: Root-Cause Factor Decomposition",
      description: "The engine decomposes the anomaly: 52% Idle Run, 21% Pressure Setting Overkill, 14% Ambient Temperature, 13% Degradation.",
      actionLabel: "Check Data Confidence →",
      onExecute: () => {
        onNavigateTab('anomalies');
      }
    },
    {
      step: 4,
      title: "Step 4: Data Readiness & Trust Protocol Check",
      description: "Overall data confidence is 88%. Notice: because vibration data is missing on Compressor 02, the system explicitly WITHHOLDS mechanical degradation diagnosis rather than hallucinating.",
      actionLabel: "Generate Candidate Actions →",
      onExecute: () => {
        onNavigateTab('progressive_levels');
      }
    },
    {
      step: 5,
      title: "Step 5: Candidate Actions Evaluated by Constraint Gate",
      description: "Two optimization actions are evaluated against shopfloor manufacturing constraints.",
      actionLabel: "Inspect Constraint Gate →",
      onExecute: () => {
        onNavigateTab('decision_engine');
      }
    },
    {
      step: 6,
      title: "Step 6: Unsafe Action Filtered & REJECTED",
      description: "Candidate Action 1 proposes dropping shop air pressure to 5.2 bar. REJECTED: Violates DISA moulding squeeze minimum (6.0 bar), causing casting surface defects and delivery delays.",
      actionLabel: "Examine Certified Safe Action →",
      onExecute: () => {
        onNavigateTab('decision_engine');
      }
    },
    {
      step: 7,
      title: "Step 7: Certified SAFE Recommendation",
      description: "Candidate Action 2 proposes 90-sec auto-idle shutdown + pressure trimming to 6.6 bar. Passes 100% of manufacturing constraints with 0% throughput or quality risk.",
      actionLabel: "Launch What-If Simulation →",
      onExecute: () => {
        onNavigateTab('what_if');
        onSimulateAction('action_compressor_unloaded_shutdown');
      }
    },
    {
      step: 8,
      title: "Step 8: What-If Simulation (Before vs After)",
      description: "Comparative matrix shows: Energy -27.2%, Monthly Cost -₹38,400, Production 100% retained, Casting Quality 97.4% retained.",
      actionLabel: "Human Operator Approves Action →",
      onExecute: () => {
        onNavigateTab('what_if');
      }
    },
    {
      step: 9,
      title: "Step 9: Approval & Factory State Update",
      description: "User clicks 'Approve & Execute into Factory'. Telemetry state machine immediately applies the operational setpoint update.",
      actionLabel: "Apply to Live Factory Twin →",
      onExecute: async () => {
        await onApproveAction('action_compressor_unloaded_shutdown');
        onNavigateTab('overview');
      }
    },
    {
      step: 10,
      title: "Step 10: Live Factory State Synchronized",
      description: "Observe the live overview: Compressor 02 status turns green (OPTIMAL), plant SEC drops back to normal, and monthly verified savings start accumulating.",
      actionLabel: "Review Verified Savings →",
      onExecute: () => {
        onNavigateTab('verification');
      }
    },
    {
      step: 11,
      title: "Step 11: IPMVP Option B Savings Verification",
      description: "Actual vs Predicted savings are verified via isolated sub-meter logs. Discrepancies are auditable and explained by production mix variances.",
      actionLabel: "Check Next Sensor Recommendation →",
      onExecute: () => {
        onNavigateTab('sensor_roi');
      }
    },
    {
      step: 12,
      title: "Step 12: Sensor ROI Advisor (What to Digitalize Next)",
      description: "The loop is complete: the system recommends the #1 highest ROI retrofit sensor (Vibration Accelerometer on Compressor 02 for ₹22k, payback in 3.1 months) to close the evidence gap.",
      actionLabel: "Finish Walkthrough 🎉",
      onExecute: () => {
        onNavigateTab('sensor_roi');
      }
    }
  ];

  const current = steps[currentStep - 1];

  const handleNext = () => {
    current.onExecute();
    if (currentStep < steps.length) {
      setCurrentStep(prev => prev + 1);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(prev => prev - 1);
      steps[currentStep - 2].onExecute();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
      <div className="bg-[#111827] border border-emerald-500/50 rounded-2xl w-full max-w-xl shadow-2xl p-6 relative overflow-hidden">
        
        {/* Glow backdrop */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-gray-800 pb-3">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
              <Play className="w-4 h-4 fill-emerald-400" />
            </span>
            <span className="text-xs uppercase font-mono tracking-wider font-bold text-white">
              2-Minute Guided Product Loop Walkthrough
            </span>
          </div>

          <button 
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-gray-800 text-gray-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Progress Bar */}
        <div className="my-4">
          <div className="flex items-center justify-between text-[11px] font-mono text-gray-400 mb-1.5">
            <span className="text-emerald-400 font-bold">Step {currentStep} of {steps.length}</span>
            <span>{Math.round((currentStep / steps.length) * 100)}% Complete</span>
          </div>
          <div className="w-full bg-gray-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full transition-all duration-300 rounded-full"
              style={{ width: `${(currentStep / steps.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Content Box */}
        <div className="p-4 rounded-xl bg-gray-950/80 border border-gray-800/80 space-y-2.5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
            {current.title}
          </h3>
          <p className="text-xs text-gray-300 leading-relaxed">
            {current.description}
          </p>
        </div>

        {/* Actions Navigation Footer */}
        <div className="mt-5 pt-3 border-t border-gray-800 flex items-center justify-between">
          <button
            onClick={handlePrev}
            disabled={currentStep === 1}
            className="px-3 py-1.5 rounded-lg border border-gray-700 bg-gray-800 hover:bg-gray-700 text-gray-300 disabled:opacity-40 text-xs font-semibold flex items-center gap-1.5"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Previous
          </button>

          <button
            onClick={handleNext}
            className="px-4 py-2 rounded-lg bg-emerald-500 hover:bg-emerald-400 text-black font-bold text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20 active:scale-95 transition-all"
          >
            <span>{current.actionLabel}</span>
          </button>
        </div>

      </div>
    </div>
  );
}
