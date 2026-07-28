import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'VehicleIQ — Real-Time Vehicle Health & Failure Prediction',
  description: 'AI-powered vehicle health prediction system learning from OBD-II sensor data.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
