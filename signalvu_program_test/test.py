import pyvisa

# VISAリソースマネージャーを作成
rm = pyvisa.ResourceManager()

# SignalVu-PCのVISAリソース名を指定
# 例: TCPIP0::192.168.0.10::INSTR のような形式
resource_name = 'GPIB8::1::INSTR'

# SignalVu-PCに接続
instrument = rm.open_resource(resource_name)

# コマンドを送信
response = instrument.query('*IDN?')

# 結果を表示
print('Response:', response)

instrument.write('MMEMory:STORe:RESults sample1.csv')

# 接続を閉じる
instrument.close()