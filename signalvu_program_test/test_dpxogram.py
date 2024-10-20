"""
DPXogramを表示
"""

import pyvisa

# signalvu と接続
rm = pyvisa.ResourceManager()
rsa = rm.open_resource('GPIB8::1::INSTR')
rsa.timeout = 10000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print('Connected to', rsa.query('*idn?'))

rsa.write('*rst') # reset
rsa.write('*cls') # clear status
rsa.write('abort') # abort 実行中の測定を中止

# 測定パラメータの設定
cf = 920e6
span = 40e6

# DPX測定の設定
rsa.write('display:general:measview:new DPX')
# DISPlay:GENeral:MEASview<y>[:SOURce<x>]:NEW  Displays a new measurement view.
rsa.write('dpx:frequency:center {}'.format(cf))
rsa.write('dpx:frequency:span {}'.format(span))

# 測定開始
rsa.write('initiate:immediate')
rsa.query('*opc?')

rsa.close()