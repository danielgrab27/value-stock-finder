"""
🎨 HTML REPORTER - Dashboard interattiva per Value Stock Finder
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo

class HTMLReporter:
    def __init__(self, output_dir):
        self.output_dir = output_dir
    
    def generate_dashboard(self, screening_results, backtest_results):
        """Genera dashboard HTML interattiva"""
        print("🔄 Creazione dashboard HTML...")
        
        # Filtra opportunità di qualità
        opportunita_qualita = [r for r in screening_results 
                             if r.get('sconto', 0) > 5.0 and r.get('qualita_ok', False)]
        
        # Crea figura con subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '📈 Performance vs S&P500', 
                '🎯 Top Value Opportunities',
                '📊 Distribuzione Sconti',
                '⚖️ Risk vs Return Profile'
            ),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Grafico Performance vs S&P500
        if backtest_results and len(backtest_results) > 1:
            self._add_performance_chart(fig, backtest_results)
        
        # 2. Bar chart top opportunities
        self._add_opportunities_chart(fig, opportunita_qualita)
        
        # 3. Distribuzione sconti
        self._add_discount_distribution(fig, screening_results)
        
        # 4. Risk vs Return
        self._add_risk_return_chart(fig, backtest_results)
        
        # Aggiorna layout
        fig.update_layout(
            height=1000,
            title_text="🎯 Value Stock Finder - Analytical Dashboard",
            showlegend=True,
            template="plotly_white"
        )
        
        # Salva HTML
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        html_path = os.path.join(self.output_dir, f"dashboard_{timestamp}.html")
        
        # Aggiungi dati tabellari
        full_html = self._create_complete_html(fig, opportunita_qualita, backtest_results)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(full_html)
        
        return html_path
    
    def _add_performance_chart(self, fig, backtest_results):
        """Aggiunge grafico performance vs S&P500"""
        stocks_data = []
        for result in backtest_results[1:]:  # Salta S&P500
            if 'rendimento_totale_perc' in result:
                stocks_data.append({
                    'ticker': result['ticker'],
                    'performance': result['rendimento_totale_perc'],
                    'alpha': result.get('alpha_perc', 0),
                    'battuto_sp500': result.get('battuto_sp500', False)
                })
        
        if stocks_data:
            df = pd.DataFrame(stocks_data)
            colors = ['green' if x else 'red' for x in df['battuto_sp500']]
            
            fig.add_trace(
                go.Bar(
                    x=df['ticker'],
                    y=df['performance'],
                    marker_color=colors,
                    name='Performance vs S&P500',
                    hovertemplate='<b>%{x}</b><br>Performance: %{y:.1f}%<br>Alpha: %{customdata:.1f}%<extra></extra>',
                    customdata=df['alpha']
                ),
                row=1, col=1
            )
    
    def _add_opportunities_chart(self, fig, opportunita_qualita):
        """Aggiunge grafico top opportunities"""
        if opportunita_qualita:
            top_10 = sorted(opportunita_qualita, key=lambda x: x.get('investment_score', 0), reverse=True)[:10]
            
            tickers = [f"{opp['ticker']}<br>{opp['investment_score']}/100" for opp in top_10]
            discounts = [opp.get('sconto', 0) for opp in top_10]
            scores = [opp.get('investment_score', 0) for opp in top_10]
            
            fig.add_trace(
                go.Bar(
                    x=tickers,
                    y=discounts,
                    marker_color=scores,
                    marker_colorscale='Viridis',
                    name='Discount %',
                    hovertemplate='<b>%{x}</b><br>Sconto: %{y:.1f}%<br>Score: %{marker.color}/100<extra></extra>'
                ),
                row=1, col=2
            )
    
    def _add_discount_distribution(self, fig, screening_results):
        """Aggiunge distribuzione sconti"""
        if screening_results:
            discounts = [r.get('sconto', 0) for r in screening_results if r.get('sconto', 0) > 0]
            if discounts:
                fig.add_trace(
                    go.Histogram(
                        x=discounts,
                        nbinsx=20,
                        name='Distribuzione Sconti',
                        marker_color='lightblue'
                    ),
                    row=2, col=1
                )
    
    def _add_risk_return_chart(self, fig, backtest_results):
        """Aggiunge scatter plot risk vs return"""
        if backtest_results and len(backtest_results) > 1:
            risk_return_data = []
            for result in backtest_results[1:]:  # Salta S&P500
                if all(k in result for k in ['rendimento_totale_perc', 'volatilita_annualizzata']):
                    risk_return_data.append({
                        'ticker': result['ticker'],
                        'return': result['rendimento_totale_perc'],
                        'risk': result['volatilita_annualizzata'],
                        'battuto_sp500': result.get('battuto_sp500', False)
                    })
            
            if risk_return_data:
                df = pd.DataFrame(risk_return_data)
                colors = ['green' if x else 'red' for x in df['battuto_sp500']]
                sizes = [20 if x else 15 for x in df['battuto_sp500']]
                
                fig.add_trace(
                    go.Scatter(
                        x=df['risk'],
                        y=df['return'],
                        mode='markers+text',
                        marker=dict(color=colors, size=sizes),
                        text=df['ticker'],
                        textposition="top center",
                        name='Risk vs Return',
                        hovertemplate='<b>%{text}</b><br>Risk: %{x:.1f}%<br>Return: %{y:.1f}%<extra></extra>'
                    ),
                    row=2, col=2
                )
    
    def _create_complete_html(self, fig, opportunita_qualita, backtest_results):
        """Crea HTML completo con tabelle e grafici - VERSIONE CON ALERT"""
    
        # 🔥 NUOVO: RILEVA OPPORTUNITÀ ECCEZIONALI
        exceptional_count = 0
        trap_count = 0
    
        try:
           # Importa il sistema di alert
           sys.path.append('src')
           from alert_system import AlertSystem
        
           alert_system = AlertSystem()
           analysis_results = alert_system.analyze_opportunities(opportunita_qualita)
           exceptional_count = len(analysis_results['exceptional'])
           trap_count = len(analysis_results['high_risk_traps'])
        except Exception as e:
           print(f"⚠️  Sistema alert non disponibile: {e}")
           # Fallback: calcola manualmente
           for opp in opportunita_qualita:
               if opp.get('investment_score', 0) >= 90 and opp.get('sconto', 0) >= 25:
                   exceptional_count += 1
               elif (opp.get('sconto', 0) > 15 and 
                     not opp.get('qualita_ok', False) and 
                     opp.get('rischio', '') == 'Alto'):
                   trap_count += 1
        
        # Converti figura Plotly in HTML
        plotly_html = pyo.plot(fig, include_plotlyjs=True, output_type='div')
    
        # Crea tabella opportunità
        opportunities_table = self._create_opportunities_table(opportunita_qualita)
    
        # 🔥 NUOVO: SEZIONE ALERT
        alert_section = ""
        if exceptional_count > 0:
            alert_section = f"""
            <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                        color: white; padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h3>🚨 ATTENZIONE: {exceptional_count} OPPORTUNITÀ ECCEZIONALI TROVATE!</h3>
                <p>Rilevate azioni con score >90 e sconto >25%. Considera priorità di investimento.</p>
            </div>
            """
    
        if trap_count > 0:
            alert_section += f"""
            <div style="background: linear-gradient(135deg, #FF6B6B 0%, #EE5A24 100%); 
                        color: white; padding: 15px; border-radius: 10px; margin: 20px 0;">
                <h3>⚠️  ATTENZIONE: {trap_count} VALUE TRAPS PERICOLOSI IDENTIFICATI!</h3>
                <p>Azioni con alto sconto ma bassa qualità e alto rischio. Approccio con cautela.</p>
            </div>
            """
    
        # Crea HTML completo
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🎯 Value Stock Finder - Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                         color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .summary {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .table th, .table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .table th {{ background-color: #f2f2f2; }}
                .positive {{ color: green; font-weight: bold; }}
                .negative {{ color: red; font-weight: bold; }}
                .exceptional {{ background-color: #FFF9C4 !important; border-left: 4px solid #FFD700; }}
                .trap {{ background-color: #FFEBEE !important; border-left: 4px solid #FF5252; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Value Stock Finder - Analytical Dashboard</h1>
                <p>Generato il: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
        
            {alert_section}
        
            <div class="summary">
                <h3>📊 Executive Summary</h3>
                <p><strong>Opportunità di Qualità Trovate:</strong> {len(opportunita_qualita)}</p>
                <p><strong>Opportunità Eccezionali:</strong> <span class="positive">{exceptional_count}</span></p>
                <p><strong>Value Traps Pericolosi:</strong> <span class="negative">{trap_count}</span></p>
                <p><strong>Azioni che battono S&P500:</strong> {len([r for r in backtest_results if r.get('battuto_sp500', False)]) if backtest_results else 0}</p>
                <p><strong>Miglior Opportunità:</strong> {max([r.get('investment_score', 0) for r in opportunita_qualita]) if opportunita_qualita else 0}/100</p>
            </div>
        
            {plotly_html}
        
            <h3>🎯 Top Value Opportunities</h3>
            {opportunities_table}
        </body>
        </html>
        """
    
        return html_template
    
    def _create_opportunities_table(self, opportunita_qualita):
        """Crea tabella HTML delle migliori opportunità - VERSIONE CON ALERT"""
        if not opportunita_qualita:
            return "<p>Nessuna opportunità di qualità trovata.</p>"
    
        top_10 = sorted(opportunita_qualita, key=lambda x: x.get('investment_score', 0), reverse=True)[:10]
    
        table_html = """
        <table class="table">
            <thead>
                <tr>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Sector</th>
                    <th>Price</th>
                    <th>Discount</th>
                    <th>Score</th>
                    <th>Risk</th>
                    <th>Quality</th>
                    <th>Alert</th>
                </tr>
            </thead>
            <tbody>
        """
    
        for opp in top_10:
            risk_class = opp.get('rischio', '')
            risk_emoji = "🟢" if risk_class == "Basso" else "🟡" if risk_class == "Medio" else "🔴"
        
            # 🔥 NUOVO: DETERMINA TIPO DI ALERT
            alert_emoji = ""
            row_class = ""
        
            if opp.get('investment_score', 0) >= 90 and opp.get('sconto', 0) >= 25:
                alert_emoji = "🔥"
                row_class = "exceptional"
            elif (opp.get('sconto', 0) > 15 and 
                  not opp.get('qualita_ok', False) and 
                  risk_class == "Alto"):
                alert_emoji = "⚠️"
                row_class = "trap"
        
            table_html += f"""
                <tr class="{row_class}">
                    <td><strong>{opp['ticker']}</strong></td>
                    <td>{opp.get('nome', '')[:20]}...</td>
                    <td>{opp.get('settore', '')}</td>
                    <td>${opp.get('prezzo', 0):.2f}</td>
                    <td class="positive">{opp.get('sconto', 0):.1f}%</td>
                    <td><strong>{opp.get('investment_score', 0):.0f}/100</strong></td>
                    <td>{risk_emoji} {risk_class}</td>
                    <td>{opp.get('quality_score_detailed', 0)}/10</td>
                    <td>{alert_emoji}</td>
                </tr>
            """
    
        table_html += "</tbody></table>"
    
        # 🔥 NUOVO: LEGENDA ALERT
        table_html += """
        <div style="margin-top: 10px; font-size: 12px; color: #666;">
            <strong>Legenda Alert:</strong> 
            <span style="margin-right: 15px;">🔥 Opportunità Eccezionale (Score ≥90, Sconto ≥25%)</span> 
            <span>⚠️ Value Trap Potenziale (Sconto alto, Qualità bassa, Rischio alto)</span>
        </div>
        """
    
        return table_html
