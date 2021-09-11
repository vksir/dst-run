import shlex
import subprocess
from typing import List

from constants import *


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


def _get_option_value(title: str, block_dict: dict = None) -> str:
    """get option value

    block_dict: {title: {option: value}}

    :return value
    """

    option_exit = {EXIT_KEY: EXIT}
    if OTHERS_KEY in block_dict:
        block_dict[OTHERS_KEY].update(option_exit)
    else:
        block_dict[OTHERS_KEY] = option_exit

    max_len = 0
    for title, option_dict in block_dict.items():
        max_len = max(max_len, len(title))
        for option in option_dict:
            max_len = max(max_len, len(option))
    max_len += 10

    print(title)
    index = 1
    value_lst = []
    for title, option_dict in block_dict.items():
        seq_line = '-' * ((max_len - len(title) - 2) // 2)
        print('{0} {1} {0}'.format(seq_line, title))
        for option, value in option_dict.items():
            value_lst.append(value)
            if option == EXIT_KEY:
                print(f'  (e) Exit')
            else:
                print(f'  ({index}) {option}')
            index += 1
    index -= 2
    print(f'Input your choice(1~{index}): ', end='')

    while True:
        choice = input()
        if choice.lower() in ['e', 'exit']:
            return CHOICE_EXIT
        if choice == '':
            return CHOICE_DEFAULT
        try:
            choice = int(choice)
            if choice < 1 or choice > index:
                raise ValueError
            break
        except ValueError:
            print('Invalid input. Input again: ', end='')
    choice -= 1
    return value_lst[choice]


def _get_yes_or_no(title: str, expect_choice: bool) -> bool:
    print(f'{title}\n'
          f'  (Y)es\n'
          f'  (N)o\n'
          f'Input y or n: ', end='')
    choice = input().lower()
    if expect_choice:
        return CHOICE_YES if choice not in ['n', 'no'] else CHOICE_NO
    else:
        return CHOICE_NO if choice not in ['y', 'yes'] else CHOICE_YES


def get_choice(title: str, block_dict: dict = None, expect_choice=False):
    """get choice

    block_dict: {title: {option: value}}

    :return: option_value, CHOICE_DEFAULT, CHOICE_EXIT
    :return: CHOICE_YES, CHOICE_NO
    """

    if block_dict:
        return _get_option_value(title, block_dict)
    else:
        return _get_yes_or_no(title, expect_choice)


class Executor:

    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        self._func(*self._args, **self._kwargs)
