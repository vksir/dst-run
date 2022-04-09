import json

from dst_run.common.utils import run_cmd


class FileLib:
    @staticmethod
    def remove(path: str):
        run_cmd(f'rm -rf {path}')

    @staticmethod
    def copy(src: str, dst: str):
        run_cmd(f'cp -rf {src} {dst}')

    @staticmethod
    def move(src: str, dst: str):
        run_cmd(f'mv -f {src} {dst}')

    @staticmethod
    def read(path, is_json=False):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return json.loads(content) if is_json else content


