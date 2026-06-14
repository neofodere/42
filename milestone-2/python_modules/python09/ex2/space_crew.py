from datetime import datetime
from enum import Enum
from typing import List
from pydantic import BaseModel, Field, model_validator


class Rank(Enum):
    cadet = "cadet"
    officer = "officer"
    lieutenant = "lieutenant"
    captain = "captain"
    commander = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: List[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission(self):
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")
        if not any(
            c.rank in {Rank.captain, Rank.commander}
            for c in self.crew
        ):
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )
        if self.duration_days > 365:
            experienced = sum(
                c.years_experience >= 5
                for c in self.crew
            )
            if experienced < len(self.crew) / 2:
                raise ValueError(
                    "Long missions require 50% experienced crew"
                )
        if not all(
            c.is_active
            for c in self.crew
        ):
            raise ValueError(
                "All crew members must be active"
            )
        return self


def main() -> None:
    print("\n=== Space Mission Crew Validation ===\n")
    crew = [
        CrewMember(member_id="C001", name="Sarah Connor", rank="commander",
                   age=40, specialization="Command", years_experience=15),
        CrewMember(member_id="C002", name="John Smith", rank="lieutenant",
                   age=32, specialization="Navigation", years_experience=8),
        CrewMember(member_id="C003", name="Alice Johnson", rank="officer",
                   age=29, specialization="Engineering", years_experience=6),
    ]
    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date="2024-06-01T09:00:00",
        duration_days=900,
        crew=crew,
        budget_millions=2500.0,
    )
    print("Valid mission created:")
    print(mission)
    print("\nExpected validation error:\n")
    try:
        SpaceMission(
            mission_id="BAD123",
            mission_name="Invalid Mission",
            destination="Moon",
            launch_date="2024-01-01T00:00:00",
            duration_days=100,
            crew=[
                CrewMember(member_id="X1", name="Bob", rank="cadet",
                           age=20, specialization="Tech", years_experience=1)
            ],
            budget_millions=10.0,
        )
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
