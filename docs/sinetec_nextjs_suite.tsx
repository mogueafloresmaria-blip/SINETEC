import React, { useState, useEffect } from 'react';

// ============================================================================
// SINETEC SENA · NEXT.JS & TAILWIND CSS ENTERPRISE SUITE (LINEAR / VERCEL UI)
// Gestión Técnica y Operativa de la Formación Profesional Integral
// ============================================================================

export type EstadoAsistencia = 'A' | 'R' | 'FJ' | 'FI';
export type EstadoFormacion = 'En Formación' | 'Condicionado' | 'Cancelado' | 'Retiro Voluntario';

interface Aprendiz {
  id: string;
  nombre: string;
  apellidos: string;
  tipoDoc: string;
  numDoc: string;
  emailMisena: string;
  emailPersonal: string;
  telefono: string;
  contactoEmergencia: string;
  fichaCodigo: string;
  programa: string;
  etapa: 'Lectiva' | 'Productiva';
  modalidadProductiva?: string;
  estado: EstadoFormacion;
  asistencias: number;
  retardos: number;
  fallasJustificadas: number;
  fallasInjustificadas: number;
  rapsAprobados: number;
  rapsTotal: number;
}

interface WidgetConfig {
  sesiones: boolean;
  asistencia: boolean;
  alertas: boolean;
  evidencias: boolean;
  raps: boolean;
  comites: boolean;
  juicios: boolean;
}

