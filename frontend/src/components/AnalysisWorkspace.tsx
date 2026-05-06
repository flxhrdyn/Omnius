/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Link2, FileText, Send, Loader2, LayoutDashboard, Settings, Info, Plus, X, Trash2, BrainCircuit, ChevronRight, CheckCircle2, History, Database, Globe, Cpu, Home, Zap, ShieldAlert, Search, Sparkles, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { analyzeNews, researchNews } from '../services/apiService';
import { AnalysisResult } from '../types';
import { ResultDashboard } from './ResultDashboard';
import { cn } from '../lib/utils';

type Step = 'input' | 'processing' | 'results';
type Tab = 'link' | 'manual' | 'research';


export const AnalysisWorkspace: React.FC = () => {
  const navigate = useNavigate();
  const [activeSidebar, setActiveSidebar] = useState<'analysis' | 'config'>('analysis');
  const [selectedModel, setSelectedModel] = useState<string>('llama-3.3-70b-versatile');
  const [currentStep, setCurrentStep] = useState<Step>('input');
  const [activeTab, setActiveTab] = useState<Tab>('research');
  const [researchTopic, setResearchTopic] = useState('');
  const [researchResults, setResearchResults] = useState<any[]>([]);
  const [isResearching, setIsResearching] = useState(false);
  const [urlInputs, setUrlInputs] = useState<string[]>(['', '']);
  const [manualInputs, setManualInputs] = useState<string[]>(['', '']);
  const [selectedResearchArticles, setSelectedResearchArticles] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [progressMsg, setProgressMsg] = useState('Initializing Analysis Engine...');
  const [progress, setProgress] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [researchStatus, setResearchStatus] = useState<string | null>(null);
  const [isFallback, setIsFallback] = useState(false);

  const handleAddInput = () => {
    if (activeTab === 'manual') {
      if (manualInputs.length < 3) setManualInputs([...manualInputs, '']);
    } else if (activeTab === 'link') {
      if (urlInputs.length < 3) setUrlInputs([...urlInputs, '']);
    }
  };

  const handleRemoveInput = (index: number) => {
    if (activeTab === 'manual') setManualInputs(manualInputs.filter((_, i) => i !== index));
    else setUrlInputs(urlInputs.filter((_, i) => i !== index));
  };

  const updateInput = (index: number, value: string) => {
    if (activeTab === 'manual') {
      const newInputs = [...manualInputs];
      newInputs[index] = value;
      setManualInputs(newInputs);
    } else {
      const newInputs = [...urlInputs];
      newInputs[index] = value;
      setUrlInputs(newInputs);
    }
  };

  const runResearch = async () => {
    if (!researchTopic.trim()) return;
    setIsResearching(true);
    setErrorMessage(null);
    setResearchStatus("Memulai riset agentic...");
    setResearchResults([]);
    
    try {
      const data = await researchNews(researchTopic, (msg) => {
        setResearchStatus(msg);
      });
      setResearchResults(data.articles);
      setIsFallback(data.isFallback || false);
      setResearchStatus(null);
    } catch (error: any) {
      setErrorMessage(error.message);
      setResearchStatus(null);
    } finally {
      setIsResearching(false);
    }
  };

  const toggleResearchArticle = (article: any) => {
    const isSelected = selectedResearchArticles.some(a => a.url === article.url);
    if (isSelected) {
      setSelectedResearchArticles(selectedResearchArticles.filter(a => a.url !== article.url));
    } else {
      if (selectedResearchArticles.length < 3) {
        setSelectedResearchArticles([...selectedResearchArticles, article]);
      } else {
        setErrorMessage("Maksimal 3 artikel dapat dipilih untuk analisis.");
      }
    }
  };

  const runAnalysis = async () => {
    let currentInputs: string[] = [];
    let mode: 'link' | 'manual' = 'link';

    if (activeTab === 'research') {
      currentInputs = selectedResearchArticles.map(a => a.url);
      mode = 'link';
    } else if (activeTab === 'manual') {
      currentInputs = manualInputs;
      mode = 'manual';
    } else {
      currentInputs = urlInputs;
      mode = 'link';
    }

    const validInputs = currentInputs.filter(i => i.trim() !== '');
    if (validInputs.length < 1) return;

    setCurrentStep('processing');
    setIsAnalyzing(true);

    try {
      const data = await analyzeNews(
        validInputs,
        mode,
        selectedModel,
        (status) => {
          setProgressMsg(status.message);
          setProgress(status.percent);
        }
      );
      setResult(data);
      setCurrentStep('results');
    } catch (error: any) {
      console.error(error);
      setErrorMessage(error.message || "Analysis failed. Please check your network or API keys.");
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
                  <div className="flex bg-[#0E1117] p-1.5 rounded-2xl border border-white/5 shadow-inner">
                    <TabButton active={activeTab === 'research'} onClick={() => setActiveTab('research')} icon={Sparkles} label="AI Research" />
                    <TabButton active={activeTab === 'link'} onClick={() => setActiveTab('link')} icon={Link2} label="News URL" />
                    <TabButton active={activeTab === 'manual'} onClick={() => setActiveTab('manual')} icon={FileText} label="Full Text" />
                  </div>
                </div>

                <AnimatePresence>
                  {errorMessage && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="bg-red-500/10 border border-red-500/20 rounded-2xl p-4 flex items-start gap-3"
                    >
                      <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm text-red-200 font-medium">{errorMessage}</p>
                        <button
                          onClick={() => setErrorMessage(null)}
                          className="text-[10px] text-red-400 font-bold uppercase tracking-widest mt-2 hover:text-red-300 transition-colors"
                        >
                          Dismiss
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                {activeTab === 'research' && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-8"
                  >
                    <div className="bg-[#11141C] border border-white/5 rounded-3xl p-8">
                      <div className="flex items-center gap-3 mb-6">
                        <Sparkles className="w-5 h-5 text-[#2A35D1]" />
                        <h2 className="text-xl font-bold text-white tracking-tight">AI News Research Assistant</h2>
                      </div>
                      <p className="text-[#808080] text-sm mb-8 leading-relaxed">
                        Masukkan sebuah topik atau isu berita. Agent AI kami akan menelusuri internet menggunakan Tavily 
                        untuk menemukan artikel-artikel yang paling relevan untuk dianalisis.
                      </p>
                      
                      <div className="flex gap-3">
                        <div className="relative flex-1">
                          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#606060]" />
                          <input
                            type="text"
                            value={researchTopic}
                            onChange={(e) => setResearchTopic(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && runResearch()}
                            placeholder="Contoh: Dampak ekonomi PPN 12% di Indonesia..."
                            className="w-full bg-[#080A0E] border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-sm focus:ring-1 focus:ring-[#2A35D1]/50 outline-none transition-all text-white"
                          />
                        </div>
                        <button
                          onClick={runResearch}
                          disabled={isResearching}
                          className="px-8 rounded-2xl bg-[#2A35D1] text-white font-bold text-sm hover:bg-[#3A45E1] transition-all disabled:opacity-50 flex items-center gap-2 whitespace-nowrap"
                        >
                          {isResearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                          Cari Berita
                        </button>
                      </div>

                      <AnimatePresence>
                        {researchStatus && (
                          <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                            className="mt-4 flex items-center gap-3 text-xs font-mono text-[#2A35D1] bg-[#2A35D1]/5 p-3 rounded-xl border border-[#2A35D1]/10"
                          >
                            <Loader2 className="w-3 h-3 animate-spin" />
                            <span className="tracking-widest uppercase">{researchStatus}</span>
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    <AnimatePresence>
                      {researchResults.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: 'auto' }}
                          className="space-y-6"
                        >
                          {isFallback && (
                            <motion.div 
                              initial={{ opacity: 0, scale: 0.95 }}
                              animate={{ opacity: 1, scale: 1 }}
                              className="bg-amber-500/10 border border-amber-500/20 p-4 rounded-2xl flex items-start gap-4 mb-6"
                            >
                              <div className="bg-amber-500/20 p-2 rounded-xl">
                                <ShieldAlert className="w-5 h-5 text-amber-500" />
                              </div>
                              <div>
                                <h4 className="text-sm font-bold text-amber-500">Hasil Tidak Spesifik</h4>
                                <p className="text-[11px] text-[#808080] mt-1 leading-relaxed">
                                  Sistem tidak menemukan berita yang benar-benar cocok dalam sebulan terakhir, 
                                  namun berikut adalah hasil pencarian yang mungkin relevan bagi Anda.
                                </p>
                              </div>
                            </motion.div>
                          )}

                          <div className="flex items-center justify-between mb-2">
                            <h3 className="text-xs font-black text-[#505050] uppercase tracking-[0.3em]">AI Recommendations</h3>
                            <div className="flex items-center gap-4">
                              <span className="text-[10px] text-emerald-500 font-bold bg-emerald-500/10 px-2 py-0.5 rounded-full">FOUND {researchResults.length} ARTICLES</span>
                              {selectedResearchArticles.length > 0 && (
                                <span className="text-[10px] text-[#2A35D1] font-bold bg-[#2A35D1]/10 px-2 py-0.5 rounded-full uppercase tracking-wider">
                                  {selectedResearchArticles.length} SELECTED
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Quick Analysis Trigger for Research Tab */}
                          {selectedResearchArticles.length >= 1 && (
                            <motion.div
                              initial={{ opacity: 0, y: 10 }}
                              animate={{ opacity: 1, y: 0 }}
                              className="bg-gradient-to-r from-[#2A35D1]/20 to-transparent border-l-2 border-[#2A35D1] p-6 rounded-r-3xl flex flex-col md:flex-row items-center justify-between gap-6 mb-8"
                            >
                              <div className="space-y-1">
                                <h4 className="text-sm font-bold text-white">Ready for Framing Analysis?</h4>
                                <p className="text-xs text-[#808080]">Anda telah memilih {selectedResearchArticles.length} artikel. Mulai dekonstruksi narasi sekarang.</p>
                              </div>
                              <button
                                onClick={runAnalysis}
                                className="px-8 py-3 rounded-xl bg-[#2A35D1] text-white text-xs font-bold shadow-lg shadow-[#2A35D1]/30 hover:scale-105 active:scale-95 transition-all flex items-center gap-2 whitespace-nowrap"
                              >
                                <Cpu className="w-4 h-4" />
                                Jalankan Analisis Sekarang
                              </button>
                            </motion.div>
                          )}

                          <div className="grid grid-cols-1 gap-4">
                            {researchResults.map((article, idx) => {
                              const isAdded = selectedResearchArticles.some(a => a.url === article.url);
                              return (
                                <motion.div
                                  key={idx}
                                  initial={{ opacity: 0, x: -20 }}
                                  animate={{ opacity: 1, x: 0 }}
                                  transition={{ delay: idx * 0.1 }}
                                  className={cn(
                                    "bg-[#0E1117] border rounded-3xl p-6 transition-all group relative overflow-hidden",
                                    isAdded ? "border-emerald-500/30 bg-emerald-500/[0.02]" : "border-white/5 hover:border-[#2A35D1]/30"
                                  )}
                                >
                                  {/* Background subtle glow on hover */}
                                  {!isAdded && <div className="absolute inset-0 bg-gradient-to-br from-[#2A35D1]/0 to-[#2A35D1]/0 group-hover:from-[#2A35D1]/5 group-hover:to-transparent transition-all duration-500" />}
                                  
                                  <div className="flex justify-between items-start gap-6 relative z-10">
                                    <div className="space-y-4 flex-1">
                                      <div className="space-y-2">
                                        <div className="flex items-center gap-2">
                                          <div className="px-2 py-0.5 rounded-md bg-white/5 border border-white/5 text-[9px] font-black text-[#808080] uppercase tracking-wider flex items-center gap-1.5">
                                            <Globe className="w-3 h-3 text-[#2A35D1]" />
                                            {article.source || 'Unknown Source'}
                                          </div>
                                          {article.publishedDate && (
                                            <div className="px-2 py-0.5 rounded-md bg-white/5 border border-white/5 text-[9px] font-black text-[#606060] uppercase tracking-wider flex items-center gap-1.5">
                                              <Calendar className="w-3 h-3 text-amber-500/50" />
                                              {article.publishedDate}
                                            </div>
                                          )}
                                          {isAdded && (
                                            <div className="px-2 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-[9px] font-black text-emerald-500 uppercase tracking-wider flex items-center gap-1">
                                              <CheckCircle2 className="w-3 h-3" />
                                              Added to Queue
                                            </div>
                                          )}
                                        </div>
                                        <a 
                                          href={article.url} 
                                          target="_blank" 
                                          rel="noopener noreferrer"
                                          className="block group/link"
                                        >
                                          <h4 className="text-lg font-bold text-white group-hover/link:text-[#2A35D1] transition-colors flex items-center gap-2">
                                            {article.title}
                                            <Link2 className="w-4 h-4 opacity-0 group-hover/link:opacity-100 transition-all -translate-x-2 group-hover/link:translate-x-0" />
                                          </h4>
                                        </a>
                                        <p className="text-sm text-[#808080] line-clamp-2 leading-relaxed">{article.snippet}</p>
                                      </div>

                                      <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2">
                                        <div className="flex items-center gap-2 text-[10px] font-black text-[#2A35D1] uppercase tracking-[0.2em]">
                                          <BrainCircuit className="w-3 h-3" />
                                          AI Insights
                                        </div>
                                        <p className="text-xs text-[#606060] leading-relaxed italic">
                                          "{article.reason}"
                                        </p>
                                      </div>
                                    </div>

                                    <button
                                      onClick={() => toggleResearchArticle(article)}
                                      className={cn(
                                        "shrink-0 w-12 h-12 rounded-2xl transition-all flex items-center justify-center shadow-lg shadow-black/20",
                                        isAdded 
                                          ? "bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white border border-red-500/20" 
                                          : "bg-[#2A35D1]/10 text-[#2A35D1] hover:bg-[#2A35D1] hover:text-white"
                                      )}
                                      title={isAdded ? "Batal pilih" : "Gunakan artikel ini untuk analisis"}
                                    >
                                      {isAdded ? <X className="w-6 h-6" /> : <Plus className="w-6 h-6" />}
                                    </button>
                                  </div>
                                </motion.div>
                              );
                            })}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                )}

                {activeTab !== 'research' && (
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {(activeTab === 'manual' ? manualInputs : urlInputs).map((input, idx) => (
                    <motion.div
                      layout
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      key={idx}
                      className="group relative bg-[#11141C] border border-white/5 rounded-3xl p-6 focus-within:border-[#2A35D1]/50 transition-all hover:bg-[#141824] hover:shadow-2xl hover:shadow-[#2A35D1]/5"
                    >
                      <div className="flex justify-between items-center mb-6">
                        <div className="flex items-center gap-2">
                          <div className="w-1.5 h-1.5 rounded-full bg-[#2A35D1]" />
                          <span className="text-[10px] font-black text-[#606060] tracking-[0.4em] uppercase">Source 0{idx + 1}</span>
                        </div>
                        {(activeTab === 'manual' ? manualInputs : urlInputs).length > 2 && (
                          <button onClick={() => handleRemoveInput(idx)} className="text-[#505050] hover:text-red-500 transition-colors p-1 rounded-lg hover:bg-red-500/10">
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                      {activeTab === 'link' ? (
                        <div className="relative">
                          <Link2 className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-[#606060] group-focus-within:text-[#2A35D1] transition-colors" />
                          <input
                            type="text"
                            value={input}
                            onChange={(e) => updateInput(idx, e.target.value)}
                            placeholder="Paste article direct link..."
                            className="w-full bg-[#080A0E] border border-white/5 rounded-2xl py-4 pl-12 pr-4 text-sm focus:ring-1 focus:ring-[#2A35D1]/50 outline-none transition-all placeholder:text-[#505050] text-white"
                          />
                        </div>

                      ) : (
                        <textarea
                          value={input}
                          onChange={(e) => updateInput(idx, e.target.value)}
                          placeholder="Paste article text content here..."
                          className="w-full bg-[#080A0E] border border-white/5 rounded-2xl p-4 text-sm focus:ring-1 focus:ring-[#2A35D1]/50 outline-none h-48 resize-none transition-all placeholder:text-[#505050] text-white leading-relaxed"
                        />
                      )}
                    </motion.div>
                  ))}
                  {(activeTab === 'manual' ? manualInputs : urlInputs).length < 3 && (
                    <motion.button
                      layout
                      onClick={handleAddInput}
                      className="h-full min-h-[140px] rounded-3xl border-2 border-dashed border-white/10 flex flex-col items-center justify-center gap-3 text-[#A0A0A0] hover:text-[#2A35D1] hover:border-[#2A35D1]/30 transition-all bg-white/[0.01] hover:bg-[#2A35D1]/5 group/add"
                    >
                      <div className="w-12 h-12 rounded-full border border-dashed border-[#606060] group-hover/add:border-[#2A35D1] flex items-center justify-center transition-colors bg-[#11141C]">
                        <Plus className="w-6 h-6" />
                      </div>
                      <span className="text-[11px] font-black uppercase tracking-[0.3em]">Add Source</span>
                    </motion.button>
                  )}
                </div>
                )}

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
                      {isAnalyzing 
                        ? "Menganalisis Framing..." 
                        : activeTab === 'research' 
                          ? "Analisis Hasil Riset" 
                          : activeTab === 'manual' 
                            ? "Analisis Teks Manual" 
                            : "Analisis Daftar URL"}
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
      active ? "bg-[#2A35D1] text-white shadow-md shadow-[#2A35D1]/10" : "text-[#A0A0A0] hover:text-white"
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
