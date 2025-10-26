# mysql-connector-python
import mysql.connector as mysqldb
import sys

#入力タイプ制限
MYSQL_FIELD_FILTER_ICHIBAITEM  = [
    'uuid','sys_datetime_created','sys_datetime_modified','executelogs_id','ichibaItems_id',
    'affiliateRate','affiliateUrl','asurakuArea','asurakuClosingTime','asurakuFlag',
    'availability','catchcopy','creditCardFlag','endTime','genreId','giftFlag',
    'imageFlag','itemCaption','itemCode','itemName','itemPrice','itemUrl',
    'pointRate','pointRateEndTime','pointRateStartTime','postageFlag','reviewAverage',
    'reviewCount','shipOverseasArea','shipOverseasFlag','shopAffiliateUrl','shopCode',
    'shopName','shopOfTheYearFlag','shopUrl','startTime',
    #'tagIds','smallImageUrls','mediumImageUrls','updatedTimestamp',
    'mediumImageUrls',
    'taxFlag','carrier','count','first','hits','last','page','pageCount','sort'
]
MYSQL_FIELD_FILTER_ICHIBAITEM_LIST_FLAG  = ['tagIds','smallImageUrls','mediumImageUrls']

MYSQL_FIELD_FILTER_ICHIBAGENRE  = ['uuid','sys_datetime_created','sys_datetime_modified','malls_id','genreId','genreName','genreLevel','parentGenreId','ichibaGenres_parent_id']
MYSQL_FIELD_FILTER_ICHIBARANKING  = ['uuid','sys_datetime_created','sys_datetime_modified','genreId','itemCode','rank','shopCode','ichibaGenres_id','ichibaItems_id','stores_id','ichibaItemGenres_id','ichibaRankingGenres_id','lastBuildDate','title']

MYSQL_FIELD_FILTER_ITEMS  = ['sys_datetime_created','sys_datetime_modified','uuid','ichibaItems_id','itemUrl','itemNumber','itemPrice',
                            'genreId','catalogId','catalogIdExemptionReason','whiteBgImageUrl','descriptionForPC','descriptionForSmartPhone','movieUrl',
                            'catchCopyForPC','catchCopyForMobile','descriptionBySalesMethod','isSaleButton','isDocumentButton','isInquiryButton','isStockNoticeButton',
                            'displayMakerContents','itemLayout','isIncludedTax','isIncludedPostage','isIncludedCashOnDeliveryPostage','displayPrice','orderLimit','postage','isNoshiEnable',
                            'isTimeSale','timeSaleStartDateTime','timeSaleEndDateTime','isUnavailableForSearch','isDepot','detailSellType','asurakuDeliveryId','deliverySetId',
                            'sizeChartLinkCode','reviewDisp','displayPriceId','itemWeight','layoutCommonId','layoutMapId','textSmallId','lossLeaderId','textLargeId','isSingleItemShipping']




