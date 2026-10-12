import React from 'react';
import { Plus, MessageSquare, Trash2, Clock, Sparkles, X, ChevronRight } from 'lucide-react';

export default function ChatHistorySidebar({
  isOpen,
  onClose,
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
  isD10S
}) {
  const themeBorder = isD10S ? 'border-cyan-500/30' : 'border-amber-500/30';
  const themeAccent = isD10S ? 'text-cyan-400' : 'text-amber-400';
  const themeBgActive = isD10S ? 'bg-cyan-950/40 border-cyan-500/50' : 'bg-amber-950/40 border-amber-500/50';
  const themeGlow = isD10S ? 'shadow-[0_0_15px_rgba(6,182,212,0.15)]' : 'shadow-[0_0_15px_rgba(245,158,11,0.15)]';
  const themeNewBtn = isD10S
    ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.4)]'
    : 'bg-gradient-to-r from-red-600 to-amber-500 text-black shadow-[0_0_15px_rgba(245,158,11,0.4)]';

  if (!isOpen) return null;

  return (
    <aside className={`fixed inset-y-0 left-0 z-50 w-72 sm:w-80 bg-slate-950/95 backdrop-blur-2xl border-r ${themeBorder} flex flex-col shadow-2xl transition-all duration-300 animate-in slide-in-from-left select-none font-sans`}>
      
      {/* HEADER DE LA BARRA LATERAL */}
      <div className="p-4 border-b border-slate-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className={`w-4 h-4 ${themeAccent}`} />
          <h2 className="font-orbitron text-xs sm:text-sm font-bold text-white tracking-wider">
            HISTORIAL // MEMORIA
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-900 transition-all"
          title="Cerrar panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* BOTÓN NUEVO CHAT (ESTILO GEMINI) */}
      <div className="p-3">
        <button
          onClick={() => {
            onNewChat();
            if (window.innerWidth < 768) onClose();
          }}
          className={`w-full py-2.5 px-3.5 rounded-xl font-rajdhani font-black text-xs sm:text-sm tracking-wider flex items-center justify-center gap-2 transition-all hover:scale-[1.02] active:scale-95 ${themeNewBtn}`}
        >
          <Plus className="w-4 h-4 stroke-[3]" />
          <span>NUEVA CONVERSACIÓN</span>
        </button>
      </div>

      {/* LISTA DE CONVERSACIONES GUARDADAS */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1.5 min-h-0">
        <div className="px-2 pb-1 text-[10px] font-mono font-bold tracking-widest text-slate-500 uppercase">
          CHATS RECIENTES ({chats.length})
        </div>

        {chats.length === 0 ? (
          <div className="p-6 text-center text-xs text-slate-500 italic">
            No hay conversaciones previas en el historial. ¡Inicia un nuevo chat!
          </div>
        ) : (
          chats.map((chat) => {
            const isActive = chat.id === activeChatId;
            return (
              <div
                key={chat.id}
                onClick={() => {
                  onSelectChat(chat.id);
                  if (window.innerWidth < 768) onClose();
                }}
                className={`group relative p-2.5 rounded-xl border transition-all cursor-pointer flex items-center justify-between gap-2 ${
                  isActive
                    ? `${themeBgActive} ${themeGlow} text-white`
                    : 'bg-slate-900/40 border-slate-800/60 text-slate-300 hover:bg-slate-900/80 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center gap-2.5 min-w-0 flex-1">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${isActive ? themeAccent : 'text-slate-500 group-hover:text-slate-400'}`} />
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-semibold truncate text-slate-200">
                      {chat.title || "Conversación 10N-AI"}
                    </p>
                    <span className="text-[10px] text-slate-500 font-mono flex items-center gap-1">
                      <Clock className="w-2.5 h-2.5" />
                      {chat.timestamp || "Reciente"}
                    </span>
                  </div>
                </div>

                {/* BOTÓN ELIMINAR */}
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChat(chat.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/40 transition-all shrink-0"
                  title="Eliminar conversación"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* FOOTER INFORMACIÓN DE MEMORIA */}
      <div className="p-3 border-t border-slate-800/80 text-[10px] font-mono text-slate-500 flex items-center justify-between">
        <span>MEMORIA LOCAL: ACTIVA</span>
        <span className="text-emerald-400 font-bold">100% PERSISTENTE</span>
      </div>

    </aside>
  );
}
