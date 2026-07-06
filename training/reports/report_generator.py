import os
import json
import pandas as pd
from typing import Dict, Any, List
from pathlib import Path

from training.utils.config_manager import ConfigurationManager
from training.utils.logger import get_logger

class ReportGenerator:
    """Generates evaluation reports in various formats."""
    
    def __init__(self, config: ConfigurationManager):
        self.config = config
        self.logger = get_logger(__name__)
        self.output_dir = Path(self.config.get("reporting.output_dir", "training/reports/"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.graphs_dir = Path(self.config.get("reporting.graphs_dir", "training/graphs/"))
        if self.config.get("reporting.include_graphs", False):
            self.graphs_dir.mkdir(parents=True, exist_ok=True)

    def generate_csv(self, metrics: Dict[str, Any], output_path: str) -> str:
        self.logger.info("generating_csv_report")
        # Filter out complex structures like confusion matrix for flat CSV
        flat_metrics = {k: v for k, v in metrics.items() if not isinstance(v, (list, dict))}
        df = pd.DataFrame([flat_metrics])
        df.to_csv(output_path, index=False)
        return output_path

    def generate_excel(self, metrics: Dict[str, Any], output_path: str) -> str:
        self.logger.info("generating_excel_report")
        flat_metrics = {k: v for k, v in metrics.items() if not isinstance(v, (list, dict))}
        df = pd.DataFrame([flat_metrics])
        df.to_excel(output_path, index=False)
        return output_path

    def generate_html(self, metrics: Dict[str, Any], model_name: str, output_path: str) -> str:
        self.logger.info("generating_html_report")
        html = f"""
        <html>
        <head><title>Report: {model_name}</title></head>
        <body style="font-family: sans-serif;">
            <h1>Evaluation Report: {model_name}</h1>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><th>Metric</th><th>Value</th></tr>
        """
        for k, v in metrics.items():
            if not isinstance(v, (list, dict)):
                html += f"<tr><td>{k}</td><td>{v:.4f}</td></tr>"
                
        html += """
            </table>
        </body>
        </html>
        """
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return output_path

    def generate_markdown(self, metrics: Dict[str, Any], model_name: str, output_path: str) -> str:
        self.logger.info("generating_markdown_report")
        md = f"# Evaluation Report: {model_name}\n\n"
        md += "| Metric | Value |\n|---|---|\n"
        for k, v in metrics.items():
            if not isinstance(v, (list, dict)):
                md += f"| {k} | {v:.4f} |\n"
                
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        return output_path

    def generate_graphs(self, metrics: Dict[str, Any], output_dir: str) -> List[str]:
        self.logger.info("generating_graphs")
        generated = []
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Example: Confusion Matrix Heatmap
            if "confusion_matrix" in metrics:
                plt.figure(figsize=(8, 6))
                cm = metrics["confusion_matrix"]
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
                plt.title("Confusion Matrix")
                plt.ylabel("True Label")
                plt.xlabel("Predicted Label")
                
                path = str(Path(output_dir) / "confusion_matrix.png")
                plt.savefig(path)
                plt.close()
                generated.append(path)
                
        except ImportError:
            self.logger.warning("matplotlib_or_seaborn_not_installed_skipping_graphs")
            
        return generated

    def generate_all(self, metrics: Dict[str, Any], model_name: str) -> Dict[str, str]:
        self.logger.info("generating_all_reports")
        formats = self.config.get("reporting.formats", ["csv", "markdown"])
        results = {}
        
        base_name = f"{model_name}_report"
        
        if "csv" in formats:
            results["csv"] = self.generate_csv(metrics, str(self.output_dir / f"{base_name}.csv"))
            
        if "excel" in formats:
            results["excel"] = self.generate_excel(metrics, str(self.output_dir / f"{base_name}.xlsx"))
            
        if "html" in formats:
            results["html"] = self.generate_html(metrics, model_name, str(self.output_dir / f"{base_name}.html"))
            
        if "markdown" in formats:
            results["markdown"] = self.generate_markdown(metrics, model_name, str(self.output_dir / f"{base_name}.md"))
            
        if self.config.get("reporting.include_graphs", False):
            results["graphs"] = self.generate_graphs(metrics, str(self.graphs_dir))
            
        return results
