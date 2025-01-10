import time
from collections import defaultdict


class Metric:
    """Base class for all metrics"""

    pass


class Counter(Metric):
    """Counts occurrences of events"""

    def __init__(self):
        self.value = 0

    def increment(self, amount=1):
        self.value += amount

    def get_value(self):
        return self.value


class Timer(Metric):
    """Measures the duration of events"""

    def __init__(self):
        self.start_time = None
        self.total_time = 0
        self.count = 0

    def start(self):
        self.start_time = time.time()

    def stop(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            self.total_time += elapsed_time
            self.count += 1
            self.start_time = None

    def get_average_time(self):
        return self.total_time / self.count if self.count > 0 else 0


class Gauge(Metric):
    """Holds a current value (e.g., number of objects)"""

    def __init__(self):
        self.value = 0

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class MetricRegistry:
    """Registry that stores metrics for each service"""

    def __init__(self):
        self.metrics = defaultdict(dict)

    def add_counter(self, service_name, metric_name):
        self.metrics[service_name][metric_name] = Counter()

    def add_timer(self, service_name, metric_name):
        self.metrics[service_name][metric_name] = Timer()

    def add_gauge(self, service_name, metric_name):
        self.metrics[service_name][metric_name] = Gauge()

    def get_metric(self, service_name, metric_name):
        return self.metrics[service_name].get(metric_name)

    def report_metrics(self, service_name):
        """Print or log the current state of all metrics for a service"""
        if service_name not in self.metrics:
            print(f"No metrics found for service: {service_name}")
            return
        print(f"Metrics for {service_name}:")
        for metric_name, metric in self.metrics[service_name].items():
            if isinstance(metric, Counter):
                print(f"  {metric_name} (Counter): {metric.get_value()}")
            elif isinstance(metric, Timer):
                print(f"  {metric_name} (Average Time): {metric.get_average_time():.4f} seconds")
            elif isinstance(metric, Gauge):
                print(f"  {metric_name} (Gauge): {metric.get_value()}")
