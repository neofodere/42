from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, List


class DataProcessor(ABC):
    """
    Abstract base class defining the common processing interface
    for all data processors in the Code Nexus.
    """

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate if the data is appropriate for this processor."""
        pass

    @abstractmethod
    def process(self, data: Any) -> str:
        """Process the data and return a formatted result string."""
        pass

    def format_output(self, result: str) -> str:
        """Default output formatting (can be overridden)."""
        return result


class NumericProcessor(DataProcessor):
    """Processor specialized in handling numeric lists."""
    def validate(self, data: Any) -> bool:
        return isinstance(data, list) and all(
            isinstance(x, (int, float)) for x in data
        )

    def process(self, data: Any) -> str:
        if not self.validate(data):
            raise ValueError("Invalid numeric data")
        count = len(data)
        total = sum(data)
        avg = total / count if count > 0 else 0
        result = (
            f"Processed {count} numeric values, "
            f"sum={total}, avg={avg}"
        )
        return self.format_output(result)


class TextProcessor(DataProcessor):
    """Processor specialized in handling text strings."""
    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def process(self, data: Any) -> str:
        if not self.validate(data):
            raise ValueError("Invalid text data")
        characters = len(data)
        words = len(data.split())

        result = (
            f"Processed text: {characters} characters, {words} words"
        )
        return self.format_output(result)


class LogProcessor(DataProcessor):
    """Processor specialized in handling log entries."""

    def validate(self, data: Any) -> bool:
        if not isinstance(data, str):
            return False
        return (
            data.startswith("ERROR")
            or data.startswith("INFO")
            or data.startswith("WARNING")
        )

    def process(self, data: Any) -> str:
        if not self.validate(data):
            raise ValueError("Invalid log entry")
        level, _, message = data.partition(":")
        level = level.strip()
        message = message.strip()
        if level == "ERROR":
            tag = "[ALERT]"
        elif level == "WARNING":
            tag = "[WARN]"
        else:
            tag = "[INFO]"
        result = f"{tag} {level} level detected: {message}"
        return self.format_output(result)


def main() -> None:
    print("=== CODE NEXUS - DATA PROCESSOR FOUNDATION ===")
    print("Initializing Numeric Processor...")
    numeric = NumericProcessor()
    data_num = [1, 2, 3, 4, 5]
    print(f"Processing data: {data_num}")
    try:
        print("Validation: Numeric data verified")
        print("Output:", numeric.process(data_num))
    except Exception as e:
        print("Error:", e)
    print("Initializing Text Processor...")
    text = TextProcessor()
    data_text = "Hello Nexus World"
    print(f'Processing data: "{data_text}"')
    try:
        print("Validation: Text data verified")
        print("Output:", text.process(data_text))
    except Exception as e:
        print("Error:", e)
    print("Initializing Log Processor...")
    log = LogProcessor()
    data_log = "ERROR: Connection timeout"
    print(f'Processing data: "{data_log}"')
    try:
        print("Validation: Log entry verified")
        print("Output:", log.process(data_log))
    except Exception as e:
        print("Error:", e)
    print("=== Polymorphic Processing Demo ===")
    print("Processing multiple data types through same interface...")
    processors: List[DataProcessor] = [
        NumericProcessor(),
        TextProcessor(),
        LogProcessor()
    ]
    batch_data = [
        [1, 2, 3],
        "Hello World!",
        "INFO: System ready"
    ]
    for count, (processor, data) in enumerate(zip(processors,
                                              batch_data), start=1):
        try:
            result = processor.process(data)
            print(f"Result {count}: {result}")
        except Exception as e:
            print(f"Result {count}: Error - {e}")
    print("Foundation systems online. Nexus ready for advanced streams.")


if __name__ == "__main__":
    main()
