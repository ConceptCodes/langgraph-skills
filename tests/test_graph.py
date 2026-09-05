from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.graph import END

from langgraph_skills.agent.main import build_graph, create_agent_app
from langgraph_skills.agent.nodes import should_continue
from langgraph_skills.agent.prompts import get_system_message
from langgraph_skills.agent.state import Context
from langgraph_skills.agent.tools import create_meta_tools
from langgraph_skills.agent.utils import SkillRegistry


class MockModelWithTools:
    def __init__(self, responses, captured_tools_history):
        self.responses = responses
        self.captured_tools_history = captured_tools_history

    def invoke(self, messages):
        if self.responses:
            return self.responses.pop(0)
        return AIMessage(content="Final default response")


class MockLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.captured_tools_history = []

    def bind_tools(self, tools):
        self.captured_tools_history.append([t.name for t in tools])
        return MockModelWithTools(self.responses, self.captured_tools_history)


def test_should_continue_router():
    # When last message has tool calls
    ai_msg_with_tool = AIMessage(
        content="",
        tool_calls=[{"name": "activate_skill", "args": {"skill_name": "math-solver"}, "id": "1"}],
    )
    state = {"messages": [ai_msg_with_tool]}
    assert should_continue(state) == "tools"

    # When last message is normal text
    ai_msg_text = AIMessage(content="Hello there!")
    state_text = {"messages": [ai_msg_text]}
    assert should_continue(state_text) == END


def test_system_prompt_dynamic_sop_injection():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)

    # Base prompt with no active skills
    base_prompt = get_system_message(
        catalog=registry.get_catalog_summary(),
        active_skills=[],
        registry=registry,
    )
    assert "### Available Skills Catalog:" in base_prompt
    assert "ACTIVE SKILLS INSTRUCTIONS" not in base_prompt

    # Prompt with active skill
    active_prompt = get_system_message(
        catalog=registry.get_catalog_summary(),
        active_skills=["text-analyzer"],
        registry=registry,
    )
    assert "### ACTIVE SKILLS INSTRUCTIONS (SOPs):" in active_prompt
    assert "Text Analyzer Operating Procedure" in active_prompt


def test_end_to_end_progressive_disclosure_graph():
    skills_dir = Path(__file__).parent.parent / "skills"
    registry = SkillRegistry(skills_dir)
    meta_tools = create_meta_tools(registry)

    # Prepare scripted mock responses:
    # 1. First turn: Agent sees user query and calls activate_skill("math-solver")
    # 2. Second turn: Agent sees skill activated and calls calculate_expression("15 * 3")
    # 3. Third turn: Agent returns the final synthesized answer
    mock_responses = [
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "activate_skill",
                    "args": {"skill_name": "math-solver"},
                    "id": "call_act_1",
                    "type": "tool_call",
                }
            ],
        ),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "calculate_expression",
                    "args": {"expression": "15 * 3"},
                    "id": "call_calc_2",
                    "type": "tool_call",
                }
            ],
        ),
        AIMessage(content="The calculation result is 45."),
    ]

    mock_llm = MockLLM(mock_responses)
    graph = build_graph(registry, mock_llm, meta_tools)
    context = Context(llm=mock_llm, registry=registry, meta_tools=meta_tools)

    initial_input = {
        "messages": [HumanMessage(content="What is 15 * 3?")],
        "active_skills": [],
        "available_catalog": registry.get_catalog_summary(),
    }

    final_state = graph.invoke(initial_input, context=context)

    # Verify tool bindings over the turns
    # Turn 1: Only meta-tools bound (Layer 1)
    turn1_tools = mock_llm.captured_tools_history[0]
    assert "activate_skill" in turn1_tools
    assert "calculate_expression" not in turn1_tools

    # Turn 2: math-solver tools dynamically bound (Layer 3)
    turn2_tools = mock_llm.captured_tools_history[1]
    assert "activate_skill" in turn2_tools
    assert "calculate_expression" in turn2_tools
    assert "compute_statistics" in turn2_tools

    # Verify final state
    assert "math-solver" in final_state["active_skills"]
    messages = final_state["messages"]

    # Verify messages chain: Human -> AI (activate) -> Tool -> AI (calc) -> Tool -> AI (final)
    assert len(messages) == 6
    assert isinstance(messages[0], HumanMessage)
    assert isinstance(messages[1], AIMessage)
    assert isinstance(messages[2], ToolMessage)
    assert "SUCCESS: Skill 'math-solver' activated" in messages[2].content
    assert isinstance(messages[3], AIMessage)
    assert isinstance(messages[4], ToolMessage)
    assert '"result": 45' in messages[4].content
    assert isinstance(messages[5], AIMessage)
    assert messages[5].content == "The calculation result is 45."


def test_create_agent_app_factory():
    skills_dir = Path(__file__).parent.parent / "skills"
    app, context = create_agent_app(skills_dir)
    assert app is not None
    assert context is not None
    assert "math-solver" in context.registry.skills
    assert "text-analyzer" in context.registry.skills
