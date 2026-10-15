import React from 'react';
import { Zap, Wifi, RotateCcw, PanelLeftOpen, PanelLeftClose } from 'lucide-react';

export default function Navbar({
  persona,
  setPersona,
  backendOnline,
  latency,
  onResetChat,
  onToggleSidebar,
  sidebarOpen,
  chatCount = 0
}) {
  const isD10S = persona === 'd10s';

  return (
    <header className="w-full px-4 sm:px-6 py-3 border-b border-slate-800/80 backdrop-blur-xl bg-slate-950/70 sticky top-0 z-50 flex items-center justify-between">
      
      {/* BRAND, LOGO & BOTÓN DE HISTORIAL */}
      <div className="flex items-center gap-2.5 sm:gap-3">
        <button
          onClick={onToggleSidebar}
          className={`p-2 rounded-xl border transition-all flex items-center gap-1.5 ${
            sidebarOpen
              ? (isD10S ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.3)]' : 'bg-amber-500/20 border-amber-400 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.3)]')
              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
          }`}
          title="Historial de conversaciones (Estilo Gemini)"
        >
          {sidebarOpen ? <PanelLeftClose className="w-4 h-4 sm:w-5 sm:h-5" /> : <PanelLeftOpen className="w-4 h-4 sm:w-5 sm:h-5" />}
          {chatCount > 0 && (
            <span className="hidden sm:inline-block text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-300">
              {chatCount}
            </span>
          )}
        </button>

        <div className={`p-2 rounded-xl border transition-all ${
          isD10S 
            ? 'bg-cyan-500/10 border-cyan-400 text-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.3)]' 
            : 'bg-amber-500/10 border-amber-400 text-amber-400 shadow-[0_0_15px_rgba(245,158,11,0.3)]'
        }`}>
          <Zap className="w-4 h-4 sm:w-5 sm:h-5 animate-pulse" />
        </div>
        <div>
          <h1 className="font-orbitron text-base sm:text-lg font-black tracking-wider text-white">
            10N-AI
          </h1>
          <p className="text-[10px] sm:text-[11px] text-slate-400 font-rajdhani font-semibold tracking-wide hidden sm:block">
            ASISTENTE INTELIGENTE MULTIMODAL
          </p>
        </div>
      </div>

      {/* SELECTOR DUAL-CORE DE PERSONALIDAD */}
      <div className="flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl shadow-inner">
        <button
          onClick={() => setPersona('d10s')}
          className={`px-4 py-1.5 rounded-lg font-rajdhani font-bold text-xs tracking-wider transition-all duration-300 ${
            isD10S
              ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)] font-black'
              : 'text-slate-400 hover:text-cyan-300'
          }`}
        >
          <span>D10S</span>
        </button>

        <button
          onClick={() => setPersona('cr7')}
          className={`px-4 py-1.5 rounded-lg font-rajdhani font-bold text-xs tracking-wider transition-all duration-300 ${
            !isD10S
              ? 'bg-gradient-to-r from-red-600 to-amber-500 text-black shadow-[0_0_15px_rgba(239,68,68,0.5)] font-black'
              : 'text-slate-400 hover:text-amber-300'
          }`}
        >
          <span>CR7</span>
        </button>
      </div>

      {/* STATUS & RESET */}
      <div className="flex items-center gap-3">
        <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-lg border text-[11px] font-mono ${
          backendOnline
            ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-400'
            : 'bg-rose-950/40 border-rose-500/40 text-rose-400'
        }`}>
          <Wifi className={`w-3 h-3 ${backendOnline ? 'animate-pulse' : ''}`} />
          <span>{backendOnline ? `${latency}ms` : 'OFFLINE'}</span>
        </div>

        <button
          onClick={onResetChat}
          className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
          title="Reiniciar conversación"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

    </header>
  );
}
