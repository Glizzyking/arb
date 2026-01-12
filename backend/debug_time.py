
import pytz
from datetime import datetime, timedelta
import sys
import os

# Mock the settings and classes for a quick test
DEFAULT_SETTINGS = {"timezone": "US/Eastern"}

class MockMarketURLGenerator:
    def __init__(self, timezone: str = None):
        self.tz = pytz.timezone(timezone or DEFAULT_SETTINGS["timezone"])
    
    def get_current_time(self) -> datetime:
        return datetime.now(self.tz)
    
    def get_target_hours(self, current_hour_offset: int = 0):
        now = self.get_current_time()
        print(f"DEBUG: Current time in {self.tz}: {now}")
        current_hour_start = now.replace(minute=0, second=0, microsecond=0)
        print(f"DEBUG: Current hour start: {current_hour_start}")
        target_start = current_hour_start + timedelta(hours=current_hour_offset)
        print(f"DEBUG: Target start (offset={current_hour_offset}): {target_start}")
        return target_start

if __name__ == "__main__":
    gen = MockMarketURLGenerator()
    print("--- Testing Offset 0 ---")
    gen.get_target_hours(0)
    print("\n--- Testing Offset 1 ---")
    gen.get_target_hours(1)
