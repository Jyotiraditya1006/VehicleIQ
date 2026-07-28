'use client';

import React, { useState, useEffect, useRef } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface VehicleProfile {
  vehicle_id: string;
  driver_name: string;
  description: string;
  scenario: string;
  model_name: string;
  tagline: string;
  specs: string;
}

interface ProblemSolution {
  component: string;
  severity: string;
  title: string;
  explanation: string;
  solution_title: string;
  diy_fix_steps: string[];
  estimated_cost: string;
  urgency: string;
  difficulty: string;
  parts_needed: string[];
}

interface HealthData {
  vehicle_id: string;
  overall_health_score: number;
  driving_style: string;
  driving_behavior_score: number;
  component_scores: {
    brake_health: number;
    engine_health: number;
    battery_health: number;
  };
  plain_language_alerts: ProblemSolution[];
  timestamp: string;
}

interface TelemetryPoint {
  rpm: number;
  speed_kph: number;
  coolant_temp_c: number;
  battery_voltage: number;
  throttle_pos_pct: number;
  maf_g_s: number;
}

export default function LuxuryDashboard() {
  const [garage] = useState<VehicleProfile[]>([
    {
      vehicle_id: 'VEHICLE_001',
      driver_name: 'Alice Smith',
      description: 'Gentle City Commuter',
      scenario: 'city_driving',
      model_name: 'Phantom GT V12',
      tagline: '6.0L Twin-Turbo Grand Tourer',
      specs: '720 HP | 0-100 in 3.1s'
    },
    {
      vehicle_id: 'VEHICLE_002',
      driver_name: 'Bob Johnson',
      description: 'Aggressive Track Driver',
      scenario: 'aggressive_sport',
      model_name: 'Apex Hyperion Track Special',
      tagline: 'Quad-Motor Carbon Hypercar',
      specs: '1450 HP | 0-100 in 1.9s'
    },
    {
      vehicle_id: 'VEHICLE_003',
      driver_name: 'Charlie Davis',
      description: 'Thermal Overheat Test',
      scenario: 'thermal_overheat',
      model_name: 'Monaco RS V10',
      tagline: 'Naturally Aspirated Track Weapon',
      specs: '640 HP | Redline 8900 RPM'
    }
  ]);

  const [selectedVehicle, setSelectedVehicle] = useState<string>('VEHICLE_001');
  const [health, setHealth] = useState<HealthData | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetryPoint>({
    rpm: 1850,
    speed_kph: 85,
    coolant_temp_c: 91,
    battery_voltage: 14.2,
    throttle_pos_pct: 24,
    maf_g_s: 8.4
  });

  const [activeSolution, setActiveSolution] = useState<ProblemSolution | null>(null);
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [reportHtml, setReportHtml] = useState<string>('');
  const [isAudioPlaying, setIsAudioPlaying] = useState<boolean>(false);

  // Audio Context Ref for V8 Engine Acoustic Sound Synthesizer
  const audioCtxRef = useRef<AudioContext | null>(null);
  const oscRef = useRef<OscillatorNode | null>(null);

  // Toggle Synthetic Engine Audio Soundscape
  const toggleEngineSound = () => {
    if (isAudioPlaying) {
      if (oscRef.current) oscRef.current.stop();
      setIsAudioPlaying(false);
    } else {
      try {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        const ctx = new AudioContextClass();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(40 + (telemetry.rpm / 100), ctx.currentTime);
        gain.gain.setValueAtTime(0.08, ctx.currentTime);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        audioCtxRef.current = ctx;
        oscRef.current = osc;
        setIsAudioPlaying(true);
      } catch (e) {
        console.warn('Audio Synthesis not supported:', e);
      }
    }
  };

  // Poll backend API for selected hypercar telemetry & ML health
  useEffect(() => {
    const fetchData = async () => {
      try {
        const healthRes = await fetch(`${API_BASE_URL}/api/v1/health-score?vehicle_id=${selectedVehicle}`);
        if (healthRes.ok) {
          const healthJson = await healthRes.json();
          setHealth(healthJson);
        }

        const telemRes = await fetch(`${API_BASE_URL}/api/v1/telemetry/recent?limit=1`);
        if (telemRes.ok) {
          const telemJson = await telemRes.json();
          if (telemJson.data && telemJson.data.length > 0) {
            setTelemetry(telemJson.data[0]);

            // Update acoustic pitch if engine audio is active
            if (oscRef.current && audioCtxRef.current) {
              oscRef.current.frequency.setValueAtTime(35 + (telemJson.data[0].rpm / 80), audioCtxRef.current.currentTime);
            }
          }
        }
      } catch (err) {
        console.warn('Backend server connection fallback active:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [selectedVehicle]);

  // Generate printable mechanic report
  const handleGenerateReport = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/report?vehicle_id=${selectedVehicle}`);
      if (res.ok) {
        const data = await res.json();
        setReportHtml(data.html_report);
        setShowReportModal(true);
      }
    } catch (e) {
      alert('Could not fetch diagnostic report from backend.');
    }
  };

  const activeCar = garage.find(c => c.vehicle_id === selectedVehicle) || garage[0];

  return (
    <div style={{ minHeight: '100vh', padding: '36px 48px', maxWidth: '1440px', margin: '0 auto' }}>

      {/* --- Top Luxury Navigation Bar --- */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '36px', flexWrap: 'wrap', gap: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{ fontSize: '32px' }}>👑</span>
            <h1 className="font-serif-luxury text-gold-gradient" style={{ fontSize: '38px', fontWeight: 900, letterSpacing: '-0.5px' }}>
              VEHICLE<span style={{ color: '#fff', fontStyle: 'italic' }}>IQ</span>
            </h1>
            <span style={{ background: 'rgba(212, 175, 55, 0.12)', color: '#d4af37', border: '1px solid rgba(212, 175, 55, 0.3)', padding: '6px 16px', borderRadius: '30px', fontSize: '11px', fontWeight: 800, letterSpacing: '1px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="gold-beacon"></span> LUXURY AUTOMOTIVE INTELLIGENCE
            </span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '6px' }}>
            Next-Generation AI Telemetry & Executive Maintenance Butler
          </p>
        </div>

        {/* Action Controls & Garage Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          
          {/* Audio Engine Acoustic Soundscape Toggle */}
          <button
            onClick={toggleEngineSound}
            style={{ background: isAudioPlaying ? 'linear-gradient(135deg, #00f2fe, #4facfe)' : 'rgba(10, 14, 26, 0.8)', color: isAudioPlaying ? '#030408' : '#d4af37', border: '1px solid rgba(212, 175, 55, 0.4)', padding: '12px 20px', borderRadius: '16px', fontWeight: 800, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', fontSize: '13px' }}
          >
            <span>{isAudioPlaying ? '🔊 Engine Acoustics Active' : '🎵 Synth Engine Acoustics'}</span>
            {isAudioPlaying && (
              <div style={{ display: 'flex', gap: '3px', alignItems: 'flex-end', height: '16px' }}>
                <div className="audio-bar" style={{ animationDelay: '0s' }}></div>
                <div className="audio-bar" style={{ animationDelay: '0.2s' }}></div>
                <div className="audio-bar" style={{ animationDelay: '0.4s' }}></div>
              </div>
            )}
          </button>

          <button
            onClick={handleGenerateReport}
            className="btn-gold-luxury"
          >
            📜 Executive Diagnostic Certificate
          </button>
        </div>
      </header>

      {/* --- Executive Hypercar Showroom Selector Cards --- */}
      <h2 className="font-serif-luxury" style={{ fontSize: '22px', color: '#fff', marginBottom: '16px' }}>
        🏛️ Select Hypercar Garage Profile
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px', marginBottom: '36px' }}>
        {garage.map((car) => {
          const isSelected = car.vehicle_id === selectedVehicle;
          return (
            <div
              key={car.vehicle_id}
              onClick={() => setSelectedVehicle(car.vehicle_id)}
              className="luxury-glass"
              style={{
                padding: '24px',
                cursor: 'pointer',
                border: isSelected ? '2px solid #d4af37' : '1px solid rgba(212, 175, 55, 0.15)',
                background: isSelected ? 'linear-gradient(135deg, rgba(212, 175, 55, 0.12), rgba(10, 14, 26, 0.9))' : 'rgba(10, 14, 26, 0.75)',
                position: 'relative'
              }}
            >
              {isSelected && (
                <span style={{ position: 'absolute', top: '16px', right: '16px', background: '#d4af37', color: '#030408', fontSize: '10px', fontWeight: 900, padding: '3px 10px', borderRadius: '12px', textTransform: 'uppercase' }}>
                  ACTIVE MONITORING
                </span>
              )}
              <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>
                {car.driver_name} • {car.description}
              </span>
              <h3 className="font-serif-luxury" style={{ fontSize: '22px', color: isSelected ? '#f3e5ab' : '#fff', marginTop: '4px', fontWeight: 800 }}>
                {car.model_name}
              </h3>
              <p style={{ fontSize: '13px', color: '#cbd5e1', marginTop: '2px' }}>{car.tagline}</p>
              <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: '#d4af37', fontWeight: 700 }}>⚡ {car.specs}</span>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>ID: {car.vehicle_id}</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* --- Live Telemetry Cockpit Instrument Cluster --- */}
      <h2 className="font-serif-luxury" style={{ fontSize: '22px', color: '#fff', marginBottom: '16px' }}>
        ⚡ Live Cockpit Instrument Telemetry & Sound Engine
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(230px, 1fr))', gap: '20px', marginBottom: '36px' }}>
        
        {/* Tachometer RPM Dial */}
        <div className="luxury-glass" style={{ padding: '24px', textAlign: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>TACHOMETER (ENGINE RPM)</span>
          <div style={{ position: 'relative', margin: '20px auto 14px', width: '140px', height: '140px', borderRadius: '50%', background: 'radial-gradient(circle, #05050a 60%, rgba(212, 175, 55, 0.1) 100%)', border: '3px solid rgba(212, 175, 55, 0.4)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', boxShadow: '0 0 30px rgba(212, 175, 55, 0.2)' }}>
            <span style={{ fontSize: '32px', fontWeight: 900, color: telemetry.rpm > 3500 ? '#ff0844' : '#d4af37' }}>
              {Math.round(telemetry.rpm)}
            </span>
            <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 700 }}>RPM</span>
          </div>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Peak Torque: 4200 RPM</span>
        </div>

        {/* Speedometer km/h Dial */}
        <div className="luxury-glass" style={{ padding: '24px', textAlign: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>SPEEDOMETER (KM/H)</span>
          <div style={{ position: 'relative', margin: '20px auto 14px', width: '140px', height: '140px', borderRadius: '50%', background: 'radial-gradient(circle, #05050a 60%, rgba(0, 242, 254, 0.1) 100%)', border: '3px solid rgba(0, 242, 254, 0.4)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', boxShadow: '0 0 30px rgba(0, 242, 254, 0.2)' }}>
            <span style={{ fontSize: '32px', fontWeight: 900, color: '#00f2fe' }}>
              {Math.round(telemetry.speed_kph)}
            </span>
            <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 700 }}>KM/H</span>
          </div>
          <span style={{ fontSize: '12px', color: '#64748b' }}>Telemetry Tele-Stream</span>
        </div>

        {/* Thermal Engine Temp */}
        <div className="luxury-glass" style={{ padding: '24px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>COOLANT THERMAL TEMP</span>
          <div style={{ fontSize: '38px', fontWeight: 900, color: telemetry.coolant_temp_c > 100 ? '#ff0844' : '#43e97b', margin: '14px 0' }}>
            {Math.round(telemetry.coolant_temp_c)}°C
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>Optimal Operating Window: 85°C - 95°C</span>
        </div>

        {/* Battery & Charging Voltage */}
        <div className="luxury-glass" style={{ padding: '24px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>ALTERNATOR / BUS VOLTAGE</span>
          <div style={{ fontSize: '38px', fontWeight: 900, color: telemetry.battery_voltage < 12.4 ? '#ff0844' : '#d4af37', margin: '14px 0' }}>
            {telemetry.battery_voltage} V
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>Target: 13.8V - 14.4V</span>
        </div>
      </div>

      {/* --- Predictive Component Degradation Metrics --- */}
      <h2 className="font-serif-luxury" style={{ fontSize: '22px', color: '#fff', marginBottom: '16px' }}>
        🧠 AI Predictive Degradation & Health Forecasting
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '20px', marginBottom: '36px' }}>
        
        {/* Brake System */}
        <div className="luxury-glass" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontWeight: 700, color: '#fff', fontSize: '15px' }}>Brake System Pad Lifespan</span>
            <span style={{ fontWeight: 900, fontSize: '18px', color: (health?.component_scores?.brake_health || 95) > 70 ? '#43e97b' : '#ff0844' }}>
              {health?.component_scores?.brake_health || 95}%
            </span>
          </div>
          <div style={{ height: '8px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ height: '100%', width: `${health?.component_scores?.brake_health || 95}%`, background: (health?.component_scores?.brake_health || 95) > 70 ? 'linear-gradient(90deg, #43e97b, #38f9d7)' : 'linear-gradient(90deg, #ff0844, #ffb199)' }}></div>
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>Braking Friction Wear: Nominal</span>
        </div>

        {/* Engine Stress */}
        <div className="luxury-glass" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontWeight: 700, color: '#fff', fontSize: '15px' }}>Engine Thermal & Mechanical</span>
            <span style={{ fontWeight: 900, fontSize: '18px', color: (health?.component_scores?.engine_health || 94) > 70 ? '#43e97b' : '#ff0844' }}>
              {health?.component_scores?.engine_health || 94}%
            </span>
          </div>
          <div style={{ height: '8px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ height: '100%', width: `${health?.component_scores?.engine_health || 94}%`, background: (health?.component_scores?.engine_health || 94) > 70 ? 'linear-gradient(90deg, #d4af37, #f3e5ab)' : 'linear-gradient(90deg, #ff0844, #ffb199)' }}></div>
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>Thermodynamic Expansion: Stable</span>
        </div>

        {/* Battery Health */}
        <div className="luxury-glass" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontWeight: 700, color: '#fff', fontSize: '15px' }}>Battery & Charging System</span>
            <span style={{ fontWeight: 900, fontSize: '18px', color: (health?.component_scores?.battery_health || 96) > 70 ? '#43e97b' : '#ff0844' }}>
              {health?.component_scores?.battery_health || 96}%
            </span>
          </div>
          <div style={{ height: '8px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ height: '100%', width: `${health?.component_scores?.battery_health || 96}%`, background: (health?.component_scores?.battery_health || 96) > 70 ? 'linear-gradient(90deg, #00f2fe, #4facfe)' : 'linear-gradient(90deg, #ff0844, #ffb199)' }}></div>
          </div>
          <span style={{ fontSize: '12px', color: '#94a3b8' }}>12V Cell Voltage Stability: Good</span>
        </div>
      </div>

      {/* --- Executive Diagnostic Findings & Step-by-Step Fix Guides --- */}
      <h2 className="font-serif-luxury" style={{ fontSize: '22px', color: '#fff', marginBottom: '16px' }}>
        🛠️ Executive Maintenance Butler & Step-by-Step Fix Solutions
      </h2>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '36px' }}>
        {health?.plain_language_alerts?.map((alert, idx) => (
          <div key={idx} className="luxury-glass" style={{ padding: '26px', borderLeft: `6px solid ${alert.severity === 'CRITICAL' ? '#ff0844' : alert.severity === 'WARNING' ? '#d4af37' : '#00f2fe'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '10px' }}>
              <h3 className="font-serif-luxury" style={{ fontSize: '20px', fontWeight: 800, color: '#fff' }}>{alert.title}</h3>
              <span style={{ background: alert.severity === 'CRITICAL' ? 'linear-gradient(135deg, #ff0844, #ffb199)' : alert.severity === 'WARNING' ? 'linear-gradient(135deg, #d4af37, #aa771c)' : 'linear-gradient(135deg, #00f2fe, #4facfe)', color: '#030408', padding: '4px 14px', borderRadius: '20px', fontSize: '11px', fontWeight: 900, letterSpacing: '0.5px' }}>
                {alert.severity} SEVERITY
              </span>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.6, marginBottom: '16px' }}>
              <strong>Diagnostic Anomaly Finding:</strong> {alert.explanation}
            </p>

            <button
              onClick={() => setActiveSolution(alert)}
              className="btn-gold-luxury"
              style={{ fontSize: '13px', padding: '10px 20px', display: 'inline-flex', alignItems: 'center', gap: '8px' }}
            >
              🛠️ View DIY Repair Solution Guide & Cost Breakdown
            </button>
          </div>
        ))}
      </div>

      {/* --- DIY Solution Guide Modal --- */}
      {activeSolution && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(3, 4, 8, 0.9)', zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
          <div className="luxury-glass" style={{ width: '100%', maxWidth: '780px', maxHeight: '90vh', overflowY: 'auto', padding: '32px', border: '1px solid #d4af37' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(212, 175, 55, 0.2)', paddingBottom: '18px', marginBottom: '24px' }}>
              <div>
                <span style={{ background: '#d4af37', color: '#030408', fontSize: '10px', fontWeight: 900, padding: '3px 10px', borderRadius: '10px', textTransform: 'uppercase' }}>
                  {activeSolution.severity} URGENCY
                </span>
                <h2 className="font-serif-luxury text-gold-gradient" style={{ fontSize: '24px', fontWeight: 900, marginTop: '8px' }}>
                  {activeSolution.solution_title}
                </h2>
              </div>
              <button onClick={() => setActiveSolution(null)} style={{ background: '#ff0844', color: '#fff', border: 'none', padding: '8px 18px', borderRadius: '10px', cursor: 'pointer', fontWeight: 800 }}>Close</button>
            </div>

            {/* Cost & Urgency Metrics */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '28px' }}>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '14px', border: '1px solid rgba(212, 175, 55, 0.2)' }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Estimated Repair Cost</span>
                <div style={{ fontSize: '20px', fontWeight: 900, color: '#43e97b', marginTop: '4px' }}>{activeSolution.estimated_cost}</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '14px', border: '1px solid rgba(212, 175, 55, 0.2)' }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Urgency Rating</span>
                <div style={{ fontSize: '15px', fontWeight: 800, color: '#d4af37', marginTop: '4px' }}>{activeSolution.urgency}</div>
              </div>
            </div>

            {/* DIY Step-by-Step Fix Instructions */}
            <h3 className="font-serif-luxury" style={{ fontSize: '18px', color: '#00f2fe', marginBottom: '14px' }}>
              🛠️ Step-by-Step DIY Repair Instructions:
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '28px' }}>
              {activeSolution.diy_fix_steps?.map((step, sIdx) => (
                <div key={sIdx} style={{ background: 'rgba(10, 14, 26, 0.9)', padding: '14px 18px', borderRadius: '12px', borderLeft: '4px solid #d4af37', color: '#cbd5e1', fontSize: '14px' }}>
                  <strong style={{ color: '#d4af37' }}>Step {sIdx + 1}:</strong> {step}
                </div>
              ))}
            </div>

            {/* Recommended OEM Replacement Parts */}
            {activeSolution.parts_needed?.length > 0 && (
              <div style={{ marginBottom: '28px' }}>
                <h4 style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '10px', textTransform: 'uppercase', fontWeight: 700 }}>Recommended OEM Replacement Parts:</h4>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  {activeSolution.parts_needed.map((part, pIdx) => (
                    <span key={pIdx} style={{ background: 'rgba(212, 175, 55, 0.1)', color: '#f3e5ab', padding: '8px 16px', borderRadius: '10px', fontSize: '13px', fontWeight: 700, border: '1px solid rgba(212, 175, 55, 0.3)' }}>
                      🔧 {part}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: 'flex', gap: '14px' }}>
              <button onClick={() => alert('Master Concierge Mechanic dispatched to your location!')} className="btn-gold-luxury" style={{ flex: 1, padding: '16px', fontSize: '15px' }}>
                👨‍🔧 Dispatch Official White-Glove Concierge Service
              </button>
            </div>

          </div>
        </div>
      )}

      {/* --- Executive Report Modal --- */}
      {showReportModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(3, 4, 8, 0.9)', zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
          <div className="luxury-glass" style={{ width: '100%', maxWidth: '880px', maxHeight: '90vh', overflowY: 'auto', padding: '28px', border: '1px solid #d4af37' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 className="font-serif-luxury text-gold-gradient" style={{ fontSize: '22px' }}>Executive Diagnostic Certificate — {activeCar.model_name}</h2>
              <button onClick={() => setShowReportModal(false)} style={{ background: '#ff0844', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 800 }}>Close</button>
            </div>
            <div dangerouslySetInnerHTML={{ __html: reportHtml }} />
          </div>
        </div>
      )}

    </div>
  );
}
