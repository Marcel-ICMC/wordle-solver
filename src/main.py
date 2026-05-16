import asyncio

from adapters import TermoAdapter
from agent import Agent
from exceptions import InvalidWordError
from game import Game


async def play() -> Agent:
    agent = Agent()

    guess = agent.make_guess("What's your first guess?")

    termo = await TermoAdapter.create()

    game = Game(game_adapter=termo)

    try:
        await game.guess(guess)
        result = f"{guess} wasn't the correct word!"
    except InvalidWordError as e:
        result = f"{guess} doesn't exist in the dataset, got message {e}"

    while game.result == 0:
        response = f"""
        {result}
        Remaining: {" ".join(sorted(list(game.remaining)))}
        Known Positions: {" ".join(game.known_positions)}
        Misplaced but in word: {str(game.misplaced)}

        You still have {6 - game.word_index} remaining
        """

        guess = agent.make_guess(response)
        try:
            await game.guess(guess)
            result = f"{guess} wasn't the correct word!"
        except InvalidWordError as e:
            result = f"{guess} doesn't exist in the dataset, got message {e}"
    agent.print_agent_history()

    return agent


async def main() -> int:
    await play()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
