"""Prometheus metrics for monitoring."""

import time
from typing import Callable, Any
from functools import wraps
from dataclasses import dataclass, field
from collections import defaultdict

from .logging import get_logger

logger = get_logger(__name__)


@dataclass
class Counter:
    """Simple counter metric."""

    name: str
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    _value: int = 0

    def inc(self, value: int = 1) -> None:
        """Increment counter."""
        self._value += value

    def get(self) -> int:
        """Get current value."""
        return self._value


@dataclass
class Gauge:
    """Simple gauge metric."""

    name: str
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    _value: float = 0.0

    def set(self, value: float) -> None:
        """Set gauge value."""
        self._value = value

    def inc(self, value: float = 1.0) -> None:
        """Increment gauge."""
        self._value += value

    def dec(self, value: float = 1.0) -> None:
        """Decrement gauge."""
        self._value -= value

    def get(self) -> float:
        """Get current value."""
        return self._value


@dataclass
class Histogram:
    """Simple histogram metric for latency tracking."""

    name: str
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    buckets: list[float] = field(
        default_factory=lambda: [
            0.005,
            0.01,
            0.025,
            0.05,
            0.1,
            0.25,
            0.5,
            1.0,
            2.5,
            5.0,
            10.0,
        ]
    )
    _values: list[float] = field(default_factory=list)

    def observe(self, value: float) -> None:
        """Record an observation."""
        self._values.append(value)

    def get_stats(self) -> dict:
        """Get histogram statistics."""
        if not self._values:
            return {"count": 0, "sum": 0, "avg": 0, "buckets": {}}

        sorted_values = sorted(self._values)
        count = len(sorted_values)
        total = sum(sorted_values)

        # Calculate percentiles
        def percentile(p: float) -> float:
            idx = int(count * p)
            return sorted_values[min(idx, count - 1)]

        buckets = {}
        for bucket_limit in self.buckets:
            bucket_count = sum(1 for v in sorted_values if v <= bucket_limit)
            buckets[f"<= {bucket_limit}"] = bucket_count

        return {
            "count": count,
            "sum": total,
            "avg": total / count,
            "p50": percentile(0.5),
            "p90": percentile(0.9),
            "p95": percentile(0.95),
            "p99": percentile(0.99),
            "max": max(sorted_values),
            "buckets": buckets,
        }


