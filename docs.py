import asyncio
from pathlib import Path
import shutil


_dir = Path(__file__).parent


async def lib():
    shutil.copytree(
        _dir.joinpath('node_modules/adwaita-icon-web/dist/'),
        _dir.joinpath('docs/lib/adwaita-icon-web/'),
        dirs_exist_ok=True
    )


async def docs():
    src_dir = _dir.joinpath('docs-src')
    dest_dir = _dir.joinpath('docs')
    cmd = f'engrave dev --server=127.0.0.1:8000 {src_dir} {dest_dir}'
    proc = await asyncio.create_subprocess_shell(cmd)
    print(cmd)
    await proc.communicate()


async def main():
    await asyncio.gather(
        lib(),
        docs(),
    )


asyncio.run(main())