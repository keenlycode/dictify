from pathlib import Path
import subprocess
import os
from watchgod import arun_process
import asyncio

sphinx_doc_dir = Path(__file__).parent.joinpath('sphinx-doc').absolute()
app_dir = Path(__file__).parent.joinpath('dictify').absolute()
os.chdir(sphinx_doc_dir)

subprocess.run(['make', 'html'])


async def main():
    await arun_process(app_dir, lambda: subprocess.run(['make', 'html']))

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
