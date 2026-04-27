/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Link2, FileText, Send, Loader2, LayoutDashboard, Settings, Info, Plus, Trash2, BrainCircuit, ChevronRight, CheckCircle2, History, Database, Globe, Cpu, Home, Zap, ShieldAlert } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { analyzeNews } from '../services/apiService';
import { AnalysisResult } from '../types';
import { ResultDashboard } from './ResultDashboard';
import { cn } from '../lib/utils';

type Step = 'input' | 'processing' | 'results';


export const AnalysisWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const [activeSidebar, setActiveSidebar] = useState<'analysis' | 'config'>('analysis');
  const [selectedModel, setSelectedModel] = useState<string>('llama-3.3-70b-versatile');
  const [currentStep, setCurrentStep] = useState<Step>('input');
  const [activeTab, setActiveTab] = useState<'link' | 'manual'>('link');
  const [inputs, setInputs] = useState<string[]>(['', '']);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [progressMsg, setProgressMsg] = useState('Initializing Analysis Engine...');
  const [progress, setProgress] = useState(0);

  const handleAddInput = () => setInputs([...inputs, '']);
  const handleRemoveInput = (index: number) => setInputs(inputs.filter((_, i) => i !== index));
  const updateInput = (index: number, value: string) => {
    const newInputs = [...inputs];
    newInputs[index] = value;
    setInputs(newInputs);
  };

  const runAnalysis = async () => {
    const validInputs = inputs.filter(i => i.trim() !== '');
    if (validInputs.length < 1) return;

    setCurrentStep('processing');
    setIsAnalyzing(true);

    const messages = [
      'Scraping & cleaning source metadata (Removing ads/scripts)...',
      'Isolating core narrative from background noise...',
      'Mapping actors and causal relationships...',
      'Applying Robert Entman framing filter...',
      'Generating comparative intelligence report...',
      'Synthesizing final findings...'
    ];

    try {
      for (let i = 0; i < messages.length; i++) {
        setProgressMsg(messages[i]);
        setProgress(Math.round(((i + 1) / messages.length) * 100));
        await new Promise(r => setTimeout(r, 800));
      }

      const data = await analyzeNews(validInputs, activeTab === 'manual' ? 'manual' : 'link', selectedModel);
      setResult(data);
      setCurrentStep('results');
    } catch (error: any) {
      console.error(error);
      alert(error.message || "Analysis failed. Please check your network or API keys.");
      setCurrentStep('input');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#06080B] overflow-hidden text-[#F0F0F0]">
      {/* Sleek Sidebar */}
      <aside className="w-20 lg:w-64 border-r border-white/5 flex flex-col bg-[#080A0E] shrink-0">
        <div className="p-6 mb-4 mt-2 flex items-center justify-center lg:justify-start gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#2A35D1] to-[#6A75E1] flex items-center justify-center shadow-lg shadow-[#2A35D1]/20 shrink-0">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-black tracking-tighter text-white uppercase hidden lg:block">Omnius</span>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-8">
          <SidebarItem icon={LayoutDashboard} label="Framing Analysis" active={activeSidebar === 'analysis'} onClick={() => setActiveSidebar('analysis')} />
          <SidebarItem icon={Settings} label="Model Config" active={activeSidebar === 'config'} onClick={() => setActiveSidebar('config')} />
          <div className="pt-4 mt-4 border-t border-white/5">
            <button
              onClick={() => navigate('/')}
              className="w-full flex items-center gap-4 px-4 py-3 rounded-2xl text-sm font-medium transition-all group text-[#606060] hover:text-white hover:bg-white/5"
            >
              <Home className="w-5 h-5 shrink-0" />
              <span className="hidden lg:block">Back to Home</span>
            </button>
          </div>
        </nav>

        <div className="p-4 m-4 mt-auto rounded-2xl bg-white/5 border border-white/5 hidden lg:block">
          <div className="flex items-center gap-2 text-[10px] text-[#505050] font-bold uppercase tracking-[0.2em] mb-3">
            <BrainCircuit className="w-3 h-3 text-[#2A35D1]" /> System Status
          </div>
          <div className="space-y-2">
            <StatusIndicator label="LLM ENGINE" active />
            <StatusIndicator label="SCRAPER V2" active />
            <StatusIndicator label="API GROQ" active />
          </div>
        </div>
      </aside>

      {/* Main Analysis Area */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        <header className="h-16 border-b border-white/5 bg-[#06080B]/60 backdrop-blur-xl px-4 lg:px-8 flex items-center justify-between sticky top-0 z-50">
          <div className="flex items-center gap-2 text-xs font-medium text-[#606060]">
            <span className={cn(currentStep === 'input' ? "text-[#2A35D1]" : "text-emerald-500")}>Input Sources</span>
            <ChevronRight className="w-3 h-3" />
            <span className={cn(currentStep === 'processing' ? "text-[#2A35D1]" : currentStep === 'results' ? "text-emerald-500" : "text-[#303030]")}>Deconstruction</span>
            <ChevronRight className="w-3 h-3" />
            <span className={cn(currentStep === 'results' ? "text-[#2A35D1]" : "text-[#303030]")}>Intelligence Report</span>
          </div>

          <div className="flex items-center gap-3">
            {currentStep === 'results' && (
              <button
                onClick={() => { setCurrentStep('input'); setResult(null); }}
                className="px-4 py-1.5 rounded-lg bg-white/5 text-[10px] font-bold text-white uppercase tracking-widest hover:bg-white/10 transition-all"
              >
                New Analysis
              </button>
            )}
          </div>
        </header>

        <div className="flex-1 overflow-y-auto px-4 lg:px-8 py-10">
          <div className="max-w-6xl mx-auto">
            {activeSidebar === 'config' && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="space-y-8"
              >
                <div>
                  <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Model Configuration</h1>
                  <p className="text-[#808080] text-sm">Pilih mesin kecerdasan buatan (LLM) yang akan mendayagunakan analisis framing.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {[
                    {
                      id: 'llama-3.3-70b-versatile',
                      name: 'Llama 3.3 70B',
                      provider: 'Meta / Groq',
                      description: 'Heavyweight model for complex reasoning and deep narrative analysis. Best for accurate causal extraction.',
                      speed: 'Fast',
                      intelligence: 'Maximum',
                      icon: BrainCircuit,
                      gradient: 'from-blue-600 to-[#2A35D1]',
                      badge: 'RECOMMENDED'
                    },
                    {
                      id: 'llama-3.1-8b-instant',
                      name: 'Llama 3.1 8B',
                      provider: 'Meta / Groq',
                      description: 'Lightweight and extremely fast. Ideal for quick sentiment checks and basic framing tasks.',
                      speed: 'Ultra Fast',
                      intelligence: 'High',
                      icon: Zap,
                      gradient: 'from-emerald-500 to-teal-600'
                    },
                    {
                      id: 'qwen/qwen3-32b',
                      name: 'Qwen 3 32B',
                      provider: 'Alibaba / Groq',
                      description: 'Strong multilingual capabilities with excellent Indonesian context understanding.',
                      speed: 'Fast',
                      intelligence: 'Very High',
                      icon: Globe,
                      gradient: 'from-amber-500 to-orange-600'
                    },
                    {
                      id: 'soon',
                      name: 'Next-Gen Model',
                      provider: 'TBA',
                      description: 'Future integration for multimodal news analysis and deeper bias detection algorithms.',
                      speed: '-',
                      intelligence: '-',
                      icon: ShieldAlert,
                      gradient: 'from-[#303030] to-[#202020]',
                      disabled: true
                    }
                  ].map((m) => {
                    const isSelected = selectedModel === m.id;
                    return (
                      <div
                        key={m.id}
                        onClick={() => !m.disabled && setSelectedModel(m.id)}
                        className={cn(
                          "relative p-6 rounded-3xl border transition-all cursor-pointer overflow-hidden group",
                          m.disabled ? "opacity-50 cursor-not-allowed border-white/5 bg-[#06080B]" :
                            isSelected ? "border-[#2A35D1] bg-[#2A35D1]/5 shadow-[0_0_30px_-10px_rgba(42,53,209,0.3)]" : "border-white/5 bg-[#0E1117] hover:border-white/20 hover:bg-[#11141C]"
                        )}
                      >
                        {m.disabled && (
                          <div className="absolute top-6 right-6 px-3 py-1 bg-white/10 text-white text-[10px] font-bold tracking-widest rounded-full uppercase backdrop-blur-md">
                            SOON
                          </div>
                        )}
                        {!m.disabled && m.badge && (
                          <div className="absolute top-6 right-6 px-3 py-1 bg-[#2A35D1]/20 text-[#2A35D1] border border-[#2A35D1]/30 text-[10px] font-bold tracking-widest rounded-full uppercase">
                            {m.badge}
                          </div>
                        )}

                        <div className={cn("w-12 h-12 rounded-2xl mb-6 flex items-center justify-center bg-gradient-to-br", m.gradient)}>
                          <m.icon className="w-6 h-6 text-white" />
                        </div>

                        <div className="mb-2 flex items-center gap-2">
                          <h3 className="text-xl font-bold text-white">{m.name}</h3>
                          {isSelected && <CheckCircle2 className="w-5 h-5 text-[#2A35D1]" />}
                        </div>

                        <div className="text-[10px] font-mono text-[#606060] uppercase tracking-widest mb-4">
                          Provider: {m.provider}
                        </div>

                        <p className="text-sm text-[#808080] mb-6 line-clamp-2">
                          {m.description}
                        </p>

                        <div className="flex items-center gap-4 pt-4 border-t border-white/5">
                          <div>
                            <div className="text-[9px] text-[#505050] uppercase tracking-widest mb-1">Speed</div>
                            <div className="text-xs font-bold text-[#A0A0A0]">{m.speed}</div>
                          </div>
                          <div className="w-px h-8 bg-white/5" />
                          <div>
                            <div className="text-[9px] text-[#505050] uppercase tracking-widest mb-1">Intelligence</div>
                            <div className="text-xs font-bold text-[#A0A0A0]">{m.intelligence}</div>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </motion.div>
            )}

            {activeSidebar === 'analysis' && currentStep === 'input' && (
              <motion.div
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                className="space-y-12"
              >
                <div className="flex justify-between items-end">
                  <div>
                    <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Intelligence Configuration</h1>
                    <p className="text-[#808080] text-sm">Pilih media dan masukkan artikel yang akan dibandingkan.</p>
                  </div>
                  <div className="flex bg-[#0E1117] p-1 rounded-xl border border-white/5">
                    <TabButton active={activeTab === 'link'} onClick={() => setActiveTab('link')} icon={Link2} label="News URL" />
                    <TabButton active={activeTab === 'manual'} onClick={() => setActiveTab('manual')} icon={FileText} label="Full Text" />
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {inputs.map((input, idx) => (
                    <div key={idx} className="group relative bg-[#0E1117] border border-white/5 rounded-3xl p-6 focus-within:border-[#2A35D1]/50 transition-all hover:bg-[#11141C]">
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-[10px] font-black text-[#303030] tracking-[0.4em] uppercase">Source 0{idx + 1}</span>
                        {inputs.length > 2 && (
                          <button onClick={() => handleRemoveInput(idx)} className="text-[#303030] hover:text-ruby-500 transition-colors">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      {activeTab === 'link' ? (
                        <div className="relative">
                          <Link2 className="absolute left-4 top-4 w-4 h-4 text-[#404040]" />
                          <input
                            type="text"
                            value={input}
                            onChange={(e) => updateInput(idx, e.target.value)}
                            placeholder="Paste article direct link..."
                            className="w-full bg-[#06080B] border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-sm focus:ring-1 focus:ring-[#2A35D1] outline-none transition-all placeholder:text-[#303030]"
                          />
                        </div>

                      ) : (
                        <textarea
                          value={input}
                          onChange={(e) => updateInput(idx, e.target.value)}
                          placeholder="Paste article text content here..."
                          className="w-full bg-[#06080B] border border-white/5 rounded-2xl p-4 text-sm focus:ring-1 focus:ring-[#2A35D1] outline-none h-44 resize-none transition-all placeholder:text-[#303030]"
                        />
                      )}
                    </div>
                  ))}
                  <button
                    onClick={handleAddInput}
                    className="h-full min-h-[120px] rounded-3xl border-2 border-dashed border-white/5 flex flex-col items-center justify-center gap-3 text-[#404040] hover:text-[#2A35D1] hover:border-[#2A35D1]/30 transition-all bg-white/[0.01] hover:bg-[#2A35D1]/5"
                  >
                    <Plus className="w-6 h-6" />
                    <span className="text-xs font-bold uppercase tracking-widest">Add Source</span>
                  </button>
                </div>

                <div className="flex flex-col items-center gap-6 pt-8">
                  <button
                    onClick={runAnalysis}
                    disabled={isAnalyzing}
                    className={cn(
                      "group relative px-16 py-5 rounded-2xl bg-[#2A35D1] text-white font-bold transition-all shadow-[0_0_40px_-10px_rgba(42,53,209,0.5)] hover:shadow-[0_0_60px_-12px_rgba(42,53,209,0.7)] hover:-translate-y-1 active:translate-y-0 disabled:opacity-50",
                      isAnalyzing && "animate-pulse"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      {isAnalyzing ? <Loader2 className="w-5 h-5 animate-spin" /> : <Cpu className="w-5 h-5 group-hover:rotate-12 transition-transform" />}
                      {isAnalyzing ? "Menganalisis Framing..." : "Jalankan Analisis Robert Entman"}
                    </div>
                  </button>
                </div>
              </motion.div>
            )}

            {activeSidebar === 'analysis' && currentStep === 'processing' && (
              <div className="h-[60vh] flex flex-col items-center justify-center max-w-lg mx-auto text-center space-y-10">
                <div className="relative">
                  <div className="w-24 h-24 rounded-3xl bg-[#2A35D1]/10 border border-[#2A35D1]/30 flex items-center justify-center animate-pulse">
                    <BrainCircuit className="w-12 h-12 text-[#2A35D1]" />
                  </div>
                  <div className="absolute inset-0 rounded-3xl border border-[#2A35D1] animate-ping opacity-20" />
                </div>

                <div className="space-y-4">
                  <h2 className="text-xl font-bold text-white">AI Analysis in Progress</h2>
                  <p className="text-xs text-[#606060] font-mono tracking-widest h-4">{progressMsg}</p>
                </div>

                <div className="w-full space-y-2">
                  <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      className="h-full bg-[#2A35D1]"
                    />
                  </div>
                  <div className="flex justify-between text-[10px] font-mono text-[#404040]">
                    <span>SYSTEM_LOADING...</span>
                    <span>{progress}%</span>
                  </div>
                </div>
              </div>
            )}

            {activeSidebar === 'analysis' && currentStep === 'results' && result && (
              <div className="animate-in fade-in slide-in-from-bottom-8 duration-700">
                <ResultDashboard data={result} />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

const SidebarItem = ({ icon: Icon, label, active, onClick }: { icon: any, label: string, active?: boolean, onClick?: () => void }) => (
  <button onClick={onClick} className={cn(
    "w-full flex items-center gap-4 px-4 py-3 rounded-2xl text-sm font-medium transition-all group",
    active ? "bg-[#2A35D1] text-white shadow-lg shadow-[#2A35D1]/20" : "text-[#606060] hover:text-white hover:bg-white/5"
  )}>
    <Icon className="w-5 h-5 shrink-0" />
    <span className="hidden lg:block">{label}</span>
  </button>
);

const TabButton = ({ active, onClick, icon: Icon, label }: { active: boolean, onClick: () => void, icon: any, label: string }) => (
  <button
    onClick={onClick}
    className={cn(
      "flex items-center gap-2 px-6 py-2 rounded-lg text-[10px] font-bold uppercase tracking-widest transition-all",
      active ? "bg-[#2A35D1] text-white shadow-md shadow-[#2A35D1]/10" : "text-[#505050] hover:text-white"
    )}
  >
    <Icon className="w-3 h-3" /> {label}
  </button>
);

const StatusIndicator = ({ label, active }: { label: string, active: boolean }) => (
  <div className="flex items-center justify-between">
    <span className="text-[9px] font-mono text-[#404040]">{label}</span>
    <div className={cn("w-1.5 h-1.5 rounded-full", active ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" : "bg-ruby-500")} />
  </div>
);
