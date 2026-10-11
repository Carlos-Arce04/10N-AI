import React, { useState } from 'react';
import { Sliders, Zap, CheckCircle2, AlertTriangle, TrendingUp, RefreshCw, Activity, Wine, Car, Users } from 'lucide-react';

export default function ModelSimulatorCard({
  msgId,
  modelType,
  initialParams,
  initialResult,
  isExecuting,
  isD10S,
  onExecute
}) {
  // Estado local para los controles interactivos del simulador
  const [params, setParams] = useState(() => {
    if (initialParams) return { ...initialParams };
    
    // Valores iniciales por defecto según el caso de uso
    switch (modelType) {
      case 'vino':
        return {
          fixed_acidity: 7.2,
          volatile_acidity: 0.27,
          citric_acid: 0.36,
          residual_sugar: 6.0,
          chlorides: 0.045,
          free_sulfur_dioxide: 35.0,
          total_sulfur_dioxide: 120.0,
          density: 0.994,
          ph: 3.20,
          sulphates: 0.45,
          alcohol: 11.5,
          is_red: 0
        };
      case 'auto':
        return {
          present_price: 9.54,
          kms_driven: 43000,
          anio: 2018,
          fuel_type: 'Petrol',
          seller_type: 'Dealer',
          transmission: 'Manual',
          owner: 0
        };
      case 'churn':
        return {
          tenure: 3,
          monthly_charges: 85.50,
          total_charges: 256.50,
          contract: 'Month-to-month',
          internet_service: 'Fiber optic',
          tech_support: 'No',
          online_security: 'No',
          paperless_billing: 'Yes',
          payment_method: 'Electronic check',
          senior: 0,
          partner: 'No'
        };
      case 'aguacate':
        return {
          total_volume: 75000.0,
          plu_4046: 15000.0,
          plu_4225: 20000.0,
          plu_4770: 1000.0,
          total_bags: 14000.0,
          small_bags: 10000.0,
          large_bags: 3800.0,
          xlarge_bags: 200.0,
          year: 2026,
          month: 9,
          is_organic: 1,
          region: 'California'
        };
      case 'stroke':
        return {
          age: 65.0,
          hypertension: 1,
          heart_disease: 0,
          avg_glucose_level: 180.0,
          bmi: 29.5,
          gender: 'Male',
          ever_married: 'Yes',
          work_type: 'Private',
          residence_type: 'Urban',
          smoking_status: 'smokes'
        };
      default:
        return {};
    }
  });

  const updateParam = (key, value) => {
    setParams(prev => {
      const next = { ...prev, [key]: value };
      if (modelType === 'churn' && (key === 'tenure' || key === 'monthly_charges')) {
        next.total_charges = Math.round(Number(next.tenure) * Number(next.monthly_charges) * 100) / 100;
      }
      return next;
    });
  };

  const handleSimulate = (e) => {
    e.preventDefault();
    onExecute(msgId, modelType, params);
  };

  const themeBorder = isD10S ? 'border-cyan-500/30' : 'border-amber-500/30';
  const themeBg = isD10S ? 'bg-slate-950/90' : 'bg-stone-950/90';
  const themeGlow = isD10S ? 'shadow-[0_0_20px_rgba(6,182,212,0.15)]' : 'shadow-[0_0_20px_rgba(245,158,11,0.15)]';
  const themeAccent = isD10S ? 'text-cyan-400' : 'text-amber-400';
  const themeBtn = isD10S
    ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-black shadow-[0_0_15px_rgba(6,182,212,0.4)]'
    : 'bg-gradient-to-r from-red-600 to-amber-500 text-black shadow-[0_0_15px_rgba(245,158,11,0.4)]';

  return (
    <div className={`mt-3 p-3.5 sm:p-4 rounded-2xl border ${themeBorder} ${themeBg} ${themeGlow} font-sans text-xs text-slate-200 select-none animate-in fade-in`}>
      {/* HEADER DEL PANEL */}
      <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-slate-800 font-rajdhani">
        <div className="flex items-center gap-2">
          <Sliders className={`w-4 h-4 ${themeAccent}`} />
          <span className="font-bold tracking-wider text-white text-xs sm:text-sm uppercase">
            {modelType === 'vino' && '🍷 EVALUACIÓN DE CALIDAD DE VINO'}
            {modelType === 'auto' && '🚗 COTIZADOR DE VEHÍCULOS'}
            {modelType === 'churn' && '👥 ANÁLISIS DE RETENCIÓN DE CLIENTES'}
            {modelType === 'aguacate' && '🥑 PROYECCIÓN DE PRECIO DEL AGUACATE'}
            {modelType === 'stroke' && '🧠 EVALUACIÓN DE RIESGO DE ACV'}
          </span>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 hidden sm:inline">
          PANEL INTERACTIVO
        </span>
      </div>

      {/* FORMULARIO DE PARÁMETROS SEGÚN EL CASO */}
      <form onSubmit={handleSimulate} className="space-y-3">

        {/* ===================== CASO 1: VINO ===================== */}
        {modelType === 'vino' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Tipo de Vino */}
            <div className="col-span-1 sm:col-span-2 flex items-center justify-between bg-slate-900/60 p-2 rounded-xl border border-slate-800/80">
              <span className="font-semibold text-slate-300">Variedad de Vino:</span>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => updateParam('is_red', 0)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    params.is_red === 0
                      ? 'bg-cyan-500 text-black font-bold shadow-[0_0_10px_rgba(6,182,212,0.4)]'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  Blanco (White)
                </button>
                <button
                  type="button"
                  onClick={() => updateParam('is_red', 1)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all ${
                    params.is_red === 1
                      ? 'bg-rose-500 text-white font-bold shadow-[0_0_10px_rgba(244,63,94,0.4)]'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  Tinto (Red)
                </button>
              </div>
            </div>

            {/* Alcohol */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Alcohol (% vol):</span>
                <span className="font-mono font-bold text-white">{Number(params.alcohol).toFixed(1)}%</span>
              </div>
              <input
                type="range"
                min="8.0"
                max="15.0"
                step="0.1"
                value={params.alcohol}
                onChange={(e) => updateParam('alcohol', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Acidez Volátil */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Acidez Volátil (g/L):</span>
                <span className="font-mono font-bold text-white">{Number(params.volatile_acidity).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="0.10"
                max="1.20"
                step="0.01"
                value={params.volatile_acidity}
                onChange={(e) => updateParam('volatile_acidity', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Azúcar Residual */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Azúcar Residual (g/L):</span>
                <span className="font-mono font-bold text-white">{Number(params.residual_sugar).toFixed(1)}</span>
              </div>
              <input
                type="range"
                min="0.5"
                max="20.0"
                step="0.5"
                value={params.residual_sugar}
                onChange={(e) => updateParam('residual_sugar', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* pH */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Nivel de pH:</span>
                <span className="font-mono font-bold text-white">{Number(params.ph).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="2.80"
                max="4.00"
                step="0.01"
                value={params.ph}
                onChange={(e) => updateParam('ph', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>
          </div>
        )}

        {/* ===================== CASO 2: AUTO ===================== */}
        {modelType === 'auto' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Año de fabricación */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Año del Vehículo:</span>
                <span className="font-mono font-bold text-white">{params.anio}</span>
              </div>
              <input
                type="range"
                min="2005"
                max="2024"
                step="1"
                value={params.anio}
                onChange={(e) => updateParam('anio', parseInt(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Kilometraje */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Kilometraje:</span>
                <span className="font-mono font-bold text-white">{Number(params.kms_driven).toLocaleString()} km</span>
              </div>
              <input
                type="range"
                min="5000"
                max="200000"
                step="2500"
                value={params.kms_driven}
                onChange={(e) => updateParam('kms_driven', parseInt(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Precio Nuevo Agencia */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Precio Agencia (Lakhs):</span>
                <span className="font-mono font-bold text-white">{Number(params.present_price).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="35.0"
                step="0.5"
                value={params.present_price}
                onChange={(e) => updateParam('present_price', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Combustible */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60 flex items-center justify-between">
              <span className="text-slate-400">Combustible:</span>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => updateParam('fuel_type', 'Petrol')}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    params.fuel_type === 'Petrol' ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Gasolina
                </button>
                <button
                  type="button"
                  onClick={() => updateParam('fuel_type', 'Diesel')}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    params.fuel_type === 'Diesel' ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Diésel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ===================== CASO 3: CHURN ===================== */}
        {modelType === 'churn' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Meses de antigüedad */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Meses de Permanencia:</span>
                <span className="font-mono font-bold text-white">{params.tenure} meses</span>
              </div>
              <input
                type="range"
                min="1"
                max="72"
                step="1"
                value={params.tenure}
                onChange={(e) => updateParam('tenure', parseInt(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Cargo mensual */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Cargo Mensual ($ USD):</span>
                <span className="font-mono font-bold text-white">${Number(params.monthly_charges).toFixed(2)}</span>
              </div>
              <input
                type="range"
                min="20.0"
                max="120.0"
                step="1.0"
                value={params.monthly_charges}
                onChange={(e) => updateParam('monthly_charges', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Tipo de contrato */}
            <div className="col-span-1 sm:col-span-2 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
              <span className="text-slate-400">Tipo de Contrato:</span>
              <div className="flex gap-1.5 flex-wrap">
                {['Month-to-month', 'One year', 'Two year'].map(c => (
                  <button
                    key={c}
                    type="button"
                    onClick={() => updateParam('contract', c)}
                    className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                      params.contract === c ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {c === 'Month-to-month' ? 'Mes a mes' : c === 'One year' ? '1 Año' : '2 Años'}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ===================== CASO 4: AGUACATE ===================== */}
        {modelType === 'aguacate' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Región */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <span className="text-slate-400 block mb-1">Región Comercial:</span>
              <select
                value={params.region}
                onChange={(e) => updateParam('region', e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg p-1.5 text-xs text-white focus:outline-none"
              >
                {['California', 'Chicago', 'GreatLakes', 'LosAngeles', 'NewYork', 'TotalUS', 'West'].map(r => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            {/* Tipo de cultivo */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60 flex flex-col justify-between">
              <span className="text-slate-400 mb-1">Tipo de Cultivo:</span>
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={() => updateParam('is_organic', 1)}
                  className={`flex-1 py-1 rounded-lg text-xs font-semibold ${
                    params.is_organic === 1 ? 'bg-emerald-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Orgánico
                </button>
                <button
                  type="button"
                  onClick={() => updateParam('is_organic', 0)}
                  className={`flex-1 py-1 rounded-lg text-xs font-semibold ${
                    params.is_organic === 0 ? 'bg-cyan-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Convencional
                </button>
              </div>
            </div>

            {/* Volumen */}
            <div className="col-span-1 sm:col-span-2 bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Volumen Total Estimado (Lbs):</span>
                <span className="font-mono font-bold text-white">{Number(params.total_volume).toLocaleString()} lbs</span>
              </div>
              <input
                type="range"
                min="10000"
                max="300000"
                step="5000"
                value={params.total_volume}
                onChange={(e) => updateParam('total_volume', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>
          </div>
        )}

        {/* ===================== CASO 5: STROKE ===================== */}
        {modelType === 'stroke' && (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Edad */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Edad del Paciente:</span>
                <span className="font-mono font-bold text-white">{params.age} años</span>
              </div>
              <input
                type="range"
                min="18"
                max="90"
                step="1"
                value={params.age}
                onChange={(e) => updateParam('age', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Glucosa */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60">
              <div className="flex justify-between mb-1">
                <span className="text-slate-400">Glucosa en Sangre:</span>
                <span className="font-mono font-bold text-white">{Number(params.avg_glucose_level).toFixed(1)} mg/dL</span>
              </div>
              <input
                type="range"
                min="60"
                max="280"
                step="5"
                value={params.avg_glucose_level}
                onChange={(e) => updateParam('avg_glucose_level', parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            {/* Hipertensión */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60 flex items-center justify-between">
              <span className="text-slate-400">Hipertensión:</span>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => updateParam('hypertension', 1)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    params.hypertension === 1 ? 'bg-rose-500 text-white font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Sí
                </button>
                <button
                  type="button"
                  onClick={() => updateParam('hypertension', 0)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    params.hypertension === 0 ? 'bg-emerald-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  No
                </button>
              </div>
            </div>

            {/* Cardiopatía */}
            <div className="bg-slate-900/40 p-2.5 rounded-xl border border-slate-800/60 flex items-center justify-between">
              <span className="text-slate-400">Cardiopatía:</span>
              <div className="flex gap-1">
                <button
                  type="button"
                  onClick={() => updateParam('heart_disease', 1)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    params.heart_disease === 1 ? 'bg-rose-500 text-white font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Sí
                </button>
                <button
                  type="button"
                  onClick={() => updateParam('heart_disease', 0)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${
                    params.heart_disease === 0 ? 'bg-emerald-500 text-black font-bold' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  No
                </button>
              </div>
            </div>
          </div>
        )}

        {/* BOTÓN DE CALCULAR */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isExecuting}
            className={`w-full py-2.5 px-4 rounded-xl font-rajdhani font-black tracking-wider text-xs sm:text-sm flex items-center justify-center gap-2 transition-all hover:scale-[1.01] active:scale-95 disabled:opacity-50 ${themeBtn}`}
          >
            {isExecuting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>CALCULANDO RESULTADO...</span>
              </>
            ) : (
              <>
                <Zap className="w-4 h-4" />
                <span>CALCULAR CON ESTOS PARÁMETROS</span>
              </>
            )}
          </button>
        </div>
      </form>

      {/* PANEL DE RESULTADOS EN TIEMPO REAL */}
      {initialResult && initialResult.success && (
        <div className="mt-3.5 pt-3 border-t border-slate-800/80 animate-in fade-in zoom-in-95">
          <div className="flex items-center gap-2 mb-2 font-rajdhani font-bold text-xs">
            <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            <span className="text-white">RESULTADO DEL ANÁLISIS:</span>
          </div>

          <div className="p-3 rounded-xl bg-black/50 border border-slate-800 space-y-2">
            
            {/* VINO RESULTADO */}
            {modelType === 'vino' && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-sm text-white">
                    {initialResult.diagnostico}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[11px] font-mono font-bold ${
                    initialResult.calidad_alta ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-amber-500/20 text-amber-400 border border-amber-500/40'
                  }`}>
                    {initialResult.probabilidad_alta_calidad}% Certeza
                  </span>
                </div>
                <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-full transition-all duration-500 ${initialResult.calidad_alta ? 'bg-cyan-400' : 'bg-amber-400'}`}
                    style={{ width: `${initialResult.probabilidad_alta_calidad}%` }}
                  />
                </div>
              </div>
            )}

            {/* AUTO RESULTADO */}
            {modelType === 'auto' && (
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-slate-400 block text-[10px]">Valor Proyectado de Mercado:</span>
                  <span className="font-mono text-base font-black text-cyan-300">
                    ${Number(initialResult.precio_estimado_usd).toLocaleString()} USD
                  </span>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 block text-[10px]">Valor en Lakhs:</span>
                  <span className="font-mono text-xs text-slate-300 font-bold">
                    {initialResult.precio_estimado_lakhs} lakhs
                  </span>
                </div>
              </div>
            )}

            {/* CHURN RESULTADO */}
            {modelType === 'churn' && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className={`font-bold text-xs sm:text-sm ${initialResult.en_riesgo_churn ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {initialResult.diagnostico}
                  </span>
                  <span className="font-mono text-xs font-bold text-slate-300">
                    {initialResult.probabilidad_cancelacion}%
                  </span>
                </div>
                <p className="text-[11px] text-slate-300 italic">
                  💡 {initialResult.recomendacion}
                </p>
              </div>
            )}

            {/* AGUACATE RESULTADO */}
            {modelType === 'aguacate' && (
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-slate-400 block text-[10px]">Precio Unitario Estimado:</span>
                  <span className="font-mono text-base font-black text-emerald-400">
                    ${Number(initialResult.precio_unitario_usd).toFixed(2)} USD / unidad
                  </span>
                </div>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-800 font-mono text-slate-300">
                  {initialResult.tipo_cultivo} // {initialResult.region}
                </span>
              </div>
            )}

            {/* STROKE RESULTADO */}
            {modelType === 'stroke' && (
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className={`font-bold text-xs sm:text-sm ${initialResult.alerta_stroke ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {initialResult.diagnostico}
                  </span>
                  <span className="font-mono text-xs font-bold text-slate-300">
                    {initialResult.probabilidad_evento_vascular}% Riesgo
                  </span>
                </div>
                <p className="text-[11px] text-slate-300">
                  📋 {initialResult.recomendacion}
                </p>
              </div>
            )}

          </div>
        </div>
      )}

    </div>
  );
}