#RakutenWebService_Ichibaitemを操作するためのクラス
class MySqlControl:
    #初期値
    def __init__(self, cn_h, cn_p, cn_u, cn_pw, cn_db):
        # データベースへの接続とカーソルの生成
        #情報を設定
        try:
            self.connection = mysqldb.connect(
                host        = str(cn_h),
                port        = int(cn_p),
                user        = str(cn_u),
                passwd      = str(cn_pw),
                database    = str(cn_db),
                )
        except Exception as e:
            print(f"RWSINFO初期設定に失敗しました。: {e}")
            sys.exit(1)

    #カーソルを設定する
    def cursor(self, dicttype=True):
      return self.connection.cursor(dictionary=dicttype, buffered=True)

    #辞書型を一括インポート01
    def execute_insert_dict(self, tbl_name,**kwargs) -> str:
        try:
            #変数を定義
            tbl_deli    = '`'   #区切り文字
            key_deli    = '`'   #区切り文字
            val_deli    = '\''  #区切り文字
            keys        = ''    #項目名
            values      = ''    #値
            #辞書のキーワード分繰り返す
            for k,v in kwargs.items():
                #クォーテーション判定【】
                key     = 'null' if k is None else\
                            key_deli + str(k) + key_deli if type(k) is str else str(k)
                value   = 'null' if v is None else\
                            val_deli + str(v) + val_deli if type(v) is str else str(v)
                keys    += key if not keys else ', ' + key
                values  += value if not values else ', ' + value
            #sql構文作成
            sql =   'INSERT INTO '+ tbl_deli + tbl_name + tbl_deli + '(' + keys + ') VALUES (' + values + ')'
            # print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート01に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    
    #辞書型を一括インポート02
    def execute_insert_dict2(self, tbl_name, **kwargs) -> str:
        try:
            columns = kwargs.keys()
            cols_comma_separated = ', '.join(columns)
            binds_comma_separated = ', '.join(['%(' + item + ')s' for item in columns])
            sql = f'INSERT INTO {tbl_name} ({cols_comma_separated}) VALUES ({binds_comma_separated})'
            # print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート02に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    
    #辞書型を一括アップデート01
    def execute_update_dict(self, tbl_name, where_column, **kwargs) -> str:
        try:
            del kwargs[where_column]
            columns = kwargs.keys()
            # cols_comma_separated = ' = %s, '.join(columns)
            binds_comma_separated = ', '.join([item + ' = %(' + item + ')s ' for item in columns])
            sql = f'UPDATE {tbl_name} SET {binds_comma_separated} WHERE {where_column} = %({where_column})s'
            # print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート02に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql

    #辞書型一致する検索条件を表示
    def execute_select_dict(self, tbl_name, *args, **kwargs) -> str:
        try:
            columns = kwargs.keys()
            cols_comma_separated = ', '.join(args)
            binds_comma_separated = 'and '.join([str(k)+'=\''+v+'\' ' for k,v in kwargs.items()])
            sql = f'SELECT {cols_comma_separated} FROM `{tbl_name}` WHERE {binds_comma_separated}'
            print(sql)
        except Exception as e:
            print(f"MySQL辞書型を一括インポート02に失敗しました。: {e}")
            sys.exit(1)
        #返却値出力
        return sql
    #保存を実行
    def commit(self):
        try:
            self.connection.commit()
        except Exception as e:
            print(f"MySQLコミットに失敗しました。: {e}")
            sys.exit(1)
    #コネクションを閉じる
    def close(self):
        try:
            self.connection.close()
        except Exception as e:
            print(f"MySQLコネクションを閉じるのに失敗しました。: {e}")
            sys.exit(1)
    #辞書型の中にある配列、辞書のみ登録する。
    def conversion_dict_ichibaItem(self,**kwargs) -> dict:
        cd = {}
        for k,v in kwargs.items():
            if k in MYSQL_FIELD_FILTER_ICHIBAITEM:
                if k in MYSQL_FIELD_FILTER_ICHIBAITEM_LIST_FLAG:
                    # すべて取得
                    # val = []
                    # for i in v:
                    #     val2 = []
                    #     for k2,v2 in i.items():
                    #         val2.append(str(k2)+':'+str(v2))
                    #     val.append(','.join(val2))
                    # cd[k] = '\n'.join(val)
                    # ###
                    # 先頭のみ取得
                    for k2 in v[0].keys():
                       cd[k] = v[0][k2]
                else:
                    cd[k] = v
        return cd
    #辞書型の中にある配列、辞書のみ登録する。
    def conversion_dict_ichibaGenre(self,**kwargs) -> dict:
        cd = {}
        for k,v in kwargs.items():
            if k in MYSQL_FIELD_FILTER_ICHIBAGENRE:
                cd[k] = v
        return cd
    #辞書型の中にある配列、辞書のみ登録する。
    def conversion_dict_ichibaRanking(self,**kwargs) -> dict:
        cd = {}
        for k,v in kwargs.items():
            if k in MYSQL_FIELD_FILTER_ICHIBARANKING:
                cd[k] = v
        return cd
    #辞書型の中にある配列、辞書のみ登録する。
    def conversion_dict_items(self,**kwargs) -> dict:
        cd = {}
        for k,v in kwargs.items():
            if k in MYSQL_FIELD_FILTER_ITEMS:
                cd[k] = v
        return cd


#mainの実行
if __name__ == '__main__':
    print("\n----------")
    print("main")
    print("----------")