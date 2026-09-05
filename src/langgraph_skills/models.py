from typing import Any, Optional

from pydantic import BaseModel, Field


class SkillMetadata(BaseModel):
    name: str
    description: str
    version: Optional[str] = "1.0.0"
    tags: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class Skill(BaseModel):
    metadata: SkillMetadata
    instructions: str
    tools: list[Any] = Field(default_factory=list)
