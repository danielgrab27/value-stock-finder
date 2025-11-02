"""
📊 REPORTING MODULE - Value Stock Finder
Genera report professionali PDF e HTML
"""

import os
import sys
from datetime import datetime

class ReportGenerator:
    def __init__(self, output_dir="outputs/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_comprehensive_report(self, screening_results, backtest_results):
        """Genera report completo screening + backtesting"""
        print("📊 Generazione report professionali...")
        
        # HTML Dashboard
        from .html_reporter import HTMLReporter
        html_reporter = HTMLReporter(self.output_dir)
        html_path = html_reporter.generate_dashboard(screening_results, backtest_results)
        
        # PDF Report
        from .pdf_reporter import PDFReporter
        pdf_reporter = PDFReporter(self.output_dir)
        pdf_path = pdf_reporter.generate_report(screening_results, backtest_results)
        
        print(f"✅ Report generati:")
        print(f"   📈 Dashboard: {html_path}")
        print(f"   📄 PDF: {pdf_path}")
        
        return {
            'html_dashboard': html_path,
            'pdf_report': pdf_path
        }

# Esporta le classi principali
__all__ = ['ReportGenerator']
