import re
import sys

mod_overrides_path = sys.argv[1]
mod_kind = sys.argv[2]

# mod_overrides_path = '1.lua'
# mod_kind = 'modid'

with open(mod_overrides_path, 'r', encoding='utf-8') as f:
    mods_1 = re.findall(r'(?<={).*(?=})', f.read(), re.S)[0]

if mod_kind == 'modoverrides':
    data = ''
    r = ''
    while r != '}':
        r = input()
        data += r + '\n'
    mods_2 = re.findall(r'(?<={).*(?=})', data, re.S)[0]

    with open(mod_overrides_path, 'w', encoding='utf-8') as f:
        f.write('return {%s,\n%s}' % (mods_1, mods_2))
elif mod_kind == 'modid':
    mod_list = input().split()
    mods_2 = ''
    for i in mod_list[: -1]:
        mods_2 += '  ["workshop-%s"]={ configuration_options={ }, enabled=true },\n' % i
    mods_2 += '  ["workshop-%s"]={ configuration_options={ }, enabled=true }\n' % mod_list[-1]

    with open(mod_overrides_path, 'w', encoding='utf-8') as f:
        f.write('return {%s,\n%s}' % (mods_1, mods_2))