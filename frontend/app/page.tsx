'use client';

import React, { useState, useEffect } from 'react';

// API Host URL (Backend FastAPI)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface VehicleProfile {
  vehicle_id: string;
  driver_name: string;
  description: string;
  scenario: string;
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

export default function Dashboard() {
  const [vehicles, setVehicles] = useState<VehicleProfile[]>([
    { vehicle_id: 'VEHICLE_001', driver_name: 'Alice Smith', description: 'Gentle City Commuter', scenario: 'city_driving' },
    { vehicle_id: 'VEHICLE_002', driver_name: 'Bob Johnson', description: 'Aggressive Sport Driver', scenario: 'aggressive_sport' },
    { vehicle_id: 'VEHICLE_003', driver_name: 'Charlie Davis', description: 'High Temp Engine Fault', scenario: 'thermal_overheat' },
  ]);
  const [selectedVehicle, setSelectedVehicle] = useState<string>('VEHICLE_001');
  const [health, setHealth] = useState<HealthData | null>(null);
  const [telemetry, setTelemetry] = useState<TelemetryPoint>({
    rpm: 1250,
    speed_kph: 45,
    coolant_temp_c: 89,
    battery_voltage: 14.1,
    throttle_pos_pct: 18,
    maf_g_s: 6.2,
  });

  // Selected solution modal state
  const [activeSolution, setActiveSolution] = useState<ProblemSolution | null>(null);
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [reportHtml, setReportHtml] = useState<string>('');

  // Fetch available vehicles list from backend
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/vehicles`)
      .then(res => res.json())
      .then(data => {
        if (data.vehicles) setVehicles(data.vehicles);
      })
      .catch(err => console.warn('Vehicles fallback active:', err));
  }, []);

  // Poll backend API for selected driver profile health & telemetry
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
          }
        }
      } catch (err) {
        console.warn('Backend server polling fallback active:', err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [selectedVehicle]);

  // Generate printable mechanic report for selected driver
  const handleGenerateReport = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/report?vehicle_id=${selectedVehicle}`);
      if (res.ok) {
        const data = await res.json();
        setReportHtml(data.html_report);
        setShowReportModal(true);
      }
    } catch (e) {
      alert('Could not connect to backend to fetch report.');
    }
  };

  const activeProfile = vehicles.find(v => v.vehicle_id === selectedVehicle) || vehicles[0];

  return (
    <div style={{ padding: '28px', maxWidth: '1380px', margin: '0 auto' }}>
      
      {/* --- Futuristic Navigation Bar --- */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <h1 style={{ fontSize: '32px', fontWeight: 900, background: 'linear-gradient(135deg, #00f2fe, #4facfe)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-0.5px' }}>
              ⚡ VehicleIQ
            </h1>
            <span style={{ background: 'rgba(0, 242, 254, 0.12)', color: '#00f2fe', border: '1px solid rgba(0, 242, 254, 0.3)', padding: '5px 14px', borderRadius: '30px', fontSize: '12px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="live-dot"></span> REAL-TIME AI TELEMETRY STREAM
            </span>
          </div>
          <p style={{ color: '#94a3b8', fontSize: '14px', marginTop: '4px' }}>
            Predictive component failure intelligence & automated repair solution guides
          </p>
        </div>

        {/* Multi-Driver Profile Selector Dropdown */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ background: 'rgba(13, 18, 36, 0.9)', border: '1px solid rgba(0, 242, 254, 0.3)', borderRadius: '14px', padding: '8px 16px', boxShadow: '0 4px 20px rgba(0, 242, 254, 0.1)' }}>
            <label style={{ color: '#94a3b8', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'block', fontWeight: 700 }}>
              Active Driver Profile
            </label>
            <select
              value={selectedVehicle}
              onChange={(e) => setSelectedVehicle(e.target.value)}
              style={{ background: 'transparent', color: '#00f2fe', border: 'none', fontSize: '15px', fontWeight: 800, cursor: 'pointer', outline: 'none' }}
            >
              {vehicles.map((v) => (
                <option key={v.vehicle_id} value={v.vehicle_id} style={{ background: '#070913', color: '#fff' }}>
                  👤 {v.driver_name} ({v.description})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGenerateReport}
            style={{ background: 'linear-gradient(135deg, #4facfe, #00f2fe)', color: '#0f172a', border: 'none', padding: '14px 22px', borderRadius: '14px', fontWeight: 800, cursor: 'pointer', boxShadow: '0 6px 20px rgba(0, 242, 254, 0.3)', fontSize: '14px' }}
          >
            📋 Printable Mechanic Report
          </button>
        </div>
      </header>

      {/* --- Active Driver Profile Hero Banner --- */}
      <div className="glass-panel" style={{ padding: '20px 28px', marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', background: 'linear-gradient(135deg, rgba(13, 18, 36, 0.95), rgba(7, 9, 19, 0.95))' }}>
        <div>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>Monitored Vehicle & Driver Profile</span>
          <h2 style={{ fontSize: '22px', color: '#f8fafc', fontWeight: 800, marginTop: '2px' }}>
            {activeProfile.driver_name} <span style={{ color: '#00f2fe', fontSize: '16px', fontWeight: 500 }}>(ID: {activeProfile.vehicle_id})</span>
          </h2>
          <p style={{ fontSize: '13px', color: '#94a3b8', marginTop: '2px' }}>Operational Mode: <strong style={{ color: '#4facfe' }}>{activeProfile.description}</strong></p>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '24px' }}>
          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>AI Predicted Vehicle Health</span>
            <div style={{ fontSize: '32px', fontWeight: 900, color: (health?.overall_health_score || 95) >= 80 ? '#43e97b' : (health?.overall_health_score || 95) >= 60 ? '#f6d365' : '#ff0844' }}>
              {health?.overall_health_score || 95}%
            </div>
          </div>
        </div>
      </div>

      {/* --- Section 1: Futuristic Speedometer & Tachometer Live Gauges --- */}
      <h2 style={{ fontSize: '18px', color: '#f8fafc', marginBottom: '16px', fontWeight: 800 }}>⚡ Real-Time OBD-II Live Instrument Cluster</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        
        {/* Tachometer RPM Dial Card */}
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>ENGINE RPM (TACHOMETER)</span>
          <div style={{ position: 'relative', margin: '16px auto', width: '130px', height: '130px', borderRadius: '50%', background: 'radial-gradient(circle, #0d1224 60%, #1e293b 100%)', border: '3px solid rgba(0, 242, 254, 0.3)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', boxShadow: '0 0 20px rgba(0, 242, 254, 0.15)' }}>
            <span style={{ fontSize: '30px', fontWeight: 900, color: telemetry.rpm > 3500 ? '#ff0844' : '#00f2fe' }}>
              {Math.round(telemetry.rpm)}
            </span>
            <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>RPM</span>
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>Limit: 7000 RPM</div>
        </div>

        {/* Speedometer km/h Dial Card */}
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>VEHICLE SPEEDOMETER</span>
          <div style={{ position: 'relative', margin: '16px auto', width: '130px', height: '130px', borderRadius: '50%', background: 'radial-gradient(circle, #0d1224 60%, #1e293b 100%)', border: '3px solid rgba(67, 233, 123, 0.3)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', boxShadow: '0 0 20px rgba(67, 233, 123, 0.15)' }}>
            <span style={{ fontSize: '30px', fontWeight: 900, color: '#43e97b' }}>
              {Math.round(telemetry.speed_kph)}
            </span>
            <span style={{ fontSize: '11px', color: '#94a3b8', fontWeight: 600 }}>KM/H</span>
          </div>
          <div style={{ fontSize: '12px', color: '#64748b' }}>OBD ECU Stream</div>
        </div>

        {/* Coolant Temperature Card */}
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>COOLANT TEMP</span>
          <div style={{ fontSize: '36px', fontWeight: 900, color: telemetry.coolant_temp_c > 100 ? '#ff0844' : '#f6d365', margin: '12px 0' }}>
            {Math.round(telemetry.coolant_temp_c)}°C
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Optimal: 85°C - 95°C</div>
        </div>

        {/* Battery Voltage Monitor */}
        <div className="glass-panel" style={{ padding: '20px', textAlign: 'center', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>CONTROL MODULE VOLTAGE</span>
          <div style={{ fontSize: '36px', fontWeight: 900, color: telemetry.battery_voltage < 12.4 ? '#ff0844' : '#4facfe', margin: '12px 0' }}>
            {telemetry.battery_voltage} V
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Target: 13.8V - 14.4V</div>
        </div>
      </div>

      {/* --- Section 2: AI Component Failure Degradation --- */}
      <h2 style={{ fontSize: '18px', color: '#f8fafc', marginBottom: '16px', fontWeight: 800 }}>⚙️ AI Component Failure Degradation Predictions</h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        
        {/* Brake Health */}
        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
            <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '15px' }}>Brake System Pad Lifespan</span>
            <span style={{ fontWeight: 900, fontSize: '18px', color: (health?.component_scores?.brake_health || 95) > 70 ? '#43e97b' : '#ff0844' }}>
              {health?.component_scores?.brake_health || 95}%
            </span>
          </div>
          <div style={{ height: '10px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ height: '100%', width: `${health?.component_scores?.brake_health || 95}%`, background: (health?.component_scores?.brake_health || 95) > 70 ? 'linear-gradient(90deg, #43e97b, #38f9d7)' : 'linear-gradient(90deg, #ff0844, #ffb199)' }}></div>
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Friction Heat Rate: Normal</div>
        </div>

        {/* Engine Stress */}
        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
            <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '15px' }}>Engine Thermal & Mechanical</span>
            <span style={{ fontWeight: 900, fontSize: '18px', color: (health?.component_scores?.engine_health || 94) > 70 ? '#43e97b' : '#ff0844' }}>
              {health?.component_scores?.engine_health || 94}%
            </span>
          </div>
          <div style={{ height: '10px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ height: '100%', width: `${health?.component_scores?.engine_health || 94}%`, background: (health?.component_scores?.engine_health || 94) > 70 ? 'linear-gradient(90deg, #00f2fe, #4facfe)' : 'linear-gradient(90deg, #ff0844, #ffb199)' }}></div>
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>Thermal Expansion Stress: Nominal</div>
        </div>

        {/* Battery Health */}
        <div className="glass-panel" style={{ padding: '22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '14px' }}>
            <span style={{ fontWeight: 700, color: '#f8fafc', fontSize: '15px' }}>Battery & Alternator Charging</span>
            <span style={{ fontWeight: 900, fontSize: '18px', color: (health?.component_scores?.battery_health || 96) > 70 ? '#43e97b' : '#ff0844' }}>
              {health?.component_scores?.battery_health || 96}%
            </span>
          </div>
          <div style={{ height: '10px', background: '#1e293b', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{ height: '100%', width: `${health?.component_scores?.battery_health || 96}%`, background: (health?.component_scores?.battery_health || 96) > 70 ? 'linear-gradient(90deg, #4facfe, #6366f1)' : 'linear-gradient(90deg, #ff0844, #ffb199)' }}></div>
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>12V Cell Voltage Stability: Good</div>
        </div>

        {/* Driving Behavior Profile Card */}
        <div className="glass-panel" style={{ padding: '22px', background: 'linear-gradient(135deg, rgba(13, 18, 36, 0.95), rgba(0, 242, 254, 0.05))' }}>
          <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 700 }}>DRIVING STYLE CLASSIFIER</span>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '10px' }}>
            <div style={{ fontSize: '24px', fontWeight: 900, color: '#00f2fe' }}>
              {health?.driving_style?.toUpperCase() || 'GENTLE'}
            </div>
            <div style={{ background: '#070913', padding: '6px 14px', borderRadius: '10px', border: '1px solid rgba(0, 242, 254, 0.3)', fontWeight: 800, color: '#43e97b', fontSize: '14px' }}>
              Score: {health?.driving_behavior_score || 90}/100
            </div>
          </div>
        </div>
      </div>

      {/* --- Section 3: Diagnostic Problems & Step-by-Step Fix Solution Cards --- */}
      <h2 style={{ fontSize: '18px', color: '#f8fafc', marginBottom: '16px', fontWeight: 800 }}>🔧 Diagnostic Problem Findings & Step-by-Step Repair Guides</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '32px' }}>
        {health?.plain_language_alerts?.map((alert, idx) => (
          <div key={idx} className="glass-panel" style={{ padding: '22px', borderLeft: `6px solid ${alert.severity === 'CRITICAL' ? '#ff0844' : alert.severity === 'WARNING' ? '#f6d365' : '#4facfe'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexWrap: 'wrap', gap: '8px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 800, color: '#f8fafc' }}>{alert.title}</h3>
              <span className={alert.severity === 'CRITICAL' ? 'badge-critical' : alert.severity === 'WARNING' ? 'badge-warning' : 'badge-info'}>
                {alert.severity}
              </span>
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '14px', lineHeight: 1.6, marginBottom: '14px' }}>
              <strong>Diagnostic Finding:</strong> {alert.explanation}
            </p>

            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              <button
                onClick={() => setActiveSolution(alert)}
                style={{ background: 'linear-gradient(135deg, #00f2fe, #4facfe)', color: '#0f172a', border: 'none', padding: '10px 18px', borderRadius: '10px', fontWeight: 800, cursor: 'pointer', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                🛠️ View DIY Repair Solution Guide & Cost
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* --- Section 4: Interactive Problem Solution Drawer / Modal --- */}
      {activeSolution && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
          <div style={{ background: '#0d1224', width: '100%', maxWidth: '750px', maxHeight: '90vh', borderRadius: '20px', overflowY: 'auto', border: '1px solid rgba(0, 242, 254, 0.4)', padding: '28px', boxShadow: '0 0 50px rgba(0, 242, 254, 0.2)' }}>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '16px', marginBottom: '20px' }}>
              <div>
                <span className={activeSolution.severity === 'CRITICAL' ? 'badge-critical' : activeSolution.severity === 'WARNING' ? 'badge-warning' : 'badge-info'}>
                  {activeSolution.severity} URGENCY
                </span>
                <h2 style={{ fontSize: '22px', fontWeight: 900, color: '#f8fafc', marginTop: '6px' }}>{activeSolution.solution_title}</h2>
              </div>
              <button onClick={() => setActiveSolution(null)} style={{ background: '#ff0844', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '8px', cursor: 'pointer', fontWeight: 800 }}>Close</button>
            </div>

            {/* Cost & Urgency Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginBottom: '24px' }}>
              <div style={{ background: '#1e293b', padding: '14px', borderRadius: '12px' }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Estimated Repair Cost</span>
                <div style={{ fontSize: '18px', fontWeight: 900, color: '#43e97b', marginTop: '4px' }}>{activeSolution.estimated_cost}</div>
              </div>
              <div style={{ background: '#1e293b', padding: '14px', borderRadius: '12px' }}>
                <span style={{ fontSize: '11px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 700 }}>Urgency Rating</span>
                <div style={{ fontSize: '14px', fontWeight: 800, color: '#f6d365', marginTop: '4px' }}>{activeSolution.urgency}</div>
              </div>
            </div>

            {/* Step-by-Step DIY Fix Steps */}
            <h3 style={{ fontSize: '16px', color: '#00f2fe', marginBottom: '12px', fontWeight: 800 }}>🛠️ Step-by-Step DIY Repair Instructions:</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
              {activeSolution.diy_fix_steps?.map((step, sIdx) => (
                <div key={sIdx} style={{ background: '#161e38', padding: '12px 16px', borderRadius: '10px', borderLeft: '4px solid #00f2fe', color: '#cbd5e1', fontSize: '14px' }}>
                  <strong style={{ color: '#00f2fe' }}>Step {sIdx + 1}:</strong> {step}
                </div>
              ))}
            </div>

            {/* Recommended Parts List */}
            {activeSolution.parts_needed?.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ fontSize: '14px', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', fontWeight: 700 }}>Recommended Replacement Parts:</h4>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {activeSolution.parts_needed.map((part, pIdx) => (
                    <span key={pIdx} style={{ background: '#1e293b', color: '#38bdf8', padding: '6px 12px', borderRadius: '8px', fontSize: '12px', fontWeight: 700, border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                      🔧 {part}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
              <button onClick={() => alert('Mechanic service booking request sent!')} style={{ flex: 1, background: 'linear-gradient(135deg, #43e97b, #38f9d7)', color: '#0f172a', border: 'none', padding: '14px', borderRadius: '12px', fontWeight: 900, cursor: 'pointer', fontSize: '15px' }}>
                👨‍🔧 Book Local Certified Mechanic Service
              </button>
            </div>
          </div>
        </div>
      )}

      {/* --- Section 5: Printable Mechanic Report Modal --- */}
      {showReportModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
          <div style={{ background: '#070913', width: '100%', maxWidth: '850px', maxHeight: '90vh', borderRadius: '20px', overflowY: 'auto', border: '1px solid rgba(0, 242, 254, 0.4)', padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '20px', color: '#00f2fe', fontWeight: 800 }}>Mechanic Diagnostic Summary for {activeProfile.driver_name}</h2>
              <button onClick={() => setShowReportModal(false)} style={{ background: '#ff0844', color: '#fff', border: 'none', padding: '6px 14px', borderRadius: '8px', cursor: 'pointer', fontWeight: 800 }}>Close</button>
            </div>
            <div dangerouslySetInnerHTML={{ __html: reportHtml }} />
          </div>
        </div>
      )}
    </div>
  );
}
