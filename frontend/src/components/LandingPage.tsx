/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React from 'react';
import { motion } from 'motion/react';
import { BookOpen, Target, Scale, Zap, Info, ArrowRight, ShieldCheck, Cpu } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen bg-[#06080B] text-[#F0F0F0] font-sans selection:bg-[#2A35D1]/40">
      {/* Background Decorative Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#2A35D1]/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#3A45E1]/5 blur-[120px] rounded-full" />
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay" />
      </div>

      {/* Navigation */}
      <nav className="relative z-20 flex justify-between items-center px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#2A35D1] to-[#6A75E1] flex items-center justify-center shadow-lg shadow-[#2A35D1]/20">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <span className="text-xl font-black tracking-tighter text-white uppercase">
            Omnius
          </span>
        </div>
        <div className="hidden md:flex absolute left-1/2 -translate-x-1/2 gap-8 text-sm font-medium text-[#808080]">
          <a href="#metode" className="hover:text-white transition-colors">Metodologi</a>
          <a href="#arsitektur" className="hover:text-white transition-colors">Arsitektur AI</a>
        </div>
        <button
          onClick={() => navigate('/workspace')}
          className="px-6 py-2 rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 text-white text-sm font-medium transition-all"
        >
          Masuk Dashboard
        </button>
      </nav>

      {/* Hero Section */}
      <section className="relative z-10 pt-20 pb-32 px-6 flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#2A35D1]/10 border border-[#2A35D1]/20 text-[#6A75E1] text-[10px] font-bold uppercase tracking-[0.2em] mb-8"
        >
          <ShieldCheck className="w-3 h-3" /> Media Intelligence Platform
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-6xl md:text-8xl font-bold tracking-tight text-white mb-8 leading-[0.9]"
        >
          Analisis Framing <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-white via-white to-[#2A35D1]">dan Bias Berita.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-lg md:text-xl text-[#A0A0A0] max-w-2xl mx-auto mb-12 font-light leading-relaxed"
        >
          Analisis framing otomatis berbasis teori <strong className="text-white font-semibold">Robert Entman</strong>, didukung infrastruktur <strong className="text-white font-semibold">LLM (Llama 3.3 & Qwen 3)</strong> untuk mengungkap bias sistemik media massa.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="flex flex-col sm:flex-row gap-4"
        >
          <button
            onClick={() => navigate('/workspace')}
            className="group px-10 py-5 rounded-2xl bg-[#2A35D1] hover:bg-[#3A45E1] text-white font-bold transition-all flex items-center gap-3 shadow-2xl shadow-[#2A35D1]/30"
          >
            Mulai Analisis Sekarang <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>
      </section>

      {/* Methodology Grid */}
      <section id="metode" className="relative z-10 py-24 border-t border-white/5 bg-[#080A0E]/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-20 lg:items-end">
            <div className="lg:col-span-7 xl:col-span-6 shrink-0">
              <span className="text-[10px] font-bold text-[#2A35D1] uppercase tracking-[0.3em] mb-4 block">Theoretical Foundation</span>
              <h2 className="text-4xl md:text-5xl lg:text-[44px] xl:text-5xl font-bold text-white leading-tight">
                <span className="inline-block whitespace-nowrap">4 Pilar Framing Theory</span> <br />Menurut Robert Entman
              </h2>
            </div>
            <div className="lg:col-span-5 xl:col-span-5 xl:col-start-8 flex flex-col gap-3">
              <p className="text-[#808080] text-lg">
                Menjembatani teori akademis dengan kecanggihan AI untuk membantu Anda memahami narasi dari segala sudut pandang secara akurat.
              </p>
              <a
                href="https://fbaum.unc.edu/teaching/articles/J-Communication-1993-Entman.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-[#2A35D1] font-bold hover:text-white transition-colors flex items-center gap-2 w-fit"
              >
                Lihat Jurnal Asli (PDF) &rarr;
              </a>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <FeatureCard
              icon={Info}
              title="Problem Definition"
              desc="Identifikasi apa yang dianggap masalah dan apa yang dipertaruhkan dalam isu tersebut."
              index={0}
            />
            <FeatureCard
              icon={Target}
              title="Causal Interpretation"
              desc="Menentukan siapa aktor yang bertanggung jawab atas terjadinya masalah tersebut."
              index={1}
            />
            <FeatureCard
              icon={Scale}
              title="Moral Evaluation"
              desc="Penilaian normatif berdasarkan norma etika yang berlaku pada masyarakat."
              index={2}
            />
            <FeatureCard
              icon={BookOpen}
              title="Treatment Policy"
              desc="Rekomendasi solusi atau hasil akhir yang diinginkan oleh narasi media."
              index={3}
            />
          </div>
        </div>
      </section>

      {/* Architecture Info */}
      <section id="arsitektur" className="py-24 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 mb-20 lg:items-end">
            <div className="lg:col-span-7 xl:col-span-6 shrink-0">
              <span className="text-[10px] font-bold text-[#2A35D1] uppercase tracking-[0.3em] mb-4 block">System Architecture</span>
              <h2 className="text-4xl md:text-5xl font-bold text-white leading-tight">
                <span className="inline-block whitespace-nowrap">High-Performance</span> <br /> AI Pipeline
              </h2>
            </div>
            <div className="lg:col-span-5 xl:col-span-5 xl:col-start-8 flex flex-col gap-3">
              <p className="text-[#808080] text-lg">
                Didukung oleh arsitektur <i>asynchronous</i> FastAPI dan integrasi Groq Cloud, menghadirkan <i>pipeline</i> NLP dengan latensi ultra-rendah untuk ekstraksi narasi skala besar.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <Zap className="w-6 h-6 text-amber-400" />
              </div>
              <h4 className="text-xl font-bold text-white">Groq API Velocity</h4>
              <p className="text-sm text-[#808080] leading-relaxed">Kecepatan inferensi AI tinggi untuk ekstraksi data secara real-time tanpa penundaan.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
              </div>
              <h4 className="text-xl font-bold text-white">Advanced Cleaning</h4>
              <p className="text-sm text-[#808080] leading-relaxed">Scraper kami secara cerdas membersihkan iklan, navigasi, dan konten tidak relevan dari website berita.</p>
            </div>
            <div className="space-y-4">
              <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-purple-400" />
              </div>
              <h4 className="text-xl font-bold text-white">Structured Output</h4>
              <p className="text-sm text-[#808080] leading-relaxed">Hasil analisis disajikan dalam laporan komprehensif untuk memperdalam wawasan strategis Anda.</p>
            </div>
          </div>
        </div>
      </section>

      <footer className="py-12 border-t border-white/5 text-center">
        <p className="text-[10px] text-[#404040] uppercase tracking-widest">Powered by Groq Cloud • Felix Hardyan 2026</p>
      </footer>
    </div>
  );
};

const FeatureCard = ({ icon: Icon, title, desc, index }: { icon: any, title: string, desc: string, index: number }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay: index * 0.1 }}
    viewport={{ once: true }}
    className="group p-8 rounded-3xl bg-[#10131A] border border-white/5 hover:border-[#2A35D1]/30 transition-all hover:bg-[#141824] relative overflow-hidden"
  >
    <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
      <Icon className="w-24 h-24" />
    </div>
    <div className="relative z-10">
      <Icon className="w-8 h-8 text-[#2A35D1] mb-6" />
      <h3 className="text-lg font-bold text-white mb-3">{title}</h3>
      <p className="text-sm text-[#808080] leading-relaxed">{desc}</p>
    </div>
  </motion.div>
);

