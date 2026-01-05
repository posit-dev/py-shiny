import asyncio
from dataclasses import dataclass
from functools import wraps


def cache_result(func):
    """Decorator to cache function results."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@dataclass
class DataProcessor:
    """Process and analyze data with async support."""

    name: str
    threshold: float = 0.75

    @cache_result
    async def process(self, values: list[float]) -> dict:
        """Process values and return statistics."""
        await asyncio.sleep(0.1)
        filtered = [v for v in values if v > self.threshold]
        return {
            "count": len(filtered),
            "mean": sum(filtered) / len(filtered) if filtered else 0,
            "message": f"Processed {len(values)} items: {100 * 0.85:.1f}%",
        }


if __name__ == "__main__":
    processor = DataProcessor("analyzer", threshold=0.5)
    data = [0.2, 0.8, 0.9, 0.3, 0.95]
