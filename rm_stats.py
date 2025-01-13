#!/usr/bin/env python3

import asyncio
from datetime import datetime

from dotenv import dotenv_values

from librootme.api import RootMeAPI
from librootme.constants import Language

CONFIG = dotenv_values(verbose=True)


async def main() -> None:
    api_key = CONFIG.get("API_KEY")
    assert api_key is not None, "API_KEY is not set in .env file"

    rm_api = RootMeAPI(api_key, lang=Language.EN)

    username = "Demat"
    user = await rm_api.get_author_by_name(username)
    if user is None:
        print(f"{username} not found")
        return
    print(user)
    print()
    print(user.pretty())
    print()

    for val in sorted(user.validations, key=lambda x: x.date):
        print(f"{val.date} - {val.titre} [{val.id_rubrique}] (#{val.id_challenge})")

    start_date = datetime(2024, 9, 20)
    print()
    print(
        f"Since {start_date.date()}: {len([val for val in user.validations if val.date >= start_date])} validations"
    )


if __name__ == "__main__":
    asyncio.run(main())
