import os

def file2num():
    # ファイルが格納されているフォルダのパス
    folder_path = '/path/to/folder'

    # フォルダ内のファイル一覧を取得する
    file_list = os.listdir(folder_path)

    # フォルダ内のwavファイルのみ抽出する
    wav_list = [file for file in file_list if file.endswith('.wav')]

    # ファイル名を変更する
    for i, wav_file in enumerate(wav_list):
        # ファイル名を変更するための新しいファイル名を生成する
        new_file_name = f"{i:04d}.wav" # 4桁の0埋めでファイル名を生成
        
        # ファイル名を変更する
        os.rename(os.path.join(folder_path, wav_file), os.path.join(folder_path, new_file_name))
        
    print('ファイル名の変更が完了しました。')



if __name__ == "__main__":
    print("開始")
    file2num()
    print("完了")