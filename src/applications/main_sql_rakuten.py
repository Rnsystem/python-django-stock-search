import os                       #ファイル確認に使用
import sys
import time
import datetime
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
# デイリー
DAILY_SEARCH_DAYS = 7
##########################################################
# monthly
DAILY_SEARCH_MONTH = 2
##########################################################
#SQLアカウント情報
MYSQL_HOST      = 'localhost'
MYSQL_PORT      = ''
MYSQL_USER      = 'root'
MYSQL_PASSWORD  = ''
MYSQL_DATABASE  = 'django_stocksearch'
DATE_TIME_FORMAT = '%Y/%m/%d %H:%M:%S'
LICENSE_WSDL = 'lic/inventoryapi.wsdl'
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
#RWSアカウント情報
RWS_APPLICATION_ID      = ''
#RWS
HITS        = 30                            #1回の検索で取得する件数
CARRIER     = 2                             #キャリア情報(PC: 0 mobile: 1 (*Japan only) smartphone: 2)
##########################################################
TIME_SLEEP  = 0.5                             #処理の待機時間(秒)


#アカウントを設定するクラス
class RwsIchibaItemSearchInformation(RwsIchibaItemSearch):
    #初期値
    def __init__(self):
        super().__init__(RWS_APPLICATION_ID)
    #パラメータをセットする
    def set(self, **kwargs):
        #利用可能の製品のみに抽出
        kwargs["availability"]  = 1
        kwargs["field"]         = 1
        #パラメーターをセット
        super().set(**kwargs)

#アカウントを設定するクラス
class RwsIchibaRankingSearchInformation(RwsIchibaRankingSearch):
    #初期値
    def __init__(self):
        super().__init__(RWS_APPLICATION_ID)
    #パラメータをセットする
    def set(self, **kwargs):
        #パラメーターをセット
        super().set(**kwargs)
    #一括取得
    def get_all(self, genreId=0, page=1) -> list:
        #パラメーターをセット
        super().get()
        # 初期設定
        page = 1
        rws_rank_data = []
        while page <= 34:
            try:
                print(str(page)+"ページ")
                # ランキングを取得
                self.set(**{"page":page, "genreId":genreId})
                # 処理の待機
                time.sleep(TIME_SLEEP)
                # ランキング取得
                res = super().get()
                # 曜日変換　ex：Sat, 12 Nov 2022 00:00:00 +0900
                for k,v in MONTH_LIST.items():
                    res['lastBuildDate'] = res['lastBuildDate'].replace(k,v)
                rank_datetime_str = res['lastBuildDate'].split(',')
                rank_datetime = datetime.datetime.strptime(rank_datetime_str[1], ' %d %m %Y %H:%M:%S +0900')
                for r in res['Items']:
                    # 値の追加
                    r['Item']['title']          = res['title']
                    r['Item']['lastBuildDate']  = rank_datetime
                    # 値の更新
                    rws_rank_data.append(r['Item'])
                # ページ更新
                page += 1
            except Exception as e:
                break
        return rws_rank_data


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

