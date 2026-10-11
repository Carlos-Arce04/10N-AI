import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ParticleAvatar from './components/ParticleAvatar';
import ChatInterface from './components/ChatInterface';

export default function App() {
  const [persona, setPersona] = useState('d10s'); // 'd10s' o 'cr7'
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [detectedEmotion, setDetectedEmotion] = useState(null);
  const [backendOnline, setBackendOnline] = useState(false);
  const [latency, setLatency] = useState(0);
  const [chatKey, setChatKey] = useState(0);

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

  return (
    <div className="h-screen w-screen bg-[#07090e] text-slate-100 flex flex-col overflow-hidden">
      {/* NAVBAR SUPERIOR ESTILO GEMINI / CHATGPT */}
      <Navbar
        persona={persona}
        setPersona={setPersona}
        backendOnline={backendOnline}
        latency={latency}
        onResetChat={() => setChatKey(prev => prev + 1)}
      />

      {/* ÁREA CENTRAL: CARA A LA IZQUIERDA A LA MITAD Y CHAT EXTENDIDO HASTA EL FONDO (CHATGPT/GEMINI) */}
      <main className="flex-1 w-full min-h-0 flex flex-row overflow-hidden relative">
        
        {/* CARA DE PARTÍCULAS: A LA IZQUIERDA, TOTALMENTE LIBRE, SIN NINGÚN FONDO NI CAJA, CENTRADA A LA MITAD */}
        <aside className="w-[320px] lg:w-[350px] shrink-0 h-full flex flex-col items-center justify-center pl-4 lg:pl-6 pr-2 select-none z-10 pointer-events-auto">
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
              key={chatKey}
              persona={persona}
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
