import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ParticleAvatar from './components/ParticleAvatar';
import ChatInterface from './components/ChatInterface';
import ChatHistorySidebar from './components/ChatHistorySidebar';

const CHATS_STORAGE_KEY = '10N_AI_CHATS_HISTORY_V1';

const createInitialChat = (persona = 'd10s') => ({
  id: `chat-${Date.now()}`,
  title: 'Nueva Conversación',
  timestamp: new Date().toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }),
  createdAt: Date.now(),
  messages: [
    {
      id: 1,
      sender: 'assistant',
      text: persona === 'd10s'
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
  const [persona, setPersona] = useState('d10s'); // 'd10s' o 'cr7'
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [latency, setLatency] = useState(0);

  // Historial de Chats (Estilo Gemini / ChatGPT con LocalStorage)
  const [chats, setChats] = useState(() => {
    try {
      const saved = localStorage.getItem(CHATS_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.warn("Error leyendo historial de chats de localStorage", e);
    }
    return [createInitialChat('d10s')];
  });

  const [activeChatId, setActiveChatId] = useState(() => {
    return chats[0]?.id || 'default';
  });

  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Persistir chats en localStorage cada vez que cambien
  useEffect(() => {
    try {
      localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));
    } catch (e) {
      console.warn("Error guardando chats en localStorage", e);
    }
  }, [chats]);

  // Ping periódico de salud al backend FastAPI
  useEffect(() => {
    const checkBackend = async () => {
      const t0 = performance.now();
      try {
        const res = await fetch('/api/health');
        if (res.ok) {
          const t1 = performance.now();
          setLatency(Math.round(t1 - t0));
          setBackendOnline(true);
        } else {
          setBackendOnline(false);
        }
      } catch (err) {
        setBackendOnline(false);
      }
    };

    checkBackend();
    const interval = setInterval(checkBackend, 5000);
    return () => clearInterval(interval);
  }, []);

  // Crear una nueva conversación
  const handleNewChat = () => {
    const newChat = createInitialChat(persona);
    setChats(prev => [newChat, ...prev]);
    setActiveChatId(newChat.id);
  };

  // Seleccionar chat existente
  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
  };

  // Eliminar chat
  const handleDeleteChat = (chatId) => {
    setChats(prev => {
      const filtered = prev.filter(c => c.id !== chatId);
      if (filtered.length === 0) {
        const fresh = createInitialChat(persona);
        setActiveChatId(fresh.id);
        return [fresh];
      }
      if (activeChatId === chatId) {
        setActiveChatId(filtered[0].id);
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

  const currentChat = chats.find(c => c.id === activeChatId) || chats[0] || createInitialChat(persona);

  return (
    <div className="h-screen w-screen bg-[#07090e] text-slate-100 flex flex-col overflow-hidden relative">
      {/* SIDEBAR DE HISTORIAL (ESTILO GEMINI) */}
      <ChatHistorySidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
        isD10S={persona === 'd10s'}
      />

      {/* NAVBAR SUPERIOR ESTILO GEMINI / CHATGPT */}
      <Navbar
        persona={persona}
        setPersona={setPersona}
        backendOnline={backendOnline}
        latency={latency}
        onResetChat={handleResetCurrentChat}
        onToggleSidebar={() => setSidebarOpen(prev => !prev)}
        sidebarOpen={sidebarOpen}
        chatCount={chats.length}
      />

      {/* ÁREA CENTRAL: AVATAR A LA IZQUIERDA Y CHAT EXTENDIDO HASTA EL FONDO */}
      <main className="flex-1 w-full min-h-0 flex flex-row overflow-hidden relative">
        
        {/* CARA DE PARTÍCULAS: A LA IZQUIERDA, TOTALMENTE LIBRE */}
        <aside className="w-[300px] lg:w-[340px] shrink-0 h-full flex flex-col items-center justify-center pl-4 lg:pl-6 pr-2 select-none z-10 pointer-events-auto">
          <ParticleAvatar
            persona={persona}
            isSpeaking={isSpeaking}
            isListening={isListening}
            emotion={detectedEmotion}
          />
        </aside>

        {/* CHAT CONVERSACIONAL EXTENDIDO HASTA ABAJO (ESTILO CHATGPT / GEMINI) */}
        <section className="flex-1 h-full min-h-0 min-w-0 flex flex-col items-center justify-between pr-3 lg:pr-8 pl-1">
          <div className="w-full max-w-4xl h-full min-h-0 flex flex-col">
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
          </div>
        </section>

      </main>
    </div>
  );
}
