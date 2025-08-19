#!/usr/bin/env python3
"""
LightRAG Analytics Report Generator
Generates comprehensive reports and exports for LightRAG analytics data
"""

import os
import sys
import json
import csv
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import pandas as pd
from core_knowledge import LightRAGManager

class AnalyticsReportGenerator:
    """Generate detailed analytics reports for LightRAG systems"""
    
    def __init__(self, base_dir="lightrag_working_dir"):
        self.manager = LightRAGManager(base_dir)
        self.report_dir = os.path.join(base_dir, "_reports")
        os.makedirs(self.report_dir, exist_ok=True)
    
    def generate_comprehensive_report(self, format_type="json", include_charts=True):
        """Generate a comprehensive analytics report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print("🚀 Generating comprehensive LightRAG analytics report...")
        
        # Gather all analytics data
        analytics = self.manager.get_comprehensive_analytics()
        system_metrics = self.manager.get_system_performance_metrics()
        
        # Add detailed bucket analysis
        bucket_analysis = {}
        for bucket_name in self.manager.bucket_metadata:
            bucket_analysis[bucket_name] = {
                **self.manager.get_knowledge_graph_stats(bucket_name),
                **self.manager.get_bucket_performance_stats(bucket_name),
                "trends": self.manager.get_bucket_usage_trends(bucket_name, 30)
            }
        
        report_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_version": "1.0",
                "system": system_metrics,
                "report_period": "All time"
            },
            "overview": analytics["overview"],
            "performance_summary": analytics["performance_summary"],
            "recent_activity": analytics["recent_activity"],
            "bucket_analysis": bucket_analysis,
            "system_health": analytics["system_health"],
            "recommendations": self._generate_recommendations(analytics, bucket_analysis)
        }
        
        # Export in requested format
        if format_type == "json":
            filename = f"lightrag_comprehensive_report_{timestamp}.json"
            filepath = os.path.join(self.report_dir, filename)
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
            
            print(f"✅ JSON report saved: {filepath}")
        
        elif format_type == "csv":
            filename = f"lightrag_comprehensive_report_{timestamp}.csv"
            filepath = os.path.join(self.report_dir, filename)
            
            self._export_to_csv(report_data, filepath)
            print(f"✅ CSV report saved: {filepath}")
        
        elif format_type == "html":
            filename = f"lightrag_comprehensive_report_{timestamp}.html"
            filepath = os.path.join(self.report_dir, filename)
            
            self._export_to_html(report_data, filepath)
            print(f"✅ HTML report saved: {filepath}")
        
        # Generate charts if requested
        if include_charts:
            chart_dir = os.path.join(self.report_dir, f"charts_{timestamp}")
            os.makedirs(chart_dir, exist_ok=True)
            self._generate_charts(report_data, chart_dir)
            print(f"📊 Charts saved in: {chart_dir}")
        
        return filepath
    
    def generate_bucket_comparison_report(self, bucket_names: List[str]):
        """Generate a detailed comparison report for specific buckets"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"📊 Generating bucket comparison report for: {', '.join(bucket_names)}")
        
        comparison_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "buckets_compared": bucket_names,
                "comparison_type": "detailed"
            },
            "buckets": {},
            "comparison_metrics": {},
            "recommendations": {}
        }
        
        # Gather data for each bucket
        for bucket_name in bucket_names:
            if bucket_name in self.manager.bucket_metadata:
                comparison_data["buckets"][bucket_name] = {
                    **self.manager.get_knowledge_graph_stats(bucket_name),
                    **self.manager.get_bucket_performance_stats(bucket_name),
                    "trends": self.manager.get_bucket_usage_trends(bucket_name, 30)
                }
        
        # Calculate comparison metrics
        comparison_data["comparison_metrics"] = self._calculate_comparison_metrics(comparison_data["buckets"])
        comparison_data["recommendations"] = self._generate_bucket_recommendations(comparison_data["buckets"])
        
        # Export comparison report
        filename = f"bucket_comparison_{'-'.join(bucket_names)}_{timestamp}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(comparison_data, f, indent=2, default=str)
        
        print(f"✅ Bucket comparison report saved: {filepath}")
        return filepath
    
    def generate_performance_timeline(self, days=30):
        """Generate a performance timeline report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"⏱️ Generating performance timeline for last {days} days...")
        
        timeline_data = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "timeline_period_days": days,
                "report_type": "performance_timeline"
            },
            "daily_metrics": [],
            "trends": {},
            "performance_insights": {}
        }
        
        # Gather timeline data (would be populated from actual performance logs)
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # For each bucket, get usage trends
        bucket_trends = {}
        for bucket_name in self.manager.bucket_metadata:
            bucket_trends[bucket_name] = self.manager.get_bucket_usage_trends(bucket_name, days)
        
        timeline_data["bucket_trends"] = bucket_trends
        timeline_data["performance_insights"] = self._analyze_performance_trends(bucket_trends)
        
        # Export timeline report
        filename = f"performance_timeline_{days}d_{timestamp}.json"
        filepath = os.path.join(self.report_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(timeline_data, f, indent=2, default=str)
        
        print(f"✅ Performance timeline saved: {filepath}")
        return filepath
    
    def _export_to_csv(self, report_data: Dict, filepath: str):
        """Export report data to CSV format"""
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write overview section
            writer.writerow(["=== OVERVIEW ==="])
            writer.writerow(["Metric", "Value"])
            for key, value in report_data["overview"].items():
                writer.writerow([key.replace("_", " ").title(), value])
            
            writer.writerow([])  # Empty row
            
            # Write bucket analysis
            writer.writerow(["=== BUCKET ANALYSIS ==="])
            writer.writerow(["Bucket", "Entities", "Relationships", "Documents", "Queries", "Avg Response Time", "Storage (MB)"])
            
            for bucket_name, bucket_data in report_data["bucket_analysis"].items():
                performance = bucket_data.get("performance", {})
                writer.writerow([
                    bucket_name,
                    bucket_data.get("entities", 0),
                    bucket_data.get("relationships", 0),
                    bucket_data.get("documents", 0),
                    performance.get("total_queries", 0),
                    performance.get("avg_query_time", 0),
                    performance.get("storage_size_mb", 0)
                ])
    
    def _export_to_html(self, report_data: Dict, filepath: str):
        """Export report data to HTML format"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>LightRAG Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; }}
                .section {{ margin: 20px 0; }}
                .metric-card {{ background: #e3f2fd; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .recommendation {{ background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🚀 LightRAG Analytics Report</h1>
                <p>Generated: {report_data["report_metadata"]["generated_at"]}</p>
            </div>
            
            <div class="section">
                <h2>📊 Overview</h2>
                <div class="metric-card">
                    <strong>Total Buckets:</strong> {report_data["overview"]["total_buckets"]}<br>
                    <strong>Active Buckets:</strong> {report_data["overview"]["active_buckets"]}<br>
                    <strong>Total Entities:</strong> {report_data["overview"]["total_entities"]}<br>
                    <strong>Total Relationships:</strong> {report_data["overview"]["total_relationships"]}<br>
                    <strong>Total Queries:</strong> {report_data["overview"]["total_queries"]}
                </div>
            </div>
            
            <div class="section">
                <h2>🏆 Performance Summary</h2>
                <div class="metric-card">
                    <strong>Average Query Time:</strong> {report_data["performance_summary"]["avg_query_time"]}s<br>
                    <strong>Most Used Bucket:</strong> {report_data["performance_summary"]["most_used_bucket"] or "N/A"}<br>
                    <strong>Most Used Query Mode:</strong> {report_data["performance_summary"]["most_used_query_mode"] or "N/A"}
                </div>
            </div>
            
            <div class="section">
                <h2>📈 Bucket Analysis</h2>
                <table>
                    <tr>
                        <th>Bucket</th>
                        <th>Entities</th>
                        <th>Relationships</th>
                        <th>Documents</th>
                        <th>Storage (MB)</th>
                    </tr>
        """
        
        for bucket_name, bucket_data in report_data["bucket_analysis"].items():
            performance = bucket_data.get("performance", {})
            html_content += f"""
                    <tr>
                        <td>{bucket_name}</td>
                        <td>{bucket_data.get("entities", 0)}</td>
                        <td>{bucket_data.get("relationships", 0)}</td>
                        <td>{bucket_data.get("documents", 0)}</td>
                        <td>{performance.get("storage_size_mb", 0)}</td>
                    </tr>
            """
        
        html_content += """
                </table>
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
        """
        
        for recommendation in report_data["recommendations"]:
            html_content += f'<div class="recommendation">{recommendation}</div>'
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(filepath, 'w') as f:
            f.write(html_content)
    
    def _generate_charts(self, report_data: Dict, chart_dir: str):
        """Generate visualization charts"""
        try:
            # Bucket entities distribution
            bucket_names = list(report_data["bucket_analysis"].keys())
            entity_counts = [report_data["bucket_analysis"][bucket].get("entities", 0) for bucket in bucket_names]
            
            plt.figure(figsize=(10, 6))
            plt.bar(bucket_names, entity_counts)
            plt.title("Entities Distribution by Bucket")
            plt.xlabel("Buckets")
            plt.ylabel("Number of Entities")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(chart_dir, "entities_distribution.png"))
            plt.close()
            
            # Storage usage pie chart
            storage_data = [report_data["bucket_analysis"][bucket].get("performance", {}).get("storage_size_mb", 0) 
                           for bucket in bucket_names]
            
            if sum(storage_data) > 0:
                plt.figure(figsize=(8, 8))
                plt.pie(storage_data, labels=bucket_names, autopct='%1.1f%%')
                plt.title("Storage Usage Distribution")
                plt.savefig(os.path.join(chart_dir, "storage_distribution.png"))
                plt.close()
            
            print(f"📊 Generated visualization charts")
            
        except Exception as e:
            print(f"⚠️ Could not generate charts: {e}")
    
    def _generate_recommendations(self, analytics: Dict, bucket_analysis: Dict) -> List[str]:
        """Generate actionable recommendations based on analytics"""
        recommendations = []
        
        # Performance recommendations
        if analytics["performance_summary"]["avg_query_time"] > 2.0:
            recommendations.append("⚡ Consider optimizing query performance - average response time is above 2 seconds")
        
        # Storage recommendations
        total_storage = sum(bucket_data.get("performance", {}).get("storage_size_mb", 0) 
                           for bucket_data in bucket_analysis.values())
        if total_storage > 1000:  # 1GB
            recommendations.append("💾 Monitor storage usage - total size exceeds 1GB")
        
        # Usage recommendations
        empty_buckets = [name for name, data in bucket_analysis.items() if data.get("entities", 0) == 0]
        if empty_buckets:
            recommendations.append(f"📦 Consider populating empty buckets: {', '.join(empty_buckets)}")
        
        # Query distribution recommendations
        if analytics["overview"]["total_queries"] < 10:
            recommendations.append("🔍 System appears underutilized - consider increasing query activity")
        
        return recommendations
    
    def _calculate_comparison_metrics(self, buckets: Dict) -> Dict:
        """Calculate comparison metrics between buckets"""
        if not buckets:
            return {}
        
        metrics = {}
        
        # Calculate ratios and efficiency metrics
        for bucket_name, bucket_data in buckets.items():
            entities = bucket_data.get("entities", 0)
            relationships = bucket_data.get("relationships", 0)
            
            # Entity-to-relationship ratio
            if entities > 0:
                metrics[bucket_name] = {
                    "entity_relationship_ratio": round(relationships / entities, 2) if entities > 0 else 0,
                    "density_score": round((entities + relationships) / max(bucket_data.get("documents", 1), 1), 2)
                }
        
        return metrics
    
    def _generate_bucket_recommendations(self, buckets: Dict) -> Dict:
        """Generate specific recommendations for each bucket"""
        recommendations = {}
        
        for bucket_name, bucket_data in buckets.items():
            bucket_recs = []
            
            entities = bucket_data.get("entities", 0)
            relationships = bucket_data.get("relationships", 0)
            documents = bucket_data.get("documents", 0)
            
            if entities == 0:
                bucket_recs.append("Add documents to build knowledge graph")
            elif entities < 50:
                bucket_recs.append("Consider adding more content for richer knowledge graph")
            
            if relationships > 0 and entities > 0:
                ratio = relationships / entities
                if ratio < 0.5:
                    bucket_recs.append("Low relationship density - consider documents with more interconnected concepts")
            
            performance = bucket_data.get("performance", {})
            if performance.get("total_queries", 0) == 0:
                bucket_recs.append("Bucket has not been queried - consider testing with sample queries")
            
            recommendations[bucket_name] = bucket_recs
        
        return recommendations
    
    def _analyze_performance_trends(self, bucket_trends: Dict) -> Dict:
        """Analyze performance trends across buckets"""
        insights = {
            "most_active_bucket": None,
            "trending_up": [],
            "trending_down": [],
            "steady_usage": []
        }
        
        total_activity = {}
        for bucket_name, trends in bucket_trends.items():
            total_activity[bucket_name] = trends.get("total_activity", 0)
        
        if total_activity:
            insights["most_active_bucket"] = max(total_activity, key=total_activity.get)
        
        return insights


def main():
    parser = argparse.ArgumentParser(description="Generate LightRAG Analytics Reports")
    parser.add_argument("--format", choices=["json", "csv", "html"], default="json",
                       help="Report format (default: json)")
    parser.add_argument("--compare", nargs="+", help="Bucket names to compare")
    parser.add_argument("--timeline", type=int, default=30, help="Days for timeline report")
    parser.add_argument("--charts", action="store_true", help="Generate visualization charts")
    parser.add_argument("--base-dir", default="lightrag_working_dir", help="LightRAG base directory")
    
    args = parser.parse_args()
    
    generator = AnalyticsReportGenerator(args.base_dir)
    
    if args.compare:
        print(f"🔍 Generating comparison report for buckets: {args.compare}")
        filepath = generator.generate_bucket_comparison_report(args.compare)
    elif args.timeline:
        print(f"⏱️ Generating timeline report for {args.timeline} days")
        filepath = generator.generate_performance_timeline(args.timeline)
    else:
        print(f"📊 Generating comprehensive report in {args.format} format")
        filepath = generator.generate_comprehensive_report(args.format, args.charts)
    
    print(f"\n✅ Report generated successfully!")
    print(f"📄 Location: {filepath}")
    
    # Show file size
    try:
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"📏 Size: {size_mb:.2f} MB")
    except:
        pass


if __name__ == "__main__":
    main()