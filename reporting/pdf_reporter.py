"""
📄 PDF REPORTER - Report professionali in PDF per Value Stock Finder
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF
import matplotlib.pyplot as plt
import io
import pandas as pd

class PDFReporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        
    def generate_report(self, screening_results, backtest_results):
        """Genera report PDF professionale"""
        print("📄 Creazione report PDF...")
        
        # Crea nome file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = os.path.join(self.output_dir, f"value_report_{timestamp}.pdf")
        
        # Crea documento
        doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=50)
        story = []
        
        # Aggiungi contenuto
        story.extend(self._create_header())
        story.extend(self._create_executive_summary(screening_results, backtest_results))
        story.extend(self._create_top_opportunities(screening_results))
        story.extend(self._create_performance_analysis(backtest_results))
        story.extend(self._create_risk_analysis(screening_results))
        story.extend(self._create_recommendations(screening_results))
        
        # Costruisci PDF
        doc.build(story)
        return filename
    
    def _create_header(self):
        """Crea intestazione del report"""
        elements = []
        
        # Titolo
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=1  # Centered
        )
        
        elements.append(Paragraph("🎯 VALUE STOCK FINDER - ANALYTICAL REPORT", title_style))
        
        # Data
        date_style = ParagraphStyle(
            'CustomDate',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.gray,
            alignment=1
        )
        elements.append(Paragraph(f"Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}", date_style))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_executive_summary(self, screening_results, backtest_results):
        """Crea summary esecutivo"""
        elements = []
        
        # Calcola metriche
        opportunita_qualita = [r for r in screening_results if r.get('sconto', 0) > 5.0 and r.get('qualita_ok', False)]
        azioni_battute = len([r for r in backtest_results if r.get('battuto_sp500', False)]) if backtest_results else 0
        avg_discount = sum([r.get('sconto', 0) for r in opportunita_qualita]) / len(opportunita_qualita) if opportunita_qualita else 0
        
        elements.append(Paragraph("📊 EXECUTIVE SUMMARY", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        summary_data = [
            ["Metrica", "Valore", "Interpretazione"],
            ["Opportunità di Qualità", f"{len(opportunita_qualita)}", "Azioni con sconto >5% e qualità OK"],
            ["Sconto Medio", f"{avg_discount:.1f}%", "Margine di sicurezza medio"],
            ["Azioni vs S&P500", f"{azioni_battute}", "Performance superiore al benchmark"],
            ["Miglior Score", f"{max([r.get('investment_score', 0) for r in opportunita_qualita]) if opportunita_qualita else 0}/100", "Punteggio investimento massimo"]
        ]
        
        table = Table(summary_data, colWidths=[200, 80, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_top_opportunities(self, screening_results):
        """Crea tabella migliori opportunità"""
        elements = []
        
        opportunita_qualita = [r for r in screening_results if r.get('sconto', 0) > 5.0 and r.get('qualita_ok', False)]
        
        if not opportunita_qualita:
            elements.append(Paragraph("🎯 TOP VALUE OPPORTUNITIES", self.styles['Heading2']))
            elements.append(Paragraph("Nessuna opportunità di qualità trovata.", self.styles['Normal']))
            return elements
        
        # Ordina per punteggio
        top_10 = sorted(opportunita_qualita, key=lambda x: x.get('investment_score', 0), reverse=True)[:10]
        
        elements.append(Paragraph("🎯 TOP VALUE OPPORTUNITIES", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Header tabella
        table_data = [['Ticker', 'Company', 'Sector', 'Price', 'Discount', 'Score', 'Risk']]
        
        for opp in top_10:
            table_data.append([
                opp['ticker'],
                opp.get('nome', '')[:15] + '...',
                opp.get('settore', '')[:12],
                f"${opp.get('prezzo', 0):.2f}",
                f"{opp.get('sconto', 0):.1f}%",
                f"{opp.get('investment_score', 0):.0f}",
                opp.get('rischio', '')
            ])
        
        table = Table(table_data, colWidths=[60, 80, 70, 60, 60, 50, 50])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_performance_analysis(self, backtest_results):
        """Crea analisi performance"""
        elements = []
        
        if not backtest_results or len(backtest_results) <= 1:
            return elements
        
        elements.append(Paragraph("📈 PERFORMANCE ANALYSIS", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Filtra solo azioni (escludi S&P500)
        stocks_data = [r for r in backtest_results if r['ticker'] != 'S&P500']
        
        if not stocks_data:
            return elements
        
        # Tabella performance
        perf_data = [['Ticker', 'Return %', 'Alpha %', 'Volatility', 'Beat S&P500']]
        
        for stock in stocks_data[:8]:  # Prime 8 per spazio
            perf_data.append([
                stock['ticker'],
                f"{stock.get('rendimento_totale_perc', 0):.1f}",
                f"{stock.get('alpha_perc', 0):.1f}",
                f"{stock.get('volatilita_annualizzata', 0):.1f}",
                "✅" if stock.get('battuto_sp500', False) else "❌"
            ])
        
        table = Table(perf_data, colWidths=[60, 60, 60, 70, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_risk_analysis(self, screening_results):
        """Crea analisi rischio"""
        elements = []
        
        if not screening_results:
            return elements
        
        elements.append(Paragraph("⚖️ RISK ANALYSIS", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Distribuzione rischio
        risk_counts = {}
        for stock in screening_results:
            risk = stock.get('rischio', 'Sconosciuto')
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        risk_data = [['Risk Level', 'Count', 'Percentage']]
        total = len(screening_results)
        
        for risk, count in risk_counts.items():
            percentage = (count / total) * 100
            risk_data.append([risk, str(count), f"{percentage:.1f}%"])
        
        table = Table(risk_data, colWidths=[80, 60, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_recommendations(self, screening_results):
        """Crea raccomandazioni finali"""
        elements = []
        
        opportunita_qualita = [r for r in screening_results if r.get('sconto', 0) > 5.0 and r.get('qualita_ok', False)]
        
        if not opportunita_qualita:
            return elements
        
        elements.append(Paragraph("💡 INVESTMENT RECOMMENDATIONS", self.styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        # Top 3 raccomandazioni
        top_3 = sorted(opportunita_qualita, key=lambda x: x.get('investment_score', 0), reverse=True)[:3]
        
        for i, stock in enumerate(top_3, 1):
            rec_text = f"""
            <b>{i}. {stock['ticker']} - {stock.get('nome', '')[:25]}</b><br/>
            <b>Score:</b> {stock.get('investment_score', 0):.0f}/100 | 
            <b>Discount:</b> {stock.get('sconto', 0):.1f}% | 
            <b>Risk:</b> {stock.get('rischio', '')}<br/>
            <b>Sector:</b> {stock.get('settore', '')} | 
            <b>Quality:</b> {stock.get('quality_score_detailed', 0)}/10
            """
            
            elements.append(Paragraph(rec_text, self.styles['Normal']))
            elements.append(Spacer(1, 8))
        
        # Riepilogo finale
        summary_text = f"""
        <b>📋 Summary:</b> Trovate {len(opportunita_qualita)} opportunità di investimento di qualità.<br/>
        <b>🎯 Focus:</b> Considera le prime 3-5 azioni con score superiore a 80 per diversificazione.
        """
        
        elements.append(Paragraph(summary_text, self.styles['Normal']))
        
        return elements
