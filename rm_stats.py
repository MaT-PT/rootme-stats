#!/usr/bin/env python3

import asyncio

from dotenv import dotenv_values

from librootme.api import RootMeAPI
from librootme.datamodel import ChallengeShort, Language

CONFIG = dotenv_values(verbose=True)


async def main() -> None:
    api_key = CONFIG.get("API_KEY")
    assert api_key is not None, "API_KEY is not set in .env file"

    rm_api = RootMeAPI(api_key, lang=Language.EN)

    async for author_short in rm_api.iter_authors("ToG"):
        print(author_short)

    author = await rm_api.get_author_by_name("ToG")
    if author is not None:
        print(author)
        print()
        print(author.pretty())
        print()

    authors = await rm_api.get_authors(name="Demat")
    print(authors)
    print()
    author = await rm_api.get_author(authors[-1])
    print(author)
    print()
    print(author.pretty())
    print()

    challenges = await rm_api.get_challenges(titre="WinKern", lang=Language.FR)
    print(challenges)
    print()

    async for chall_short in rm_api.iter_list_elements(challenges):
        challenge = await rm_api.get_challenge(chall_short.as_type(ChallengeShort))
        print(challenge)
        print()
        print(challenge.pretty())
        print()


if __name__ == "__main__":
    asyncio.run(main())
