import asyncio

import twitchio

CLIENT_ID: str = "lrr9pig28ku70m2288ky18qwotlqkd"
CLIENT_SECRET: str = "vnadmqrb3egmsbb0npl89zijmv8ter"


async def main() -> None:
    async with twitchio.Client(client_id=CLIENT_ID, client_secret=CLIENT_SECRET) as client:
        await client.login()
        user = await client.fetch_users(logins=["pororangerblack", "milkiiubot"])
        for u in user:
            print(f"User: {u.name} - ID: {u.id}")


if __name__ == "__main__":
    asyncio.run(main())
