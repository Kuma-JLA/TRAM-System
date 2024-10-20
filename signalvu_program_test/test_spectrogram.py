import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import time

def fetch_spectrogram_data(instrument, num_traces):
    spectrogram_data = []
    for _ in range(num_traces):
        # 測定データの取得 (例：TRACE1)
        try:
            data = instrument.query(':TRACe:DATA? TRACE1')
            data_list = data.split(',')
            data_array = np.array(data_list, dtype=float)
            spectrogram_data.append(data_array)
            
            # 適切な遅延を挿入
            time.sleep(0.5)
        except pyvisa.VisaIOError as e:
            print(f"Error fetching data: {e}")
            continue

    return np.array(spectrogram_data)

try:
    # VISAリソースマネージャーを作成
    rm = pyvisa.ResourceManager()

    # SignalVu-PCのVISAリソース名を指定
    resource_name = 'GPIB8::1::INSTR'

    # SignalVu-PCに接続
    instrument = rm.open_resource(resource_name)

    # タイムアウトを設定 (30000ミリ秒)
    instrument.timeout = 30000

    # デバイス情報の取得 (接続確認)
    response = instrument.query('*IDN?')
    print('Device Information:', response)

    # 測定設定の送信 (周波数範囲の設定など)
    instrument.write('SPEC:FREQ:START 1GHz')
    time.sleep(1)  # コマンド間に遅延を挿入
    instrument.write('SPEC:FREQ:STOP 2GHz')
    time.sleep(1)
    instrument.write(':INIT:IMM')
    time.sleep(1)

    # スペクトログラムデータの取得
    num_traces = 100  # 取得するトレースの数
    spectrogram_data = fetch_spectrogram_data(instrument, num_traces)

    # スペクトログラムのプロット
    plt.imshow(spectrogram_data, aspect='auto', cmap='inferno', origin='lower')
    plt.colorbar(label='Power (dBm)')
    plt.xlabel('Frequency Bin')
    plt.ylabel('Trace Number')
    plt.title('Spectrogram')
    plt.show()

    # スペクトログラムデータの保存
    np.savetxt('spectrogram_data.csv', spectrogram_data, delimiter=',')

except pyvisa.VisaIOError as e:
    print(f"VISA I/O error occurred: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # 接続を閉じる
    if 'instrument' in locals():
        instrument.close()
