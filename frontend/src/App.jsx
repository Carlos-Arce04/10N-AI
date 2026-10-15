import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ParticleAvatar from './components/ParticleAvatar';
import ChatInterface from './components/ChatInterface';
import ChatHistorySidebar from './components/ChatHistorySidebar';

const CHATS_STORAGE_KEY = '10N_AI_CHATS_HISTORY_V1';

const createInitialChat = (core = 'd10s') => ({
  id: `chat-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
  title: 'Nueva Conversación',
  persona: core,
  timestamp: new Date().toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
  createdAt: Date.now(),
  messages: [
    {
      id: 1,
      sender: 'assistant',
      text: core === 'd10s'
        ? "Hola, ¿cómo andás? Soy 10N-AI con el Core D10S. Preguntame lo que necesites sobre el valor de un auto, la calidad de un vino, precio de aguacates, retención de clientes o riesgo de salud. Podés seleccionar una opción abajo para ajustar los parámetros o escribirme directamente."
        : "¡Siuuu! Asistente 10N-AI activado con el Core CR7. Máxima potencia y precisión para responder a tus consultas. Elige una de las opciones a continuación para simular los parámetros o pregúntame lo que necesites.",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      interactiveModel: null,
      modelParams: null,
      modelResult: null,
      isExecuting: false
    }
  ]
});

export default function App() {
  // Historial de Chats (Estilo Gemini / ChatGPT con LocalStorage)
  const [chats, setChats] = useState(() => {
    try {
      const saved = localStorage.getItem(CHATS_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) return parsed;
      }
    } catch (e) {
      console.warn("Error leyendo historial de chats de localStorage", e);
    }
    return [createInitialChat('d10s')];
  });

  const [activeChatId, setActiveChatId] = useState(() => {
    return chats[0]?.id || null;
  });

  // Persona sincronizada con la conversación activa
  const [persona, setPersona] = useState(() => {
    return chats[0]?.persona || 'd10s';
  });

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Persistir chats en localStorage cada vez que cambien
  useEffect(() => {
    try {
      localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));
    } catch (e) {
      console.warn("Error guardando chats en localStorage", e);
    }
  }, [chats]);

  // Cortar de inmediato cualquier audio/voz en ejecución
  const stopVoice = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  // Crear una nueva conversación
  const handleNewChat = (specificPersona = null) => {
    stopVoice();
    const targetCore = specificPersona || persona;
    setPersona(targetCore);
    const newChat = createInitialChat(targetCore);
    setChats(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  // Cambio de Core desde el Navbar: siempre inicia una conversación nueva exclusiva para ese core
  const handleSwitchPersona = (newPersona) => {
    if (newPersona === persona && activeChatId) return;
    stopVoice();
    setPersona(newPersona);
    const newChat = createInitialChat(newPersona);
    setChats(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  // Seleccionar chat existente: corta voz y sincroniza automáticamente el avatar al core de ese chat
  const handleSelectChat = (chatId) => {
    stopVoice();
    setActiveChatId(chatId);
    const target = chats.find(c => c.id === chatId);
    if (target?.persona) {
      setPersona(target.persona);
    }
  };

  // Eliminar chat: si se borran todos, queda en estado vacío (no fuerza uno de Messi)
  const handleDeleteChat = (chatId) => {
    stopVoice();
    setChats(prev => {
      const filtered = prev.filter(c => c.id !== chatId);
      if (filtered.length === 0) {
        setActiveChatId(null);
        return [];
      }
      if (activeChatId === chatId) {
        setActiveChatId(filtered[0].id);
        if (filtered[0].persona) {
          setPersona(filtered[0].persona);
        }
      }
      return filtered;
    });
  };

  // Actualizar mensajes y título del chat activo
  const handleUpdateActiveChatMessages = (newMessages, autoTitle = null) => {
    setChats(prev => prev.map(chat => {
      if (chat.id === activeChatId) {
        const updated = { ...chat, messages: newMessages };
        if (autoTitle && (chat.title === 'Nueva Conversación' || !chat.title)) {
          updated.title = autoTitle.slice(0, 32) + (autoTitle.length > 32 ? '...' : '');
        }
        return updated;
      }
      return chat;
    }));
  };

  // Reset del chat actual manteniendo el mismo id
  const handleResetCurrentChat = () => {
    stopVoice();
    if (!activeChatId) return;
    const freshMessages = [
      {
        id: Date.now(),
        sender: 'assistant',
        text: persona === 'd10s'
          ? "Conversación reiniciada. ¿Con qué predicción o modelo de IA querés seguir, hermano?"
          : "¡Siuuu! Conversación restablecida a punto cero. Listo para ejecutar nuevas inferencias.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        interactiveModel: null,
        modelParams: null,
        modelResult: null,
        isExecuting: false
      }
    ];
    handleUpdateActiveChatMessages(freshMessages);
  };

  const currentChat = chats.find(c => c.id === activeChatId) || null;

  return (
    <div className="h-screen w-screen bg-[#07090e] text-slate-100 flex flex-col overflow-hidden relative">
      {/* SIDEBAR DE HISTORIAL (ESTILO GEMINI) */}
      <ChatHistorySidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={() => handleNewChat()}
        onDeleteChat={handleDeleteChat}
        isD10S={persona === 'd10s'}
      />

      {/* NAVBAR SUPERIOR LIMPIO (SIN PING, SIN RAYO, SIN SUBTÍTULO) */}
      <Navbar
        persona={persona}
        onSwitchPersona={handleSwitchPersona}
        onResetChat={handleResetCurrentChat}
        onToggleSidebar={() => setSidebarOpen(prev => !prev)}
        sidebarOpen={sidebarOpen}
        chatCount={chats.length}
      />

      {/* ÁREA CENTRAL: AVATAR A LA IZQUIERDA Y CHAT EXTENDIDO */}
      <main className="flex-1 w-full min-h-0 flex flex-row overflow-hidden relative">
        
        {/* CARA DE PARTÍCULAS: A LA IZQUIERDA */}
        <aside className="w-[300px] lg:w-[340px] shrink-0 h-full flex flex-col items-center justify-center pl-4 lg:pl-6 pr-2 select-none z-10 pointer-events-auto">
          <ParticleAvatar
            persona={persona}
            isSpeaking={isSpeaking}
            isListening={isListening}
            emotion={detectedEmotion}
          />
        </aside>

        {/* CHAT CONVERSACIONAL EXTENDIDO O PANTALLA DE CREAR NUEVO CHAT */}
        <section className="flex-1 h-full min-h-0 min-w-0 flex flex-col items-center justify-between pr-3 lg:pr-8 pl-1">
          <div className="w-full max-w-4xl h-full min-h-0 flex flex-col">
            {currentChat ? (
              <ChatInterface
                key={activeChatId}
                persona={persona}
                chatId={activeChatId}
                initialMessages={currentChat.messages}
                onUpdateMessages={handleUpdateActiveChatMessages}
                isSpeaking={isSpeaking}
                setIsSpeaking={setIsSpeaking}
                isListening={isListening}
                setIsListening={setIsListening}
                detectedEmotion={detectedEmotion}
              />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-6 text-center select-none">
                <div className="w-16 h-16 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center justify-center mb-5 shadow-[0_0_30px_rgba(6,182,212,0.15)]">
                  <span className="text-3xl">💬</span>
                </div>
                <h2 className="font-orbitron text-xl sm:text-2xl font-bold text-white mb-2 tracking-wide">
                  No hay conversaciones activas
                </h2>
                <p className="text-sm text-slate-400 max-w-md mb-8 font-rajdhani">
                  Elige un núcleo inteligente para comenzar una nueva conversación y explorar los modelos predictivos de IA.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-lg">
                  {/* Tarjeta Core D10S */}
                  <button
                    onClick={() => handleNewChat('d10s')}
                    className="group p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-cyan-500/30 hover:border-cyan-400 text-left transition-all duration-300 hover:shadow-[0_0_25px_rgba(6,182,212,0.25)] hover:scale-[1.02]"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-orbitron font-black text-sm text-cyan-400 tracking-wider">CORE D10S</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 font-mono">Messi</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed group-hover:text-slate-300">
                      Tono argentino cálido y analítico. Inferencia experta en predicciones y modelos.
                    </p>
                    <div className="mt-4 flex items-center gap-1.5 text-xs text-cyan-400 font-semibold">
                      <span>Iniciar conversación</span>
                      <span>→</span>
                    </div>
                  </button>

                  {/* Tarjeta Core CR7 */}
                  <button
                    onClick={() => handleNewChat('cr7')}
                    className="group p-5 rounded-2xl bg-gradient-to-b from-slate-900/90 to-slate-950/90 border border-amber-500/30 hover:border-amber-400 text-left transition-all duration-300 hover:shadow-[0_0_25px_rgba(245,158,11,0.25)] hover:scale-[1.02]"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-orbitron font-black text-sm text-amber-400 tracking-wider">CORE CR7</span>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 font-mono">Cristiano</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed group-hover:text-slate-300">
                      Máxima potencia, ambición y respuestas directas con mentalidad ganadora.
                    </p>
                    <div className="mt-4 flex items-center gap-1.5 text-xs text-amber-400 font-semibold">
                      <span>Iniciar conversación</span>
                      <span>→</span>
                    </div>
                  </button>
                </div>
              </div>
            )}
          </div>
        </section>

      </main>
    </div>
  );
}
