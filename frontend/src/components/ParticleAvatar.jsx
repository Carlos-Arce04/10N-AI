import React, { useRef, useEffect } from 'react';
import facePoints from '../data/facePoints.json';

export default function ParticleAvatar({ persona, isSpeaking, isListening }) {
  const canvasRef = useRef(null);
  const particlesRef = useRef([]);
  const mouseRef = useRef({ x: -1000, y: -1000, active: false });

  const isD10S = persona === 'd10s';

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const size = 300;
    canvas.width = size * 2;
    canvas.height = size * 2;
    ctx.scale(2, 2);

    const targetPoints = isD10S ? facePoints.d10s : facePoints.cr7;
    const count = targetPoints.length;

    // Inicializar o remapear partículas existentes para morphing
    if (particlesRef.current.length === 0) {
      particlesRef.current = targetPoints.map((pt) => ({
        x: 150 + (Math.random() - 0.5) * 160,
        y: 150 + (Math.random() - 0.5) * 160,
        vx: (Math.random() - 0.5) * 2,
        vy: (Math.random() - 0.5) * 2,
        baseX: pt.x,
        baseY: pt.y,
        isMouth: pt.isMouth,
        isLower: pt.isLower,
        isUpper: pt.isUpper,
        isChin: pt.isChin,
        brightness: pt.brightness || 0.8,
        size: Math.random() * 0.4 + 1.0,
        colorSeed: Math.random()
      }));
    } else {
      // Reasignar coordenadas objetivo para morphing fluido entre núcleos
      particlesRef.current.forEach((p, idx) => {
        const pt = targetPoints[idx % count];
        p.baseX = pt.x;
        p.baseY = pt.y;
        p.isMouth = pt.isMouth;
        p.isLower = pt.isLower;
        p.isUpper = pt.isUpper;
        p.isChin = pt.isChin;
        p.brightness = pt.brightness || 0.8;
      });
    }

    let tick = 0;

    const render = () => {
      tick += 0.04;
      ctx.clearRect(0, 0, size, size);

      // Biomecánica de articulación mandibular humana:
      // El maxilar superior (labio superior, bigote y nariz) permanece fijo al cráneo.
      // Es la mandíbula inferior (labio inferior y barbilla) la que desciende para abrir la boca.
      const mouthCenter = { x: 151.0, y: 183.0 };
      let openAmount = 0;
      let widthMod = 0;
      let lateralShift = 0;

      if (isSpeaking) {
        // Cadencia silábica realista (~3.5 sílabas por segundo)
        const speechSpeed = tick * 6.8;
        // Solo abre en la fase positiva de la onda; en la fase negativa (0) la boca se cierra completamente
        const openRatio = Math.max(0, Math.sin(speechSpeed));
        const vowelWeight = 0.65 + 0.35 * Math.sin(tick * 2.8);
        // Apertura sutil y proporcionada (máximo 3.8 píxeles, nunca una caverna)
        openAmount = Math.pow(openRatio, 1.4) * 3.8 * vowelWeight;

        // Modulación horizontal de labios según fonemas
        widthMod = Math.sin(tick * 3.8) * 0.15;
        // Asimetría humana sutil
        lateralShift = Math.sin(tick * 5.2) * 0.45;
      }

      const particles = particlesRef.current;
      const mouse = mouseRef.current;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Coordenada objetivo según fonética / movimiento de boca
        let tx = p.baseX;
        let ty = p.baseY;

        if (isSpeaking) {
          // Distancia horizontal normalizada al centro de la boca (-1 = comisura izq, +1 = comisura der)
          const relX = (p.baseX - mouthCenter.x) / 24.0;
          const distNorm = Math.min(1.0, Math.abs(relX));
          const centerWeight = Math.cos(distNorm * (Math.PI / 2)); // 1.0 en el centro, 0.0 en comisuras
          const cornerWeight = 1.0 - centerWeight;

          if (p.isLower) {
            // Labio inferior: cae con arco natural hacia abajo (más al centro, menos en comisuras)
            ty += openAmount * (0.9 * centerWeight + 0.25 * cornerWeight);
            tx += (p.baseX - mouthCenter.x) * widthMod * 0.2 + lateralShift * 0.3;
          } else if (p.isUpper) {
            // Labio superior y bigote: FIJOS al cráneo superior, NO se mueven verticalmente
            tx += (p.baseX - mouthCenter.x) * widthMod * 0.1 + lateralShift * 0.1;
          } else if (p.isChin) {
            // Barbilla/mandíbula: acompaña sutilmente la caída de la mandíbula inferior
            const chinProximity = Math.max(0, 1.0 - Math.abs(p.baseX - mouthCenter.x) / 36.0);
            ty += openAmount * 0.45 * chinProximity;
            tx += lateralShift * 0.15;
          } else if (p.isMouth) {
            // Comisuras: modulación horizontal sutil
            tx += (p.baseX - mouthCenter.x) * widthMod * 0.15 + lateralShift * 0.2;
          }
        }

        const isAnyMouth = p.isMouth || p.isLower || p.isUpper;

        // Micro-ondulación orgánica sutil para que el holograma respire (no entorpece los labios al hablar)
        const shimmer = (isSpeaking && isAnyMouth) ? 0 : Math.sin(tick * 2.0 + i * 0.08) * 0.35;

        // Física elástica: articulación más ágil y precisa en labios y mandíbula
        const springK = (isSpeaking && (isAnyMouth || p.isChin)) ? 0.16 : 0.08;
        const damping = (isSpeaking && (isAnyMouth || p.isChin)) ? 0.74 : 0.82;

        const dx = tx - p.x;
        const dy = (ty + shimmer) - p.y;
        p.vx += dx * springK;
        p.vy += dy * springK;
        p.vx *= damping;
        p.vy *= damping;

        // Repulsión magnética del cursor
        if (mouse.active) {
          const mdx = p.x - mouse.x;
          const mdy = p.y - mouse.y;
          const mdist = Math.hypot(mdx, mdy);
          if (mdist < 45 && mdist > 0) {
            const force = (45 - mdist) / 45 * 3.5;
            p.vx += (mdx / mdist) * force;
            p.vy += (mdy / mdist) * force;
          }
        }

        p.x += p.vx;
        p.y += p.vy;

        // Paleta según núcleo
        // Messi: Albiceleste / Cyan con blanco puro y celeste brillante
        // CR7: Oro Real Madrid / Carmesí fuego con blanco y ámbar brillante
        if (isD10S) {
          ctx.fillStyle = p.colorSeed > 0.65 ? '#ffffff' : p.colorSeed > 0.25 ? '#00f0ff' : '#38bdf8';
          ctx.shadowColor = '#00f0ff';
        } else {
          ctx.fillStyle = p.colorSeed > 0.65 ? '#ffffff' : p.colorSeed > 0.3 ? '#f59e0b' : '#ef4444';
          ctx.shadowColor = '#f59e0b';
        }

        ctx.shadowBlur = isSpeaking ? 4 : 2;

        // Dibujar partícula nítida con pulso elástico en labios
        ctx.beginPath();
        const pSize = p.size * (isSpeaking && isAnyMouth ? 1.2 : 1.0);
        ctx.arc(p.x, p.y, pSize, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, [persona, isSpeaking, isListening]);

  // Manejo de interacción de mouse
  const handleMouseMove = (e) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (rect) {
      mouseRef.current = {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
        active: true
      };
    }
  };

  const handleMouseLeave = () => {
    mouseRef.current.active = false;
  };

  return (
    <div className="flex flex-col items-center justify-center select-none py-2">
      <div className="relative">
        {/* CANVAS DE PARTÍCULAS FORMANDO EL ROSTRO FLOTANTE (SIN CÍRCULOS NI BORDES) */}
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{ width: 300, height: 300 }}
          className="cursor-pointer transition-transform duration-300 hover:scale-[1.02]"
        />
      </div>
    </div>
  );
}
