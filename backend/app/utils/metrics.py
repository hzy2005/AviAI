from threading import Lock


class MetricsCollector:
    def __init__(self):
        self._lock = Lock()
        self.request_count = 0
        self.error_count = 0
        self.total_duration_ms = 0.0
        self.active_requests = 0
        self.status_codes = {}

    def start_request(self):
        with self._lock:
            self.active_requests += 1

    def finish_request(self, status_code, duration_ms):
        with self._lock:
            self.request_count += 1
            self.total_duration_ms += duration_ms
            self.active_requests = max(0, self.active_requests - 1)
            self.status_codes[str(status_code)] = self.status_codes.get(str(status_code), 0) + 1

            if status_code >= 500:
                self.error_count += 1

    def snapshot(self):
        with self._lock:
            average_response_ms = (
                self.total_duration_ms / self.request_count if self.request_count else 0.0
            )
            error_rate = self.error_count / self.request_count if self.request_count else 0.0

            return {
                "requestCount": self.request_count,
                "errorCount": self.error_count,
                "errorRate": round(error_rate, 4),
                "averageResponseMs": round(average_response_ms, 2),
                "activeRequests": self.active_requests,
                "statusCodes": dict(self.status_codes),
            }

    def prometheus_text(self):
        snapshot = self.snapshot()
        lines = [
            "# HELP aviai_requests_total Total number of processed HTTP requests.",
            "# TYPE aviai_requests_total counter",
            f"aviai_requests_total {snapshot['requestCount']}",
            "# HELP aviai_errors_total Total number of 5xx HTTP requests.",
            "# TYPE aviai_errors_total counter",
            f"aviai_errors_total {snapshot['errorCount']}",
            "# HELP aviai_error_rate Current 5xx error rate.",
            "# TYPE aviai_error_rate gauge",
            f"aviai_error_rate {snapshot['errorRate']}",
            "# HELP aviai_average_response_ms Average response time in milliseconds.",
            "# TYPE aviai_average_response_ms gauge",
            f"aviai_average_response_ms {snapshot['averageResponseMs']}",
            "# HELP aviai_active_requests Current active HTTP requests.",
            "# TYPE aviai_active_requests gauge",
            f"aviai_active_requests {snapshot['activeRequests']}",
            "# HELP aviai_status_codes_total Total HTTP requests by status code.",
            "# TYPE aviai_status_codes_total counter",
        ]

        for status_code, count in sorted(snapshot["statusCodes"].items()):
            lines.append(f'aviai_status_codes_total{{status_code="{status_code}"}} {count}')

        return "\n".join(lines) + "\n"

    def reset(self):
        with self._lock:
            self.request_count = 0
            self.error_count = 0
            self.total_duration_ms = 0.0
            self.active_requests = 0
            self.status_codes = {}


metrics_collector = MetricsCollector()
