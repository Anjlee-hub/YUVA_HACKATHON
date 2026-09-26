import React, { useState } from 'react';
import { 
  Bot, 
  Send, 
  Sparkles, 
  User, 
  CheckCircle2, 
  ShieldCheck, 
  Database, 
  HelpCircle,
  X,
  Zap,
  CornerDownLeft
} from 'lucide-react';
import { queryCopilot } from '../api';

const QUICK_PROMPTS = [
  "Why did energy increase?",
  "What caused the anomaly?",
  "What action is safe?",
  "How much could we save?",
  "Why was an action rejected?",
  "What data should we collect next?",
  "Did the intervention work?",
  "What is our current data maturity?",
  "What savings have been verified?"
];

export default function CopilotModal({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: "👋 Welcome to the **Shakti Foundry Energy Copilot**. I serve as an explainable interface into our production-safe energy analytics and real-time sub-meter telemetry.\n\nAsk me any operational question or select one of the quick prompts below to inspect root-cause evidence or safety certifications.",
      dataSource: "Ground Truth Sub-meter Telemetry",
      timestamp: "Just now"
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (questionText) => {
    const q = questionText || input;
    if (!q.trim()) return;

    // Add user message
    const userMsg = {
      sender: 'user',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await queryCopilot(q);
      const botMsg = {
        sender: 'bot',
        text: response.answer,
        dataSource: response.data_source,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: "### ⚠️ Insufficient Data to Answer Reliably\n\nLive plant telemetry data is currently unreachable or disconnected. Under our strict **Data Trust Protocol**, the Energy Copilot strictly withholds operational diagnoses and numerical recommendations until sub-meter and sensor telemetry streams are verified to prevent ungrounded or fabricated responses.\n\n• **Status:** Insufficient factory telemetry stream.\n• **Safety Policy:** Zero numerical hallucination when sensor stream is unavailable.\n• **Recommended Action:** Verify that the backend service and telemetry gateway are connected.",
        dataSource: "Data Trust Protocol (Insufficient Data)",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl p-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-purple-500/20 text-purple-400 border border-purple-500/30">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-bold text-white">
                  Explainable AI Energy Copilot
                </h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  INTERFACE LAYER ONLY
                </span>
              </div>
              <p className="text-xs text-gray-400 mt-0.5">
                Answers are grounded 100% in shopfloor sensor models and manufacturing constraint tables. Zero numerical hallucination.
              </p>
            </div>
          </div>

          <div className="text-xs text-gray-400 font-mono">
            Grounding Source: <strong className="text-emerald-400">Shakti Plant 01 Sub-meters</strong>
          </div>
        </div>
      </div>

      {/* Main Chat Interface */}
      <div className="bg-gray-900/80 border border-gray-800 rounded-xl overflow-hidden flex flex-col h-[550px]">
        
        {/* Quick Prompts Bar */}
        <div className="p-3 bg-gray-950/60 border-b border-gray-800 overflow-x-auto">
          <div className="flex items-center gap-2 whitespace-nowrap">
            <span className="text-xs font-semibold text-gray-400 flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-purple-400" />
              Quick Questions:
            </span>
            {QUICK_PROMPTS.map((prompt, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(prompt)}
                className="px-2.5 py-1 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-300 text-xs transition-all border border-gray-700/60 hover:text-white"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Message Log */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 max-w-3xl ${m.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
            >
              <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center ${
                m.sender === 'user' 
                  ? 'bg-cyan-600 text-white' 
                  : 'bg-purple-600 text-white shadow-lg shadow-purple-900/30'
              }`}>
                {m.sender === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              <div className={`p-4 rounded-xl text-xs space-y-2 ${
                m.sender === 'user'
                  ? 'bg-cyan-950/40 border border-cyan-500/40 text-cyan-100'
                  : 'bg-gray-950/80 border border-gray-800 text-gray-200'
              }`}>
                <div className="prose prose-invert prose-xs max-w-none leading-relaxed whitespace-pre-line font-sans">
                  {m.text}
                </div>

                {m.dataSource && (
                  <div className="pt-2 border-t border-gray-800/80 flex items-center justify-between text-[10px] font-mono text-gray-500">
                    <span className="flex items-center gap-1 text-emerald-400/90">
                      <Database className="w-3 h-3" />
                      Grounded in: {m.dataSource}
                    </span>
                    <span>{m.timestamp}</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 max-w-lg">
              <div className="w-8 h-8 rounded-lg bg-purple-600 text-white flex items-center justify-center animate-pulse">
                <Bot className="w-4 h-4" />
              </div>
              <div className="p-3 rounded-xl bg-gray-950/80 border border-gray-800 text-xs text-gray-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping"></span>
                Synthesizing analytical evidence from plant data...
              </div>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div className="p-3 bg-gray-950/80 border-t border-gray-800">
          <form 
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Copilot (e.g., 'Why is this recommendation safe?' or 'Which machine is wasting energy?')"
              className="flex-1 p-2.5 rounded-lg bg-gray-900 border border-gray-700 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="px-4 py-2.5 rounded-lg bg-purple-600 hover:bg-purple-500 disabled:bg-gray-800 text-white font-semibold text-xs transition-all flex items-center gap-1.5"
            >
              <span>Query</span>
              <Send className="w-3.5 h-3.5" />
            </button>
          </form>
        </div>

      </div>

    </div>
  );
}
