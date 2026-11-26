import React from 'react';
import { RotateCcw, PanelLeftOpen, PanelLeftClose, MessageSquare, Sparkles } from 'lucide-react';

export default function Navbar({
  persona,
  onSwitchPersona,
  onResetChat,
  onToggleSidebar,
  sidebarOpen,
  chatCount = 0,
  viewMode = 'chat',
  onSwitchViewMode
}) {
  const isD10S = persona === 'd10s';

  return (
    <header className="w-full px-4 sm:px-6 py-3 border-b border-slate-800/80 backdrop-blur-xl bg-slate-950/70 sticky top-0 z-50 flex items-center justify-between gap-2">
      
      {/* BRAND & BOTÓN DE HISTORIAL */}
      <div className="flex items-center gap-3">
        {viewMode === 'chat' && (
          <button
            onClick={onToggleSidebar}
            className={`p-2 rounded-xl border transition-all flex items-center gap-1.5 ${
              sidebarOpen
                ? (isD10S ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(6,182,212,0.3)]' : 'bg-amber-500/20 border-amber-400 text-amber-300 shadow-[0_0_12px_rgba(245,158,11,0.3)]')
                : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
            title="Historial de conversaciones"
          >
            {sidebarOpen ? <PanelLeftClose className="w-4 h-4 sm:w-5 sm:h-5" /> : <PanelLeftOpen className="w-4 h-4 sm:w-5 sm:h-5" />}
            {chatCount > 0 && (
              <span className="hidden sm:inline-block text-[10px] font-mono px-1.5 py-0.5 rounded-full bg-slate-800 text-slate-300">
                {chatCount}
              </span>
            )}
          </button>
        )}

        <div>
          <h1 className="font-orbitron text-base sm:text-xl font-black tracking-wider text-white">
            10N-AI
          </h1>
        </div>
      </div>

      {/* SELECTOR DE VISTA: HUD CHAT vs STUDIO MULTIMODAL DEEP LEARNING */}
      <div className="flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl shadow-inner">
        <button
          type="button"
          onClick={() => onSwitchViewMode && onSwitchViewMode('chat')}
          className={`flex items-center gap-1.5 px-3 sm:px-4 py-1.5 rounded-lg font-rajdhani font-bold text-xs tracking-wider transition-all duration-300 ${
            viewMode === 'chat'
              ? 'bg-slate-800 text-white shadow-sm font-black'
              : 'text-slate-400 hover:text-white'
          }`}
          title="Modo Asistente Conversacional y Modelos Predictivos"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">HUD CHAT</span>
        </button>

        <button
          type="button"
          onClick={() => onSwitchViewMode && onSwitchViewMode('studio')}
          className={`flex items-center gap-1.5 px-3 sm:px-4 py-1.5 rounded-lg font-rajdhani font-bold text-xs tracking-wider transition-all duration-300 ${
            viewMode === 'studio'
              ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-slate-950 shadow-[0_0_12px_rgba(6,182,212,0.4)] font-black'
              : 'text-slate-400 hover:text-cyan-300'
          }`}
          title="Modo Studio Deep Learning Multimodal (Proyecto 2)"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>STUDIO DL</span>
        </button>
      </div>

      {/* SELECTOR DUAL-CORE DE PERSONALIDAD (EN MODO CHAT) Y ACCIONES */}
      <div className="flex items-center gap-2">
        {viewMode === 'chat' ? (
          <>
            <div className="flex items-center bg-slate-900/90 border border-slate-800 p-1 rounded-xl shadow-inner">
              <button
                type="button"
                onClick={() => onSwitchPersona('d10s')}
                className={`px-3 sm:px-4 py-1.5 rounded-lg font-rajdhani font-bold text-xs tracking-wider transition-all duration-300 ${
                  isD10S
                    ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.5)] font-black'
                    : 'text-slate-400 hover:text-cyan-300'
                }`}
                title="Cambiar al Core D10S (Messi)"
              >
                <span>D10S</span>
              </button>

              <button
                type="button"
                onClick={() => onSwitchPersona('cr7')}
                className={`px-3 sm:px-4 py-1.5 rounded-lg font-rajdhani font-bold text-xs tracking-wider transition-all duration-300 ${
                  !isD10S
                    ? 'bg-gradient-to-r from-red-600 to-amber-500 text-black shadow-[0_0_15px_rgba(239,68,68,0.5)] font-black'
                    : 'text-slate-400 hover:text-amber-300'
                }`}
                title="Cambiar al Core CR7 (Cristiano Ronaldo)"
              >
                <span>CR7</span>
              </button>
            </div>

            <button
              onClick={onResetChat}
              className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800 transition-all"
              title="Reiniciar conversación actual"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </>
        ) : (
          <div className="hidden sm:flex items-center px-3 py-1 rounded-xl bg-cyan-950/30 border border-cyan-500/30 text-[11px] font-mono text-cyan-300">
            PROYECTO 2 · DL STUDIO
          </div>
        )}
      </div>

    </header>
  );
}