# 商品実行ログ作成
def insert_items_executelogs():
    # 開始時間
    start_time = time.perf_counter()
    # RWSジャンルID取得処理
    try:
        # MySQL接続情報取得
        ssdb = StockSearchDB()
        # カーソルを設定
        cur = ssdb.cursor()
        # モールID取得
        sql = 'SELECT uuid FROM mst_malls WHERE name=%s'
        param = ("楽天市場",)
        cur.execute(sql,param)
        mst_malls_data = cur.fetchall()
        for mst_malls in mst_malls_data:
            # ストアID取得
            sql = 'SELECT uuid FROM mst_stores WHERE malls_id=%s'
            param = (mst_malls['uuid'],)
            cur.execute(sql,param)
            mst_stores_data = cur.fetchall()
            # 現在日時の設定
            datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
            datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
            for mst_stores in mst_stores_data:
                executelogs = {}
                # システム更新日設定 
                executelogs['sys_datetime_modified'] = datetime_now_str
                executelogs['sys_datetime_created'] = datetime_now_str
                # UUID設定 
                executelogs['uuid'] = str(uuid.uuid4().hex)
                executelogs['stores_id'] = mst_stores['uuid']
                # ユーザ設定
                executelogs['user_id'] = 2#自動処理ユーザ指定
                # status設定 
                executelogs['execute_status'] = 1# 未処理
                executelogs['execute_type'] = 2# 商品タイプ
                executelogs['memo'] = '【定期処理】未処理'
                # 新規追加処理
                cur.execute(ssdb.execute_insert_dict2('tbl_executelogs',**executelogs),executelogs)
            #SQLコミット
            ssdb.commit()
            #処理の待機
            # time.sleep(TIME_SLEEP)
        #閉じる
        cur.close()
        ssdb.close()
    except Exception as e:
        print("商品実行ログ作成SQLインポート処理に失敗しました。")
        print(e)
        print("失敗","商品実行ログ作成SQLインポート処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return   

# #ランキングを取得する
def get_ranking():
    # 開始時間
    start_time = time.perf_counter()
    #RWSジャンルID取得処理
    try:
        #MySQL接続情報取得
        ssdb = StockSearchDB()
        #カーソルを設定
        cur = ssdb.cursor()
        # 登録商品中のジャンルID一覧取得
        sql =   '''
                    SELECT
	                    tmp_ichibaitemgenres.uuid,
	                    tmp_ichibaitemgenres.ichibaGenres_id,
	                    tmp_ichibagenres.genreId
	                FROM
	                    tmp_ichibaitemgenres 
	                INNER JOIN
		                tmp_ichibagenres
	                    ON
	                        tmp_ichibaitemgenres.ichibaGenres_id = tmp_ichibagenres.uuid
	                WHERE
	                    tmp_ichibagenres.genreId is not Null
	                GROUP BY
	                    tmp_ichibaitemgenres.ichibaGenres_id
                '''
        cur.execute(sql)
        tmp_ichibaitemgenres_data = cur.fetchall()
        for tmp_ichibaitemgenres in tmp_ichibaitemgenres_data:
        # if len(tmp_ichibaItems_data) > 0:
            # 初期設定
            print("ジャンルID："+str(tmp_ichibaitemgenres['genreId']))
            rws = RwsIchibaRankingSearchInformation()
            # RWS APIでランキング取得
            rws_rank_data = rws.get_all(genreId=tmp_ichibaitemgenres['genreId'])
            print("ランキング数："+str(len(rws_rank_data)))
            # 現在日時の取得
            datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
            datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
            # レコード毎にsqlインポート処理
            for rws_rank in rws_rank_data:
                # システム更新日設定 
                rws_rank['sys_datetime_modified'] = datetime_now_str
                # ランキングジャンルID設定 
                rws_rank['ichibaRankingGenres_id'] = tmp_ichibaitemgenres['ichibaGenres_id']
                # ストアID取得判定
                sql = 'SELECT uuid,shop_Code FROM mst_stores WHERE shop_Code=%s'
                param = (rws_rank['shopCode'],)
                cur.execute(sql,param)
                mst_stores_data = cur.fetchall()
                if len(mst_stores_data) > 0:
                    rws_rank['stores_id'] = mst_stores_data[0]['uuid']
                # ジャンルID取得判定
                sql = 'SELECT uuid,genreId,genreName FROM tmp_ichibagenres WHERE genreId=%s'
                param = (rws_rank['genreId'],)
                cur.execute(sql,param)
                tmp_ichibagenres_data = cur.fetchall()
                if len(tmp_ichibagenres_data) > 0:
                    rws_rank['ichibaGenres_id'] = tmp_ichibagenres_data[0]['uuid']
                    print(str(rws_rank['rank'])+"位："+rws_rank['itemCode']+"("+tmp_ichibagenres_data[0]['genreName']+")")
                # 市場商品ID取得判定
                sql = 'SELECT uuid,itemCode FROM tmp_ichibaItems WHERE itemCode=%s'
                param = (rws_rank['itemCode'],)
                cur.execute(sql,param)
                tmp_ichibaItems_data = cur.fetchall()
                if len(tmp_ichibaItems_data) > 0:
                    rws_rank['ichibaItems_id'] = tmp_ichibaItems_data[0]['uuid']
                    # 市場商品ジャンル取得判定
                    sql = 'SELECT uuid FROM tmp_ichibaItemGenres WHERE ichibaItems_id=%s and ichibaGenres_id=%s'
                    param = (rws_rank['ichibaItems_id'],rws_rank['ichibaGenres_id'])
                    cur.execute(sql,param)
                    ichibaItemGenres_data = cur.fetchall()
                    if len(ichibaItemGenres_data) > 0:
                        rws_rank['ichibaItemGenres_id'] = ichibaItemGenres_data[0]['uuid']
                    # 市場ランキング取得判定【ボトルネック】
                    sql = 'SELECT uuid,itemCode FROM tbl_ichibaRankings WHERE ichibaItems_id=%s and rank=%s and ichibaRankingGenres_id=%s and lastBuildDate=%s'
                    param = (rws_rank['ichibaItems_id'],rws_rank['rank'],rws_rank['ichibaRankingGenres_id'],rws_rank['lastBuildDate'])
                    cur.execute(sql,param)
                    tbl_ichibaRankings_data = cur.fetchall()
                    # 集計値の判定
                    if len(tbl_ichibaRankings_data)>0:
                        # 【存在するとき】
                        rws_rank['uuid'] = tbl_ichibaRankings_data[0]['uuid']
                        # 既存レコードに上書更新
                        cur.execute(ssdb.execute_update_dict( 'tbl_ichibarankings', 'uuid', **ssdb.conversion_dict_ichibaRanking(**rws_rank)),ssdb.conversion_dict_ichibaRanking(**rws_rank))
                        print('上書更新')
                    else:
                        # 【存在しないとき】
                        # UUID
                        rws_rank['uuid'] = str(uuid.uuid4().hex)
                        # システム作成日設定
                        rws_rank['sys_datetime_created'] = datetime_now_str
                        cur.execute(ssdb.execute_insert_dict2('tbl_ichibarankings',**ssdb.conversion_dict_ichibaRanking(**rws_rank)),ssdb.conversion_dict_ichibaRanking(**rws_rank))
                        print('追加更新')
            #SQLコミット
            ssdb.commit()
            #処理の待機
            # time.sleep(TIME_SLEEP)
        #閉じる
        cur.close()
        ssdb.close()
        # 終了時間
        end_time = time.perf_counter()
        # 計測時間を出力
        elapsed_time = end_time - start_time
        print("処理時間")
        print(elapsed_time)
    except Exception as e:
        print("ジャンルID取得SQLインポート処理に失敗しました。")
        print(e)
        print("失敗","ランキング取得SQLインポート処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return


# ジャンルID、ジャンル名を取得する
def get_itemgenre(storesUUID, ichibaItemsUUID, ichibaGenreUUID):
    # RWSジャンルID取得処理
    try:
        #MySQL接続情報取得
        ssdb = StockSearchDB()
        #カーソルを設定
        cur = ssdb.cursor()
        # 初期値
        tmp_ichibaItemGenres = {}
        # 登録商品中のジャンルID一覧取得
        sql = 'SELECT uuid, ichibaItems_id, ichibaGenres_id, stores_id FROM tmp_ichibaItemGenres WHERE  ichibaItems_id = %s and ichibaGenres_id = %s and stores_id = %s'
        param = (ichibaItemsUUID, ichibaGenreUUID, storesUUID)
        cur.execute(sql,param)
        tmp_ichibaItemGenres_data = cur.fetchall()
        # 現在日時の取得
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        # システム更新日設定 
        tmp_ichibaItemGenres['sys_datetime_modified'] = datetime_now_str
        # print("ichibaItemsUUID:"+ichibaItemsUUID)
        # print("ichibaGenreUUID:"+ichibaGenreUUID)
        if len(tmp_ichibaItemGenres_data) > 0:
            #【存在するとき】
            tmp_ichibaItemGenres['uuid'] = tmp_ichibaItemGenres_data[0]['uuid']
            # 既存レコードに上書き更新
            cur.execute(ssdb.execute_update_dict( 'tmp_ichibaItemGenres', 'uuid', **tmp_ichibaItemGenres),tmp_ichibaItemGenres)
        else:
            # 【存在しないとき】 
            tmp_ichibaItemGenres['uuid'] = str(uuid.uuid4().hex)
            tmp_ichibaItemGenres['sys_datetime_created'] = datetime_now_str
            tmp_ichibaItemGenres['ichibaItems_id'] = ichibaItemsUUID
            tmp_ichibaItemGenres['ichibaGenres_id'] = ichibaGenreUUID
            tmp_ichibaItemGenres['stores_id'] = storesUUID
            cur.execute(ssdb.execute_insert_dict2('tmp_ichibaItemGenres',**tmp_ichibaItemGenres),tmp_ichibaItemGenres)
        # print(tmp_ichibaItemGenres)
        # SQLコミット
        ssdb.commit()
        # モールUUID取得
        sql = 'SELECT uuid, malls_id FROM mst_stores WHERE uuid = %s'
        param = (storesUUID, )
        cur.execute(sql,param)
        mst_stores_data = cur.fetchall()
        # モールUUID存在判定
        if len(mst_stores_data) > 0:
            mallsUUID = mst_stores_data[0]['malls_id']
            # 親ジャンルID存在判定
            sql = 'SELECT uuid, ichibaGenres_parent_id FROM tmp_ichibagenres WHERE uuid = %s and malls_id = %s'
            param = (ichibaGenreUUID, mallsUUID)
            cur.execute(sql,param)
            tmp_ichibagenres_data = cur.fetchall()
            #閉じる
            cur.close()
            ssdb.close()
            # 親ジャンルIDも再帰的に処理
            if len(tmp_ichibagenres_data) > 0:
                if tmp_ichibagenres_data[0]['ichibaGenres_parent_id'] is not None:
                    get_itemgenre(storesUUID, ichibaItemsUUID, tmp_ichibagenres_data[0]['ichibaGenres_parent_id'])
    except Exception as e:
        print("itemgenres取得SQLインポート処理に失敗しました。")
        print(e)
        print("失敗","itemgenres取得SQLインポート処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return


# ジャンルID、ジャンル名を取得する
def get_itemgenres():
    # RWSジャンルID取得処理
    try:
        #MySQL接続情報取得
        ssdb = StockSearchDB()
        #カーソルを設定
        cur = ssdb.cursor()
        # itemsリストを取得
        sql = 'SELECT uuid, ichibaGenres_id, stores_id, stores_id FROM tmp_ichibaitems'
        cur.execute(sql)
        tmp_ichibaitems_data = cur.fetchall()
        #閉じる
        cur.close()
        ssdb.close()
        # 処理の回数繰り返す
        print("get_itemgenres処理中・・・")
        for tmp_ichibaitems in tmp_ichibaitems_data:
            get_itemgenre(tmp_ichibaitems['stores_id'], tmp_ichibaitems['uuid'], tmp_ichibaitems['ichibaGenres_id'])
        print("get_itemgenres処理完了しました。")
    except Exception as e:
        print("itemgenres取得SQLインポート処理に失敗しました。")
        print(e)
        print("失敗","itemgenres取得SQLインポート処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return


#ジャンルID、ジャンル名を取得する
def get_genre(get_id='0'):
    # 開始時間
    start_time = time.perf_counter()
    #RWSRWSパラメータの更新
    rws = RwsIchibaGenreSearch(RWS_APPLICATION_ID, g_id = get_id)
    #RWSジャンルID取得処理
    try:
        #MySQL接続情報取得
        ssdb = StockSearchDB()
        #カーソルを設定
        cur = ssdb.cursor()
        #モールID取得
        sql = 'SELECT uuid FROM mst_malls WHERE name=%s'
        param = ("楽天市場",)
        cur.execute(sql,param)
        mst_malls_data = cur.fetchall()
        if len(mst_malls_data) > 0:
            #request処理
            r = rws.get()
            #楽天API規約に則って1secあける
            time.sleep(TIME_SLEEP)
            #総合の存在確認
            sql = 'SELECT uuid,genreId FROM tmp_ichibaGenres WHERE genreId=%s'
            param = ('0',)
            cur.execute(sql,param)
            tmp_ichibaGenres_data = cur.fetchall()
            #存在判定
            if len(tmp_ichibaGenres_data) == 0:
                # 現在日時の取得
                datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
                datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
                # 存在しない時
                sougou_data = {
                    'sys_datetime_created'      : datetime_now_str,
                    'sys_datetime_modified'     : datetime_now_str,
                    'uuid'                      : str(uuid.uuid4().hex),
                    'genreId'                   : '0',
                    'genreName'                 : '総合',
                    'genreLevel'                : '0',
                    #'parentGenreId'             : None,
                    'malls_id'                  : mst_malls_data[0]['uuid']
                    #'ichibaGenres_parent_id' 
                }
                cur.execute(ssdb.execute_insert_dict2('tmp_ichibaGenres',**ssdb.conversion_dict_ichibaGenre(**sougou_data)),ssdb.conversion_dict_ichibaGenre(**sougou_data))
                #SQLコミット
                ssdb.commit()
            #追加する行の初期化
            rws_ichibaGenres_data = {}
            #取得件数毎繰り返して情報を取得する
            for i in r["children"]:
                print(i)
                #エレメント情報繰り返し取得する
                for k,v in i.items():
                    #縦軸情報を行変数に格納
                    rws_ichibaGenres_data[k] = v
                # 親情報追加
                rws_ichibaGenres_data["parentGenreId"] = get_id
                # 親情報UUID存在確認 
                #カーソルを設定
                sql = 'SELECT uuid,genreId FROM tmp_ichibaGenres WHERE genreId=%s'
                param = (rws_ichibaGenres_data['parentGenreId'],)
                cur.execute(sql,param)
                tmp_ichibaGenres_parent_data = cur.fetchall()
                # 親情報UUID存在判定
                if len(tmp_ichibaGenres_parent_data)>0:
                    # 【存在するとき】
                    rws_ichibaGenres_data["ichibaGenres_parent_id"] = tmp_ichibaGenres_parent_data[0]['uuid']
                # モールIDの取得
                rws_ichibaGenres_data["malls_id"] = mst_malls_data[0]['uuid']
                # 現在日時の取得
                datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
                datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
                # システム更新日設定
                rws_ichibaGenres_data['sys_datetime_modified'] = datetime_now_str
                # tmp_ichibaItemsの存在確認
                sql = 'SELECT * FROM tmp_ichibaGenres WHERE genreId=%s'
                param = (rws_ichibaGenres_data['genreId'],)
                cur.execute(sql,param)
                tmp_ichibaGenres_data = cur.fetchall()
                # 集計値の判定
                if len(tmp_ichibaGenres_data)>0:
                    # 【存在するとき】
                    rws_ichibaGenres_data['uuid'] = tmp_ichibaGenres_data[0]['uuid']
                    # 既存レコードに上書更新
                    cur.execute(ssdb.execute_update_dict( 'tmp_ichibaGenres', 'uuid', **rws_ichibaGenres_data),rws_ichibaGenres_data)
                else:
                    # 【存在しないとき】
                    # UUID
                    rws_ichibaGenres_data['uuid'] = str(uuid.uuid4().hex)
                    # システム作成日設定
                    rws_ichibaGenres_data['sys_datetime_created'] = datetime_now_str
                    cur.execute(ssdb.execute_insert_dict2('tmp_ichibaGenres',**ssdb.conversion_dict_ichibaGenre(**rws_ichibaGenres_data)),ssdb.conversion_dict_ichibaGenre(**rws_ichibaGenres_data))
                #処理の待機
                # time.sleep(TIME_SLEEP)
                #SQLコミット
                ssdb.commit()
                #再帰的に呼び出して深い階層を取得する
                get_genre(rws_ichibaGenres_data["genreId"])
                
            #処理の待機
            # time.sleep(TIME_SLEEP)
        #閉じる
        cur.close()
        ssdb.close()
        # 終了時間
        end_time = time.perf_counter()
        # 計測時間を出力
        elapsed_time = end_time - start_time
    except Exception as e:
        print("ジャンルID取得SQLインポート処理に失敗しました。")
        print(e)
        print("失敗","ジャンルID取得SQLインポート処理に失敗しました。\n\n【エラー内容】\n"+e)
        sys.exit(1)
    return



# get_itemの実行
def get_ichibaItems_daily():
    # MySQL接続情報取得
    try:
        ssdb = StockSearchDB()
    except Exception as e:
        print("MySQL接続情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    # カーソルを設定
    cur = ssdb.cursor()
    # 実行ログUUID取得
    # デイリー集計値を取得
    sql =   '''
                SELECT 
                 ichibaItems_id AS ichibaItems_id,
                 DATE_FORMAT(sys_datetime_created, '%Y%m%d') AS daily, 
                 MAX(itemPrice) AS itemPrice,
                 MAX(reviewAverage) AS reviewAverage,
                 MAX(reviewCount) AS reviewCount,
                 COUNT(*) AS summaryCount
                FROM tbl_ichibaitems_logs
                WHERE DATE_FORMAT(sys_datetime_created, '%Y%m%d 00:00:00') > DATE_FORMAT((NOW() - INTERVAL %s DAY), '%Y%m%d 00:00:00')
                GROUP BY ichibaItems_id DESC,DATE_FORMAT(sys_datetime_created, '%Y%m%d');
            '''
    # print(sql.format(10))
    param = (DAILY_SEARCH_DAYS,)
    cur.execute(sql,param)
    ichibaitems_logs_data = cur.fetchall()
    # デイリー集計値毎に処理
    for ichibaitems_logs in ichibaitems_logs_data:
        # 現在日時の取得
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        # システム更新日設定
        ichibaitems_logs['sys_datetime_modified'] = datetime_now_str
        # tmp_ichibaItemsの存在確認
        sql = 'SELECT * FROM tmp_ichibaItems WHERE uuid=%s'
        param = (ichibaitems_logs['ichibaItems_id'],)
        cur.execute(sql,param)
        tmp_ichibaItems_data = cur.fetchall()
        # tmp_ichibaItemsの判定
        if len(tmp_ichibaItems_data)>0:
            # 集計値の存在確認
            sql = 'SELECT * FROM tbl_ichibaItems_daily WHERE daily=%s and ichibaItems_id=%s'
            param = (ichibaitems_logs['daily'],ichibaitems_logs['ichibaItems_id'])
            cur.execute(sql,param)
            tbl_ichibaItems_daily_data = cur.fetchall()
            # 集計値の判定
            if len(tbl_ichibaItems_daily_data)>0:
                # 【存在するとき】
                ichibaitems_logs['uuid'] = tbl_ichibaItems_daily_data[0]['uuid']
                # 既存レコードに上書更新
                cur.execute(ssdb.execute_update_dict( 'tbl_ichibaItems_daily', 'uuid', **ichibaitems_logs),ichibaitems_logs)
            else:
                # 【存在しないとき】
                # UUID
                ichibaitems_logs['uuid'] = str(uuid.uuid4().hex)
                # システム作成日設定
                ichibaitems_logs['sys_datetime_created'] = datetime_now_str
                cur.execute(ssdb.execute_insert_dict2('tbl_ichibaItems_daily',**ichibaitems_logs),ichibaitems_logs)
    # SQLコミット
    try:
        # 処理の待機
        time.sleep(TIME_SLEEP)
        ssdb.commit()
        print("SQLコミットに成功しました。")
    except Exception as e:
        print("SQLコミットに失敗しました。")
        print(e)
        nt(CH_FILE_NAME + "失敗","SQLコミットに失敗しました。\n\n【エラー内容】\n"+e)
        lg("失敗" + CH_FILE_NAME)
        sys.exit(1)

# get_itemの実行
def get_ichibaItems_monthly():
    # MySQL接続情報取得
    try:
        ssdb = StockSearchDB()
    except Exception as e:
        print("MySQL接続情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    # カーソルを設定
    cur = ssdb.cursor()
    # 実行ログUUID取得
    # デイリー集計値を取得
    sql =   '''
                SELECT 
                 ichibaItems_id AS ichibaItems_id,
                 DATE_FORMAT(sys_datetime_created, '%Y%m01') AS monthly, 
                 MAX(itemPrice) AS itemPrice,
                 MAX(reviewAverage) AS reviewAverage,
                 MAX(reviewCount) AS reviewCount,
                 COUNT(*) AS summaryCount
                FROM tbl_ichibaitems_logs
                WHERE DATE_FORMAT(sys_datetime_created, '%Y%m01 00:00:00') > DATE_FORMAT((NOW() - INTERVAL %s MONTH), '%Y%m01 00:00:00')
                GROUP BY ichibaItems_id DESC,DATE_FORMAT(sys_datetime_created, '%Y%m01');
            '''
    # print(sql.format(10))
    param = (DAILY_SEARCH_MONTH,)
    cur.execute(sql,param)
    ichibaitems_logs_data = cur.fetchall()
    # マンスリー集計値毎に処理
    for ichibaitems_logs in ichibaitems_logs_data:
        # 現在日時の取得
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        # システム更新日設定
        ichibaitems_logs['sys_datetime_modified'] = datetime_now_str
        # tmp_ichibaItemsの存在確認
        sql = 'SELECT * FROM tmp_ichibaItems WHERE uuid=%s'
        param = (ichibaitems_logs['ichibaItems_id'],)
        cur.execute(sql,param)
        tmp_ichibaItems_data = cur.fetchall()
        # tmp_ichibaItemsの判定
        if len(tmp_ichibaItems_data)>0:
            # 集計値の存在確認
            sql = 'SELECT * FROM tbl_ichibaItems_monthly WHERE monthly=%s and ichibaItems_id=%s'
            param = (ichibaitems_logs['monthly'],ichibaitems_logs['ichibaItems_id'])
            cur.execute(sql,param)
            tbl_ichibaItems_daily_data = cur.fetchall()
            # 集計値の判定
            if len(tbl_ichibaItems_daily_data)>0:
                # 【存在するとき】
                ichibaitems_logs['uuid'] = tbl_ichibaItems_daily_data[0]['uuid']
                # 既存レコードに上書更新
                cur.execute(ssdb.execute_update_dict( 'tbl_ichibaItems_monthly', 'uuid', **ichibaitems_logs),ichibaitems_logs)
            else:
                # 【存在しないとき】
                # UUID
                ichibaitems_logs['uuid'] = str(uuid.uuid4().hex)
                # システム作成日設定
                ichibaitems_logs['sys_datetime_created'] = datetime_now_str
                cur.execute(ssdb.execute_insert_dict2('tbl_ichibaItems_monthly',**ichibaitems_logs),ichibaitems_logs)
    # SQLコミット
    try:
        # 処理の待機
        time.sleep(TIME_SLEEP)
        ssdb.commit()
        print("SQLコミットに成功しました。")
    except Exception as e:
        print("SQLコミットに失敗しました。")
        print(e)
        nt(CH_FILE_NAME + "失敗","SQLコミットに失敗しました。\n\n【エラー内容】\n"+e)
        lg("失敗" + CH_FILE_NAME)
        sys.exit(1)


# get_itemの実行
def get_ichibaItems_all():
    # MySQL接続情報取得
    try:
        ssdb = StockSearchDB()
        # カーソルを設定
        cur = ssdb.cursor()
        # 実行ログUUID取得
        # ステータス待機中の情報を取得
        cur.execute("SELECT * FROM tbl_executelogs WHERE execute_status=1 AND execute_type=2 ORDER BY sys_datetime_created ASC")
        executelogs_data = cur.fetchall()
        cur.close()
        ssdb.close()
    except Exception as e:
        print("MySQL接続情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    for executelogs in executelogs_data:
        print("executelogsUUID："+str(executelogs['uuid']))
        get_ichibaItems()


# get_itemの実行
def get_ichibaItems():
    # RWS商品情報取得
    try:
        rws = RwsIchibaItemSearchInformation()
    except Exception as e:
        print("RWS商品情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    # MySQL接続情報取得
    try:
        ssdb = StockSearchDB()
    except Exception as e:
        print("MySQL接続情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    # カーソルを設定
    cur = ssdb.cursor()
    # 実行ログUUID取得
    # ステータス待機中の情報を取得
    cur.execute("SELECT * FROM tbl_executelogs WHERE execute_status=1 AND execute_type=2 ORDER BY sys_datetime_created ASC")
    executelogs_data = cur.fetchall()
    # 取得対象が存在するかで条件分岐
    # for executelogs in executelogs_data:
    if len(executelogs_data) > 0:
        # 取得対象が存在するとき
        executelogs = executelogs_data[0]
        # ステータス待機中を処理中,処理開始日時を更新
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        sql = 'UPDATE  tbl_executelogs SET sys_datetime_created = %s, sys_datetime_modified = %s, execute_status = %s, execute_datetime_start = %s, memo = %s WHERE uuid = %s'
        param = (datetime_now_str, datetime_now_str, 2, datetime_now_str, '対象処理は現在実行中です。', executelogs['uuid'])
        cur.execute(sql,param)
        ssdb.commit()
        # 店舗ライセンス情報を取得
        sql = 'SELECT * FROM mst_stores WHERE uuid=%s'
        param = (executelogs['stores_id'],)
        cur.execute(sql,param)
        stores_data = cur.fetchall()
        # SHOPコード毎にデータダウンロード処理
        for sd in stores_data:
            # 変数初期定義
            page = 0
            hits = 0
            pageCount   = 1
            params = {
                "shopCode"      : sd['shop_Code'],
                "hits"          : HITS,
                "carrier"       : CARRIER
            }
            # ページ毎繰り返し処理
            while page < pageCount:
                # RWS全体情報取得用受け皿【初期化】
                r_overall_info = {
                    "carrier"   :   None,
                    "count"     :   None,
                    "first"     :   None,
                    "hits"      :   None,
                    "last"      :   None,
                    "page"      :   None,
                    "pageCount" :   None
                }
                # パラメーター更新
                page += 1
                params["page"]  = page
                rws.set( **params)
                # RWS取得処理
                try:
                    r = rws.get()
                except Exception as e:
                    print("RWSページ取得処理に失敗しました。")
                    print(e)
                    sys.exit(1)
                # RWS全体情報取得用受け皿【更新】
                for k in r_overall_info.keys():
                    r_overall_info[k] = r[k]
                # 変数設定（ページ繰り返し用）
                pageCount       = r_overall_info["pageCount"]
                hits            += r_overall_info["hits"]
                print("【" + sd['name'] + "】" + str(r_overall_info["page"]) + "/" + str(r_overall_info["pageCount"]) + "ページ取得成功。")
                # 変数設定（sql一括インポート用辞書リスト作成）
                urlCount = 0
                # 取得したURL毎繰り返し処理実施
                while urlCount < r_overall_info["hits"]:
                    # 取得したJson型を辞書型に変換
                    data_dict = {}
                    for k,v in r['Items'][urlCount]['Item'].items():
                        data_dict[k] = v
                    # RWS全体情報取得用受け皿【挿入】
                    for k in r_overall_info.keys():
                        data_dict[k] = r_overall_info[k]
                    # ソート番号【挿入】
                    data_dict["sort"] = urlCount + 1
                    # UUID更新
                    data_dict["uuid"] = str(uuid.uuid4().hex)
                    data_dict["executelogs_id"] = executelogs['uuid']
                    # タイムスタンプ更新
                    # ステータス待機中を処理中,処理開始日時を更新
                    datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
                    datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
                    data_dict["sys_datetime_created"] = datetime_now_str
                    data_dict["sys_datetime_modified"] = datetime_now_str
                    # tmp_ichibaItems存在確認
                    sql = 'SELECT * FROM tmp_ichibaItems WHERE itemUrl=%s'
                    param = (data_dict['itemUrl'],)
                    cur.execute(sql,param)
                    tmp_ichibaItems_data = cur.fetchall()
                    # 入力情報の取得
                    # itemCode抽出
                    itemUrl_split =  data_dict['itemUrl'].split('/')
                    # imageUrl抽出
                    key = 'mediumImageUrls'
                    if key in data_dict.keys():
                        # 先頭のみ取得
                        for key2 in data_dict[key][0].keys():
                            imageUrl = data_dict[key][0][key2]
                    else:
                        imageUrl = ""
                    # dict初期化
                    d_dict = {
                        "sys_datetime_modified" :datetime_now_str,
                        "itemUrl"               :data_dict['itemUrl'],
                        "itemCode"              :data_dict['itemCode'],
                        "itemNumber"            :itemUrl_split[len(itemUrl_split)-2],
                        "imageUrl"              :imageUrl,
                        "itemPrice"             :data_dict['itemPrice'],
                        "reviewAverage"         :data_dict['reviewAverage'],
                        "reviewCount"           :data_dict['reviewCount'],
                        "genreId"               :data_dict['genreId'],
                        "stores_id"             :sd['uuid']
                    }
                    # ジャンルUUID存在確認
                    sql = 'SELECT * FROM tmp_ichibaGenres WHERE genreId=%s'
                    param = (d_dict['genreId'],)
                    cur.execute(sql,param)
                    tmp_ichibaGenres_data = cur.fetchall()
                    if len(tmp_ichibaGenres_data)>0:
                        d_dict["ichibaGenres_id"] = tmp_ichibaGenres_data[0]['uuid']
                    # tmp_ichibaItems存在確認
                    if len(tmp_ichibaItems_data)>0:
                        # tmp_ichibaItems存在する時【uuid取得】
                        data_dict["ichibaItems_id"] = tmp_ichibaItems_data[0]['uuid']
                        d_dict["uuid"] = data_dict["ichibaItems_id"]
                        # 既存レコードに上書更新
                        cur.execute(ssdb.execute_update_dict( 'tmp_ichibaItems', 'uuid', **d_dict),d_dict)
                    else:
                        # tmp_ichibaItems存在しない時【新規追加】
                        # uuid生成
                        data_dict["ichibaItems_id"] = str(uuid.uuid4().hex)
                        d_dict["uuid"] = data_dict["ichibaItems_id"]
                        # 作成日時更新
                        d_dict["sys_datetime_created"] = datetime_now_str
                        cur.execute(ssdb.execute_insert_dict2('tmp_ichibaItems',**d_dict),d_dict)
                    # tmp_ichibaItemgenres登録更新処理
                    # 処理ログ記載
                    print("     " + str(page) + "ページ：" + str(urlCount+1) + "/" + str(r_overall_info["hits"]) + "URL取得成功。")
                    # sqlインポート処理【ichiba_item】
                    try:
                        print(ssdb.execute_insert_dict2('tbl_ichibaItems_logs',**ssdb.conversion_dict_ichibaItem(**data_dict)))
                        print(ssdb.conversion_dict_ichibaItem(**data_dict))
                        print('---')
                        cur.execute(ssdb.execute_insert_dict2('tbl_ichibaItems_logs',**ssdb.conversion_dict_ichibaItem(**data_dict)),ssdb.conversion_dict_ichibaItem(**data_dict))
                    except Exception as e:
                        print("sqlインポート処理に失敗しました。【ichiba_item】")
                        print(e)
                        sys.exit(1)
                    # 処理の待機
                    time.sleep(TIME_SLEEP)
                    # URL更新
                    urlCount += 1
                # SQLコミット
                try:
                    ssdb.commit()
                except Exception as e:
                        print("SQLコミットに失敗しました。")
                        print(e)
                        nt(CH_FILE_NAME + "失敗","SQLコミットに失敗しました。\n\n【エラー内容】\n"+e)
                        lg("失敗" + CH_FILE_NAME)
                        sys.exit(1)
                # 処理の待機
                time.sleep(TIME_SLEEP)
            # 取得合計結果
            print("---")
            print("【合計値】")
            print("合計ページ数：" + str(r_overall_info["pageCount"]))
            print("合計url数（検索）：" + str(r_overall_info["count"]))
            print("合計url数（取得）：" + str(hits))
            print("---")
        # ExecuteLogsDB更新
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_end = datetime_now.strftime(DATE_TIME_FORMAT)
        # error_memo = '対象処理は成功しました。(ichibaItems合計url数（検索）：{})'.format(r_overall_info["count"])
        error_memo = '対象処理は成功しました。'
        sql = 'UPDATE  tbl_executelogs SET sys_datetime_modified = %s, execute_status = %s, execute_datetime_end = %s, memo = %s WHERE uuid = %s'
        param = (datetime_now_end, 3, datetime_now_end, error_memo, executelogs['uuid'])
        cur.execute(sql,param)
        ssdb.commit()
    # SQL閉じる処理
    try:
        cur.close()
        ssdb.close()
    except Exception as e:
        print("SQL閉じる処理に失敗しました。")
        print(e)
        sys.exit(1)


# get_itemの実行
def get_item():
    # RWS商品情報取得
    try:
        rws = RwsIchibaItemSearchInformation()
    except Exception as e:
        print("RWS商品情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    # MySQL接続情報取得
    try:
        ssdb = StockSearchDB()
    except Exception as e:
        print("MySQL接続情報取得に失敗しました。")
        print(e)
        sys.exit(1)
    # カーソルを設定
    cur = ssdb.cursor()
    # 実行ログUUID取得
    # ステータス待機中の情報を取得
    cur.execute("SELECT * FROM executelogs WHERE execute_status=1 AND execute_type=2 ORDER BY sys_datetime_created ASC")
    sql_res = cur.fetchall()
    # 取得対象が存在するかで条件分岐
    if len(sql_res) > 0:
        # 取得対象が存在するとき
        executelogs_data = sql_res[0]
        # ステータス待機中を処理中,処理開始日時を更新
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        sql = 'UPDATE  executelogs SET sys_datetime_created = %s, sys_datetime_modified = %s, execute_status = %s, execute_datetime_start = %s, memo = %s WHERE uuid = %s'
        param = (datetime_now_str, datetime_now_str, 2, datetime_now_str, '対象処理は現在実行中です。', executelogs_data['uuid'])
        cur.execute(sql,param)
        ssdb.commit()
        # 店舗ライセンス情報を取得
        sql = 'SELECT * FROM stores WHERE uuid=%s'
        param = (executelogs_data['stores_id'],)
        cur.execute(sql,param)
        stores_data = cur.fetchall()
        # SHOPコード毎にデータダウンロード処理
        for sd in stores_data:
            # 変数初期定義
            page = 0
            hits = 0
            pageCount   = 1
            params = {
                "shopCode"      : sd['shop_URL'],
                "hits"          : HITS,
                "carrier"       : CARRIER
            }
            # 楽天商品API定義
            print(sd['api_ID'])
            rgia = RwsGetItemyApi(sd['api_ID'].encode(encoding='utf-8'), sd['api_Key'].encode(encoding='utf-8'),)
            # ページ毎繰り返し処理
            while page < pageCount:
                # RWS全体情報取得用受け皿【初期化】
                r_overall_info = {
                    "carrier"   :   None,
                    "count"     :   None,
                    "first"     :   None,
                    "hits"      :   None,
                    "last"      :   None,
                    "page"      :   None,
                    "pageCount" :   None
                }
                # パラメーター更新
                page += 1
                params["page"]  = page
                rws.set( **params)
                # RWS取得処理
                try:
                    r = rws.get()
                except Exception as e:
                    print("RWSページ取得処理に失敗しました。")
                    print(e)
                    sys.exit(1)
                # RWS全体情報取得用受け皿【更新】
                for k in r_overall_info.keys():
                    r_overall_info[k] = r[k]
                # 変数設定（ページ繰り返し用）
                pageCount       = r_overall_info["pageCount"]
                hits            += r_overall_info["hits"]
                print("【" + sd['name'] + "】" + str(r_overall_info["page"]) + "/" + str(r_overall_info["pageCount"]) + "ページ取得成功。")
                # 変数設定（sql一括インポート用辞書リスト作成）
                urlCount = 0
                # 取得したURL毎繰り返し処理実施
                while urlCount < r_overall_info["hits"]:
                    # 取得したJson型を辞書型に変換
                    data_dict = {}
                    for k,v in r['Items'][urlCount]['Item'].items():
                        data_dict[k] = v
                    # RWS全体情報取得用受け皿【挿入】
                    for k in r_overall_info.keys():
                        data_dict[k] = r_overall_info[k]
                    # ソート番号【挿入】
                    data_dict["sort"] = urlCount + 1
                    # UUID更新
                    data_dict["uuid"] = str(uuid.uuid4().hex)
                    data_dict["executelogs_id"] = executelogs_data['uuid']
                    # タイムスタンプ更新
                    # ステータス待機中を処理中,処理開始日時を更新
                    datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
                    datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
                    data_dict["sys_datetime_created"] = datetime_now_str
                    data_dict["sys_datetime_modified"] = datetime_now_str
                    # 処理ログ記載
                    print("     " + str(page) + "ページ：" + str(urlCount+1) + "/" + str(r_overall_info["hits"]) + "URL取得成功。")
                    # sqlインポート処理【ichiba_item】
                    try:
                        print(ssdb.execute_insert_dict2('ichiba_item',**ssdb.conversion_dict_ichibaItem(**data_dict)))
                        print(ssdb.conversion_dict_ichibaItem(**data_dict))
                        print('---')
                        cur.execute(ssdb.execute_insert_dict2('ichiba_item',**ssdb.conversion_dict_ichibaItem(**data_dict)),ssdb.conversion_dict_ichibaItem(**data_dict))
                    except Exception as e:
                        print("sqlインポート処理に失敗しました。【ichiba_item】")
                        print(e)
                        sys.exit(1)
                    # sqlインポート処理【items】
                    # items取得フラグがONになっているとき
                    try:
                        # itemUrl抽出
                        itemUrl = data_dict['itemUrl'].split('/')
                        items_data = rgia.get(itemUrl[len(itemUrl)-2])
                        # uuid更新
                        items_data['uuid'] = str(uuid.uuid4().hex)
                        items_data['ichiba_item_id'] = data_dict['uuid']
                        # タイムスタンプ更新
                        items_data['sys_datetime_created'] = datetime_now_str
                        items_data['sys_datetime_modified'] = datetime_now_str
                        cur.execute(ssdb.execute_insert_dict2('items',**ssdb.conversion_dict_items(**items_data)),ssdb.conversion_dict_items(**items_data))
                    except Exception as e:
                        print("sqlインポート処理に失敗しました。【items】")
                        print(e)
                        sys.exit(1)
                    # 処理の待機
                    time.sleep(TIME_SLEEP)
                    # URL更新
                    urlCount += 1
                # SQLコミット
                try:
                    ssdb.commit()
                except Exception as e:
                        print("SQLコミットに失敗しました。")
                        print(e)
                        nt(CH_FILE_NAME + "失敗","SQLコミットに失敗しました。\n\n【エラー内容】\n"+e)
                        lg("失敗" + CH_FILE_NAME)
                        sys.exit(1)
                # 処理の待機
                time.sleep(TIME_SLEEP)
            # 取得合計結果
            print("---")
            print("【合計値】")
            print("合計ページ数：" + str(r_overall_info["pageCount"]))
            print("合計url数（検索）：" + str(r_overall_info["count"]))
            print("合計url数（取得）：" + str(hits))
            print("---")
        # ExecuteLogsDB更新
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_end = datetime_now.strftime(DATE_TIME_FORMAT)
        # error_memo = '対象処理は成功しました。(ichibaItems合計url数（検索）：{})'.format(r_overall_info["count"])
        error_memo = '対象処理は成功しました。'
        sql = 'UPDATE  executelogs SET sys_datetime_modified = %s, execute_status = %s, execute_datetime_end = %s, memo = %s WHERE uuid = %s'
        param = (datetime_now_end, 3, datetime_now_end, error_memo, executelogs_data['uuid'])
        cur.execute(sql,param)
        ssdb.commit()
    # SQL閉じる処理
    try:
        cur.close()
        ssdb.close()
    except Exception as e:
        print("SQL閉じる処理に失敗しました。")
        print(e)
        sys.exit(1)


# get_inventoryの実行
def get_inventory():
    ssdb  = StockSearchDB()
    cur01 = ssdb.cursor()
    # ステータス待機中の情報を取得
    cur01.execute("SELECT * FROM executelogs WHERE execute_status=1 AND execute_type=3 ORDER BY sys_datetime_created ASC")
    sql_res = cur01.fetchall()
    # 取得対象が存在するかで条件分岐
    if len(sql_res) > 0:
        # 取得対象が存在するとき
        executelogs_data = sql_res[0]
        # ステータス待機中を処理中,処理開始日時を更新
        datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
        datetime_now_str = datetime_now.strftime(DATE_TIME_FORMAT)
        sql = 'UPDATE  executelogs SET sys_datetime_created = %s, sys_datetime_modified = %s, execute_status = %s, execute_datetime_start = %s, memo = %s WHERE uuid = %s'
        param = (datetime_now_str, datetime_now_str, 2, datetime_now_str, '対象処理は現在実行中です。', executelogs_data['uuid'])
        cur01.execute(sql,param)
        ssdb.commit()
        # 店舗ライセンス情報を取得
        sql = 'SELECT * FROM stores WHERE uuid=%s'
        param = (executelogs_data['stores_id'],)
        cur01.execute(sql,param)
        stores_data = cur01.fetchall()[0]
        # 店舗ライセンス情報を基に在庫情報を取得
        rew_inventory = RwsGetInventoryApi(LICENSE_WSDL, stores_data['shop_Name'], stores_data['url'], stores_data['api_ID'].encode('utf-8'), stores_data['api_Key'].encode('utf-8'))
        inventory_res = rew_inventory.get_inventorySearchRange(99999)
        # エラーコードにより処理を分岐
        if inventory_res['errCode'] == 'N00-000':
            # 正常処理時
            print('処理は正常に取得できました：{}'.format(inventory_res['errCode']))
            # データを成形
            data = []
            for item in inventory_res['getResponseExternalItem']['GetResponseExternalItem']:
                for detail in item['getResponseExternalItemDetail']['GetResponseExternalItemDetail']:
                    row = {
                        'uuid'              : str(uuid.uuid4().hex),
                        'executelogs_id'    : executelogs_data['uuid'],
                        # ---
                        'itemNumber'        : item['itemNumber'],
                        'itemUrl'           : item['itemUrl'],
                        'inventoryType'     : item['inventoryType'],
                        'horizontalName'    : detail['HChoiceName'],
                        'verticalName'      : detail['VChoiceName'],
                        'inventoryCount'    : detail['inventoryCount'],
                        'normalDeliveryId'  : detail['normalDeliveryId'],
                        'lackDeliveryId'    : detail['lackDeliveryId']
                    }
                    data.append(row)
            # InventoriesDB全レコード削除
            sql = 'DELETE FROM inventories WHERE 1'
            cur01.execute(sql)
            ssdb.commit()
            # print('SKU数：'+str(len(data)))
            # 取得SKU単位に処理を繰り返す
            for d in data:
                # DeliveriesDB更新
                sql = 'SELECT * FROM deliveries WHERE stores_id=%s and delivery_id=%s'
                param = (executelogs_data['stores_id'], d['normalDeliveryId'])
                cur01.execute(sql,param)
                deliveries_data = cur01.fetchall()
                if len(deliveries_data) > 0 :
                    d['deliveries_id'] = deliveries_data[0]['uuid']
                # InventoriesDB更新
                sql = ssdb.execute_insert_dict2('inventories', **d)
                cur01.execute(sql,d)
            # sqlにデータ反映
            ssdb.commit()
            # ExecuteLogsDB更新
            datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
            datetime_now_end = datetime_now.strftime(DATE_TIME_FORMAT)
            error_memo = '対象処理は成功しました。(処理SKU件数：{})'.format(len(data))
            sql = 'UPDATE  executelogs SET sys_datetime_modified = %s, execute_status = %s, execute_datetime_end = %s, memo = %s WHERE uuid = %s'
            param = (datetime_now_end, 3, datetime_now_end, error_memo, executelogs_data['uuid'])
            cur01.execute(sql,param)
            ssdb.commit()
        else:
            # エラー発生時
            print('処理の取得は失敗しました：{}'.format(inventory_res['errCode']))
            # 実行ログ更新
            datetime_now = datetime.datetime.now(pytz.timezone(TIME_ZONE)) # 現在時刻の取得
            datetime_now_end = datetime_now.strftime(DATE_TIME_FORMAT)
            error_memo = '対象処理は失敗しました。{}（{}）'.format(inventory_res['errMessage'], inventory_res['errCode'])
            sql = 'UPDATE  executelogs SET execute_status = %s, execute_datetime_end = %s, memo = %s WHERE uuid = %s'
            param = (99, datetime_now_end, error_memo, executelogs_data['uuid'])
            cur01.execute(sql,param)
            ssdb.commit()
    else:
        # 取得対象が存在しない場合
        # エラー発生時
        print('処理の取得対象が存在しませんでした。')
    #閉じる
    cur01.close()
    ssdb.close()


if __name__ == '__main__':
    argument_code = sys.argv[1]
    print(argument_code)
    # time.sleep(100)
    print("----------")
    if argument_code == 'insert_items_executelogs':
        insert_items_executelogs()
    elif argument_code == 'get_ichibaItems':
        # get_ichibaItems()
        get_ichibaItems_all()
    elif argument_code == 'get_ichibaItems_total':
        get_ichibaItems_daily()
        get_ichibaItems_monthly()
    elif argument_code == 'get_genre':
        get_genre()
        get_itemgenres()
    elif argument_code == 'get_ranking':
        get_ranking()
    elif argument_code == 'get_inventory':
        get_inventory()
    else:
        print("error")
    print("----------")
    sys.exit()
