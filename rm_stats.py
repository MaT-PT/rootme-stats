#!/usr/bin/env python3

import asyncio

from dotenv import dotenv_values

from rm_api import RootMeAPI
from rm_datamodel import Language

CONFIG = dotenv_values(verbose=True)


async def main() -> None:
    api_key = CONFIG.get("API_KEY")
    assert api_key is not None, "API_KEY is not set in .env file"

    rm_api = RootMeAPI(api_key, lang=Language.EN)

    # authors = await rm_api.get_authors(lang=Language.RU)
    # print(authors)
    # print(len(authors))
    # print("Prev:", authors.prev)
    # print("Next:", authors.next)

    # author = await rm_api.get_author(authors[0].id_auteur)
    # print(author)

    challenges = await rm_api.get_challenges(lang=Language.RU)
    # print(challenges)
    # print(len(challenges))
    # print("Prev:", challenges.prev)
    # print("Next:", challenges.next)

    challenge = await rm_api.get_challenge(challenges[0].id_challenge)
    print(challenge)


if __name__ == "__main__":
    asyncio.run(main())
