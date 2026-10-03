import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Overview from './components/Overview';
import DigitalTwin from './components/DigitalTwin';
import SecBaselineView from './components/SecBaselineView';
import AnomalyRootCauseView from './components/AnomalyRootCauseView';
import DecisionEngineView from './components/DecisionEngineView';
import WhatIfSimulatorView from './components/WhatIfSimulatorView';
import SavingsVerificationView from './components/SavingsVerificationView';
import SensorRoiView from './components/SensorRoiView';
import ProgressiveIntelligenceView from './components/ProgressiveIntelligenceView';
import CopilotModal from './components/CopilotModal';
import GuidedDemoModal from './components/GuidedDemoModal';
import SmeSetupModal from './components/SmeSetupModal';

import {
  fetchFactoryOverview,
  fetchFactoryMachines,
  fetchFactoryHistory,
  fetchAnomalies,
  fetchCandidateActions,
  postWhatIfSimulation,
  approveAction,
  resetSimulationActions,
  fetchVerifiedSavings,
  fetchReadiness,
  setProgressiveLevel,
  fetchSensorROI,
  changeScenario,
  resetDemo
} from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [machines, setMachines] = useState([]);
  const [history, setHistory] = useState([]);
  const [anomalies, setAnomalies] = useState([]);
  const [candidateActions, setCandidateActions] = useState([]);
  const [simulationResult, setSimulationResult] = useState(null);
  const [selectedActionId, setSelectedActionId] = useState('action_compressor_unloaded_shutdown');
  const [verifiedRecords, setVerifiedRecords] = useState([]);
  const [readiness, setReadiness] = useState(null);
  const [sensorRecommendations, setSensorRecommendations] = useState([]);
  const [activeScenario, setActiveScenario] = useState('normal');

  // Modals
  const [isDemoOpen, setIsDemoOpen] = useState(false);
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  // Initial Data Load
  const refreshAllData = async () => {
    try {
      const [
        overviewData,
        machinesData,
        historyData,
        anomaliesData,
        actionsData,
        verifiedData,
        readinessData,
        sensorData
      ] = await Promise.all([
        fetchFactoryOverview(),
        fetchFactoryMachines(),
        fetchFactoryHistory(),
        fetchAnomalies(),
        fetchCandidateActions(),
        fetchVerifiedSavings(),
        fetchReadiness(),
        fetchSensorROI()
      ]);

      setOverview(overviewData);
      setMachines(machinesData);
      setHistory(historyData);
      setAnomalies(anomaliesData);
      setCandidateActions(actionsData);
      setVerifiedRecords(verifiedData);
      setReadiness(readinessData);
      setSensorRecommendations(sensorData);
      setActiveScenario(overviewData.active_scenario || 'normal');
    } catch (err) {
      console.error("Data refresh error:", err);
    }
  };

  useEffect(() => {
    refreshAllData();
    // Default load simulation for compressor action
    postWhatIfSimulation('action_compressor_unloaded_shutdown')
      .then(res => setSimulationResult(res))
      .catch(console.error);

    // Periodic live synchronization polling every 3.5 seconds
    const interval = setInterval(() => {
      fetchFactoryOverview().then(ov => setOverview(ov)).catch(() => {});
      fetchFactoryMachines().then(m => setMachines(m)).catch(() => {});
    }, 3500);

    return () => clearInterval(interval);
  }, []);

  // Handlers
  const handleScenarioChange = async (scenario) => {
    try {
      await changeScenario(scenario);
      setActiveScenario(scenario);
      await refreshAllData();
      // If compressor anomaly, select its safe action
      if (scenario === 'compressor_waste') {
        setSelectedActionId('action_compressor_unloaded_shutdown');
        const res = await postWhatIfSimulation('action_compressor_unloaded_shutdown');
        setSimulationResult(res);
      } else if (scenario === 'furnace_degradation') {
        setSelectedActionId('action_furnace_refractory_patch');
        const res = await postWhatIfSimulation('action_furnace_refractory_patch');
        setSimulationResult(res);
      } else if (scenario === 'production_scheduling') {
        setSelectedActionId('action_tod_rescheduling');
        const res = await postWhatIfSimulation('action_tod_rescheduling');
        setSimulationResult(res);
      } else if (scenario === 'missing_sensor') {
        setSelectedActionId('action_compressor_bearing_overhaul_unsupported');
        const res = await postWhatIfSimulation('action_compressor_bearing_overhaul_unsupported');
        setSimulationResult(res);
      } else {
        setSelectedActionId('action_compressor_unloaded_shutdown');
        const res = await postWhatIfSimulation('action_compressor_unloaded_shutdown');
        setSimulationResult(res);
      }
    } catch (err) {
      console.error("Scenario change failed:", err);
    }
  };

  const handleSimulateAction = async (actionId) => {
    setSelectedActionId(actionId);
    try {
      const res = await postWhatIfSimulation(actionId);
      setSimulationResult(res);
      setActiveTab('what_if');
    } catch (err) {
      console.error("Simulation failed:", err);
    }
  };

  const handleApproveAction = async (actionId) => {
    try {
      await approveAction(actionId);
      await refreshAllData();
      const updatedSim = await postWhatIfSimulation(actionId);
      setSimulationResult(updatedSim);
    } catch (err) {
      console.error("Approval failed:", err);
    }
  };

  const handleRejectAction = async (actionId) => {
    // Rejection resets the active candidate
    refreshAllData();
  };

  const handleResetActions = async () => {
    try {
      await resetSimulationActions();
      await refreshAllData();
      const res = await postWhatIfSimulation('action_compressor_unloaded_shutdown');
      setSimulationResult(res);
    } catch (err) {
      console.error("Reset failed:", err);
    }
  };

  const handleResetDemo = async () => {
    try {
      await resetDemo();
      await refreshAllData();
      setSelectedActionId('action_compressor_unloaded_shutdown');
      const res = await postWhatIfSimulation('action_compressor_unloaded_shutdown');
      setSimulationResult(res);
      setActiveTab('overview');
    } catch (err) {
      console.error("Reset demo failed:", err);
    }
  };

  const handleSetLevel = async (level) => {
    try {
      await setProgressiveLevel(level);
      await refreshAllData();
    } catch (err) {
      console.error("Set level failed:", err);
    }
  };

  const handleNavigateToDecision = (anomalyId) => {
    setActiveTab('decision_engine');
  };

  const safeActionsCount = candidateActions.filter(a => a.is_safe).length;

  return (
    <div className="min-h-screen bg-[#0B1220] text-[#F8FAFC] flex flex-col font-sans">
      
      {/* 1. Header */}
      <Header
        overview={overview}
        onScenarioChange={handleScenarioChange}
        onOpenDemo={() => setIsDemoOpen(true)}
        onOpenConfig={() => setIsConfigOpen(true)}
        onResetActions={handleResetActions}
        onResetDemo={handleResetDemo}
        activeScenario={activeScenario}
      />

      {/* 2. Main Body with Fixed Sidebar */}
      <div className="flex-1 flex overflow-hidden">
        
        {/* Left Navigation */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          anomaliesCount={overview?.active_anomalies_count || 0}
          verifiedCount={verifiedRecords.length}
          safeActionsCount={safeActionsCount}
        />

        {/* Dynamic Center Stage */}
        <main className="flex-1 overflow-y-auto p-5 lg:p-6 space-y-6">
          
          {activeTab === 'overview' && (
            <Overview
              overview={overview}
              machines={machines}
              history={history}
              anomalies={anomalies}
              safeActions={candidateActions.filter(a => a.is_safe)}
              onNavigate={setActiveTab}
              onSimulateAction={handleSimulateAction}
            />
          )}

          {activeTab === 'digital_twin' && (
            <DigitalTwin
              machines={machines}
              onSelectAnomalyMachine={(machineId) => {
                setActiveTab('anomalies');
              }}
            />
          )}

          {activeTab === 'sec_baseline' && (
            <SecBaselineView
              overview={overview}
            />
          )}

          {activeTab === 'anomalies' && (
            <AnomalyRootCauseView
              anomalies={anomalies}
              onNavigateToDecision={handleNavigateToDecision}
            />
          )}

          {activeTab === 'decision_engine' && (
            <DecisionEngineView
              candidateActions={candidateActions}
              onLaunchWhatIf={handleSimulateAction}
            />
          )}

          {activeTab === 'what_if' && (
            <WhatIfSimulatorView
              simulationResult={simulationResult}
              onSimulate={handleSimulateAction}
              onApprove={handleApproveAction}
              onReject={handleRejectAction}
              appliedActions={overview?.applied_actions || []}
              candidateActions={candidateActions}
              selectedActionId={selectedActionId}
              setSelectedActionId={setSelectedActionId}
            />
          )}

          {activeTab === 'verification' && (
            <SavingsVerificationView
              verifiedRecords={verifiedRecords}
            />
          )}

          {activeTab === 'sensor_roi' && (
            <SensorRoiView
              sensorRecommendations={sensorRecommendations}
            />
          )}

          {activeTab === 'progressive_levels' && (
            <ProgressiveIntelligenceView
              readiness={readiness}
              onSetLevel={handleSetLevel}
            />
          )}

          {activeTab === 'copilot' && (
            <CopilotModal
              isOpen={true}
              onClose={() => {}}
            />
          )}

        </main>
      </div>

      {/* Guided 2-Minute Demo Walkthrough Modal */}
      <GuidedDemoModal
        isOpen={isDemoOpen}
        onClose={() => setIsDemoOpen(false)}
        onScenarioChange={handleScenarioChange}
        onNavigateTab={setActiveTab}
        onSimulateAction={handleSimulateAction}
        onApproveAction={handleApproveAction}
      />

      {/* SME Onboarding / Plant Configuration Modal */}
      <SmeSetupModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
        onApplyConfig={(cfg) => {
          refreshAllData();
        }}
      />

    </div>
  );
}