class MetricsCollector:
    """Collector for application metrics."""

    def __init__(self):
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}
        self._request_times: dict[str, list[float]] = defaultdict(list)
        self._start_time = time.time()

    def counter(
        self, name: str, description: str = "", labels: dict | None = None
    ) -> Counter:
        """Get or create a counter."""
        key = self._metric_key(name, labels)
        if key not in self._counters:
            self._counters[key] = Counter(
                name=name,
                description=description,
                labels=labels or {},
            )
        return self._counters[key]

    def gauge(
        self, name: str, description: str = "", labels: dict | None = None
    ) -> Gauge:
        """Get or create a gauge."""
        key = self._metric_key(name, labels)
        if key not in self._gauges:
            self._gauges[key] = Gauge(
                name=name,
                description=description,
                labels=labels or {},
            )
        return self._gauges[key]

    def histogram(
        self,
        name: str,
        description: str = "",
        labels: dict | None = None,
        buckets: list[float] | None = None,
    ) -> Histogram:
        """Get or create a histogram."""
        key = self._metric_key(name, labels)
        if key not in self._histograms:
            self._histograms[key] = Histogram(
                name=name,
                description=description,
                labels=labels or {},
                buckets=buckets,
            )
        return self._histograms[key]

    def _metric_key(self, name: str, labels: dict | None) -> str:
        """Generate a unique key for a metric."""
        if not labels:
            return name
        label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def record_request(
        self, method: str, endpoint: str, status: int, duration: float
    ) -> None:
        """Record an HTTP request."""
        labels = {"method": method, "endpoint": endpoint, "status": str(status)}

        # Counter for total requests
        self.counter("http_requests_total", "Total HTTP requests", labels).inc()

        # Histogram for latency
        self.histogram(
            "http_request_duration_seconds", "HTTP request latency", labels
        ).observe(duration)

    def record_llm_request(
        self,
        provider: str,
        model: str,
        success: bool,
        duration: float,
        tokens: int = 0,
    ) -> None:
        """Record an LLM API request."""
        labels = {"provider": provider, "model": model, "success": str(success)}

        self.counter("llm_requests_total", "Total LLM requests", labels).inc()
        self.histogram(
            "llm_request_duration_seconds", "LLM request latency", labels
        ).observe(duration)

        if tokens > 0:
            self.counter("llm_tokens_total", "Total LLM tokens", labels).inc(tokens)

    def record_error(self, error_type: str, endpoint: str | None = None) -> None:
        """Record an error."""
        labels = {"error_type": error_type}
        if endpoint:
            labels["endpoint"] = endpoint
        self.counter("errors_total", "Total errors", labels).inc()

    def get_prometheus_output(self) -> str:
        """Generate Prometheus-formatted metrics output."""
        lines = []
        uptime = time.time() - self._start_time

        lines.append(f"# HELP app_uptime_seconds Application uptime")
        lines.append(f"# TYPE app_uptime_seconds gauge")
        lines.append(f"app_uptime_seconds {uptime:.2f}")
        lines.append("")

        lines.append("# HELP python_gc_objects_collected Objects collected by GC")
        lines.append("# TYPE python_gc_objects_collected counter")
        import gc

        for i, count in enumerate(gc.get_count()):
            lines.append(f'python_gc_objects_collected{{generation="{i}"}} {count}')
        lines.append("")

        # Output counters
        for counter in self._counters.values():
            lines.append(f"# HELP {counter.name} {counter.description}")
            lines.append(f"# TYPE {counter.name} counter")
            if counter.labels:
                label_str = ",".join(f'{k}="{v}"' for k, v in counter.labels.items())
                lines.append(f"{counter.name}{{{label_str}}} {counter.get()}")
            else:
                lines.append(f"{counter.name} {counter.get()}")
        lines.append("")

        # Output gauges
        for gauge in self._gauges.values():
            lines.append(f"# HELP {gauge.name} {gauge.description}")
            lines.append(f"# TYPE {gauge.name} gauge")
            if gauge.labels:
                label_str = ",".join(f'{k}="{v}"' for k, v in gauge.labels.items())
                lines.append(f"{gauge.name}{{{label_str}}} {gauge.get()}")
            else:
                lines.append(f"{gauge.name} {gauge.get()}")
        lines.append("")

        # Output histograms
        for histogram in self._histograms.values():
            lines.append(f"# HELP {histogram.name} {histogram.description}")
            lines.append(f"# TYPE {histogram.name} histogram")
            stats = histogram.get_stats()

            if stats["count"] > 0:
                cumulative = 0
                for bucket_limit in histogram.buckets:
                    cumulative = sum(1 for v in histogram._values if v <= bucket_limit)
                    bucket_label = f'le="{bucket_limit}"'
                    if histogram.labels:
                        label_str = ",".join(
                            f'{k}="{v}"' for k, v in histogram.labels.items()
                        )
                        lines.append(
                            f"{histogram.name}_bucket{{{bucket_label},{label_str}}} {cumulative}"
                        )
                    else:
                        lines.append(
                            f"{histogram.name}_bucket{{{bucket_label}}} {cumulative}"
                        )

                # +Inf bucket
                if histogram.labels:
                    label_str = ",".join(
                        f'{k}="{v}"' for k, v in histogram.labels.items()
                    )
                    lines.append(
                        f'{histogram.name}_bucket{{le="+Inf",{label_str}}} {stats["count"]}'
                    )
                else:
                    lines.append(
                        f'{histogram.name}_bucket{{le="+Inf"}} {stats["count"]}'
                    )

                lines.append(f"{histogram.name}_sum {stats['sum']:.6f}")
                lines.append(f"{histogram.name}_count {stats['count']}")
        lines.append("")

        return "\n".join(lines)

    def get_summary(self) -> dict:
        """Get a summary of all metrics."""
        return {
            "uptime_seconds": time.time() - self._start_time,
            "counters": {c.name: c.get() for c in self._counters.values()},
            "gauges": {g.name: g.get() for g in self._gauges.values()},
            "histograms": {h.name: h.get_stats() for h in self._histograms.values()},
        }


# Global metrics instance
metrics = MetricsCollector()


def track_request(method: str, endpoint: str):
    """Decorator to track HTTP request metrics."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start

                # Get status from response if available
                status = getattr(result, "status_code", 200)
                metrics.record_request(method, endpoint, status, duration)

                return result
            except Exception as e:
                duration = time.time() - start
                metrics.record_request(method, endpoint, 500, duration)
                metrics.record_error(type(e).__name__, endpoint)
                raise

        return wrapper

    return decorator
