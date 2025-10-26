import inspect      #現在の関数名を取得(ログ用)
import csv          #CSV出力に使用
import os           #ファイル削除に使用

# 辞書データをCSVで出力する
def exportCsvFromDict(exportPath, *data):
    ###############
    # 関数初期値
    cframe = inspect.currentframe()
    fname = inspect.getframeinfo(cframe).function
    print("関数 '{}'を起動します。".format(fname))
    ###############
    #出力データの存在
    if len(data)>0:
        # ヘッダ名リストの抽出
        headerNames = [k for k in data[0].keys()]
        # CSV出力
        with open(exportPath, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames = headerNames)
            writer.writeheader()
            writer.writerows(data)
        print('CSVデータを出力しました。({})'.format(fname))
        print('出力先：'+str(exportPath))
    else:
        print('出力データが存在しませんでした。({})'.format(fname))
        print('処理をスキップします。')
    ###############
    # 関数終了処理
    print("関数 '{}'を終了します。".format(fname))
    ###############

# CSVデータを辞書で入力する
def importDictFromCsv(importPath) -> list:
    ###############
    # 関数初期値
    cframe = inspect.currentframe()
    fname = inspect.getframeinfo(cframe).function
    print("関数 '{}'を起動します。".format(fname))
    ###############
    # 入力データの存在確認
    if os.path.isfile(importPath):
        # CSV出力
        with open(importPath, 'rt', newline='', encoding='utf-8') as csvfile:
            dict_reader = csv.DictReader(csvfile)
            data = [row for row in dict_reader]
        print('CSVデータを入力しました。({})'.format(fname))
        print('入力先：'+str(importPath))
        ###############
        # 関数終了処理
        print("関数 '{}'を終了します。".format(fname))
        ###############
        return data
    else:
        print('入力データが存在しませんでした。({})'.format(fname))
        print('処理をスキップします。')
        ###############
        # 関数終了処理
        print("関数 '{}'を終了します。".format(fname))
        ###############
        return []

# 辞書型の中にある配列、辞書のみ抽出する。
def conversion_dict(self, *args, **kwargs) -> dict:
    cd = {}
    for k,v in kwargs.items():
        if k in args:
            cd[k] = v
    return cd


# 最初の実行される
if __name__ == "__main__":
    print("処理を開始します。")
    # mainテスト
    print("処理が正常終了しました。")