from pathlib import Path
import os
from watchgod import awatch
import asyncio
import shutil

base_dir = Path(__file__).parent.absolute()
sphinx_dir_src = base_dir.joinpath('docs/source').absolute()
sphinx_dir = base_dir.joinpath('docs').absolute()
app_dir = base_dir.joinpath('dictify').absolute()
os.chdir(sphinx_dir)


async def make():
    await asyncio.create_subprocess_shell('make html')


async def py_watch():
    async for change in awatch(app_dir):
        await asyncio.create_subprocess_shell('make html')
        

async def sphinx_dir_src_watch():
    async for change in awatch(sphinx_dir_src):
        await asyncio.create_subprocess_shell('make html')


async def bits_ui():
    src_dir = base_dir.joinpath('node_modules/bits-ui/dist/')
    dest_dir = base_dir.joinpath('docs/build/html/_static/lib/bits-ui/')
    try:
        shutil.rmtree(dest_dir)
    except FileNotFoundError:
        pass
    shutil.copytree(src_dir, dest_dir)


async def bits_ui_stylus():
    src = base_dir.joinpath('docs/source/bits-ui/bits-ui.styl')
    dest = base_dir.joinpath('docs/build/html/_static/bits-ui/bits-ui.css')
    await asyncio.create_subprocess_shell(f'stylus {src} -o {dest}')

    async for change in awatch(src.parent.absolute()):
        await asyncio.create_subprocess_shell(f'stylus {src} -o {dest}')


async def main():
    await asyncio.gather(
        make(), py_watch(), sphinx_dir_src_watch(), bits_ui(), bits_ui_stylus()
    )

asyncio.run(main())
