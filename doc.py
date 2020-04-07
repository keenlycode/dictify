from pathlib import Path
import os
from watchgod import awatch
import asyncio

sphinx_doc_dir = Path(__file__).parent.joinpath('docs').absolute()
app_dir = Path(__file__).parent.joinpath('dictify').absolute()
os.chdir(sphinx_doc_dir)


async def start():
    await asyncio.create_subprocess_shell('make html')


async def py_watch():
    async for change in awatch(str(app_dir)):
        await asyncio.create_subprocess_shell('make html')
        

async def sphinx_watch():
    async for change in awatch(str(sphinx_doc_dir)):
        await asyncio.create_subprocess_shell('make html')


async def main():
    await asyncio.gather(
        start(), py_watch(), sphinx_watch()
    )

asyncio.run(main())
