import os
from regipy.registry import RegistryHive
reg_path = "test/windows/sam/sam"
# reg = RegistryHive(reg_path)
# 逐行打印注册表文件的内容
# for entry in reg.recurse_subkeys(as_json=True):
#     print(entry)
# 导出为json
output_file = reg_path + ".json"
os.system("registry-dump -t {} -o {}".format(reg_path, output_file))