export default function SinetecApp() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'fichas' | 'asistencia' | 'ia' | 'config'>('dashboard');
  const [showWidgetModal, setShowWidgetModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState(false);
  const [selectedAprendiz, setSelectedAprendiz] = useState<Aprendiz | null>(null);

  // Configuración de widgets reactivos con persistencia
  const [widgets, setWidgets] = useState<WidgetConfig>({
    sesiones: true,
    asistencia: true,
    alertas: true,
    evidencias: true,
    raps: true,
    comites: true,
    juicios: true,
  });

  // Aprendices de muestra
  const [aprendices] = useState<Aprendiz[]>([
    {
      id: '1',
      nombre: 'Mateo',
      apellidos: 'Gómez Silva',
      tipoDoc: 'CC',
      numDoc: '1082987123',
      emailMisena: 'mgomez@misena.edu.co',
      emailPersonal: 'mateo.gomez@gmail.com',
      telefono: '3015551234',
      contactoEmergencia: 'María Silva (Madre) · 3109876543',
      fichaCodigo: '2670123',
      programa: 'Análisis y Desarrollo de Software (ADSO)',
      etapa: 'Lectiva',
      estado: 'En Formación',
      asistencias: 42,
      retardos: 1,
      fallasJustificadas: 1,
      fallasInjustificadas: 0,
      rapsAprobados: 12,
      rapsTotal: 14,
    },
    {
      id: '2',
      nombre: 'Valentina',
      apellidos: 'Ríos Mendoza',
      tipoDoc: 'TI',
      numDoc: '1002345678',
      emailMisena: 'vrios@misena.edu.co',
      emailPersonal: 'valen.rios@outlook.com',
      telefono: '3124449876',
      contactoEmergencia: 'Carlos Ríos (Padre) · 3156667788',
      fichaCodigo: '2670123',
      programa: 'Análisis y Desarrollo de Software (ADSO)',
      etapa: 'Lectiva',
      estado: 'En Formación',
      asistencias: 38,
      retardos: 3,
      fallasJustificadas: 2,
      fallasInjustificadas: 4,
      rapsAprobados: 9,
      rapsTotal: 14,
    },
  ]);

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A] font-sans flex flex-col xl:flex-row antialiased">
      {/* -------------------------------------------------------------
          SIDEBAR FIJO ADHESIVO (STICKY TOP-0 CON SCROLL INDEPENDIENTE)
          ------------------------------------------------------------- */}
      <aside className="w-full xl:w-72 bg-[#0B2414] text-[#E2E8F0] xl:sticky xl:top-0 xl:h-screen flex flex-col justify-between border-r border-[#153E23] z-40">
        <div>
          {/* Marca / Logo */}
          <div className="p-6 border-b border-[#153E23] flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#39A900] to-[#22C55E] flex items-center justify-center text-white font-extrabold text-xl shadow-lg shadow-[#39A900]/25">
              S
            </div>
            <div>
              <div className="font-extrabold text-lg tracking-tight text-white flex items-center gap-1">
                SINE<span className="text-[#39A900]">TEC</span>
              </div>
              <div className="text-[10px] font-bold text-[#86EFAC] tracking-wider uppercase">
                Gestión Operativa SENA
              </div>
            </div>
          </div>

          {/* Navegación Principal */}
          <nav className="p-4 space-y-1.5 overflow-y-auto max-h-[calc(100vh-180px)]">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'dashboard'
                  ? 'bg-[#39A900] text-white shadow-md shadow-[#39A900]/30'
                  : 'text-[#94A3B8] hover:text-white hover:bg-[#153E23]/60'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
              Dashboard Operativo
            </button>

            <button
              onClick={() => setActiveTab('fichas')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'fichas'
                  ? 'bg-[#39A900] text-white shadow-md shadow-[#39A900]/30'
                  : 'text-[#94A3B8] hover:text-white hover:bg-[#153E23]/60'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
              Fichas & Aprendices
            </button>

            <button
              onClick={() => setActiveTab('asistencia')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'asistencia'
                  ? 'bg-[#39A900] text-white shadow-md shadow-[#39A900]/30'
                  : 'text-[#94A3B8] hover:text-white hover:bg-[#153E23]/60'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
              Control de Asistencia
            </button>

            <button
              onClick={() => setActiveTab('ia')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'ia'
                  ? 'bg-[#39A900] text-white shadow-md shadow-[#39A900]/30'
                  : 'text-[#94A3B8] hover:text-white hover:bg-[#153E23]/60'
              }`}
            >
              <svg className="w-5 h-5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" /></svg>
              Asistente de Productividad IA
            </button>

            <button
              onClick={() => setActiveTab('config')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                activeTab === 'config'
                  ? 'bg-[#39A900] text-white shadow-md shadow-[#39A900]/30'
                  : 'text-[#94A3B8] hover:text-white hover:bg-[#153E23]/60'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Configuración & Firmas
            </button>
          </nav>
        </div>

        {/* Footer Sidebar */}
        <div className="p-4 border-t border-[#153E23] text-xs text-[#94A3B8]">
          <div className="font-bold text-white mb-0.5">Regional Magdalena</div>
          <div>Ctro. Logística y Prom. Ecoturística</div>
        </div>
      </aside>

      {/* -------------------------------------------------------------
          CONTENIDO PRINCIPAL
          ------------------------------------------------------------- */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header Superior estilo Linear */}
        <header className="sticky top-0 bg-white/80 backdrop-blur-md border-b border-[#E2E8F0] px-6 py-4 flex items-center justify-between z-30 shadow-sm">
          <div className="flex items-center gap-4">
            <h1 className="text-xl font-extrabold text-[#0F172A] tracking-tight">
              {activeTab === 'dashboard' && 'Dashboard Operativo'}
              {activeTab === 'fichas' && 'Administración de Fichas & Expedientes'}
              {activeTab === 'asistencia' && 'Registro Técnico de Asistencia (4 Estados)'}
              {activeTab === 'ia' && 'Asistente Inteligente de Productividad SENA'}
              {activeTab === 'config' && 'Configuración de Centro & Firmas Digitalizadas'}
            </h1>
            <span className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0]">
              <span className="w-2 h-2 rounded-full bg-[#10B981] animate-pulse"></span>
              En Línea · Vigencia 2026
            </span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setSelectedAprendiz(aprendices[0]);
                setShowQRModal(true);
              }}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold bg-[#0B2414] text-white hover:bg-[#153E23] transition-all shadow-sm"
            >
              <svg className="w-4 h-4 text-[#39A900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" /></svg>
              Creador de Código QR
            </button>

            <button
              onClick={() => setShowWidgetModal(true)}
              className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold border border-[#E2E8F0] bg-white hover:bg-[#F8FAFC] text-[#334155] transition-all shadow-sm"
            >
              <svg className="w-4 h-4 text-[#39A900]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
              Personalizar Widgets
            </button>
          </div>
        </header>

        {/* -------------------------------------------------------------
            MÓDULO 1: DASHBOARD CON WIDGETS CONFIGURABLES
            ------------------------------------------------------------- */}
        {activeTab === 'dashboard' && (
          <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
            {/* Grid de Widgets */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {widgets.sesiones && (
                <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-sm hover:shadow-md transition-all">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Sesiones de Hoy</span>
                    <span className="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-[#ECFDF5] text-[#065F46]">Ambiente 204</span>
                  </div>
                  <div className="space-y-3">
                    <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#F1F5F9]">
                      <div className="font-bold text-sm text-[#0F172A]">ADSO · Ficha 2670123</div>
                      <div className="text-xs text-[#64748B]">07:00 AM - 01:00 PM · Fase Ejecución</div>
                    </div>
                  </div>
                </div>
              )}

              {widgets.asistencia && (
                <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-sm hover:shadow-md transition-all">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Control Rápido de Asistencia</span>
                    <span className="text-xs font-bold text-[#39A900]">28 / 30 Registrados</span>
                  </div>
                  <div className="w-full bg-[#E2E8F0] h-2.5 rounded-full overflow-hidden mb-4">
                    <div className="bg-[#39A900] h-full rounded-full w-[93%]"></div>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-center text-xs font-bold">
                    <div className="p-2 rounded-xl bg-[#ECFDF5] text-[#065F46]">28 [A]</div>
                    <div className="p-2 rounded-xl bg-[#FFFBEB] text-[#92400E]">1 [R]</div>
                    <div className="p-2 rounded-xl bg-[#EFF6FF] text-[#1E40AF]">1 [FJ]</div>
                    <div className="p-2 rounded-xl bg-[#FEF2F2] text-[#991B1B]">0 [FI]</div>
                  </div>
                </div>
              )}

              {widgets.alertas && (
                <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-sm hover:shadow-md transition-all">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-bold text-[#64748B] uppercase tracking-wider">Monitor de Deserción</span>
                    <span className="px-2 py-0.5 rounded-full text-[11px] font-extrabold bg-[#FEF2F2] text-[#991B1B]">1 Caso Crítico</span>
                  </div>
                  <div className="p-3 rounded-xl bg-[#FEF2F2]/60 border border-[#FECACA] flex items-start gap-3">
                    <svg className="w-5 h-5 text-[#DC2626] shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                    <div>
                      <div className="font-bold text-xs text-[#991B1B]">Valentina Ríos Mendoza</div>
                      <div className="text-[11px] text-[#7F1D1D]">Acumula 4 fallas injustificadas continuas. Citar a Comité.</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------
            MÓDULO 2: FICHAS Y EXPEDIENTE TÉCNICO INTEGRAL
            ------------------------------------------------------------- */}
        {activeTab === 'fichas' && (
          <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
            {/* Barra de Filtro y Acciones */}
            <div className="bg-white p-4 rounded-2xl border border-[#E2E8F0] shadow-sm flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3 flex-1 min-w-[280px]">
                <input
                  type="text"
                  placeholder="Buscar por documento (CC, TI, PEP) o nombres..."
                  className="w-full px-4 py-2.5 rounded-xl border border-[#E2E8F0] bg-[#F8FAFC] text-sm focus:outline-none focus:border-[#39A900] focus:ring-2 focus:ring-[#39A900]/10 transition-all"
                />
              </div>

              <div className="flex items-center gap-2">
                <button className="px-3.5 py-2 rounded-xl text-xs font-bold border border-[#CBD5E1] bg-white hover:bg-[#F8FAFC] text-[#334155]">
                  Exportar Planilla PDF
                </button>
                <button className="px-3.5 py-2 rounded-xl text-xs font-bold border border-[#CBD5E1] bg-white hover:bg-[#F8FAFC] text-[#334155]">
                  Plantilla Excel
                </button>
                <button className="px-4 py-2 rounded-xl text-xs font-bold bg-[#39A900] text-white hover:bg-[#2e8800] shadow-sm">
                  + Nuevo Aprendiz
                </button>
              </div>
            </div>

            {/* Listado de Aprendices */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {aprendices.map((ap) => (
                <div key={ap.id} className="bg-white p-6 rounded-2xl border border-[#E2E8F0] shadow-sm hover:shadow-md transition-all">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 rounded-xl bg-[#0B2414] text-[#4EFA8A] font-extrabold flex items-center justify-center text-lg">
                        {ap.nombre[0]}
                      </div>
                      <div>
                        <div className="font-bold text-base text-[#0F172A]">{ap.nombre} {ap.apellidos}</div>
                        <div className="text-xs text-[#64748B]">{ap.tipoDoc} {ap.numDoc} · Ficha {ap.fichaCodigo}</div>
                      </div>
                    </div>
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-[#ECFDF5] text-[#065F46]">
                      {ap.estado}
                    </span>
                  </div>

                  {/* Tarjetas Segmentadas del Expediente */}
                  <div className="grid grid-cols-2 gap-3 text-xs mb-4">
                    <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#F1F5F9]">
                      <span className="text-[#64748B] block font-bold mb-0.5">Contacto Misena</span>
                      <span className="font-semibold text-[#0F172A] truncate block">{ap.emailMisena}</span>
                    </div>
                    <div className="p-3 rounded-xl bg-[#F8FAFC] border border-[#F1F5F9]">
                      <span className="text-[#64748B] block font-bold mb-0.5">Rendimiento RAP</span>
                      <span className="font-semibold text-[#15803D] block">{ap.rapsAprobados} / {ap.rapsTotal} Aprobados</span>
                    </div>
                  </div>

                  {/* Acciones de Expediente */}
                  <div className="flex items-center gap-2 pt-3 border-t border-[#F1F5F9]">
                    <button
                      onClick={() => {
                        setSelectedAprendiz(ap);
                        setShowQRModal(true);
                      }}
                      className="flex-1 py-2 px-3 rounded-xl text-xs font-bold border border-[#86EFAC] bg-[#F0FDF4] text-[#166534] hover:bg-[#DCFCE7] transition-all flex items-center justify-center gap-1.5"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" /></svg>
                      Generar QR
                    </button>
                    <a
                      href={`/estudiantes/${ap.id}/boletin-pdf/`}
                      target="_blank"
                      rel="noreferrer"
                      className="py-2 px-4 rounded-xl text-xs font-bold bg-[#0B2414] text-white hover:bg-[#153E23] transition-all"
                    >
                      Boletín Oficial PDF
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* -------------------------------------------------------------
            MÓDULO 3: CONTROL DE ASISTENCIA (4 ESTADOS)
            ------------------------------------------------------------- */}
        {activeTab === 'asistencia' && (
          <div className="p-6 space-y-6 max-w-7xl mx-auto w-full">
            <div className="bg-white p-5 rounded-2xl border border-[#E2E8F0] shadow-sm space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                <div>
                  <label className="text-xs font-bold text-[#64748B] uppercase block mb-1">Ficha Técnica</label>
                  <select className="w-full p-2.5 rounded-xl border border-[#E2E8F0] text-sm font-semibold bg-[#F8FAFC]">
                    <option>2670123 - ADSO</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-[#64748B] uppercase block mb-1">Competencia</label>
                  <select className="w-full p-2.5 rounded-xl border border-[#E2E8F0] text-sm font-semibold bg-[#F8FAFC]">
                    <option>220501096 - Desarrollo de Software</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-[#64748B] uppercase block mb-1">Resultado (RAP)</label>
                  <select className="w-full p-2.5 rounded-xl border border-[#E2E8F0] text-sm font-semibold bg-[#F8FAFC]">
                    <option>RAP-01: Construcción de Interfaces</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold text-[#64748B] uppercase block mb-1">Fecha</label>
                  <input type="date" defaultValue="2026-09-20" className="w-full p-2 rounded-xl border border-[#E2E8F0] text-sm font-semibold bg-[#F8FAFC]" />
                </div>
              </div>

              {/* Botonera Rápida de Marcación */}
              <div className="border-t border-[#F1F5F9] pt-4 space-y-3">
                {aprendices.map((ap) => (
                  <div key={ap.id} className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                    <div>
                      <span className="font-bold text-sm text-[#0F172A]">{ap.nombre} {ap.apellidos}</span>
                      <span className="text-xs text-[#64748B] block">Doc: {ap.numDoc}</span>
                    </div>

                    <div className="flex gap-2">
                      <button className="px-3 py-1.5 rounded-lg text-xs font-extrabold bg-[#ECFDF5] text-[#065F46] border border-[#A7F3D0] hover:bg-[#D1FAE5]">
                        [A] Asistió
                      </button>
                      <button className="px-3 py-1.5 rounded-lg text-xs font-extrabold bg-[#FFFBEB] text-[#92400E] border border-[#FDE68A] hover:bg-[#FEF3C7]">
                        [R] Retardo
                      </button>
                      <button className="px-3 py-1.5 rounded-lg text-xs font-extrabold bg-[#EFF6FF] text-[#1E40AF] border border-[#BFDBFE] hover:bg-[#DBEAFE]">
                        [FJ] Justificada
                      </button>
                      <button className="px-3 py-1.5 rounded-lg text-xs font-extrabold bg-[#FEF2F2] text-[#991B1B] border border-[#FECACA] hover:bg-[#FEE2E2]">
                        [FI] Injustificada
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* -------------------------------------------------------------
          MODAL FLOTANTE: PERSONALIZADOR DE WIDGETS
          ------------------------------------------------------------- */}
      {showWidgetModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-[#E2E8F0] space-y-4">
            <div className="flex items-center justify-between border-b border-[#E2E8F0] pb-4">
              <div>
                <h3 className="text-lg font-extrabold text-[#0F172A]">Personalizar Dashboard</h3>
                <p className="text-xs text-[#64748B]">Activa o desactiva módulos según tus prioridades formativas</p>
              </div>
              <button onClick={() => setShowWidgetModal(false)} className="text-[#94A3B8] hover:text-black">✕</button>
            </div>

            <div className="space-y-3">
              {Object.entries(widgets).map(([key, val]) => (
                <div key={key} className="flex items-center justify-between p-3 rounded-xl bg-[#F8FAFC] border border-[#E2E8F0]">
                  <span className="text-xs font-bold text-[#0F172A] capitalize">{key}</span>
                  <input
                    type="checkbox"
                    checked={val}
                    onChange={(e) => setWidgets({ ...widgets, [key]: e.target.checked })}
                    className="w-4 h-4 accent-[#39A900] cursor-pointer"
                  />
                </div>
              ))}
            </div>

            <button
              onClick={() => setShowWidgetModal(false)}
              className="w-full py-2.5 rounded-xl bg-[#39A900] text-white font-bold text-sm shadow-md"
            >
              Guardar Cambios
            </button>
          </div>
        </div>
      )}

      {/* -------------------------------------------------------------
          MODAL FLOTANTE: CREADOR DE CÓDIGO QR DEL APRENDIZ
          ------------------------------------------------------------- */}
      {showQRModal && selectedAprendiz && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-[#E2E8F0] space-y-4 text-center">
            <div className="flex justify-between items-center border-b border-[#E2E8F0] pb-3">
              <span className="text-xs font-extrabold text-[#0B2414] uppercase">Credencial QR Oficial</span>
              <button onClick={() => setShowQRModal(false)} className="text-[#94A3B8] hover:text-black">✕</button>
            </div>

            <div className="p-4 bg-[#F8FAFC] rounded-2xl border border-[#E2E8F0] inline-block mx-auto">
              <div className="w-48 h-48 bg-white border-2 border-dashed border-[#39A900] rounded-xl flex items-center justify-center relative">
                <span className="text-xs text-[#64748B]">QR Render Canvas</span>
                <div className="absolute w-8 h-8 rounded-lg bg-[#39A900] text-white font-extrabold flex items-center justify-center text-sm shadow-md">
                  S
                </div>
              </div>
            </div>

            <div>
              <div className="font-extrabold text-base text-[#0F172A]">{selectedAprendiz.nombre} {selectedAprendiz.apellidos}</div>
              <div className="text-xs text-[#64748B]">CC {selectedAprendiz.numDoc} · Ficha {selectedAprendiz.fichaCodigo}</div>
              <div className="text-[11px] font-mono text-[#39A900] mt-1">TOKEN: SHA256-ROTATIVO-24H</div>
            </div>

            <div className="grid grid-cols-2 gap-2 pt-2">
              <button className="py-2 px-3 rounded-xl text-xs font-bold bg-[#39A900] text-white hover:bg-[#2d8800]">
                Descargar PNG
              </button>
              <button className="py-2 px-3 rounded-xl text-xs font-bold border border-[#CBD5E1] bg-white text-[#334155] hover:bg-[#F8FAFC]">
                Imprimir Carnet
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
