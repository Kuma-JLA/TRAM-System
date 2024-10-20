import pyvisa

# VISAリソースマネージャーを作成
rm = pyvisa.ResourceManager()

# 利用可能なリソースを一覧表示
resources = rm.list_resources()
print("Available VISA resources:")
for resource in resources:
    print(resource)