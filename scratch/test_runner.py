import asyncio
import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from agent.orchestration import AcademicCommanderRunner

async def test():
    runner = AcademicCommanderRunner()
    res = await runner.run("hello")
    print("RESULT:", res)
    for k, v in res.items():
        print(f"{k}: {type(v)}")

asyncio.run(test())
