import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Sparkles, User, Volume2, VolumeX, Camera, Image, X, RefreshCw } from 'lucide-react';
import confetti from 'canvas-confetti';
import ModelSimulatorCard from './ModelSimulatorCard';

export default function ChatInterface({
  persona,
  chatId,
  initialMessages,
  onUpdateMessages,
  isSpeaking,
  setIsSpeaking,
  isListening,
  setIsListening,
  detectedEmotion
}) {
  const [messages, setMessages] = useState(() => {
    if (initialMessages && initialMessages.length > 0) return initialMessages;
    return [
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
    ];
  });

  const [inputVal, setInputVal] = useState('');
  const [loading, setLoading] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);

  // Reconocimiento de voz avanzado & dialecto
  const [voiceDialect, setVoiceDialect] = useState('es-419'); // 'es-419' (LatAm universal), 'es-CR', 'es-ES'
  const [interimTranscript, setInterimTranscript] = useState('');
  const recognitionRef = useRef(null);
  const silenceTimerRef = useRef(null);

  // Estados para cámara y adjuntos
  const [showCameraMenu, setShowCameraMenu] = useState(false);
  const [liveCameraActive, setLiveCameraActive] = useState(false);
  const [capturing, setCapturing] = useState(false);

  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const messagesEndRef = useRef(null);

  const isD10S = persona === 'd10s';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading, liveCameraActive]);

  // Sincronizar mensajes localmente y con el storage de la conversación
  const setMessagesAndSync = (updater, autoTitle = null) => {
    setMessages(prev => {
      const next = typeof updater === 'function' ? updater(prev) : updater;
      if (onUpdateMessages) {
        onUpdateMessages(next, autoTitle);
      }
      return next;
    });
  };

  // Manejar encendido de cámara en tiempo real
  const openLiveCamera = async () => {
    setShowCameraMenu(false);
    try {
      setLiveCameraActive(true);
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" }
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Error al acceder a la cámara:", err);
      alert("No se pudo acceder a la cámara web. Asegurate de dar permisos en Chrome.");
      setLiveCameraActive(false);
    }
  };

  const closeLiveCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop());
      videoRef.current.srcObject = null;
    }
    setLiveCameraActive(false);
  };

  // Capturar fotograma de la cámara en vivo
  const captureFrame = async () => {
    if (!videoRef.current || capturing) return;
    setCapturing(true);

    try {
      const video = videoRef.current;
      const canvas = document.createElement('canvas');
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const base64Data = canvas.toDataURL('image/jpeg', 0.85);

      closeLiveCamera();

      // Agregar mensaje del usuario con la foto capturada
      const userMsg = {
        id: Date.now(),
        sender: 'user',
        text: '📸 Foto tomada en tiempo real desde la cámara web',
        image: base64Data,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessagesAndSync(prev => [...prev, userMsg]);
      setLoading(true);

      // Enviar a la API de visión local
      const res = await fetch('/api/vision/sentiment-base64', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64Data })
      });
      const data = await res.json();

      handleVisionResponse(data);

    } catch (e) {
      console.error(e);
      alert("Error procesando captura");
    } finally {
      setCapturing(false);
      setLoading(false);
    }
  };

  // Adjuntar foto desde archivo local
  const handleFileSelect = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setShowCameraMenu(false);

    const reader = new FileReader();
    reader.onload = async () => {
      const base64Data = reader.result;

      // Mensaje de usuario
      const userMsg = {
        id: Date.now(),
        sender: 'user',
        text: `📁 Foto adjuntada: ${file.name}`,
        image: base64Data,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessagesAndSync(prev => [...prev, userMsg]);
      setLoading(true);

      try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch('/api/vision/sentiment', {
          method: 'POST',
          body: formData
        });
        const data = await res.json();

        handleVisionResponse(data);

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    reader.readAsDataURL(file);
    e.target.value = '';
  };

  // Procesar respuesta de visión e incorporar al chat con personalidad
  const handleVisionResponse = (data) => {
    let replyText = "";
    if (data.detected) {
      const em = data.dominant_emotion;
      const conf = Math.round((data.detection_confidence || 0.95) * 100);
      
      if (isD10S) {
        replyText = `Che, te analicé con el modelo de visión por computadora: Detecté tu rostro con emoción dominante **${em.toUpperCase()}** (${conf}% de certeza). ${
          em.includes('Alegría') ? '¡Se te nota contento, hermano! Qué lindo ver esa sonrisa.' : 'Todo tranquilo, enfocate y seguimos adelante con los datos.'
        }`;
      } else {
        replyText = `¡Siuuu! Análisis biométrico completado: Rostro fijado con emoción dominante **${em.toUpperCase()}** (${conf}% de certeza). ${
          em.includes('Alegría') ? '¡Esa es la energía de un campeón! ¡Actitud ganadora al máximo!' : 'Concentración absoluta y disciplina. ¡A romperla, Comandante!'
        }`;
      }

      confetti({
        particleCount: 50,
        spread: 70,
        origin: { y: 0.8 },
        colors: isD10S ? ['#00f0ff', '#38bdf8', '#fbbf24'] : ['#ef4444', '#f59e0b', '#ffffff']
      });
    } else {
      replyText = isD10S
        ? "Mirá che, revisé la foto pero no alcancé a detectar un rostro claro. Probá con buena luz o de frente, hermano."
        : "¡Atención! No se localizó ningún rostro en el fotograma. Ajusta la iluminación y encuadra con precisión para la IA.";
    }

    const assistantMsg = {
      id: Date.now() + 1,
      sender: 'assistant',
      text: replyText,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      interactiveModel: null,
      modelParams: null,
      modelResult: null,
      isExecuting: false
    };
    setMessagesAndSync(prev => [...prev, assistantMsg]);

    // Respuesta hablada
    if (soundEnabled && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      const utter = new SpeechSynthesisUtterance(replyText.replace(/\*\*/g, ''));
      utter.lang = 'es-ES';
      utter.rate = isD10S ? 1.05 : 1.15;
      utter.pitch = isD10S ? 0.95 : 1.1;
      utter.onstart = () => setIsSpeaking(true);
      utter.onend = () => setIsSpeaking(false);
      utter.onerror = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utter);
    }
  };

  // Detener reconocimiento de voz de manera limpia
  const stopListening = () => {
    if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {}
    }
    setIsListening(false);
    setInterimTranscript('');
  };

  // Enviar mensaje de texto o voz procesada al backend con memoria conversacional
  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputVal).trim();
    if (!query || loading) return;

    if (isListening) stopListening();

    setInputVal('');
    setInterimTranscript('');
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const isFirstUserMessage = messages.filter(m => m.sender === 'user').length === 0;
    setMessagesAndSync(prev => [...prev, userMsg], isFirstUserMessage ? query : null);
    setLoading(true);

    try {
      // Memoria de conversación: recopilamos los turnos previos con sus parámetros
      const historyPayload = messages.slice(-8).map(m => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        text: m.text,
        interactive_model: m.interactiveModel || null,
        params: m.modelParams || null
      }));

      const res = await fetch('/api/command/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript: query,
          personality: persona,
          history: historyPayload
        })
      });

      const data = await res.json();
      const replyText = data.respuesta_texto || "Disculpá, probá seleccionando uno de los modelos interactivos de abajo.";

      const assistantMsg = {
        id: Date.now() + 1,
        sender: 'assistant',
        text: replyText,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        interactiveModel: data.interactive_model || null,
        modelParams: data.params || null,
        modelResult: data.datos || null,
        isExecuting: false
      };

      setMessagesAndSync(prev => [...prev, assistantMsg]);

      if (data.intencion && data.interactive_model) {
        confetti({
          particleCount: 30,
          spread: 60,
          origin: { y: 0.85 },
          colors: isD10S ? ['#00f0ff', '#38bdf8', '#fef08a'] : ['#ef4444', '#f59e0b', '#ffffff']
        });
      }

      if (soundEnabled && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(replyText.replace(/\*\*/g, ''));
        utter.lang = 'es-ES';
        utter.rate = isD10S ? 1.05 : 1.15;
        utter.pitch = isD10S ? 0.95 : 1.1;
        utter.onstart = () => setIsSpeaking(true);
        utter.onend = () => setIsSpeaking(false);
        utter.onerror = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utter);
      }

    } catch (err) {
      console.error(err);
      setMessagesAndSync(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'assistant',
        text: "Error comunicando con el núcleo 10N-AI.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        interactiveModel: null,
        modelParams: null,
        modelResult: null,
        isExecuting: false
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Función para ejecutar inferencia interactiva en tiempo real desde el ModelSimulatorCard
  const executeModelPrediction = async (msgId, modelType, currentParams) => {
    try {
      setMessagesAndSync(prev => prev.map(m => m.id === msgId ? { ...m, isExecuting: true } : m));

      const endpoint = `/api/predict/${modelType}`;
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(currentParams)
      });
      const result = await res.json();

      let feedback = "";
      if (modelType === 'vino') {
        feedback = isD10S
          ? `¡Listo! Con esos parámetros el vino resulta: ${result.diagnostico} con ${result.probabilidad_alta_calidad}% de probabilidad.`
          : `¡Predicción completada! El resultado para este vino es: ${result.diagnostico} con ${result.probabilidad_alta_calidad}% de certeza.`;
      } else if (modelType === 'auto') {
        feedback = isD10S
          ? `Cotización calculada: Valor estimado de $${result.precio_estimado_usd.toLocaleString()} USD (${result.precio_estimado_lakhs} lakhs).`
          : `¡Tasación precisa! Valor estimado de $${result.precio_estimado_usd.toLocaleString()} USD para el vehículo.`;
      } else if (modelType === 'churn') {
        feedback = isD10S
          ? `Diagnóstico de cliente: ${result.diagnostico} con ${result.probabilidad_cancelacion}%. ${result.recomendacion}`
          : `¡Alerta de retención! ${result.diagnostico} con ${result.probabilidad_cancelacion}%. ${result.recomendacion}`;
      } else if (modelType === 'aguacate') {
        feedback = isD10S
          ? `Precio proyectado: $${result.precio_unitario_usd} USD por aguacate en ${result.region}.`
          : `¡Proyección lista! $${result.precio_unitario_usd} USD por unidad para aguacate ${result.tipo_cultivo}.`;
      } else if (modelType === 'stroke') {
        feedback = isD10S
          ? `Evaluación de salud: ${result.diagnostico} con ${result.probabilidad_evento_vascular}% de probabilidad. ${result.recomendacion}`
          : `¡Evaluación de salud completada! ${result.diagnostico} con ${result.probabilidad_evento_vascular}%. ${result.recomendacion}`;
      } else if (modelType === 'bodyfat') {
        feedback = isD10S
          ? `Grasa corporal estimada en ${result.grasa_corporal_pct}%. Categoría: ${result.categoria}.`
          : `¡Estimación precisa! Porcentaje de grasa corporal: ${result.grasa_corporal_pct}%, nivel ${result.categoria}.`;
      } else if (modelType === 'hepatitis') {
        feedback = isD10S
          ? `Diagnóstico hepático: ${result.diagnostico} con ${result.probabilidad_patologia}% de probabilidad.`
          : `¡Análisis completado! Diagnóstico: ${result.diagnostico} con ${result.probabilidad_patologia}% de certeza.`;
      } else if (modelType === 'cirrosis') {
        feedback = isD10S
          ? `Estadificación de cirrosis: ${result.nombre_estadio} (${result.severidad}) con ${result.confidence}% de certeza.`
          : `¡Clasificación clínica lista! ${result.nombre_estadio} (${result.severidad}) con ${result.confidence}% de certeza.`;
      } else if (modelType === 'bitcoin') {
        feedback = isD10S
          ? `Cotización de Bitcoin proyectada: $${Number(result.precio_cierre_usd).toLocaleString()} USD con tendencia ${result.tendencia}.`
          : `¡Proyección de Bitcoin lista! Precio de cierre: $${Number(result.precio_cierre_usd).toLocaleString()} USD (${result.tendencia}).`;
      } else if (modelType === 'sp500') {
        feedback = isD10S
          ? `Acción S&P 500 proyectada en $${result.precio_cierre_usd} USD con tendencia ${result.tendencia}.`
          : `¡Proyección bursátil completada! Precio de cierre S&P 500: $${result.precio_cierre_usd} USD.`;
      }

      setMessagesAndSync(prev => prev.map(m => {
        if (m.id === msgId) {
          return {
            ...m,
            isExecuting: false,
            modelResult: result,
            modelParams: currentParams
          };
        }
        return m;
      }));

      if (soundEnabled && 'speechSynthesis' in window && feedback) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(feedback);
        utter.lang = 'es-ES';
        utter.rate = isD10S ? 1.05 : 1.15;
        utter.pitch = isD10S ? 0.95 : 1.1;
        utter.onstart = () => setIsSpeaking(true);
        utter.onend = () => setIsSpeaking(false);
        utter.onerror = () => setIsSpeaking(false);
        window.speechSynthesis.speak(utter);
      }

      confetti({
        particleCount: 45,
        spread: 60,
        origin: { y: 0.8 },
        colors: isD10S ? ['#00f0ff', '#38bdf8', '#fbbf24'] : ['#ef4444', '#f59e0b', '#ffffff']
      });

    } catch (err) {
      console.error("Error executing model prediction:", err);
      setMessagesAndSync(prev => prev.map(m => m.id === msgId ? { ...m, isExecuting: false } : m));
    }
  };

  // Reconocimiento de voz continuo con visualización en tiempo real y debounce inteligente
  const handleMicClick = () => {
    if (isListening) {
      stopListening();
      if (inputVal.trim()) {
        handleSendMessage(inputVal.trim());
      }
      return;
    }

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert("Tu navegador no soporta Web Speech API. Por favor utilizá Google Chrome o Microsoft Edge.");
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.lang = voiceDialect;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    let accumulatedFinal = '';

    recognition.onstart = () => {
      setIsListening(true);
      setInterimTranscript('');
    };

    recognition.onresult = (event) => {
      let interim = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          accumulatedFinal += event.results[i][0].transcript + ' ';
        } else {
          interim += event.results[i][0].transcript;
        }
      }

      const fullCandidate = (accumulatedFinal + interim).trim();
      setInputVal(fullCandidate);
      setInterimTranscript(interim || accumulatedFinal.trim());

      // Debounce de silencio: Si el usuario se queda en silencio por 1.8 segundos, auto-enviar
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = setTimeout(() => {
        if (fullCandidate) {
          stopListening();
          handleSendMessage(fullCandidate);
        }
      }, 1800);
    };

    recognition.onerror = (event) => {
      console.warn("Speech recognition error:", event.error);
      if (event.error === 'not-allowed') {
        alert("Permiso de micrófono bloqueado. Por favor permití el acceso al micrófono en el navegador.");
      }
      setIsListening(false);
      setInterimTranscript('');
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
    };

    try {
      recognition.start();
    } catch (e) {
      console.error("Error al iniciar recognition:", e);
      setIsListening(false);
    }
  };

  useEffect(() => {
    return () => {
      if (silenceTimerRef.current) clearTimeout(silenceTimerRef.current);
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch (e) {}
      }
    };
  }, []);

  return (
    <div className="flex-1 flex flex-col h-full min-h-0 w-full relative">
      
      {/* HEADER DE CHAT */}
      <div className="shrink-0 flex items-center justify-between px-4 py-2 border-b border-slate-800/60 text-xs font-rajdhani">
        <div className="flex items-center gap-2">
          <Sparkles className={`w-3.5 h-3.5 ${isD10S ? 'text-cyan-400' : 'text-amber-400'}`} />
          <span className="font-bold tracking-wider text-slate-300">
            CONVERSACIÓN // {isD10S ? 'CORE D10S' : 'CORE CR7'}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {/* SELECTOR DE DIALECTO DE MICRÓFONO */}
          <div className="hidden sm:flex items-center gap-1.5 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded-lg text-[11px] font-mono text-slate-400">
            <span className="text-[10px] text-slate-500 font-bold uppercase">MIC:</span>
            <select
              value={voiceDialect}
              onChange={(e) => setVoiceDialect(e.target.value)}
              className="bg-transparent text-slate-300 focus:outline-none cursor-pointer text-[11px]"
              title="Acento del reconocimiento de voz"
            >
              <option value="es-419" className="bg-slate-950 text-slate-200">LatAm (es-419)</option>
              <option value="es-CR" className="bg-slate-950 text-slate-200">Costa Rica (es-CR)</option>
              <option value="es-ES" className="bg-slate-950 text-slate-200">España (es-ES)</option>
            </select>
          </div>

          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`flex items-center gap-1 px-2.5 py-1 rounded-lg border text-[11px] transition-all ${
              soundEnabled ? 'bg-slate-900 border-slate-700 text-slate-300' : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
            }`}
            title="Activar/desactivar respuesta hablada"
          >
            {soundEnabled ? <Volume2 className="w-3.5 h-3.5 text-emerald-400" /> : <VolumeX className="w-3.5 h-3.5 text-rose-400" />}
            <span>{soundEnabled ? 'VOZ: ON' : 'VOZ: OFF'}</span>
          </button>
        </div>
      </div>

      {/* MODAL INLINE DE CÁMARA WEB EN TIEMPO REAL */}
      {liveCameraActive && (
        <div className="shrink-0 mx-4 my-2 p-3.5 rounded-2xl bg-slate-950 border border-slate-800 shadow-2xl flex flex-col items-center relative animate-in fade-in zoom-in-95">
          <button
            onClick={closeLiveCamera}
            className="absolute top-2 right-2 p-1.5 rounded-full bg-slate-900 text-slate-400 hover:text-white"
          >
            <X className="w-4 h-4" />
          </button>
          <div className="w-64 aspect-video rounded-xl bg-black overflow-hidden border border-slate-800 mb-3 relative">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover transform -scale-x-100"
            />
            <div className={`absolute top-2 right-2 w-2 h-2 rounded-full ${isD10S ? 'bg-cyan-400' : 'bg-amber-400'} animate-ping`}></div>
          </div>
          <button
            onClick={captureFrame}
            disabled={capturing}
            className={`flex items-center gap-2 px-5 py-2 rounded-xl font-rajdhani font-bold text-xs tracking-wider transition-all ${
              isD10S ? 'bg-cyan-500 text-black shadow-[0_0_15px_#00f0ff]' : 'bg-amber-500 text-black shadow-[0_0_15px_#f59e0b]'
            }`}
          >
            <Camera className="w-4 h-4" />
            <span>{capturing ? 'PROCESANDO...' : 'CAPTURAR Y ANALIZAR'}</span>
          </button>
        </div>
      )}

      {/* HISTORIAL DE MENSAJES CON SIMULADORES INTERACTIVOS */}
      <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((m) => {
          const isUser = m.sender === 'user';
          return (
            <div
              key={m.id}
              className={`flex gap-3 ${isUser ? 'ml-auto flex-row-reverse max-w-xl' : 'mr-auto w-full max-w-2xl'}`}
            >
              {/* AVATAR */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 font-orbitron font-bold text-xs border ${
                isUser
                  ? 'bg-slate-800 border-slate-700 text-slate-200'
                  : isD10S
                    ? 'bg-gradient-to-tr from-cyan-600 to-blue-500 border-cyan-300 text-black shadow-[0_0_10px_rgba(6,182,212,0.4)]'
                    : 'bg-gradient-to-tr from-red-600 to-amber-500 border-amber-300 text-black shadow-[0_0_10px_rgba(239,68,68,0.4)]'
              }`}>
                {isUser ? <User className="w-4 h-4" /> : isD10S ? '10' : 'CR7'}
              </div>

              {/* CONTENIDO DEL MENSAJE */}
              <div className="flex flex-col flex-1 min-w-0">
                <div className={`p-4 rounded-2xl text-sm leading-relaxed backdrop-blur-md ${
                  isUser
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-none shadow-md'
                    : isD10S
                      ? 'bg-slate-900/80 border border-cyan-500/20 text-slate-100 rounded-tl-none shadow-[0_4px_20px_rgba(0,0,0,0.3)]'
                      : 'bg-stone-900/80 border border-amber-500/20 text-slate-100 rounded-tl-none shadow-[0_4px_20px_rgba(0,0,0,0.3)]'
                }`}>
                  {m.image && (
                    <img
                      src={m.image}
                      alt="Captura de rostro"
                      className="w-48 h-auto rounded-lg mb-2.5 border border-white/20 object-cover"
                    />
                  )}
                  <p className="whitespace-pre-wrap font-sans">{m.text}</p>

                  {/* SIMULADOR INTERACTIVO SI EL MENSAJE CONTIENE UN MODELO DE MACHINE LEARNING */}
                  {m.interactiveModel && (
                    <ModelSimulatorCard
                      msgId={m.id}
                      modelType={m.interactiveModel}
                      initialParams={m.modelParams}
                      initialResult={m.modelResult}
                      isExecuting={m.isExecuting}
                      isD10S={isD10S}
                      onExecute={executeModelPrediction}
                    />
                  )}
                </div>
                <span className={`text-[10px] font-mono mt-1 text-slate-500 ${isUser ? 'text-right' : 'text-left'}`}>
                  {m.time}
                </span>
              </div>
            </div>
          );
        })}

        {/* LOADING INDICATOR */}
        {loading && (
          <div className="flex gap-3 items-center text-slate-400 text-xs font-rajdhani">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-orbitron font-bold text-xs border ${
              isD10S ? 'bg-cyan-950 border-cyan-400 text-cyan-300' : 'bg-amber-950 border-amber-400 text-amber-300'
            }`}>
              {isD10S ? '10' : 'CR7'}
            </div>
            <div className="flex items-center gap-1.5 p-3 rounded-2xl bg-slate-900/80 border border-slate-800">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce"></span>
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]"></span>
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.4s]"></span>
              <span className="ml-2 font-mono text-[11px] text-slate-400">Analizando tu consulta...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* SELECTOR / LAUNCHER DE MODELOS DE MACHINE LEARNING INTERACTIVOS */}
      <div className="shrink-0 px-4 pb-2">
        <div className="flex flex-wrap gap-1.5 justify-center">
          <button
            onClick={() => handleSendMessage("Quiero clasificar la calidad de un vino")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🍷</span>
            <span>Calidad Vino</span>
          </button>
          <button
            onClick={() => handleSendMessage("Quiero cotizar el precio de un auto")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🚗</span>
            <span>Tasar Auto</span>
          </button>
          <button
            onClick={() => handleSendMessage("Analizar probabilidad de fuga de clientes")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>👥</span>
            <span>Fuga Clientes</span>
          </button>
          <button
            onClick={() => handleSendMessage("Cotizar precio del aguacate en California")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🥑</span>
            <span>Precio Aguacate</span>
          </button>
          <button
            onClick={() => handleSendMessage("Diagnosticar riesgo de accidente cerebrovascular")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🧠</span>
            <span>Riesgo de Salud</span>
          </button>
          <button
            onClick={() => handleSendMessage("Calcular porcentaje de grasa corporal")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🏃</span>
            <span>Grasa Corporal</span>
          </button>
          <button
            onClick={() => handleSendMessage("Diagnosticar prueba de hepatitis C")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🧪</span>
            <span>Hepatitis C</span>
          </button>
          <button
            onClick={() => handleSendMessage("Evaluar estadio de cirrosis hepática")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>🏥</span>
            <span>Cirrosis</span>
          </button>
          <button
            onClick={() => handleSendMessage("Predecir cotización de Bitcoin")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>₿</span>
            <span>Bitcoin</span>
          </button>
          <button
            onClick={() => handleSendMessage("Proyectar precio de acciones S&P 500")}
            className="text-xs font-rajdhani font-semibold px-3 py-1.5 rounded-full bg-slate-900/90 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-400 transition-all hover:scale-[1.02] flex items-center gap-1.5 shadow-sm"
          >
            <span>📈</span>
            <span>S&P 500</span>
          </button>
        </div>
      </div>

      {/* BARRA DE ENTRADA CON CÁMARA Y MICRÓFONO */}
      <div className="shrink-0 p-4 pt-2 pb-4 relative w-full">

        {/* BANNER ANIMADO DE GRABACIÓN DE VOZ EN TIEMPO REAL */}
        {isListening && (
          <div className="mb-2 p-3 rounded-2xl bg-slate-950/95 border border-cyan-500/40 backdrop-blur-2xl flex items-center justify-between gap-3 animate-in fade-in slide-in-from-bottom-2 shadow-[0_0_25px_rgba(6,182,212,0.25)]">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className="relative flex items-center justify-center shrink-0">
                <span className="w-3 h-3 rounded-full bg-rose-500 animate-ping absolute"></span>
                <span className="w-3 h-3 rounded-full bg-rose-500"></span>
              </div>
              <div className="flex items-center gap-1 h-5 px-1 shrink-0">
                <span className="w-1 h-3 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                <span className="w-1 h-5 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                <span className="w-1 h-2 bg-cyan-400 rounded-full animate-bounce"></span>
                <span className="w-1 h-6 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.2s]"></span>
                <span className="w-1 h-3 bg-cyan-400 rounded-full animate-bounce [animation-delay:-0.35s]"></span>
              </div>
              <p className="text-xs text-slate-200 truncate font-mono flex-1">
                {interimTranscript ? (
                  <span className="text-cyan-300 font-sans italic font-medium">"{interimTranscript}"</span>
                ) : (
                  <span className="text-slate-400 font-sans">Escuchando micrófono ({voiceDialect})... Di un comando o consulta</span>
                )}
              </p>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={() => {
                  stopListening();
                  if (inputVal.trim()) handleSendMessage(inputVal.trim());
                }}
                className="px-3 py-1 rounded-xl bg-cyan-500/20 border border-cyan-400 text-cyan-300 hover:bg-cyan-500/30 text-xs font-bold font-rajdhani transition-all"
              >
                Detener y Enviar
              </button>
              <button
                type="button"
                onClick={stopListening}
                className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-900 transition-all"
                title="Cancelar micrófono"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
        
        {/* MENÚ DE OPCIONES DE CÁMARA */}
        {showCameraMenu && (
          <div className="absolute bottom-20 left-4 p-2 rounded-xl bg-slate-950/95 border border-slate-800 shadow-2xl backdrop-blur-xl flex flex-col gap-1 z-30 font-rajdhani font-bold text-xs text-slate-300">
            <button
              onClick={openLiveCamera}
              className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-900 hover:text-white transition-all text-left"
            >
              <Camera className="w-4 h-4 text-cyan-400" />
              <span>Tomar foto en tiempo real con la cámara</span>
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-900 hover:text-white transition-all text-left"
            >
              <Image className="w-4 h-4 text-amber-400" />
              <span>Adjuntar foto desde mi computadora</span>
            </button>
          </div>
        )}

        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          accept="image/*"
          className="hidden"
        />

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className={`flex items-center gap-2 p-2 rounded-2xl border backdrop-blur-xl transition-all shadow-2xl ${
            isD10S
              ? 'bg-slate-950/80 border-cyan-500/30 focus-within:border-cyan-400 shadow-[0_0_25px_rgba(6,182,212,0.15)]'
              : 'bg-stone-950/80 border-amber-500/30 focus-within:border-amber-400 shadow-[0_0_25px_rgba(245,158,11,0.15)]'
          }`}
        >
          {/* BOTÓN DE CÁMARA A LA PAR DEL MICRÓFONO */}
          <button
            type="button"
            onClick={() => setShowCameraMenu(!showCameraMenu)}
            className={`p-3 rounded-xl transition-all ${
              showCameraMenu
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400'
                : 'bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white'
            }`}
            title="Cámara (tiempo real o adjuntar foto)"
          >
            <Camera className="w-5 h-5" />
          </button>

          {/* BOTÓN DE MICRÓFONO */}
          <button
            type="button"
            onClick={handleMicClick}
            className={`p-3 rounded-xl transition-all duration-300 relative ${
              isListening
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/60 shadow-[0_0_20px_rgba(244,63,94,0.4)] animate-pulse'
                : isD10S
                  ? 'bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 active:scale-95'
                  : 'bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 active:scale-95'
            }`}
            title={isListening ? "Detener grabación de voz" : "Hablar al micrófono (Speech-to-Text)"}
          >
            <Mic className="w-5 h-5" />
          </button>

          {/* INPUT DE TEXTO */}
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="Preguntale a 10N-AI (autos, vino, aguacate, clientes, stroke)..."
            className="flex-1 bg-transparent border-none text-slate-100 placeholder:text-slate-500 text-sm focus:outline-none px-2 font-sans"
            disabled={loading}
          />

          {/* BOTÓN ENVIAR */}
          <button
            type="submit"
            disabled={!inputVal.trim() || loading}
            className={`p-3 rounded-xl transition-all ${
              inputVal.trim() && !loading
                ? isD10S
                  ? 'bg-cyan-500 hover:bg-cyan-400 text-black shadow-[0_0_15px_#00f0ff]'
                  : 'bg-amber-500 hover:bg-amber-400 text-black shadow-[0_0_15px_#f59e0b]'
                : 'opacity-30 text-slate-600 cursor-not-allowed'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>

    </div>
  );
}
