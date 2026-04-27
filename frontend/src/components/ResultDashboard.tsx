/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { motion } from 'motion/react';
import { AnalysisResult, NewsAnalysis } from '../types';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { KeywordRelationshipGraph } from './KeywordRelationshipGraph';
import { Share2, FileText, TrendingUp, Users, AlertCircle, Bookmark, Compass, Download, Filter, Network, GitCompare } from 'lucide-react';
import { cn } from '../lib/utils';

interface ResultDashboardProps {
  data: AnalysisResult;
}

export const ResultDashboard: React.FC<ResultDashboardProps> = ({ data }) => {
  const { analyses, comparativeReport } = data;

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      default: return '#3b82f6';
    }
  };

  return (
    <div className="space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-1000">
      {/* Header Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-[#0E1117] p-6 rounded-3xl border border-white/5">
        <div>
          <h2 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <Compass className="w-6 h-6 text-[#2A35D1]" /> Result Summary & Reporting
          </h2>
          <p className="text-xs text-[#606060] mt-1 font-mono tracking-tighter italic">Berdasarkan Metodologi Robert Entman (1993)</p>
        </div>
      </div>

      {/* 1. Bias Intelligence (Moved to top as requested) */}
      <section className="bg-[#11151F] border border-[#2A35D1]/30 rounded-3xl p-10 flex flex-col md:flex-row items-center gap-8 shadow-2xl shadow-[#2A35D1]/10">
        <div className="w-20 h-20 rounded-2xl bg-[#2A35D1]/10 border border-[#2A35D1]/30 flex items-center justify-center shrink-0">
          <AlertCircle className="w-10 h-10 text-[#2A35D1]" />
        </div>
        <div>
          <h4 className="text-[#2A35D1] font-black mb-2 uppercase tracking-[0.3em] text-[10px]">Bias Intelligence Indicator</h4>
          <p className="text-xl md:text-2xl text-white font-medium italic leading-snug">
            "{comparativeReport.biasIndicator}"
          </p>
        </div>
      </section>

      {/* 2. Narrative Synthesis (Comparative Summary) */}
      <section className="bg-[#0E1117] border border-white/5 rounded-3xl p-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#2A35D1]/5 blur-[120px] rounded-full" />
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-8">
            <GitCompare className="w-5 h-5 text-[#2A35D1]" />
            <h3 className="text-lg font-bold text-white tracking-tight">Analisis Komparatif Narasi Berita</h3>
          </div>
          <p className="text-sm text-[#808080] leading-relaxed font-light mb-8">
            {comparativeReport.summary}
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CollapsibleItem 
              title="Shared Narratives" 
              items={comparativeReport.sharedNarratives} 
              color="text-emerald-400" 
              bg="bg-emerald-500/5"
              border="border-emerald-500/10"
            />
            <CollapsibleItem 
              title="Key Discrepancies" 
              items={comparativeReport.keyDifferences} 
              color="text-ruby-400" 
              bg="bg-ruby-500/5"
              border="border-ruby-500/10"
            />
          </div>
        </div>
      </section>

      {/* 3. Framing Analysis per Media (Entman Pillars) */}
      <section className="p-8 rounded-3xl bg-[#0E1117] border border-white/5">
        <div className="flex items-center gap-3 mb-8">
          <FileText className="w-5 h-5 text-[#2A35D1]" />
          <h3 className="text-lg font-bold text-white tracking-tight">Framing Analysis Deconstruction</h3>
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {analyses.map((analysis, idx) => (
            <div key={idx} className="bg-[#06080B] border border-white/5 rounded-3xl overflow-hidden flex flex-col group transition-all hover:border-[#2A35D1]/30">
              <div className="p-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
                <div>
                  <span className="text-[10px] font-black text-[#2A35D1] tracking-[0.3em] uppercase">{analysis.source}</span>
                  <h3 className="text-lg font-bold text-white truncate max-w-sm">{analysis.title}</h3>
                </div>
                <Bookmark className="w-4 h-4 text-[#303030] group-hover:text-[#2A35D1] transition-colors" />
              </div>
              
              <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-8">
                <PillarBox label="Problem Definition" content={analysis.framing.problemDefinition} />
                <PillarBox label="Causal Interpretation" content={analysis.framing.causalInterpretation} />
                <PillarBox label="Moral Evaluation" content={analysis.framing.moralEvaluation} />
                <PillarBox label="Treatment Recommendation" content={analysis.framing.treatmentRecommendation} />
              </div>

              <div className="mt-auto p-6 bg-white/[0.02] flex flex-wrap gap-2">
                {analysis.keywords.map((k, i) => (
                  <span key={i} className="px-3 py-1 rounded-full bg-[#1A1E26] text-[10px] text-[#505050] font-medium border border-white/5">
                    #{k}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. Sentiment Distribution */}
      <section className="p-8 rounded-3xl bg-[#0E1117] border border-white/5">
        <div className="flex items-center gap-3 mb-10">
          <TrendingUp className="w-5 h-5 text-[#2A35D1]" />
          <h3 className="text-lg font-bold text-white tracking-tight">Sentiment Distribution Across Media</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
          {analyses.map((a, i) => (
            <div key={i} className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-xs font-black text-[#2A35D1] uppercase tracking-[0.2em]">{a.source}</span>
                <span className={cn(
                  "text-sm font-mono font-bold",
                  a.overallSentiment > 0.1 ? "text-emerald-400" : a.overallSentiment < -0.1 ? "text-ruby-400" : "text-blue-400"
                )}>
                  {a.overallSentiment > 0.1 ? 'OPTIMISTIK' : a.overallSentiment < -0.1 ? 'KRITIS' : 'NETRAL'} ({Math.round(a.overallSentiment * 100)})
                </span>
              </div>
              <div className="h-3 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
                <motion.div 
                  initial={{ width: 0 }}
                  animate={{ width: `${((a.overallSentiment + 1) / 2) * 100}%` }}
                  className={cn(
                    "h-full rounded-full transition-all duration-1000",
                    a.overallSentiment > 0.1 ? "bg-gradient-to-r from-emerald-600 to-emerald-400" : 
                    a.overallSentiment < -0.1 ? "bg-gradient-to-r from-ruby-600 to-ruby-400" : "bg-gradient-to-r from-blue-600 to-blue-400"
                  )}
                />
              </div>
              <div className="flex justify-between text-[9px] font-mono text-[#404040] uppercase tracking-widest">
                <span>Negative</span>
                <span>Neutral</span>
                <span>Positive</span>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 5. Improved Actor Mapping (Grouped by Source) */}
      <section className="p-8 rounded-3xl bg-[#0E1117] border border-white/5">
        <div className="flex items-center gap-3 mb-8">
          <Users className="w-5 h-5 text-[#2A35D1]" />
          <h3 className="text-lg font-bold text-white tracking-tight">Actor Mapping Matrix</h3>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {analyses.map((a, idx) => (
            <div key={idx} className="space-y-4">
              <h4 className="text-[10px] font-black text-[#606060] uppercase tracking-[0.4em] mb-4">{a.source} Perspectives</h4>
              <div className="space-y-3">
                {a.actors.map((actor, aidx) => (
                  <div key={aidx} className="flex items-center justify-between p-4 rounded-2xl bg-[#06080B] border border-white/5 hover:border-[#2A35D1]/30 transition-all">
                    <div className="flex items-center gap-4">
                      <div className={cn(
                        "w-2 h-2 rounded-full",
                        getSentimentColor(actor.sentiment)
                      )} style={{ backgroundColor: getSentimentColor(actor.sentiment) }} />
                      <div>
                        <div className="text-sm font-bold text-white">{actor.name}</div>
                        <div className="text-[10px] text-[#505050] uppercase tracking-wider">{actor.role}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-[10px] font-mono text-[#404040]">{actor.relevance}% RELEVANCE</div>
                      <div className={cn(
                        "px-2 py-1 rounded text-[9px] font-bold uppercase tracking-widest",
                        actor.sentiment.toLowerCase() === 'positive' ? "bg-emerald-500/10 text-emerald-400" :
                        actor.sentiment.toLowerCase() === 'negative' ? "bg-ruby-500/10 text-ruby-400" : "bg-blue-500/10 text-blue-400"
                      )}>
                        {actor.sentiment}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 6. Narrative Network Matrix */}
      <section className="p-8 rounded-3xl bg-[#0E1117] border border-white/5 overflow-hidden">
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <Network className="w-5 h-5 text-[#2A35D1]" />
            <h3 className="text-lg font-bold text-white tracking-tight">Narrative Network Matrix</h3>
          </div>
          <div className="text-[10px] font-mono text-[#404040] uppercase tracking-widest hidden md:block">
            Algorithm: Force-Directed Narrative Mapping
          </div>
        </div>
        
        <KeywordRelationshipGraph analyses={analyses} />
        
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
            <h4 className="text-[10px] font-bold text-[#606060] uppercase mb-2 tracking-widest">Shared Nucleus</h4>
            <div className="flex flex-wrap gap-2">
              {Array.from(new Set(analyses.flatMap(a => a.keywords)))
                .filter(k => analyses.filter(a => a.keywords.includes(k)).length > 1)
                .map((k, i) => (
                <span key={i} className="px-3 py-1 rounded-full bg-[#2A35D1]/10 text-[#2A35D1] text-[10px] font-bold border border-[#2A35D1]/20">
                  {k}
                </span>
              ))}
            </div>
          </div>
          <div className="p-4 rounded-2xl bg-white/5 border border-white/5">
            <h4 className="text-[10px] font-bold text-[#606060] uppercase mb-2 tracking-widest">Divergent Points</h4>
            <div className="flex flex-wrap gap-2">
              {Array.from(new Set(analyses.flatMap(a => a.keywords)))
                .filter(k => analyses.filter(a => a.keywords.includes(k)).length === 1)
                .slice(0, 10)
                .map((k, i) => (
                <span key={i} className="px-3 py-1 rounded-full bg-white/5 text-[#808080] text-[10px] border border-white/5">
                  #{k}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

const ActionButton = ({ icon: Icon, label }: { icon: any, label: string }) => (
  <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/5 text-[10px] font-bold text-white uppercase tracking-widest hover:bg-[#2A35D1] hover:border-[#2A35D1] transition-all">
    <Icon className="w-3 h-3" /> {label}
  </button>
);

const CollapsibleItem = ({ title, items, color, bg, border }: { title: string, items: string[], color: string, bg: string, border: string }) => (
  <div className={cn("p-5 rounded-2xl border", bg, border)}>
    <span className={cn("text-[9px] font-black uppercase tracking-[0.3em] block mb-4", color)}>{title}</span>
    <ul className="space-y-3">
      {items.map((item, i) => (
        <li key={i} className="text-sm text-[#808080] leading-relaxed font-light flex gap-3">
          <span className="opacity-30 self-start mt-2 w-1.5 h-1.5 rounded-full bg-current shrink-0" />
          {item}
        </li>
      ))}
    </ul>
  </div>
);

const PillarBox = ({ label, content }: { label: string, content: string }) => (
  <div className="space-y-2">
    <h4 className="text-[9px] font-bold text-[#404040] uppercase tracking-[0.2em]">{label}</h4>
    <p className="text-sm text-[#808080] leading-relaxed font-light">{content}</p>
  </div>
);
