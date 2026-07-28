"""
VehicleIQ Mechanic Diagnostic PDF Report Exporter
Fetches real-time ML diagnostic reports for any driver/vehicle and exports them as clean PDF files.
"""

import sys
import os
import argparse
from datetime import datetime

def export_mechanic_pdf(vehicle_id: str = "VEHICLE_001", output_pdf_name: str = None):
    """Fetches diagnostic report data and generates printable PDF document."""
    # Add root directory to sys.path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    if BASE_DIR not in sys.path:
        sys.path.insert(0, BASE_DIR)

    from backend.app.main import get_health_score
    from backend.app.pdf_generator import generate_mechanic_report_html

    print(f"Fetching ML health diagnosis for vehicle ID: {vehicle_id}...")
    health_data = get_health_score(vehicle_id=vehicle_id)

    html_content = generate_mechanic_report_html(
        vehicle_id=health_data.vehicle_id,
        overall_health=health_data.overall_health_score,
        driving_style=health_data.driving_style,
        driving_score=health_data.driving_behavior_score,
        component_scores=health_data.component_scores,
        alerts=[a.dict() for a in health_data.plain_language_alerts]
    )

    if not output_pdf_name:
        output_pdf_name = f"Mechanic_Report_{vehicle_id}.pdf"

    # Save HTML view
    html_path = f"Mechanic_Report_{vehicle_id}.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Convert HTML/Data to PDF using ReportLab
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors

        doc = SimpleDocTemplate(output_pdf_name, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle('ReportTitle', parent=styles['Heading1'], fontSize=20, leading=24, textColor=colors.HexColor('#0284c7'), alignment=1)
        story.append(Paragraph(f"VehicleIQ Diagnostic Report — {vehicle_id}", title_style))
        story.append(Spacer(1, 10))

        sub_style = ParagraphStyle('ReportSub', parent=styles['Normal'], fontSize=11, leading=14, textColor=colors.HexColor('#64748b'), alignment=1)
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | Driver Profile Mode", sub_style))
        story.append(Spacer(1, 16))

        # Metrics Table
        table_data = [
            ["Overall Health", "Brake Health", "Engine Health", "Battery Health", "Driving Style"],
            [
                f"{health_data.overall_health_score}%",
                f"{health_data.component_scores.get('brake_health', 100)}%",
                f"{health_data.component_scores.get('engine_health', 100)}%",
                f"{health_data.component_scores.get('battery_health', 100)}%",
                f"{health_data.driving_style.upper()} ({health_data.driving_behavior_score}/100)"
            ]
        ]
        t = Table(table_data, colWidths=[100, 95, 95, 95, 145])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#0f172a')),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))

        # Diagnostic Findings & Solutions
        story.append(Paragraph("Diagnostic Findings & Repair Solution Guides", styles['Heading2']))
        story.append(Spacer(1, 6))

        for alert in health_data.plain_language_alerts:
            sev_color = "#ef4444" if alert.severity == "CRITICAL" else "#f59e0b" if alert.severity == "WARNING" else "#0284c7"
            a_head = f"<b>[{alert.severity}] {alert.title}</b>"
            story.append(Paragraph(a_head, ParagraphStyle('AlertHead', parent=styles['Normal'], fontSize=12, leading=15, textColor=colors.HexColor(sev_color))))
            story.append(Spacer(1, 3))
            
            p_desc = f"<b>Finding:</b> {alert.explanation}<br/><b>Solution:</b> {alert.solution_title}<br/><b>Estimated Cost:</b> {alert.estimated_cost} | <b>Urgency:</b> {alert.urgency}"
            story.append(Paragraph(p_desc, styles['Normal']))
            story.append(Spacer(1, 10))

        doc.build(story)
        print(f"Successfully exported PDF mechanic report at: {os.path.abspath(output_pdf_name)}")
        print(f"HTML view saved at: {os.path.abspath(html_path)}")
    except Exception as e:
        print(f"PDF Export Notice: {e}. HTML report saved at {html_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--vehicle-id", default="VEHICLE_001", help="Vehicle ID to export")
    parser.add_argument("--out", default=None, help="Output PDF filename")
    args = parser.parse_args()
    export_mechanic_pdf(vehicle_id=args.vehicle_id, output_pdf_name=args.out)
