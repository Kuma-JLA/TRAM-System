import pyvisa

try:
    # VISAリソースマネージャーを作成
    rm = pyvisa.ResourceManager()

    # SignalVu-PCのVISAリソース名を指定
    resource_name = 'GPIB8::1::INSTR'

    # SignalVu-PCに接続
    instrument = rm.open_resource(resource_name)

    # タイムアウトを設定 (5000ミリ秒)
    instrument.timeout = 10000

    # 測定設定の送信 (周波数範囲の設定など)
    instrument.write(':FREQ:START 1GHz')
    instrument.write(':FREQ:STOP 2GHz')

    # 測定の開始
    instrument.write(':INIT:IMM')

    # 測定データの取得 (例：最大ホールド)
    max_hold = instrument.query(':TRACe:DATA? MAXH')
    print('Max Hold Data:', max_hold)

except pyvisa.VisaIOError as e:
    print(f"VISA I/O error occurred: {e}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # 接続を閉じる
    instrument.close()
