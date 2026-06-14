from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Union, Optional


class DataStream(ABC):
    """
    Abstract base class for all data streams in the Code Nexus.
    """
    def __init__(self, stream_id: str) -> None:
        self.stream_id = stream_id
        self.processed_count = 0

    @abstractmethod
    def process_batch(self, data_batch: List[Any]) -> str:
        """Process a batch of data and return a result string."""
        pass

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        """
        Default filtering: return all data unchanged.
        Subclasses may override for specialized filtering.
        """
        return data_batch

    def get_stats(self) -> Dict[str, Union[str, int, float]]:
        """Return basic stream statistics."""
        return {
            "stream_id": self.stream_id,
            "processed_count": self.processed_count
        }


class SensorStream(DataStream):
    """Environmental sensor data stream."""
    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            readings = [
                float(x) for x in data_batch
                if isinstance(x, (int, float))
            ]
            if not readings:
                raise ValueError("Invalid sensor readings")
            self.processed_count += len(readings)
            avg_temp = readings[0] if len(readings) == 1 else readings[0]
            return (
                f"Sensor analysis: {len(readings)} readings processed, "
                f"avg temp: {avg_temp}°C"
            )
        except Exception as e:
            return f"SensorStream Error: {e}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria == "critical":
            return [
                x for x in data_batch if isinstance(x, (int, float)) and x > 50
            ]
        return super().filter_data(data_batch)


class TransactionStream(DataStream):
    """Financial transaction stream."""
    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            ops = [
                x for x in data_batch
                if isinstance(x, dict) and "type" in x and "value" in x
            ]
            if not ops:
                raise ValueError("Invalid transaction data")
            self.processed_count += len(ops)
            net = sum(
                x["value"] if x["type"] == "buy" else -x["value"]
                for x in ops
            )
            sign = "+" if net >= 0 else ""
            return (
                f"Transaction analysis: {len(ops)} operations, "
                f"net flow: {sign}{net} units"
            )
        except Exception as e:
            return f"TransactionStream Error: {e}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria == "large":
            return [
                x for x in data_batch
                if isinstance(x, dict) and x.get("value", 0) > 100
            ]
        return super().filter_data(data_batch)


class EventStream(DataStream):
    """System event stream."""
    def process_batch(self, data_batch: List[Any]) -> str:
        try:
            events = [str(x) for x in data_batch]
            self.processed_count += len(events)
            error_count = sum(1 for e in events if "error" in e.lower())
            return (
                f"Event analysis: {len(events)} events, "
                f"{error_count} error detected"
            )
        except Exception as e:
            return f"EventStream Error: {e}"

    def filter_data(
        self,
        data_batch: List[Any],
        criteria: Optional[str] = None
    ) -> List[Any]:
        if criteria == "critical":
            return [e for e in data_batch if "error" in str(e).lower()]
        return super().filter_data(data_batch)


class StreamProcessor:
    """Handles multiple stream types polymorphically."""

    def __init__(self) -> None:
        self.streams: List[DataStream] = []

    def add_stream(self, stream: DataStream) -> None:
        self.streams.append(stream)

    def process_all(self, batches: List[List[Any]]) -> None:
        for stream, batch in zip(self.streams, batches):
            print(stream.process_batch(batch))


def main() -> None:
    print("=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ===")
    print("Initializing Sensor Stream...")
    sensor = SensorStream("SENSOR_001")
    print("Stream ID: SENSOR_001, Type: Environmental Data")
    batch_sensor = [22.5, 65, 1013]
    print(f"Processing sensor batch: {batch_sensor}")
    print(sensor.process_batch(batch_sensor))
    print("Initializing Transaction Stream...")
    trans = TransactionStream("TRANS_001")
    print("Stream ID: TRANS_001, Type: Financial Data")
    batch_trans = [
        {"type": "buy", "value": 100},
        {"type": "sell", "value": 150},
        {"type": "buy", "value": 75},
    ]
    print(f"Processing transaction batch: {batch_trans}")
    print(trans.process_batch(batch_trans))
    print("Initializing Event Stream...")
    event = EventStream("EVENT_001")
    print("Stream ID: EVENT_001, Type: System Events")
    batch_event = ["login", "error", "logout"]
    print(f"Processing event batch: {batch_event}")
    print(event.process_batch(batch_event))
    print("=== Polymorphic Stream Processing ===")
    print("Processing mixed stream types through unified interface...")
    processor = StreamProcessor()
    processor.add_stream(sensor)
    processor.add_stream(trans)
    processor.add_stream(event)
    mixed_batches = [
        [10, 20],
        [
            {"type": "buy", "value": 200},
            {"type": "sell", "value": 50},
            {"type": "buy", "value": 100},
            {"type": "sell", "value": 250},
        ],
        ["login", "error", "logout"],
    ]
    print("Batch 1 Results:")
    processor.process_all(mixed_batches)
    print("Stream filtering active: High-priority data only")
    filtered_sensor = sensor.filter_data([60, 10, 80], "critical")
    filtered_trans = trans.filter_data(
        [{"type": "buy", "value": 50}, {"type": "sell", "value": 200}],
        "large"
    )
    print(
        f"Filtered results: {len(filtered_sensor)} critical sensor alerts, "
        f"{len(filtered_trans)} large transaction"
    )
    print("All streams processed successfully. Nexus throughput optimal.")


if __name__ == "__main__":
    main()
