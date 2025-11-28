"""
Observability: Logging, Tracing, and Metrics.
Demonstrates: Observability, Distributed tracing, Metrics collection
"""
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
from pathlib import Path


@dataclass
class TraceSpan:
    """Represents a trace span."""
    span_id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    parent_span_id: Optional[str] = None
    events: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def duration_ms(self) -> Optional[float]:
        """Get duration in milliseconds."""
        if self.end_time is None:
            return None
        return (self.end_time - self.start_time) * 1000


class AgentTracer:
    """
    Distributed tracing for agent operations.
    
    Implements:
    - Span-based tracing
    - Event logging
    - Trace visualization
    """
    
    def __init__(self, export_path: Optional[str] = None):
        """
        Initialize tracer.
        
        Args:
            export_path: Path to export traces
        """
        self.spans: Dict[str, TraceSpan] = {}
        self.trace_log: List[Dict[str, Any]] = []
        self.export_path = Path(export_path) if export_path else Path(".traces")
        self.export_path.mkdir(exist_ok=True)
        
        self._span_counter = 0
    
    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Start a new trace span.
        
        Args:
            name: Span name
            attributes: Span attributes
            
        Returns:
            Span ID
        """
        self._span_counter += 1
        span_id = f"span_{self._span_counter}_{int(time.time() * 1000)}"
        
        parent_span_id = attributes.pop("parent", None) if attributes else None
        
        span = TraceSpan(
            span_id=span_id,
            name=name,
            start_time=time.time(),
            attributes=attributes or {},
            parent_span_id=parent_span_id,
        )
        
        self.spans[span_id] = span
        
        self.log_event("span_started", {
            "span_id": span_id,
            "name": name,
            "parent": parent_span_id,
        })
        
        return span_id
    
    def end_span(self, span_id: str) -> None:
        """
        End a trace span.
        
        Args:
            span_id: Span ID
        """
        if span_id in self.spans:
            span = self.spans[span_id]
            span.end_time = time.time()
            
            self.log_event("span_ended", {
                "span_id": span_id,
                "duration_ms": span.duration_ms,
            })
    
    def add_span_event(
        self,
        span_id: str,
        event_name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add an event to a span.
        
        Args:
            span_id: Span ID
            event_name: Event name
            attributes: Event attributes
        """
        if span_id in self.spans:
            self.spans[span_id].events.append({
                "name": event_name,
                "timestamp": time.time(),
                "attributes": attributes or {},
            })
    
    def log_event(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Log an event.
        
        Args:
            event_type: Event type
            data: Event data
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data,
        }
        
        self.trace_log.append(event)
    
    def get_trace_log(
        self,
        event_type: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get trace log.
        
        Args:
            event_type: Filter by event type
            limit: Limit number of events
            
        Returns:
            List of events
        """
        events = self.trace_log
        
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        
        if limit:
            events = events[-limit:]
        
        return events
    
    def get_span_summary(self) -> Dict[str, Any]:
        """
        Get summary of all spans.
        
        Returns:
            Span summary
        """
        total_spans = len(self.spans)
        completed_spans = sum(1 for s in self.spans.values() if s.end_time is not None)
        
        span_durations = [
            s.duration_ms for s in self.spans.values()
            if s.duration_ms is not None
        ]
        
        return {
            "total_spans": total_spans,
            "completed_spans": completed_spans,
            "in_progress_spans": total_spans - completed_spans,
            "avg_duration_ms": sum(span_durations) / len(span_durations) if span_durations else 0,
            "max_duration_ms": max(span_durations) if span_durations else 0,
            "min_duration_ms": min(span_durations) if span_durations else 0,
        }
    
    def export_traces(self, filename: Optional[str] = None) -> str:
        """
        Export traces to file.
        
        Args:
            filename: Output filename
            
        Returns:
            Path to exported file
        """
        if filename is None:
            filename = f"traces_{int(time.time())}.json"
        
        filepath = self.export_path / filename
        
        export_data = {
            "spans": [asdict(span) for span in self.spans.values()],
            "events": self.trace_log,
            "summary": self.get_span_summary(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return str(filepath)


class MetricsCollector:
    """
    Metrics collection for agent performance.
    
    Implements:
    - Counter metrics
    - Timing metrics
    - Value metrics
    - Aggregations
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.counters: Dict[str, int] = defaultdict(int)
        self.timings: Dict[str, List[float]] = defaultdict(list)
        self.values: Dict[str, List[float]] = defaultdict(list)
        self.start_time = time.time()
    
    def increment(self, metric_name: str, value: int = 1) -> None:
        """
        Increment a counter metric.
        
        Args:
            metric_name: Metric name
            value: Increment value
        """
        self.counters[metric_name] += value
    
    def record_timing(self, metric_name: str, duration: float) -> None:
        """
        Record a timing metric.
        
        Args:
            metric_name: Metric name
            duration: Duration in seconds
        """
        self.timings[metric_name].append(duration)
    
    def record_value(self, metric_name: str, value: float) -> None:
        """
        Record a value metric.
        
        Args:
            metric_name: Metric name
            value: Value to record
        """
        self.values[metric_name].append(value)
    
    def get_counter(self, metric_name: str) -> int:
        """Get counter value."""
        return self.counters.get(metric_name, 0)
    
    def get_timing_stats(self, metric_name: str) -> Dict[str, float]:
        """Get timing statistics."""
        timings = self.timings.get(metric_name, [])
        
        if not timings:
            return {"count": 0}
        
        return {
            "count": len(timings),
            "sum": sum(timings),
            "avg": sum(timings) / len(timings),
            "min": min(timings),
            "max": max(timings),
            "p50": self._percentile(timings, 50),
            "p95": self._percentile(timings, 95),
            "p99": self._percentile(timings, 99),
        }
    
    def get_value_stats(self, metric_name: str) -> Dict[str, float]:
        """Get value statistics."""
        values = self.values.get(metric_name, [])
        
        if not values:
            return {"count": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get full metrics summary.
        
        Returns:
            Metrics summary
        """
        return {
            "uptime_seconds": time.time() - self.start_time,
            "counters": dict(self.counters),
            "timings": {
                name: self.get_timing_stats(name)
                for name in self.timings.keys()
            },
            "values": {
                name: self.get_value_stats(name)
                for name in self.values.keys()
            },
        }
    
    @staticmethod
    def _percentile(values: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * (percentile / 100))
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def reset(self) -> None:
        """Reset all metrics."""
        self.counters.clear()
        self.timings.clear()
        self.values.clear()
        self.start_time = time.time()
    
    def export_metrics(self, filepath: str) -> None:
        """
        Export metrics to file.
        
        Args:
            filepath: Output file path
        """
        with open(filepath, 'w') as f:
            json.dump(self.get_summary(), f, indent=2)

