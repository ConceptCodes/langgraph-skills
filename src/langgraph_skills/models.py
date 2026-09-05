from typing import Optional

from langchain_core.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field


class SkillMetadata(BaseModel):
    name: str
    description: str
    version: Optional[str] = "1.0.0"
    tags: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)


class Skill(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    metadata: SkillMetadata
    instructions: str
    tools: list[BaseTool] = Field(default_factory=list)
