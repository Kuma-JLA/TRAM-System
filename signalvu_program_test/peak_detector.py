import pyvisa as visa
from csv import writer
import matplotlib.pyplot as plt

# VISAリソースマネージャーの作成
rm = visa.ResourceManager()

# SignalVu-PCに接続
rsa = rm.open_resource('GPIB8::1::INSTR')
rsa.timeout = 10000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'

# デバイス情報の取得と表示
print(rsa.query('*idn?'))

# 測定前のリセットとクリア
rsa.write('*rst')
rsa.write('*cls')
rsa.write('abort')

# スペクトラムアナライザーの設定
freq = 2e9
span = 40e6
rbw = 100
refLevel = -50

# 設定の反映
rsa.write('spectrum:frequency:center {}'.format(freq))
rsa.write('spectrum:frequency:span {}'.format(span))
rsa.write('spectrum:bandwidth {}'.format(rbw))
rsa.write('input:rlevel {}'.format(refLevel))

# 実際の設定値の取得と表示
actualFreq = float(rsa.query('spectrum:frequency:center?'))
actualSpan = float(rsa.query('spectrum:frequency:span?'))
actualRbw = float(rsa.query('spectrum:bandwidth?'))
actualRefLevel = float(rsa.query('input:rlevel?'))

print('CF: {} Hz'.format(actualFreq))
print('Span: {} Hz'.format(actualSpan))
print('RBW: {} Hz'.format(actualRbw))
print('Reference Level: {}'.format(actualRefLevel))
print()  # 改行

# トリガーをオフにして、連続測定モードをオフに設定
rsa.write('trigger:status off')
rsa.write('initiate:continuous off')

# データ取得と処理
rsa.write('calculate:marker:add')
peakFreq = []
peakAmp = []

# CSVファイルに書き込む準備
with open('peak_detector.csv', 'w') as f:
    w = writer(f, lineterminator='\n')  # 改行コードの指定
    w.writerow(['Frequency', 'Amplitude'])  # ヘッダー行の書き込み

    # 測定ループ
    for i in range(10):
        rsa.write('initiate:immediate')
        rsa.query('*opc?')

        # マーカー0で最大値を計算し、周波数と振幅を取得
        rsa.write('calculate:spectrum:marker0:maximum')
        peakFreq.append(float(rsa.query('calculate:spectrum:marker0:X?')))
        peakAmp.append(float(rsa.query('calculate:spectrum:marker0:Y?')))
        
        # CSVファイルにデータを書き込み
        w.writerow([peakFreq[i], peakAmp[i]])

# 散布図の作成と表示
plt.scatter(peakFreq, peakAmp)
plt.title('Scatter Plot of Amplitude vs Frequency')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Amplitude (dBm)')
plt.xlim((freq - span / 2), (freq + span / 2))
plt.ylim(refLevel, refLevel - 100)
plt.show()

# 接続のクローズ
rsa.close()
