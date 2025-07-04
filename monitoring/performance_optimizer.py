"""
Intelligent Performance Optimizer for A2A System
Automated performance tuning and optimization recommendations
"""

import json
import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import threading
import statistics

from monitoring.advanced_analytics import PerformanceAnalyzer, PerformanceBaseline


class PerformanceOptimizer:
    """Intelligent performance optimization engine"""
    
    def __init__(self, api_base_url: str = "http://127.0.0.1:5000"):
        self.api_base_url = api_base_url
        self.analyzer = PerformanceAnalyzer()
        self.baseline = PerformanceBaseline()
        
        self.optimization_history = []
        self.active_optimizations = []
        self.optimization_config = {
            "auto_optimize": True,
            "response_time_target": 200,  # ms
            "error_rate_target": 1,  # %
            "optimization_interval": 300,  # seconds
            "min_data_points": 20
        }
        
        self.optimization_strategies = {
            "response_time": [
                self._optimize_connection_pooling,
                self._optimize_timeout_settings,
                self._optimize_request_batching
            ],
            "error_handling": [
                self._optimize_retry_logic,
                self._optimize_circuit_breaker,
                self._optimize_health_checks
            ],
            "throughput": [
                self._optimize_concurrent_requests,
                self._optimize_queue_management,
                self._optimize_resource_allocation
            ]
        }
        
        self.current_config = self._load_current_config()
        
    def analyze_and_optimize(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance and apply optimizations"""
        optimization_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "analysis_results": {},
            "optimizations_applied": [],
            "recommendations": [],
            "performance_impact": {},
            "next_analysis": (datetime.now(timezone.utc) + timedelta(seconds=self.optimization_config["optimization_interval"])).isoformat()
        }
        
        if len(metrics_history) < self.optimization_config["min_data_points"]:
            optimization_report["status"] = "insufficient_data"
            optimization_report["message"] = f"Need at least {self.optimization_config['min_data_points']} data points"
            return optimization_report
        
        # Perform analysis
        print("🧠 Analyzing system performance...")
        analysis = self.analyzer.analyze_performance_trends(metrics_history)
        optimization_report["analysis_results"] = analysis
        
        # Identify optimization opportunities
        opportunities = self._identify_optimization_opportunities(analysis)
        
        # Apply automatic optimizations if enabled
        if self.optimization_config["auto_optimize"]:
            applied_optimizations = self._apply_optimizations(opportunities)
            optimization_report["optimizations_applied"] = applied_optimizations
        
        # Generate recommendations
        optimization_report["recommendations"] = self._generate_optimization_recommendations(analysis, opportunities)
        
        # Measure impact of previous optimizations
        if self.optimization_history:
            impact = self._measure_optimization_impact(metrics_history)
            optimization_report["performance_impact"] = impact
        
        # Store optimization history
        self.optimization_history.append(optimization_report)
        
        # Save optimization report
        self._save_optimization_report(optimization_report)
        
        return optimization_report
    
    def _identify_optimization_opportunities(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific optimization opportunities"""
        opportunities = []
        
        # Response time optimization opportunities
        rt_analysis = analysis.get("response_time_analysis", {})
        if rt_analysis.get("current_avg", 0) > self.optimization_config["response_time_target"]:
            opportunities.append({
                "type": "response_time",
                "severity": "high" if rt_analysis["current_avg"] > 500 else "medium",
                "current_value": rt_analysis["current_avg"],
                "target_value": self.optimization_config["response_time_target"],
                "strategies": ["connection_pooling", "timeout_optimization", "request_batching"]
            })
        
        # Error rate optimization opportunities
        error_analysis = analysis.get("error_rate_analysis", {})
        if error_analysis.get("recent_error_rate", 0) > self.optimization_config["error_rate_target"]:
            opportunities.append({
                "type": "error_handling",
                "severity": "high" if error_analysis["recent_error_rate"] > 5 else "medium",
                "current_value": error_analysis["recent_error_rate"],
                "target_value": self.optimization_config["error_rate_target"],
                "strategies": ["retry_logic", "circuit_breaker", "health_check_optimization"]
            })
        
        # Throughput optimization opportunities
        throughput_analysis = analysis.get("throughput_analysis", {})
        if throughput_analysis.get("queue_trend") == "growing":
            opportunities.append({
                "type": "throughput",
                "severity": "medium",
                "current_trend": "growing_queue",
                "strategies": ["concurrent_requests", "queue_management", "resource_allocation"]
            })
        
        # Resource optimization opportunities
        resources = analysis.get("resource_utilization", {})
        if "cpu" in resources and resources["cpu"].get("current_avg", 0) > 70:
            opportunities.append({
                "type": "resource_optimization",
                "severity": "high" if resources["cpu"]["current_avg"] > 85 else "medium",
                "resource": "cpu",
                "current_value": resources["cpu"]["current_avg"],
                "strategies": ["process_optimization", "caching", "load_balancing"]
            })
        
        return opportunities
    
    def _apply_optimizations(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply automatic optimizations based on opportunities"""
        applied_optimizations = []
        
        for opportunity in opportunities:
            if opportunity["severity"] == "high":
                optimization_type = opportunity["type"]
                
                if optimization_type in self.optimization_strategies:
                    for strategy_func in self.optimization_strategies[optimization_type]:
                        try:
                            result = strategy_func(opportunity)
                            if result["applied"]:
                                applied_optimizations.append({
                                    "timestamp": datetime.now(timezone.utc).isoformat(),
                                    "type": optimization_type,
                                    "strategy": result["strategy"],
                                    "details": result["details"],
                                    "expected_impact": result.get("expected_impact", "unknown")
                                })
                                print(f"✅ Applied optimization: {result['strategy']}")
                                break  # Apply only one strategy per opportunity
                        except Exception as e:
                            print(f"❌ Failed to apply optimization {strategy_func.__name__}: {e}")
        
        return applied_optimizations
    
    def _optimize_connection_pooling(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize HTTP connection pooling settings"""
        current_config = self.current_config.get("connection_pooling", {})
        
        # Increase pool size if response times are high
        new_pool_size = min(current_config.get("max_pool_size", 10) + 5, 50)
        new_timeout = max(current_config.get("timeout", 30) - 5, 10)
        
        optimized_config = {
            "max_pool_size": new_pool_size,
            "timeout": new_timeout,
            "keep_alive": True,
            "retry_on_timeout": True
        }
        
        # Update configuration
        self.current_config["connection_pooling"] = optimized_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "connection_pooling_optimization",
            "details": optimized_config,
            "expected_impact": "5-15% response time improvement"
        }
    
    def _optimize_timeout_settings(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize request timeout settings"""
        current_timeout = self.current_config.get("request_timeout", 30)
        
        # Adjust timeout based on current response times
        current_rt = opportunity.get("current_value", 0)
        if current_rt > 1000:  # > 1 second
            new_timeout = min(current_timeout + 10, 60)
        else:
            new_timeout = max(current_timeout - 5, 5)
        
        self.current_config["request_timeout"] = new_timeout
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "timeout_optimization",
            "details": {"new_timeout": new_timeout, "previous_timeout": current_timeout},
            "expected_impact": "Reduced timeout-related errors"
        }
    
    def _optimize_request_batching(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize request batching strategies"""
        batching_config = {
            "enabled": True,
            "batch_size": 10,
            "batch_timeout": 100,  # ms
            "concurrent_batches": 3
        }
        
        self.current_config["request_batching"] = batching_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "request_batching",
            "details": batching_config,
            "expected_impact": "10-20% throughput improvement"
        }
    
    def _optimize_retry_logic(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize retry logic for failed requests"""
        retry_config = {
            "max_retries": 3,
            "backoff_strategy": "exponential",
            "base_delay": 1000,  # ms
            "max_delay": 10000,  # ms
            "retry_on_status": [500, 502, 503, 504]
        }
        
        self.current_config["retry_logic"] = retry_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "retry_logic_optimization",
            "details": retry_config,
            "expected_impact": "20-30% error rate reduction"
        }
    
    def _optimize_circuit_breaker(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Implement circuit breaker pattern for error handling"""
        circuit_breaker_config = {
            "enabled": True,
            "failure_threshold": 5,
            "recovery_timeout": 30000,  # ms
            "monitoring_window": 60000,  # ms
            "half_open_max_calls": 3
        }
        
        self.current_config["circuit_breaker"] = circuit_breaker_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "circuit_breaker_implementation",
            "details": circuit_breaker_config,
            "expected_impact": "Improved system stability during failures"
        }
    
    def _optimize_health_checks(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize health check frequency and timeouts"""
        health_check_config = {
            "interval": 10,  # seconds
            "timeout": 5,   # seconds
            "failure_threshold": 3,
            "success_threshold": 2
        }
        
        self.current_config["health_checks"] = health_check_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "health_check_optimization",
            "details": health_check_config,
            "expected_impact": "Earlier failure detection and faster recovery"
        }
    
    def _optimize_concurrent_requests(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize concurrent request handling"""
        concurrency_config = {
            "max_concurrent": 20,
            "queue_size": 100,
            "worker_threads": 4,
            "async_processing": True
        }
        
        self.current_config["concurrency"] = concurrency_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "concurrent_request_optimization",
            "details": concurrency_config,
            "expected_impact": "25-40% throughput improvement"
        }
    
    def _optimize_queue_management(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize task queue management"""
        queue_config = {
            "priority_queue": True,
            "max_queue_size": 1000,
            "processing_batch_size": 10,
            "queue_timeout": 300,  # seconds
            "auto_scaling": True
        }
        
        self.current_config["queue_management"] = queue_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "queue_management_optimization",
            "details": queue_config,
            "expected_impact": "Improved queue processing efficiency"
        }
    
    def _optimize_resource_allocation(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize system resource allocation"""
        resource_config = {
            "memory_limit": "512MB",
            "cpu_limit": "2 cores",
            "gc_optimization": True,
            "cache_size": "128MB",
            "connection_reuse": True
        }
        
        self.current_config["resource_allocation"] = resource_config
        self._save_current_config()
        
        return {
            "applied": True,
            "strategy": "resource_allocation_optimization",
            "details": resource_config,
            "expected_impact": "10-15% resource efficiency improvement"
        }
    
    def _generate_optimization_recommendations(self, analysis: Dict[str, Any], 
                                            opportunities: List[Dict[str, Any]]) -> List[str]:
        """Generate human-readable optimization recommendations"""
        recommendations = []
        
        for opportunity in opportunities:
            if opportunity["type"] == "response_time":
                recommendations.append(
                    f"🚀 RESPONSE TIME: Current avg {opportunity['current_value']:.0f}ms "
                    f"(target: {opportunity['target_value']}ms) - Consider connection pooling optimization"
                )
            elif opportunity["type"] == "error_handling":
                recommendations.append(
                    f"🛡️ ERROR RATE: Current {opportunity['current_value']:.1f}% "
                    f"(target: {opportunity['target_value']}%) - Implement enhanced retry logic"
                )
            elif opportunity["type"] == "throughput":
                recommendations.append(
                    f"📈 THROUGHPUT: Queue growing trend detected - Consider concurrent request optimization"
                )
            elif opportunity["type"] == "resource_optimization":
                recommendations.append(
                    f"💻 RESOURCES: {opportunity['resource'].upper()} at {opportunity['current_value']:.1f}% "
                    f"- Consider resource allocation optimization"
                )
        
        # Performance score recommendations
        perf_score = analysis.get("performance_score", 0)
        if perf_score < 70:
            recommendations.append(
                f"⚠️ OVERALL PERFORMANCE: Score {perf_score:.0f}/100 - Multiple optimizations recommended"
            )
        elif perf_score < 85:
            recommendations.append(
                f"📊 PERFORMANCE: Score {perf_score:.0f}/100 - Fine-tuning opportunities available"
            )
        else:
            recommendations.append(
                f"✅ PERFORMANCE: Score {perf_score:.0f}/100 - System performing well"
            )
        
        return recommendations
    
    def _measure_optimization_impact(self, metrics_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Measure the impact of previously applied optimizations"""
        if len(self.optimization_history) < 2:
            return {"status": "insufficient_history"}
        
        # Compare performance before and after last optimization
        last_optimization = self.optimization_history[-1]
        optimization_time = datetime.fromisoformat(last_optimization["timestamp"])
        
        # Get metrics before and after optimization
        before_metrics = [
            m for m in metrics_history
            if datetime.fromisoformat(m["timestamp"]) < optimization_time - timedelta(minutes=10)
        ][-10:]  # Last 10 before optimization
        
        after_metrics = [
            m for m in metrics_history
            if datetime.fromisoformat(m["timestamp"]) > optimization_time + timedelta(minutes=5)
        ][:10]  # First 10 after optimization
        
        if len(before_metrics) < 5 or len(after_metrics) < 5:
            return {"status": "insufficient_data_for_comparison"}
        
        # Calculate impact
        impact = {
            "optimization_timestamp": last_optimization["timestamp"],
            "response_time_impact": self._calculate_response_time_impact(before_metrics, after_metrics),
            "error_rate_impact": self._calculate_error_rate_impact(before_metrics, after_metrics),
            "overall_impact": "unknown"
        }
        
        # Determine overall impact
        rt_improvement = impact["response_time_impact"].get("improvement_percentage", 0)
        error_improvement = impact["error_rate_impact"].get("improvement_percentage", 0)
        
        avg_improvement = (rt_improvement + error_improvement) / 2
        
        if avg_improvement > 10:
            impact["overall_impact"] = "significant_improvement"
        elif avg_improvement > 5:
            impact["overall_impact"] = "moderate_improvement"
        elif avg_improvement > -5:
            impact["overall_impact"] = "minimal_change"
        else:
            impact["overall_impact"] = "degradation"
        
        return impact
    
    def _calculate_response_time_impact(self, before_metrics: List[Dict[str, Any]], 
                                      after_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate response time impact of optimizations"""
        before_times = [
            m.get("api_health", {}).get("response_time")
            for m in before_metrics
            if m.get("api_health", {}).get("response_time") is not None
        ]
        
        after_times = [
            m.get("api_health", {}).get("response_time")
            for m in after_metrics
            if m.get("api_health", {}).get("response_time") is not None
        ]
        
        if not before_times or not after_times:
            return {"status": "no_data"}
        
        before_avg = statistics.mean(before_times)
        after_avg = statistics.mean(after_times)
        improvement = ((before_avg - after_avg) / before_avg) * 100
        
        return {
            "before_avg": before_avg,
            "after_avg": after_avg,
            "improvement_ms": before_avg - after_avg,
            "improvement_percentage": improvement,
            "status": "improved" if improvement > 0 else "degraded"
        }
    
    def _calculate_error_rate_impact(self, before_metrics: List[Dict[str, Any]], 
                                   after_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate error rate impact of optimizations"""
        before_errors = sum(
            1 for m in before_metrics
            if m.get("api_health", {}).get("status") == "error"
        )
        before_rate = (before_errors / len(before_metrics)) * 100
        
        after_errors = sum(
            1 for m in after_metrics
            if m.get("api_health", {}).get("status") == "error"
        )
        after_rate = (after_errors / len(after_metrics)) * 100
        
        improvement = before_rate - after_rate
        improvement_percentage = (improvement / before_rate) * 100 if before_rate > 0 else 0
        
        return {
            "before_rate": before_rate,
            "after_rate": after_rate,
            "improvement_percentage": improvement_percentage,
            "status": "improved" if improvement > 0 else "degraded"
        }
    
    def _load_current_config(self) -> Dict[str, Any]:
        """Load current optimization configuration"""
        config_file = Path("monitoring/optimization_config.json")
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Default configuration
        return {
            "connection_pooling": {"max_pool_size": 10, "timeout": 30},
            "request_timeout": 30,
            "optimization_enabled": True
        }
    
    def _save_current_config(self):
        """Save current optimization configuration"""
        config_file = Path("monitoring/optimization_config.json")
        try:
            config_file.parent.mkdir(exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self.current_config, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save optimization config: {e}")
    
    def _save_optimization_report(self, report: Dict[str, Any]):
        """Save optimization report"""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_file = Path(f"monitoring/optimization_report_{timestamp}.json")
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save optimization report: {e}")


if __name__ == "__main__":
    print("🚀 A2A Performance Optimizer")
    print("=" * 50)
    
    optimizer = PerformanceOptimizer()
    
    print("✅ Performance optimizer initialized")
    print("🎯 Ready for intelligent performance optimization")
    print("🔧 Automatic optimization strategies loaded")