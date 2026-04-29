from langchain.agents import create_agent
from langchain_core.runnables import Runnable
from pydantic import BaseModel, Field


class Guess(BaseModel):
    guess: str = Field(
        description="5 letter word that corresponds to your next guess in the wordle or termo game"
    )
    logic: str | None = Field(
        default=None, description="Reasoning behing the guess made"
    )


def start_agent() -> Runnable:
    return create_agent(
        model="groq:qwen/qwen3-32b",
        system_prompt="""
        You're playing a term.ooo game, which is a Brazilian Portuguese version of Wordle.
        To play all you need to do is respond with your next guess, you'll receive a feed on how that guess did.
        Here's a reminder on how the Wordle game works:
        1. Each letter is 5-letter only
        2. You have 6 guesses, if you're able to find the correct word by then you win and lose if not.
        3. Here's the format you'll get after each guess:
            Known Positions: "_ _ _ A _"
            Misplaced: ["O": [2]]
            Remaining: 
        
        Where Known Positions are the correct letter in it's correct positions
        Misplaced means that letter is in the answer but not in the correct position
        Remaining are the remaining letters left unguessed
        """,
        response_format=Guess,
    )
