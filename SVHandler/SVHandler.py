import pyvisa
import time
import os
import requests
from datetime import datetime
import csv
import math
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# VISAの接続設定
rm = pyvisa.ResourceManager()
rsa = rm.open_resource('GPIB8::1::INSTR')
rsa.timeout = 10000
rsa.encoding = 'latin_1'
rsa.write_termination = None
rsa.read_termination = '\n'
print('CNCT ', rsa.query('*idn?'))

rsa.write('*rst') # reset
rsa.write('*cls') # clear status
rsa.write('abort') # abort 実行中の測定を中止
print('INIT CMPL')

# 測定周波数リストを生成
def generate_frequency_list(request_center_freq, request_total_span, step_span=20e6):
    num_steps = math.ceil(request_total_span / step_span)
    frequencies = []
    # 測定回数が奇数
    if num_steps % 2 == 1:
        mid_index = num_steps // 2
        for i in range(num_steps):
            freq = request_center_freq + (i - mid_index) * step_span
            frequencies.append(freq)
    # 測定回数が偶数
    else:
        mid_index = num_steps // 2 - 1
        for i in range(num_steps):
            freq = request_center_freq + (i - mid_index - 0.5) * step_span
            frequencies.append(freq)
    print('FREQ RSLT')
    print(frequencies)
    return frequencies

# 画像を取得して保存
def capture_image(save_path, filename_base, idx):
    capture_url = "http://127.0.0.1:9091/capture"
    response = requests.get(capture_url)
    if response.status_code == 200:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        image_path = os.path.join(save_path, f"{filename_base}_camera_{idx}.jpg")
        with open(image_path, 'wb') as file:
            file.write(response.content)
        print('PICT SUCC')
    else:
        print('PICT EROR')

# 測定のメモを保存
def save_memo(save_path, filename_base, memo_content):
    memo_file = os.path.join(save_path, 'memo.csv')
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    with open(memo_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time, filename_base, memo_content])
    print('MEMO SAVED')

# スペクトログラムの測定を行いデータを保存
def measure_spectrogram(center_freqs, span, bandwidth, minutes, save_path, filename_base, camera_enabled):
    print("MEAS STRT")
    seconds = minutes * 60
    for idx, center_freq in enumerate(center_freqs):
        rsa.write('display:general:measview:new sgram')
        rsa.write('INPUT:RF:GAIN:STATE ON')
        rsa.write('INPUT:RF:ATTENUATION:AUTO OFF')
        rsa.write('INPUT:RF:ATTENUATION 0')
        rsa.write(f'sgram:frequency:center {center_freq}')
        rsa.write(f'sgram:frequency:span 20e6')
        rsa.write(f'sgram:bandwidth {bandwidth}')
        rsa.write('SENSE:SGRam:COLor:MAXimum -60')
        rsa.write('SENSE:SGRam:COLor:MINimum -115')
        rsa.write('initiate:immediate')
        rsa.query('*opc?')
        time.sleep(seconds)
        rsa.write('initiate:continuous off')
        files = int(seconds / 25) + 2
        for i in range(files):
            div = 20 * i
            rsa.write(f'display:sgram:time:offset:divisions {div}')
            rsa.write(f'mmemory:store:results "{save_path}/{filename_base}_cf{int(center_freq)}_sgram_{i}.csv"')
        if camera_enabled:
            capture_image(save_path, filename_base, idx)
        rsa.write('*rst')
        rsa.write('*cls')
        rsa.write('abort')
    print("MEAS CMPL")

# Flaskのエンドポイント
@app.route('/measure', methods=['POST'])
def receive_measurement_request():
    print('RQST RECV')
    data = request.json
    measurements = data.get('measurements', [])
    minutes = data.get('minutes', 2)
    save_path = data.get('save_path', "C:/TRAMs/data")
    filename_base = data.get('filename', 'spectrogram')
    camera_enabled = data.get('camera', 0) == 1
    memo_content = data.get('memo', '')

    # 複数の測定を順次実施
    for measurement in measurements:
        request_center_freq = measurement.get('centerFreq')
        request_total_span = measurement.get('span', 20e6)
        bandwidth = measurement.get('bandwidth', 1e3)
        # 測定する中心周波数のリストを生成
        center_freqs = generate_frequency_list(request_center_freq, request_total_span)
        # 測定を実行しデータを保存
        measure_spectrogram(center_freqs, request_total_span, bandwidth, minutes, save_path, filename_base, camera_enabled)
    # memoを保存
    save_memo(save_path, filename_base, memo_content)

    print('RQST CMPL')
    return jsonify({"status": "Measurement complete"})

# Flaskサーバー起動
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9090)
