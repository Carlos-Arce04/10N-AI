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

      // Cálculo de animación de labios / habla
      let mouthOffset = 0;
      if (isSpeaking) {
        // Oscilación natural con cadencia de habla que abre y cierra la boca
        const openCycle = Math.sin(tick * 11) * 0.5 + 0.5;
        const speechCadence = Math.sin(tick * 17) * 0.3 + 0.7;
        mouthOffset = openCycle * speechCadence * 6.5; // Apertura de 0 a 6.5 píxeles
      }

      const particles = particlesRef.current;
      const mouse = mouseRef.current;

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Coordenada objetivo según fonética / movimiento de boca
        let tx = p.baseX;
        let ty = p.baseY;

        if (isSpeaking) {
          if (p.isLower) {
            ty += mouthOffset;
          } else if (p.isChin) {
            ty += mouthOffset * 0.55;
          } else if (p.isUpper) {
            ty -= mouthOffset * 0.2;
          }
        }

        // Micro-ondulación orgánica sutil para que el holograma respire
        const shimmer = Math.sin(tick * 2.0 + i * 0.08) * 0.35;

        // Física tipo resorte hacia la coordenada del rostro
        const dx = tx - p.x;
        const dy = (ty + shimmer) - p.y;
        p.vx += dx * 0.08;
        p.vy += dy * 0.08;
        p.vx *= 0.82;
        p.vy *= 0.82;

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

        // Dibujar partícula nítida
        ctx.beginPath();
        const pSize = p.size * (isSpeaking && p.isMouth ? 1.25 : 1.0);
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
