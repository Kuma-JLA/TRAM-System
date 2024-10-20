"""
spectrogramデータを出力
"""

import pyvisa
import time

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
rbw = 1e3



# spectrogram 表示
rsa.write('display:general:measview:new sgram')

# パラメータ反映
rsa.write('sgram:frequency:center {}'.format(cf))
rsa.write('sgram:frequency:span {}'.format(span))
rsa.write('sgram:bandwidth {}'.format(rbw))


# 測定開始
rsa.write('initiate:immediate')
rsa.query('*opc?')

# 一定時間待機
time.sleep(120)

# 測定終了
rsa.write('initiate:continuous off') 


for i in range(4):
    div = 0
    div = div + 20*i
    rsa.write('display:sgram:time:offset:divisions {}'.format(div))
    rsa.write('mmemory:store:results "sample_sgram_div{}.csv"'.format(div))
    time.sleep(3)




rsa.close()

# 下端位置変更
# rsa.write('display:sgram:time:offset:divisions 20') 