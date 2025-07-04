"""
Advanced Analytics Engine for A2A System
Real-time performance analysis and intelligent insights
"""

import json
import statistics
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import math

class PerformanceAnalyzer:
    """Advanced performance analysis and trend detection"""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.performance_history = []
        self.anomaly_threshold = 2.0  # Standard deviations
        self.trend_window = 20  # Number of data points for trend analysis
        
    def analyze_performance_trends(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance trends and detect anomalies"""
        if len(metrics_history) < 5:
            return {"status": "insufficient_data", "message": "Need at least 5 data points"}
        
        analysis = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_time_analysis": self._analyze_response_times(metrics_history),
            "error_rate_analysis": self._analyze_error_rates(metrics_history),
            "throughput_analysis": self._analyze_throughput(metrics_history),
            "resource_utilization": self._analyze_resource_utilization(metrics_history),
            "anomaly_detection": self._detect_anomalies(metrics_history),
            "trend_predictions": self._predict_trends(metrics_history),
            "performance_score": 0,
            "recommendations": []
        }
        
        # Calculate overall performance score
        analysis["performance_score"] = self._calculate_performance_score(analysis)
        
        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _analyze_response_times(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze response time patterns"""
        response_times = []
        timestamps = []
        
        for metric in metrics_history:
            if metric.get("api_health", {}).get("response_time") is not None:
                response_times.append(metric["api_health"]["response_time"])
                timestamps.append(metric["timestamp"])
        
        if not response_times:
            return {"status": "no_data"}
        
        recent_times = response_times[-10:]  # Last 10 measurements
        historical_times = response_times[:-10] if len(response_times) > 10 else []
        
        analysis = {
            "current_avg": statistics.mean(recent_times),
            "current_median": statistics.median(recent_times),
            "current_p95": self._percentile(recent_times, 95),
            "current_max": max(recent_times),
            "current_min": min(recent_times),
            "trend": "stable"
        }
        
        if historical_times:
            historical_avg = statistics.mean(historical_times)
            improvement = ((historical_avg - analysis["current_avg"]) / historical_avg) * 100
            
            if improvement > 10:
                analysis["trend"] = "improving"
            elif improvement < -10:
                analysis["trend"] = "degrading"
            
            analysis["improvement_percentage"] = improvement
            analysis["historical_avg"] = historical_avg
        
        # Detect response time spikes
        if len(recent_times) > 3:
            recent_std = statistics.stdev(recent_times)
            analysis["volatility"] = recent_std
            analysis["stability_score"] = max(0, 100 - (recent_std / analysis["current_avg"]) * 100)
        
        return analysis
    
    def _analyze_error_rates(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze error rate patterns"""
        total_checks = len(metrics_history)
        error_count = sum(
            1 for metric in metrics_history
            if metric.get("api_health", {}).get("status") == "error"
        )
        
        recent_metrics = metrics_history[-10:]
        recent_errors = sum(
            1 for metric in recent_metrics
            if metric.get("api_health", {}).get("status") == "error"
        )
        
        analysis = {
            "overall_error_rate": (error_count / total_checks) * 100 if total_checks > 0 else 0,
            "recent_error_rate": (recent_errors / len(recent_metrics)) * 100 if recent_metrics else 0,
            "total_errors": error_count,
            "recent_errors": recent_errors,
            "error_trend": "stable"
        }
        
        # Determine error trend
        if len(metrics_history) > 20:
            early_metrics = metrics_history[:10]
            early_errors = sum(
                1 for metric in early_metrics
                if metric.get("api_health", {}).get("status") == "error"
            )
            early_error_rate = (early_errors / len(early_metrics)) * 100
            
            if analysis["recent_error_rate"] > early_error_rate + 5:
                analysis["error_trend"] = "increasing"
            elif analysis["recent_error_rate"] < early_error_rate - 5:
                analysis["error_trend"] = "decreasing"
        
        return analysis
    
    def _analyze_throughput(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze system throughput patterns"""
        task_counts = []
        time_intervals = []
        
        for i, metric in enumerate(metrics_history):
            task_count = metric.get("task_queue", {}).get("total_tasks", 0)
            if task_count is not None:
                task_counts.append(task_count)
                
                if i > 0:
                    prev_time = datetime.fromisoformat(metrics_history[i-1]["timestamp"])
                    curr_time = datetime.fromisoformat(metric["timestamp"])
                    interval = (curr_time - prev_time).total_seconds()
                    time_intervals.append(interval)
        
        if not task_counts:
            return {"status": "no_data"}
        
        # Calculate task processing rate
        if len(task_counts) > 1:
            task_changes = [
                task_counts[i] - task_counts[i-1]
                for i in range(1, len(task_counts))
            ]
            
            # Positive changes indicate new tasks, negative indicate processed tasks
            tasks_added = sum(change for change in task_changes if change > 0)
            tasks_processed = abs(sum(change for change in task_changes if change < 0))
            
            avg_interval = statistics.mean(time_intervals) if time_intervals else 60
            
            analysis = {
                "tasks_added": tasks_added,
                "tasks_processed": tasks_processed,
                "current_queue_size": task_counts[-1],
                "processing_rate": tasks_processed / (len(time_intervals) * avg_interval / 60) if time_intervals else 0,  # tasks per minute
                "queue_trend": "growing" if task_counts[-1] > task_counts[0] else "shrinking"
            }
        else:
            analysis = {
                "current_queue_size": task_counts[-1],
                "status": "insufficient_data"
            }
        
        return analysis
    
    def _analyze_resource_utilization(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze system resource utilization"""
        cpu_values = []
        memory_values = []
        
        for metric in metrics_history:
            resources = metric.get("system_resources", {})
            if "cpu_percent" in resources:
                cpu_values.append(resources["cpu_percent"])
            if "memory" in resources and "percent" in resources["memory"]:
                memory_values.append(resources["memory"]["percent"])
        
        analysis = {}
        
        if cpu_values:
            analysis["cpu"] = {
                "current_avg": statistics.mean(cpu_values[-5:]) if len(cpu_values) >= 5 else statistics.mean(cpu_values),
                "peak": max(cpu_values),
                "trend": self._calculate_trend(cpu_values[-10:]) if len(cpu_values) >= 10 else "stable"
            }
        
        if memory_values:
            analysis["memory"] = {
                "current_avg": statistics.mean(memory_values[-5:]) if len(memory_values) >= 5 else statistics.mean(memory_values),
                "peak": max(memory_values),
                "trend": self._calculate_trend(memory_values[-10:]) if len(memory_values) >= 10 else "stable"
            }
        
        return analysis
    
    def _detect_anomalies(self, metrics_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect performance anomalies using statistical analysis"""
        anomalies = []
        
        if len(metrics_history) < 10:
            return anomalies
        
        # Analyze response time anomalies
        response_times = [
            metric.get("api_health", {}).get("response_time")
            for metric in metrics_history
            if metric.get("api_health", {}).get("response_time") is not None
        ]
        
        if len(response_times) >= 10:
            mean_rt = statistics.mean(response_times)
            std_rt = statistics.stdev(response_times)
            
            for i, metric in enumerate(metrics_history):
                rt = metric.get("api_health", {}).get("response_time")
                if rt and abs(rt - mean_rt) > self.anomaly_threshold * std_rt:
                    anomalies.append({
                        "type": "response_time_anomaly",
                        "timestamp": metric["timestamp"],
                        "value": rt,
                        "expected_range": [mean_rt - std_rt, mean_rt + std_rt],
                        "severity": "high" if abs(rt - mean_rt) > 3 * std_rt else "medium"
                    })
        
        # Detect error clusters
        recent_errors = []
        for metric in metrics_history[-10:]:
            if metric.get("api_health", {}).get("status") == "error":
                recent_errors.append(metric["timestamp"])
        
        if len(recent_errors) >= 3:
            anomalies.append({
                "type": "error_cluster",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error_count": len(recent_errors),
                "severity": "high"
            })
        
        return anomalies
    
    def _predict_trends(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Predict future performance trends"""
        if len(metrics_history) < 10:
            return {"status": "insufficient_data"}
        
        predictions = {}
        
        # Predict response time trend
        response_times = [
            metric.get("api_health", {}).get("response_time")
            for metric in metrics_history[-20:]
            if metric.get("api_health", {}).get("response_time") is not None
        ]
        
        if len(response_times) >= 10:
            trend_slope = self._calculate_linear_trend(response_times)
            current_avg = statistics.mean(response_times[-5:])
            
            predictions["response_time"] = {
                "current_avg": current_avg,
                "predicted_change_10min": trend_slope * 10,
                "predicted_value_10min": current_avg + (trend_slope * 10),
                "trend_direction": "increasing" if trend_slope > 0 else "decreasing" if trend_slope < 0 else "stable",
                "confidence": min(100, max(0, 100 - abs(trend_slope) * 20))
            }
        
        return predictions
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100
        
        # Response time scoring
        rt_analysis = analysis.get("response_time_analysis", {})
        if "current_avg" in rt_analysis:
            avg_rt = rt_analysis["current_avg"]
            if avg_rt > 1000:  # > 1 second
                score -= 30
            elif avg_rt > 500:  # > 500ms
                score -= 15
            elif avg_rt > 200:  # > 200ms
                score -= 5
        
        # Error rate scoring
        error_analysis = analysis.get("error_rate_analysis", {})
        if "recent_error_rate" in error_analysis:
            error_rate = error_analysis["recent_error_rate"]
            score -= error_rate * 2  # 2 points per % error rate
        
        # Anomaly scoring
        anomalies = analysis.get("anomaly_detection", [])
        high_severity_anomalies = sum(1 for a in anomalies if a.get("severity") == "high")
        medium_severity_anomalies = sum(1 for a in anomalies if a.get("severity") == "medium")
        
        score -= high_severity_anomalies * 20
        score -= medium_severity_anomalies * 10
        
        # Resource utilization scoring
        resources = analysis.get("resource_utilization", {})
        if "cpu" in resources and "current_avg" in resources["cpu"]:
            cpu_avg = resources["cpu"]["current_avg"]
            if cpu_avg > 90:
                score -= 20
            elif cpu_avg > 80:
                score -= 10
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Response time recommendations
        rt_analysis = analysis.get("response_time_analysis", {})
        if "current_avg" in rt_analysis:
            avg_rt = rt_analysis["current_avg"]
            if avg_rt > 1000:
                recommendations.append("HIGH PRIORITY: Response time > 1s - investigate system bottlenecks")
            elif avg_rt > 500:
                recommendations.append("MEDIUM PRIORITY: Response time > 500ms - consider performance optimization")
            
            if rt_analysis.get("trend") == "degrading":
                recommendations.append("WARNING: Response time trending upward - monitor system resources")
        
        # Error rate recommendations
        error_analysis = analysis.get("error_rate_analysis", {})
        if error_analysis.get("recent_error_rate", 0) > 5:
            recommendations.append("HIGH PRIORITY: Error rate > 5% - investigate system stability")
        elif error_analysis.get("error_trend") == "increasing":
            recommendations.append("MEDIUM PRIORITY: Error rate increasing - monitor system health")
        
        # Resource recommendations
        resources = analysis.get("resource_utilization", {})
        if "cpu" in resources and resources["cpu"].get("current_avg", 0) > 80:
            recommendations.append("HIGH PRIORITY: CPU utilization > 80% - consider scaling or optimization")
        if "memory" in resources and resources["memory"].get("current_avg", 0) > 85:
            recommendations.append("HIGH PRIORITY: Memory utilization > 85% - investigate memory leaks")
        
        # Anomaly recommendations
        anomalies = analysis.get("anomaly_detection", [])
        if any(a.get("severity") == "high" for a in anomalies):
            recommendations.append("CRITICAL: High severity anomalies detected - immediate investigation required")
        
        # Throughput recommendations
        throughput = analysis.get("throughput_analysis", {})
        if throughput.get("queue_trend") == "growing":
            recommendations.append("MEDIUM PRIORITY: Task queue growing - monitor processing capacity")
        
        if not recommendations:
            recommendations.append("✅ System performing well - no immediate actions required")
        
        return recommendations
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _calculate_trend(self, data: List[float]) -> str:
        """Calculate trend direction for data series"""
        if len(data) < 3:
            return "stable"
        
        slope = self._calculate_linear_trend(data)
        
        if abs(slope) < 0.1:  # Threshold for "stable"
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"
    
    def _calculate_linear_trend(self, data: List[float]) -> float:
        """Calculate linear trend slope using least squares"""
        if len(data) < 2:
            return 0
        
        n = len(data)
        x = list(range(n))
        
        sum_x = sum(x)
        sum_y = sum(data)
        sum_xy = sum(x[i] * data[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope


class PerformanceBaseline:
    """Establish and maintain performance baselines"""
    
    def __init__(self):
        self.baseline_file = Path("monitoring/performance_baseline.json")
        self.baseline_data = self._load_baseline()
    
    def establish_baseline(self, metrics_history: List[Dict[str, Any]], 
                          confidence_window: int = 50) -> Dict[str, Any]:
        """Establish performance baseline from historical data"""
        if len(metrics_history) < confidence_window:
            return {"status": "insufficient_data", "required": confidence_window}
        
        # Use stable period for baseline (exclude anomalies)
        stable_metrics = self._filter_stable_metrics(metrics_history)
        
        baseline = {
            "established": datetime.now(timezone.utc).isoformat(),
            "sample_size": len(stable_metrics),
            "confidence_level": min(100, (len(stable_metrics) / confidence_window) * 100),
            "response_time": self._calculate_baseline_response_time(stable_metrics),
            "error_rate": self._calculate_baseline_error_rate(stable_metrics),
            "throughput": self._calculate_baseline_throughput(stable_metrics),
            "resource_utilization": self._calculate_baseline_resources(stable_metrics)
        }
        
        self.baseline_data = baseline
        self._save_baseline()
        
        return baseline
    
    def compare_to_baseline(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current performance to established baseline"""
        if not self.baseline_data or "response_time" not in self.baseline_data:
            return {"status": "no_baseline", "message": "No baseline established"}
        
        comparison = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline_age_hours": self._get_baseline_age_hours(),
            "response_time_comparison": self._compare_response_time(current_metrics),
            "error_rate_comparison": self._compare_error_rate(current_metrics),
            "overall_performance": "unknown"
        }
        
        # Calculate overall performance vs baseline
        deviations = []
        
        if "deviation_percentage" in comparison.get("response_time_comparison", {}):
            deviations.append(comparison["response_time_comparison"]["deviation_percentage"])
        
        if "deviation_percentage" in comparison.get("error_rate_comparison", {}):
            deviations.append(comparison["error_rate_comparison"]["deviation_percentage"])
        
        if deviations:
            avg_deviation = statistics.mean(deviations)
            if avg_deviation < -10:
                comparison["overall_performance"] = "significantly_better"
            elif avg_deviation < -5:
                comparison["overall_performance"] = "better"
            elif avg_deviation < 5:
                comparison["overall_performance"] = "similar"
            elif avg_deviation < 20:
                comparison["overall_performance"] = "worse"
            else:
                comparison["overall_performance"] = "significantly_worse"
        
        return comparison
    
    def _filter_stable_metrics(self, metrics_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out anomalous metrics to get stable baseline period"""
        # For now, simple filter - exclude metrics with errors
        stable_metrics = [
            metric for metric in metrics_history
            if metric.get("api_health", {}).get("status") == "healthy"
        ]
        
        # Also exclude response time outliers
        response_times = [
            metric.get("api_health", {}).get("response_time")
            for metric in stable_metrics
            if metric.get("api_health", {}).get("response_time") is not None
        ]
        
        if len(response_times) > 10:
            mean_rt = statistics.mean(response_times)
            std_rt = statistics.stdev(response_times)
            
            filtered_metrics = []
            for metric in stable_metrics:
                rt = metric.get("api_health", {}).get("response_time")
                if rt and abs(rt - mean_rt) <= 2 * std_rt:  # Within 2 standard deviations
                    filtered_metrics.append(metric)
            
            return filtered_metrics
        
        return stable_metrics
    
    def _calculate_baseline_response_time(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate baseline response time metrics"""
        response_times = [
            metric.get("api_health", {}).get("response_time")
            for metric in metrics
            if metric.get("api_health", {}).get("response_time") is not None
        ]
        
        if not response_times:
            return {}
        
        return {
            "mean": statistics.mean(response_times),
            "median": statistics.median(response_times),
            "p95": self._percentile(response_times, 95),
            "p99": self._percentile(response_times, 99),
            "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
        }
    
    def _calculate_baseline_error_rate(self, metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate baseline error rate"""
        total_checks = len(metrics)
        error_count = sum(
            1 for metric in metrics
            if metric.get("api_health", {}).get("status") == "error"
        )
        
        return {
            "error_rate_percentage": (error_count / total_checks) * 100 if total_checks > 0 else 0,
            "total_checks": total_checks,
            "error_count": error_count
        }
    
    def _calculate_baseline_throughput(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate baseline throughput metrics"""
        # Implementation depends on how throughput is measured
        return {"status": "calculated"}  # Placeholder
    
    def _calculate_baseline_resources(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate baseline resource utilization"""
        # Implementation depends on resource metrics availability
        return {"status": "calculated"}  # Placeholder
    
    def _compare_response_time(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current response time to baseline"""
        baseline_rt = self.baseline_data.get("response_time", {})
        current_rt = current_metrics.get("api_health", {}).get("response_time")
        
        if not baseline_rt or current_rt is None:
            return {"status": "insufficient_data"}
        
        baseline_mean = baseline_rt.get("mean", 0)
        deviation = ((current_rt - baseline_mean) / baseline_mean) * 100 if baseline_mean > 0 else 0
        
        return {
            "current_value": current_rt,
            "baseline_mean": baseline_mean,
            "deviation_ms": current_rt - baseline_mean,
            "deviation_percentage": deviation,
            "status": "better" if deviation < -5 else "worse" if deviation > 20 else "similar"
        }
    
    def _compare_error_rate(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current error rate to baseline"""
        # Implementation depends on how current error rate is calculated
        return {"status": "calculated"}  # Placeholder
    
    def _get_baseline_age_hours(self) -> float:
        """Get age of current baseline in hours"""
        if not self.baseline_data or "established" not in self.baseline_data:
            return 0
        
        established = datetime.fromisoformat(self.baseline_data["established"])
        age = datetime.now(timezone.utc) - established
        return age.total_seconds() / 3600
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _load_baseline(self) -> Dict[str, Any]:
        """Load baseline from file"""
        try:
            if self.baseline_file.exists():
                with open(self.baseline_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save_baseline(self):
        """Save baseline to file"""
        try:
            self.baseline_file.parent.mkdir(exist_ok=True)
            with open(self.baseline_file, 'w') as f:
                json.dump(self.baseline_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save baseline: {e}")


if __name__ == "__main__":
    print("🧠 A2A Advanced Analytics Engine")
    print("=" * 50)
    
    # Example usage
    analyzer = PerformanceAnalyzer()
    baseline = PerformanceBaseline()
    
    print("✅ Advanced analytics engine initialized")
    print("📊 Ready for performance analysis and baseline establishment")
    print("🎯 Integration with monitoring dashboard available")