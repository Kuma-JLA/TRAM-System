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
log_path = "C:/TRAMs/data"

# 測定のリクエスト内容を保存
def save_received_request(data, log_path):
    log_file = os.path.join(log_path, 'receivedrequest.csv')
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time, str(data)])  # 受信したデータを文字列として保存

# 測定のログを保存
def save_log(log_path, log_content):
    log_file = os.path.join(log_path, 'log.csv')
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([current_time, log_content])

# VISAの接続設定
try:
    rm = pyvisa.ResourceManager()
    rsa = rm.open_resource('GPIB8::1::INSTR')
    rsa.timeout = 10000
    rsa.encoding = 'latin_1'
    rsa.write_termination = None
    rsa.read_termination = '\n'
    rsaid = rsa.query('*idn?')
    save_log(log_path, f'CNCT CMPL {rsaid}')
    print('CNCT ', rsaid)
except Exception as e:
    save_log(log_path, f'CNCT FAIL {str(e)}')
    print('CNCT FAIL', str(e))

save_log(log_path, 'INIT STRT')
rsa.write('*rst') # reset
rsa.write('*cls') # clear status
rsa.write('abort') # abort 実行中の測定を中止
rsa.query('*opc?')
save_log(log_path, 'INIT CMPL')
print('INIT CMPL')

# 測定周波数リストを生成
def generate_frequency_list(request_center_freq, request_total_span, step_span=20e6):
    save_log(log_path, f'FCAL STRT {request_center_freq} {request_total_span}')
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
    save_log(log_path, f'FCAL CMPL {request_center_freq} {request_total_span}')
    save_log(log_path, f'FREQ RSLT {frequencies}')
    print(f'FREQ RSLT')
    print(frequencies)
    return frequencies

# 画像を取得して保存
def capture_image(save_path, filename_base, center_freq):
    capture_url = "http://127.0.0.1:9091/capture"
    response = requests.get(capture_url)
    if response.status_code == 200:
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        image_path = os.path.join(save_path, f"{filename_base}_{center_freq}_camera.jpg")
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
    save_log(log_path, 'BAND STRT')
    print("BAND STRT")
    seconds = minutes * 60
    max_retries = 3  # 最大再試行回数

    for idx, center_freq in enumerate(center_freqs):
        attempt = 0  # 試行回数
        while attempt < max_retries:
            try:
                save_log(log_path, f'MEAS STRT {center_freq}')
                save_log(log_path, 'CMND EXEC display:general:measview:new sgram')
                rsa.write('display:general:measview:new sgram')
                save_log(log_path, 'CMND EXEC INPUT:RF:GAIN:STATE ON')
                rsa.write('INPUT:RF:GAIN:STATE ON')
                save_log(log_path, 'CMND EXEC INPUT:RF:ATTENUATION:AUTO OFF')
                rsa.write('INPUT:RF:ATTENUATION:AUTO OFF')
                save_log(log_path, 'CMND EXEC INPUT:RF:ATTENUATION 0')
                rsa.write('INPUT:RF:ATTENUATION 0')
                save_log(log_path, f'CMND EXEC sgram:frequency:center {center_freq}')
                rsa.write(f'sgram:frequency:center {center_freq}')
                save_log(log_path, f'CMND EXEC sgram:frequency:span 20e6')
                rsa.write(f'sgram:frequency:span 20e6')
                save_log(log_path, f'CMND EXEC sgram:bandwidth {bandwidth}')
                rsa.write(f'sgram:bandwidth {bandwidth}')
                save_log(log_path, 'CMND EXEC *opc?')
                rsa.query('*opc?')
                save_log(log_path, 'CMND EXEC initiate:immediate')
                rsa.write('initiate:immediate')
                save_log(log_path, 'CMND EXEC *opc?')
                rsa.query('*opc?')
                save_log(log_path, 'CMND EXEC MEAS STRT')
                time.sleep(seconds)
                save_log(log_path, 'CMND EXEC initiate:continuous off')
                rsa.write('initiate:continuous off')
                save_log(log_path, 'MEAS CMPL {center_freq}')
                files = int(seconds / 25) + 2
                save_log(log_path, 'SAVE STRT')
                for i in range(files):
                    div = 20 * i
                    rsa.write(f'display:sgram:time:offset:divisions {div}')
                    rsa.write(f'mmemory:store:results "{save_path}/{filename_base}_cf{int(center_freq)}_sgram_{i}.csv"')
                save_log(log_path, 'SAVE CMPL')
                if camera_enabled:
                    capture_image(save_path, filename_base, center_freq)
                break  # 成功したらループを抜ける
            except Exception as e:
                attempt += 1
                save_log(log_path, f'MEAS FAIL {center_freq} {str(e)}')
                print(f'MEAS FAIL {center_freq}, Attempt {attempt} of {max_retries}', str(e))
                if attempt >= max_retries:
                    print(f'MAX RETRIES REACHED for {center_freq}, skipping...')
                    break  # 最大再試行回数に達したら次の周波数に進む
            finally:
                rsa.write('*rst')
                rsa.write('*cls')
                rsa.write('abort')
                rsa.query('*opc?')
            save_log(log_path, f'MEAS CMPL {center_freq}')

    save_log(log_path, 'BAND CMPL')
    print("BAND CMPL")

# Flaskのエンドポイント
@app.route('/measure', methods=['POST'])
def receive_measurement_request():
    try:
        save_log(log_path, 'RQST RECV')
        print('RQST RECV')
        data = request.json

        # 受信データの保存
        save_received_request(data, log_path)

        measurements = data.get('measurements', [])
        minutes = data.get('minutes', 2)
        save_path = data.get('save_path', "C:/TRAMs/data")
        filename_base = data.get('filename', 'spectrogram')
        camera_enabled = data.get('camera', 0) == 1
        memo_content = data.get('memo', '')

        rsa.write('abort')
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

        save_log(log_path, 'RQST CMPL')
        print('RQST CMPL')
        return jsonify({"status": "Measurement complete"})
    except Exception as e:
        save_log(log_path, f'RQST FAIL {str(e)}')
        print('RQST FAIL', str(e))
        return jsonify({"status": "Request failed", "error": str(e)})

# Flaskサーバー起動
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9090)
