from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, model_validator


class ContactType(Enum):
    radio = "radio"
    visual = "visual"
    physical = "physical"
    telepathic = "telepathic"


class AlienContact(BaseModel):
    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_business_rules(self):
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC'")
        if (
            self.contact_type == ContactType.physical
            and not self.is_verified
        ):
            raise ValueError("Physical contact reports must be verified")
        if (
            self.contact_type == ContactType.telepathic
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )
        if (
            self.signal_strength > 7.0
            and not self.message_received
        ):
            raise ValueError(
                "Strong signals (>7.0) require a received message"
            )
        return self


def main() -> None:
    print("\n=== Alien Contact Log Validation ===\n")
    valid = AlienContact(
        contact_id="AC_2024_001",
        timestamp="2024-05-01T12:00:00",
        location="Area 51, Nevada",
        contact_type="radio",
        signal_strength=8.5,
        duration_minutes=45,
        witness_count=5,
        message_received="Greetings from Zeta Reticuli",
    )
    print("Valid contact report:")
    print(valid)
    print("\nExpected validation error:\n")
    try:
        AlienContact(
            contact_id="AC_BAD",
            timestamp="2024-05-01T12:00:00",
            location="Mars Base",
            contact_type="telepathic",
            signal_strength=5.0,
            duration_minutes=10,
            witness_count=1,
        )
    except Exception as err:
        print(err)


if __name__ == "__main__":
    main()
