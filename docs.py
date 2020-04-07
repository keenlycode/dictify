from pathlib import Path
import os
from watchgod import awatch
import asyncio

sphinx_dir_src = Path(__file__).parent.joinpath('docs/source').absolute()
sphinx_dir = Path(__file__).parent.joinpath('docs').absolute()
app_dir = Path(__file__).parent.joinpath('dictify').absolute()
os.chdir(sphinx_dir)


async def start():
    await asyncio.create_subprocess_shell('make html')


async def py_watch():
    async for change in awatch(app_dir):
        await asyncio.create_subprocess_shell('make html')
        

async def sphinx_dir_src_watch():
    async for change in awatch(sphinx_dir_src):
        await asyncio.create_subprocess_shell('make html')


async def main():
    await asyncio.gather(
        start(), py_watch(), sphinx_dir_src_watch()
    )

asyncio.run(main())
