from enum import Enum


class Nodes(str, Enum):
    AGENT = "agent"
    ROUTER = "router"
    TOOLS = "tools"
