import shlex
import subprocess
from typing import List


def run_cmd(*cmd: str, cwd=None, sudo=False, block=True) -> List[subprocess.Popen]:
    proc = []
    for i in cmd:
        if sudo:
            i += 'sudo '
        if block:
            p = subprocess.Popen(shlex.split(i), cwd=cwd)
            p.wait()
        else:
            p = subprocess.Popen(shlex.split(i), cwd=cwd, encoding='utf-8',
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 stdin=None)
            proc.append(p)
    if proc:
        return proc


def get_choose(info: dict, expect_no=True) -> int:
    """get choose

    :param info: {
        'title': str,
        'blocks': [{'title': str, 'chooses': [str]}],
        'end': str
    }
    :param expect_no
    :return: index, 0(default), -1(exit)
    """

    print(info['title'])
    if 'blocks' in info:
        max_len = max(max(len(i['title']) for i in info['blocks']),
                      max([max([len(j) for j in i['chooses']]) for i in info['blocks']])) + 10
        index = 1
        for block in info['blocks']:
            print('{0} {1} {0}'.format('-' * ((max_len - len(block['title']) - 2) // 2),
                                       block['title']))
            for choose in block['chooses']:
                print('  ({}) {}'.format(index, choose))
                index += 1
        print('Input your choice(1~{}): '.format(index - 1), end='')
        while True:
            user_in = input()
            if user_in in ['e', 'exit']:
                return -1
            if user_in == '':
                return 0
            try:
                user_in = int(user_in)
                break
            except ValueError:
                print('Invalid input. Input again: ', end='')
        return user_in
    else:
        print('  (Y)es\n'
              '  (N)o\n'
              'Input y or n: ', end='')
        user_in = input()
        if expect_no:
            return 2 if user_in not in ['Y', 'y'] else 1
        else:
            return 1 if user_in not in ['N', 'n'] else 2
