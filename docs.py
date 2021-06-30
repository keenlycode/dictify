import asyncio
from pathlib import Path


_dir = Path(__file__).parent


async def main():
    src_dir = _dir.joinpath('docs-src')
    dest_dir = _dir.joinpath('docs')
    cmd = f'engrave dev --server=0.0.0.0:8000 {src_dir} {dest_dir}'
    proc = await asyncio.create_subprocess_shell(cmd)
    print(cmd)
    await proc.communicate()


asyncio.run(main())