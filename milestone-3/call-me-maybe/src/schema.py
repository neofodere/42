"""Pydantic data models used across the function-calling pipeline.

Every class that carries structured data in this project goes through
pydantic validation, as required by the project specification (see
"Requisitos adicionales" in the assignment PDF: "Todas las clases deben
usar pydantic para validacion.").
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

# JSON-schema-like primitive types we know how to constrain-decode.
SupportedType = Literal["number", "integer", "string", "boolean"]


class ParameterSpec(BaseModel):
    """Describes a single argument of a callable function.

    Attributes:
        type: The primitive JSON type expected for this argument.
    """

    type: SupportedType

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, value: Any) -> Any:
        """Lowercase the type string so "Number"/"NUMBER" also work."""
        if isinstance(value, str):
            return value.lower()
        return value


class ReturnSpec(BaseModel):
    """Describes the return type of a callable function."""

    type: SupportedType

    @field_validator("type", mode="before")
    @classmethod
    def _normalize_type(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.lower()
        return value


class FunctionDefinition(BaseModel):
    """A single entry of ``function_definitions.json``.

    Attributes:
        name: The callable function's identifier (e.g. ``fn_add_numbers``).
        description: Human readable description, used to build the prompt.
        parameters: Mapping of argument name to its :class:`ParameterSpec`.
        returns: The function's return type.
    """

    name: str
    description: str = ""
    parameters: dict[str, ParameterSpec] = Field(default_factory=dict)
    returns: ReturnSpec | None = None


class FunctionCallResult(BaseModel):
    """A single entry of the produced ``function_calling_results.json``.

    Attributes:
        prompt: The original natural language request.
        fn_name: The name of the function chosen by the model.
        args: The generated arguments, already type-coerced.
    """

    prompt: str
    fn_name: str
    args: dict[str, Any]
