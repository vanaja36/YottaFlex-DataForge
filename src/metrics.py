import time
from dataclasses import dataclass, asdict


@dataclass
class PipelineMetrics:
    dataset: str
    total_records: int = 0
    valid_records: int = 0
    rejected_records: int = 0
    duration_seconds: float = 0.0
    records_per_second: float = 0.0

    def calculate_performance(self, start_time: float):
        self.duration_seconds = round(time.perf_counter() - start_time, 4)

        if self.duration_seconds > 0:
            self.records_per_second = round(
                self.total_records / self.duration_seconds, 2
            )

    def to_dict(self):
        return asdict(self)
