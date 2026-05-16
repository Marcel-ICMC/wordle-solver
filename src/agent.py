from typing import Any

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pydantic import BaseModel, Field, field_validator


class Guess(BaseModel):
    guess: str = Field(
        default="",
        description="5 letter word that corresponds to your next guess in the wordle or termo game, this should contain only 5 letters",
    )
    logic: str | None = Field(
        default=None, description="Reasoning behind the guess made"
    )

    @field_validator("guess", mode="before")
    @classmethod
    def normalize_guess(cls, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError("guess must be a string")

        guess = "".join(value.split()).upper()

        if len(guess) != 5 or not guess.isalpha():
            raise ValueError("guess must be exactly 5 letters")

        return guess


class Agent:
    def __init__(
        self,
        model: str = "groq:openai/gpt-oss-120b",
    ):
        self.config: RunnableConfig = {"configurable": {"thread_id": "termo-game-2"}}
        self.agent = create_agent(
            model=model,
            system_prompt="""
                You are playing term.ooo, the Brazilian Portuguese version of Wordle.
                Your task is to choose the next 5-letter Brazilian Portuguese word guess.
                Respond only in this JSON format:
                {"guess":"PALAV","logic":"Brief explanation of why this guess fits the clues."}
                Game rules:
                1. The answer is always exactly 5 letters.
                2. You have up to 6 guesses.
                3. After each guess, you will receive feedback.
                Feedback example:
                
                "ESTAR wasn't the correct word!
                Remaining: b c d f g h i j k l m n o p q r s t u v w x y z
                Known Positions: _ _ T _ _
                Misplaced but in word: {'R': {4}}

                You still have 5 remaining"

                How to interpret the feedback:
                - Remaining:
                    These are letters that have not yet been guessed. This is NOT the full set of allowed letters. Letters already confirmed as present may be missing from this list.
                - Known Positions:
                    These letters are fixed in the answer at those exact positions.
                    Example: `_ _ T _ _` means the answer has `T` at index 2.
                - Misplaced but in word:
                    These letters are definitely in the answer, but NOT at the listed positions.
                    This is very important: the listed positions are forbidden positions, not correct positions.
                    Example: `{'R': {4}}` means `R` is in the answer, but `R` cannot be at index 4.
                    Indexes are zero-based:
                    0 = first letter, 1 = second, 2 = third, 3 = fourth, 4 = fifth.
            """,
            response_format=ProviderStrategy(Guess),
            checkpointer=InMemorySaver(
                serde=JsonPlusSerializer(allowed_msgpack_modules=[("agent", "Guess")])
            ),
        )

    def make_guess(self, message: str) -> str:
        result = self.agent.invoke(
            {"messages": [HumanMessage(content=message)]}, config=self.config
        )

        response: Guess = result["structured_response"]
        return response.guess

    def print_agent_history(self) -> None:
        state = self.agent.get_state(self.config)
        messages = state.values["messages"]
        for message in messages:
            message.pretty_print()
