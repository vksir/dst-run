import re
import sys

mod_overrides_path = sys.argv[1]
mod_setup_path = sys.argv[2]

with open(mod_overrides_path, 'r', encoding='utf-8') as f:
        data = f.read()
mod = re.findall(r'(?<=\[\"workshop-).*?(?=\"\])', data)
# print(mod)

with open(mod_setup_path, 'w') as f:
        for i in mod:
                f.write('ServerModSetup("' + i + '")\n')
