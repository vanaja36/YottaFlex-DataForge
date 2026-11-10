import time
from src.metrics import PipelineMetrics

metrics = PipelineMetrics(
    dataset="customers",
    total_records=100000,
    valid_records=98000,
    rejected_records=2000
)

start_time = time.perf_counter()
time.sleep(1)
metrics.calculate_performance(start_time)

print("Pipeline Performance:")
for key, value in metrics.to_dict().items():
    print(f"{key}: {value}")
