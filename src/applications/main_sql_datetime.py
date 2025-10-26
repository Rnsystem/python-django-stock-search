import os                       #ファイル確認に使用
import sys
import time
import datetime
import calendar
import pytz # タイムゾーンを指定
import uuid # uuid生成
import re # 正規表現
# 独自関数呼び出し
import myFunction
# MariaDB操作クラス呼び出し
from mariadb import MySqlControl
# 楽天操作クラス呼び出し
from api_rakuten import RwsLicenseManagementApi
from api_rakuten import RwsGetInventoryApi
from api_rakuten import RwsGetItemyApi
from api_rakuten import RwsIchibaItemSearch
from api_rakuten import RwsIchibaGenreSearch
from api_rakuten import RwsIchibaRankingSearch
##########################################################
# タイムゾーン 
# TIME_ZONE = 'Asia/Tokyo'
TIME_ZONE = 'UTC'
##########################################################
#SQLアカウント情報
MYSQL_HOST      = 'localhost'
MYSQL_PORT      = ''
MYSQL_USER      = 'root'
MYSQL_PASSWORD  = ''
MYSQL_DATABASE  = 'django_stocksearch'
##########################################################
#DATETIMEのフォーマット
DATE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
DATE_TIME_FORMAT_START = '%Y/%m/%d 00:00:00'
DATE_TIME_FORMAT_END = '%Y/%m/%d 23:59:59'
# ---
DATE_TIME_FORMAT_YEAR = '%Y'
DATE_TIME_FORMAT_YEAR_START = '%Y/01/01 00:00:00'
DATE_TIME_FORMAT_YEAR_END = '%Y/12/31 23:59:59'
# ---
DATE_TIME_FORMAT_MONTH = '%Y/%m'
# ---
DATE_TIME_FORMAT_DAY = '%Y/%m/%d'
##########################################################
MONTH_LIST = {
    "Jan":"1",
    "Feb":"2",
    "Mar":"3",
    "Apr":"4",
    "May":"5",
    "Jun":"6",
    "Jul":"7",
    "Aug":"8",
    "Sep":"9",
    "Oct":"10",
    "Nov":"11",
    "Dec":"12"
    }
##########################################################
TIME_SLEEP  = 0.5                             #処理の待機時間(秒)


# 月の初日
def get_first_date(dt):
    return dt.replace(day=1)

# 月の月末
def get_last_date(dt):
    return dt.replace(day=calendar.monthrange(dt.year, dt.month)[1])

# データベース操作をするクラス
class StockSearchDB(MySqlControl):
    # 初期値
    def __init__(self):
        super().__init__(
                MYSQL_HOST,
                MYSQL_PORT,
                MYSQL_USER,
                MYSQL_PASSWORD,
                MYSQL_DATABASE
                )

