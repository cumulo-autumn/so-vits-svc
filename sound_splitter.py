import os
from tqdm import tqdm
import soundfile as sf
import math
import numpy as np

#################

DATA_DIR             = "./data/"
WAV_FOLDER_NAME      = "wav_dir"
SPLITTED_FOLDER_NAME = "splitted_wav"
SAMPLING_RATIO       = 44100

#################

def vocals_splitter():
    in_dir = os.path.join(DATA_DIR, WAV_FOLDER_NAME)        # wavが格納されてるディレクトリパス
    out_dir = os.path.join(DATA_DIR, SPLITTED_FOLDER_NAME)  # 分割後のwavのディレクトリパス
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)
    
    buffer_time = 0.1                       # 0.1秒間隔でチェックする
    threshold   = 0.05                      # 音量の閾値チェック（多分変えなくて大丈夫
    minimum_time= 5                         # 最小時間を 5秒にする
    maximum_time= 15                        # 最大時間を15秒にする
    
    save_count = 0
    # wavファイルごとに処理するfor文
    for filename in tqdm(os.listdir(in_dir),desc="Vocal_Splitting..."):
        # なんか偶に出るエラー対策
        if filename == "Thumb.db" or filename == "desktop.ini":
            continue
        
        # 今回処理するwavファイル
        target_wav = os.path.join(in_dir, filename)

        # 音声読み込みと、判定用パラメータ計算
        sound, _ = sf.read(file=target_wav)
        sound = np.array(sound)
        buffer_size = math.floor(SAMPLING_RATIO * buffer_time)
        sound_length = len(sound)
        range_num = math.floor(sound_length / buffer_size)
        check_list = []

        # 閾値チェック
        for idx in range(range_num):

            # tryは最初～途中まで、exceptは最後のみ突入
            try:
                check_data = sound[int(buffer_size*idx):int(buffer_size*(idx+1))]
            except:
                check_data = sound[int(buffer_size*idx):]

            # 二乗して合計を計算
            doubled = np.sum(np.square(check_data))

            #print(idx, doubled)        # 閾値チェック用

            # 閾値チェック実装
            if doubled > threshold:
                check_list.append("1")
            else:
                check_list.append("0")

        # 保存用パラメータ設定
        start_idx = 0
        end_idx = 0
        z1_data = 0

        # 各種フラグ
        start_flag = False
        end_flag = False
        time_flag = False
        sample_counter = 0

        # 最小時間分のサンプル数を計算
        minimum_n = int(minimum_time / buffer_time) 

        # 閾値チェック結果を使って、wavを保存する
        for idx, data in enumerate(check_list):
            
            # 1なら発話オンタイミング、-1なら発話オフタイミング
            checker = int(data) - int(z1_data)    

            # ON検出
            if checker ==  1 and start_flag is False:
                sample_counter = 0
                start_idx = idx
                start_flag = True   # 開始地点準備OK
            
            # ON カウント   発話開始からどれくらい経ったかをチェック
            if start_flag:
                sample_counter += 1

            # 最小時間以上のフラグ作成
            if sample_counter > minimum_n:
                time_flag = True

            # OFF検出             
            if checker == -1 and end_flag is False and time_flag is True:
                end_idx = idx
                end_flag = True     # 終了地点準備OK

            # ON検出、OFF検出、時間もOKならば、保存フラグを建てて、他を初期化
            if start_flag and end_flag and time_flag:
                sample_counter = 0
                start_flag = False
                end_flag = False
                time_flag = False

                save_count += 1
                save_data = sound[start_idx*buffer_size:end_idx*buffer_size]
                save_path = os.path.join(out_dir, str(save_count).zfill(5) + ".wav")
                sf.write(save_path, save_data, SAMPLING_RATIO)
                #print(start_idx, end_idx)
                start_flag = True
                start_idx = end_idx
                print("Save Count =", save_count)

            # 過去データ保持
            z1_data = data

    # 最大秒数越えを消す（閾値的に少ないとは思うけども
    for filename in os.listdir(out_dir):
        # なんか偶に出るエラー対策
        if filename == "Thumb.db" or filename == "desktop.ini":
            continue

        # 検査対象wav
        wav_path = os.path.join(out_dir, filename)

        # 読み込み
        try:
            y, _ = sf.read(wav_path)
        except:
            continue

        time_y = len(y)/ SAMPLING_RATIO

        if time_y > maximum_time:
            print("最大時間越えで消去 :",wav_path)
            os.remove(wav_path)
            continue
        

# このファイル自体が実行されたときのみ、if文に突入する
if __name__ == "__main__":
    print("開始")
    vocals_splitter()
    print("完了")