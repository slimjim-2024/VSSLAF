import asyncio

import AgentCore
from AgentCore.engine import start_engine

async def main():
    await start_engine()

if __name__ == '__main__':
    asyncio.run(main())