# 年データ更新
def insert_datetime_years():
    # 開始時間
    start_time = time.perf_counter()
    # RWSジャンルID取得処理
    try:
        # 現在日時を取得
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        # MySQL接続情報取得
        ssdb = StockSearchDB()
        # カーソルを設定
        cur = ssdb.cursor()
        # モールID取得
        sql = 'SELECT uuid FROM mst_years WHERE datetime_start<=%s and datetime_end>=%s'
        param = (datetime_now_str,datetime_now_str)
        cur.execute(sql,param)
        mst_years_data = cur.fetchall()
        # データ送信用受皿初期化
        mst_years = {}
        mst_years['sys_datetime_modified'] = datetime_now_str # システム更新日設定 
        if len(mst_years_data) > 0:
            # 存在するとき
            mst_years['uuid'] = mst_years_data[0]['uuid'] # UUID設定 
            # 更新
            cur.execute(ssdb.execute_update_dict('mst_years', 'uuid', **mst_years),mst_years)
        else:
            # 存在しないとき
            mst_years['uuid'] = str(uuid.uuid4().hex) # UUID設定
            mst_years['sys_datetime_created'] = datetime_now_str # システム更新日設定 
            mst_years['name'] = datetime_now.strftime(DATE_TIME_FORMAT_YEAR)
            mst_years['datetime_start'] = datetime_now.strftime(DATE_TIME_FORMAT_YEAR_START)
            mst_years['datetime_end'] = datetime_now.strftime(DATE_TIME_FORMAT_YEAR_END)
            # 新規追加処理
            cur.execute(ssdb.execute_insert_dict2('mst_years',**mst_years),mst_years)
        #SQLコミット
        ssdb.commit()
        #処理の待機
        # time.sleep(TIME_SLEEP)
        #閉じる
        cur.close()
        ssdb.close()
    except Exception as e:
        print("SQL mst_yearsテーブル更新処理に失敗しました。")
        print(e)
        print("失敗","SQL mst_yearsテーブル更新処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return   


# 月データ更新
def insert_datetime_months():
    # 開始時間
    start_time = time.perf_counter()
    # RWSジャンルID取得処理
    try:
        # 現在日時を取得
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        # MySQL接続情報取得
        ssdb = StockSearchDB()
        # カーソルを設定
        cur = ssdb.cursor()
        # モールID取得
        sql = 'SELECT uuid FROM mst_months WHERE datetime_start<=%s and datetime_end>=%s'
        param = (datetime_now_str,datetime_now_str)
        cur.execute(sql,param)
        mst_months_data = cur.fetchall()
        # データ送信用受皿初期化
        mst_months = {}
        # yearsUUID取得
        sql = 'SELECT uuid FROM mst_years WHERE datetime_start<=%s and datetime_end>=%s'
        param = (datetime_now_str,datetime_now_str)
        cur.execute(sql,param)
        mst_years_data = cur.fetchall()
        # years存在判定
        if len(mst_years_data) > 0:
            mst_months['years_id'] = mst_years_data[0]['uuid']
        mst_months['sys_datetime_modified'] = datetime_now_str # システム更新日設定 
        if len(mst_months_data) > 0:
            # 存在するとき
            mst_months['uuid'] = mst_months_data[0]['uuid'] # UUID設定 
            # 更新
            cur.execute(ssdb.execute_update_dict('mst_months', 'uuid', **mst_months),mst_months)
        else:
            # 存在しないとき
            mst_months['uuid'] = str(uuid.uuid4().hex) # UUID設定
            mst_months['sys_datetime_created'] = datetime_now_str # システム更新日設定 
            mst_months['name'] = datetime_now.strftime(DATE_TIME_FORMAT_MONTH)
            datetime_start = get_first_date(datetime_now)
            mst_months['datetime_start'] = datetime_start.strftime(DATE_TIME_FORMAT_START)
            datetime_end = get_last_date(datetime_now)
            mst_months['datetime_end'] = datetime_end.strftime(DATE_TIME_FORMAT_END)
            # 新規追加処理
            cur.execute(ssdb.execute_insert_dict2('mst_months',**mst_months),mst_months)
        #SQLコミット
        ssdb.commit()
        #処理の待機
        # time.sleep(TIME_SLEEP)
        #閉じる
        cur.close()
        ssdb.close()
    except Exception as e:
        print("SQL mst_yearsテーブル更新処理に失敗しました。")
        print(e)
        print("失敗","SQL mst_yearsテーブル更新処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return   


# 日データ更新
def insert_datetime_days():
    # 開始時間
    start_time = time.perf_counter()
    # RWSジャンルID取得処理
    try:
        # 現在日時を取得
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE))
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        # MySQL接続情報取得
        ssdb = StockSearchDB()
        # カーソルを設定
        cur = ssdb.cursor()
        # モールID取得
        sql = 'SELECT uuid FROM mst_days WHERE datetime_start<=%s and datetime_end>=%s'
        param = (datetime_now_str,datetime_now_str)
        cur.execute(sql,param)
        mst_days_data = cur.fetchall()
        # データ送信用受皿初期化
        mst_days = {}
        # monthsUUID取得
        sql = 'SELECT uuid FROM mst_months WHERE datetime_start<=%s and datetime_end>=%s'
        param = (datetime_now_str,datetime_now_str)
        cur.execute(sql,param)
        mst_months_data = cur.fetchall()
        # months存在判定
        if len(mst_months_data) > 0:
            mst_days['months_id'] = mst_months_data[0]['uuid']
        mst_days['sys_datetime_modified'] = datetime_now_str # システム更新日設定 
        if len(mst_days_data) > 0:
            # 存在するとき
            mst_days['uuid'] = mst_days_data[0]['uuid'] # UUID設定 
            # 更新
            cur.execute(ssdb.execute_update_dict('mst_days', 'uuid', **mst_days),mst_days)
        else:
            # 存在しないとき
            mst_days['uuid'] = str(uuid.uuid4().hex) # UUID設定
            mst_days['sys_datetime_created'] = datetime_now_str # システム更新日設定 
            mst_days['name'] = datetime_now.strftime(DATE_TIME_FORMAT_DAY)
            mst_days['datetime_start'] = datetime_now.strftime(DATE_TIME_FORMAT_START)
            mst_days['datetime_end'] = datetime_now.strftime(DATE_TIME_FORMAT_END)
            # 新規追加処理
            cur.execute(ssdb.execute_insert_dict2('mst_days',**mst_days),mst_days)
        #SQLコミット
        ssdb.commit()
        #処理の待機
        # time.sleep(TIME_SLEEP)
        #閉じる
        cur.close()
        ssdb.close()
    except Exception as e:
        print("SQL mst_yearsテーブル更新処理に失敗しました。")
        print(e)
        print("失敗","SQL mst_yearsテーブル更新処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return  


if __name__ == '__main__':
    # argument_code = sys.argv[1]
    # print(argument_code)
    # time.sleep(100)
    print("----------")
    insert_datetime_years()
    insert_datetime_months()
    insert_datetime_days()
    print("----------")
    sys.exit()
