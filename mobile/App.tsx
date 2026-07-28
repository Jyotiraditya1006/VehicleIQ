import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  ScrollView,
  SafeAreaView,
  StatusBar,
  Alert,
} from 'react-native';

// Target FastAPI Backend Endpoint
const API_URL = 'http://localhost:8000';

interface HealthScores {
  overall: number;
  brake: number;
  engine: number;
  battery: number;
  drivingStyle: string;
}

export default function App() {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [rpm, setRpm] = useState<number>(850);
  const [speed, setSpeed] = useState<number>(0);
  const [temp, setTemp] = useState<number>(88);
  const [voltage, setVoltage] = useState<number>(14.1);
  const [health, setHealth] = useState<HealthScores>({
    overall: 95,
    brake: 96,
    engine: 94,
    battery: 95,
    drivingStyle: 'GENTLE',
  });

  // Simulated Bluetooth OBD-II data streaming & backend sync loop
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isConnected) {
      interval = setInterval(() => {
        // Generate continuous OBD telemetry
        const newRpm = Math.floor(1500 + Math.random() * 1200);
        const newSpeed = Math.floor(30 + Math.random() * 45);
        const newTemp = Math.floor(88 + Math.random() * 6);
        const newVolt = Number((13.8 + Math.random() * 0.5).toFixed(1));

        setRpm(newRpm);
        setSpeed(newSpeed);
        setTemp(newTemp);
        setVoltage(newVolt);

        // Sync live sample frame to backend API
        syncToBackend({
          vehicle_id: 'MOBILE_APP_VEH',
          rpm: newRpm,
          speed_kph: newSpeed,
          coolant_temp_c: newTemp,
          battery_voltage: newVolt,
          throttle_pos_pct: 22.0,
          short_fuel_trim_pct: 0.5,
          long_fuel_trim_pct: 1.0,
          maf_g_s: 12.0,
          scenario: 'mobile_live',
        });
      }, 2000);
    }
    return () => clearInterval(interval);
  }, [isConnected]);

  // Sync to FastAPI Backend
  const syncToBackend = async (sample: any) => {
    try {
      await fetch(`${API_URL}/api/v1/ingest`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ samples: [sample] }),
      });
    } catch (e) {
      // Background sync silent handle
    }
  };

  // Toggle Bluetooth Dongle Connection
  const handleToggleBluetooth = () => {
    if (isConnected) {
      setIsConnected(false);
      Alert.alert('Disconnected', 'Disconnected from ELM327 Bluetooth OBD-II Dongle.');
    } else {
      setIsScanning(true);
      setTimeout(() => {
        setIsScanning(false);
        setIsConnected(true);
        Alert.alert('Connected!', 'Successfully paired with ELM327 Bluetooth (COM3).');
      }, 1500);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        
        {/* Header Branding */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>⚡ VehicleIQ Mobile</Text>
            <Text style={styles.subtitle}>OBD-II Bluetooth Telemetry & AI Health</Text>
          </View>
          <TouchableOpacity
            style={[styles.bluetoothBtn, isConnected ? styles.connectedBtn : styles.disconnectedBtn]}
            onPress={handleToggleBluetooth}
          >
            <Text style={styles.btnText}>
              {isScanning ? 'Scanning...' : isConnected ? '🟢 Connected' : '🔵 Connect Dongle'}
            </Text>
          </TouchableOpacity>
        </View>

        {/* Live Gauges Grid */}
        <Text style={styles.sectionTitle}>Live Sensor Telemetry</Text>
        <View style={styles.gaugeGrid}>
          <View style={styles.gaugeCard}>
            <Text style={styles.gaugeLabel}>ENGINE RPM</Text>
            <Text style={[styles.gaugeVal, { color: rpm > 3500 ? '#ef4444' : '#38bdf8' }]}>{rpm}</Text>
            <Text style={styles.gaugeUnit}>RPM</Text>
          </View>

          <View style={styles.gaugeCard}>
            <Text style={styles.gaugeLabel}>SPEED</Text>
            <Text style={[styles.gaugeVal, { color: '#10b981' }]}>{speed}</Text>
            <Text style={styles.gaugeUnit}>KM/H</Text>
          </View>

          <View style={styles.gaugeCard}>
            <Text style={styles.gaugeLabel}>COOLANT TEMP</Text>
            <Text style={[styles.gaugeVal, { color: temp > 100 ? '#ef4444' : '#f59e0b' }]}>{temp}°C</Text>
            <Text style={styles.gaugeUnit}>Celsius</Text>
          </View>

          <View style={styles.gaugeCard}>
            <Text style={styles.gaugeLabel}>BATTERY</Text>
            <Text style={[styles.gaugeVal, { color: '#818cf8' }]}>{voltage}</Text>
            <Text style={styles.gaugeUnit}>Volts</Text>
          </View>
        </View>

        {/* AI Predictive Component Health */}
        <Text style={styles.sectionTitle}>AI Component Degradation</Text>
        <View style={styles.healthCard}>
          <View style={styles.healthRow}>
            <Text style={styles.healthLabel}>Brake Pad Lifespan</Text>
            <Text style={styles.healthVal}>{health.brake}%</Text>
          </View>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${health.brake}%`, backgroundColor: '#10b981' }]} />
          </View>

          <View style={[styles.healthRow, { marginTop: 14 }]}>
            <Text style={styles.healthLabel}>Engine Stress Score</Text>
            <Text style={styles.healthVal}>{health.engine}%</Text>
          </View>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${health.engine}%`, backgroundColor: '#38bdf8' }]} />
          </View>

          <View style={[styles.healthRow, { marginTop: 14 }]}>
            <Text style={styles.healthLabel}>Battery & Charging</Text>
            <Text style={styles.healthVal}>{health.battery}%</Text>
          </View>
          <View style={styles.progressBarBg}>
            <View style={[styles.progressBarFill, { width: `${health.battery}%`, backgroundColor: '#818cf8' }]} />
          </View>
        </View>

        {/* Plain-Language Push Alert Preview */}
        <Text style={styles.sectionTitle}>Plain-Language Vehicle Alert</Text>
        <View style={styles.alertCard}>
          <View style={styles.alertHeader}>
            <Text style={styles.alertTitle}>Nominal System Operation</Text>
            <Text style={styles.badgeInfo}>INFO</Text>
          </View>
          <Text style={styles.alertBody}>
            Vehicle sensors operating within safe parameters. Driving behavior classified as GENTLE.
          </Text>
          <Text style={styles.alertRec}>💡 Recommendation: Maintain regular oil check interval.</Text>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f172a',
  },
  scrollContent: {
    padding: 20,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#38bdf8',
  },
  subtitle: {
    fontSize: 12,
    color: '#94a3b8',
    marginTop: 2,
  },
  bluetoothBtn: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
  },
  connectedBtn: {
    backgroundColor: '#064e3b',
    borderWidth: 1,
    borderColor: '#10b981',
  },
  disconnectedBtn: {
    backgroundColor: '#1e293b',
    borderWidth: 1,
    borderColor: '#334155',
  },
  btnText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#e2e8f0',
    marginBottom: 12,
  },
  gaugeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  gaugeCard: {
    backgroundColor: '#1e293b',
    width: '48%',
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#334155',
  },
  gaugeLabel: {
    fontSize: 11,
    color: '#94a3b8',
    fontWeight: '600',
  },
  gaugeVal: {
    fontSize: 26,
    fontWeight: 'bold',
    marginVertical: 4,
  },
  gaugeUnit: {
    fontSize: 10,
    color: '#64748b',
  },
  healthCard: {
    backgroundColor: '#1e293b',
    padding: 18,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#334155',
    marginBottom: 24,
  },
  healthRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  healthLabel: {
    color: '#cbd5e1',
    fontSize: 13,
    fontWeight: '500',
  },
  healthVal: {
    color: '#38bdf8',
    fontWeight: 'bold',
    fontSize: 14,
  },
  progressBarBg: {
    height: 8,
    backgroundColor: '#0f172a',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
  },
  alertCard: {
    backgroundColor: '#1e293b',
    padding: 16,
    borderRadius: 12,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
    borderColor: '#334155',
    borderWidth: 1,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 6,
  },
  alertTitle: {
    color: '#f8fafc',
    fontWeight: 'bold',
    fontSize: 15,
  },
  badgeInfo: {
    backgroundColor: '#3b82f6',
    color: '#fff',
    fontSize: 10,
    fontWeight: 'bold',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  alertBody: {
    color: '#94a3b8',
    fontSize: 13,
    marginBottom: 6,
  },
  alertRec: {
    color: '#38bdf8',
    fontSize: 12,
    fontWeight: '500',
  },
});
