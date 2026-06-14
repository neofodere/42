from datetime import datetime
from pydantic import BaseModel, Field


class SpaceStation(BaseModel):
    station_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=1, max_length=50)
    crew_size: int = Field(ge=1, le=20)
    power_level: float = Field(ge=0.0, le=100.0)
    oxygen_level: float = Field(ge=0.0, le=100.0)
    last_maintenance: datetime
    is_operational: bool = True
    notes: str | None = Field(default=None, max_length=200)


def main() -> None:
    print("\n=== Space Station Data Validation ===\n")
    valid_station = SpaceStation(
        station_id="ISS001",
        name="International Space Station",
        crew_size=6,
        power_level=85.5,
        oxygen_level=92.3,
        last_maintenance="2024-01-15T10:00:00",
    )
    print("Valid station created:")
    print(valid_station)
    print("\nExpected validation error:\n")
    try:
        SpaceStation(
            station_id="BAD",
            name="Too Many People",
            crew_size=50,
            power_level=50,
            oxygen_level=50,
            last_maintenance="2024-01-01T00:00:00",
        )
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
