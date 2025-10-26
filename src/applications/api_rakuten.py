#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# RMS WEB SERVICE InventoryAPIを使用して商品在庫情報を一括取得する処理
# 以下プログラム

from stat import FILE_ATTRIBUTE_SPARSE_FILE
import zeep         #wsdl認証に使用
import base64       #API認証で使用
import json         #API取得結果を変換するのに使用
import requests #serchOrderリクエスト処理で使用
import time         #処理の待機時間で使用
import xmltodict    #XMLを辞書に変換する作業
#################################################

#待機時間
SLEEP_TIME = 0.25
#RWS inventoryapi 設定情報
RWS_INVENTORY_UPDATE_MAX = 400 # 更新上限数最大400
#RWS searchOrderApi 設定情報
RWS_SEARCH_ORDER_URL = 'https://api.rms.rakuten.co.jp/es/2.0/order/searchOrder/'
#RWS getOrderApi 設定情報
RWS_GET_ORDER_URL = 'https://api.rms.rakuten.co.jp/es/2.0/order/getOrder/'
RWS_GET_ORDER_NUMBER_LIST_MAX_COUNT = 100 # 最大値100
#RWS getItemyApi 設定情報
RWS_GET_ITEM_URL = 'https://api.rms.rakuten.co.jp/es/1.0/item/get'
#RWS LicenseManagementApi 設定情報
RWS_GET_LICENSE_MANAGEMENT_URL = 'https://api.rms.rakuten.co.jp/es/1.0/license-management/license-key/expiry-date'
# ############################################
# IchibaItem固定変数定義
ICHIBAITEMSEARCH__URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706'
# IchibaGenre固定変数定義
ICHIBAGENRESEARCH__URL = 'https://app.rakuten.co.jp/services/api/IchibaGenre/Search/20140222'
# IchibaRanking固定変数定義
ICHIBARANKINGSEARCH__URL = 'https://app.rakuten.co.jp/services/api/IchibaItem/Ranking/20170628'
# ############################################

# RakutenWebService_Ichibaitemを操作するためのクラス
class RwsIchibaItemSearch:
    #初期値
    def __init__(self, aplid, fmt='json', hits='30', page=1, availability=0, field=0,sort='-updateTimestamp'):
        try:
            #情報を設定
            self.url    = ICHIBAITEMSEARCH__URL
            self.params = {
                    "format"        : str(fmt),  #json or xml
                    "shopCode"      : '',
                    "keyword"       : '',
                    "itemCode"      : '',
                    "shopCode"      : '',
                    "genreId"       : '',
                    "applicationId" : str(aplid),
                    "availability"  : str(availability),
                    "field"         : str(field),
                    "hits"          : str(hits),
                    "page"          : str(page),
                    "sort"          : str(sort) 
            }
            #レスポンス結果を辞書型で保存(もとはjsonかxml)
            self.res        = {}
        except Exception as e:
            print(f"RWS情報設定に失敗しました。: {e}")
            sys.exit(1)
    #パラメータをセットする
    def set(self, **kwargs):
        try:
            #辞書のキーワード分繰り返す
            for k,v in kwargs.items():
                self.params[k] = str(v)
            # print(self.params)
        except Exception as e:
            print(f"RWSパラメートセットに失敗しました。: {e}")
            sys.exit(1)
    #レスポンスを取得する
    def get(self) -> dict:
        try:
            #初期化
            params = {}
            for k,v in self.params.items():
                if not len(self.params[k]) == 0:
                    params[k] = v
            # print(params)
            #Webサイトの情報を変数rに格納し、そのうちのテキスト部分を出力
            r = requests.get(self.url, params)
            #json形式を辞書型に変更
            self.res = r.json()
        except Exception as e:
            print(f"RWSレスポンス取得に失敗しました。: {e}")
            sys.exit(1)
        return self.res

#RakutenWebService_IchibaGenreを操作するためのクラス
class RwsIchibaGenreSearch:
    #初期値
    def __init__(self, aplid, fmt='json', fmtver=2, g_id=0 ):
        #情報を設定
        self.set(aplid, fmt , fmtver, g_id)
    #セット
    def set(self, aplid, fmt='json', fmtver=2, g_id=0 ):
        #情報を設定
        self.url    = ICHIBAGENRESEARCH__URL
        self.params = {
            'applicationId'     : aplid,
            'format'            : fmt,
            'formatVersion'     : fmtver,
            'genreId'           : g_id
        }
    #取得
    def get(self)-> dict:
        try:
            #Webサイトの情報を変数rに格納し、そのうちのテキスト部分を出力
            r = requests.get(self.url, self.params)
            #json形式を辞書型に変更
            self.res = r.json()
        except Exception as e:
            print(f"RWS情報設定に失敗しました。: {e}")
            sys.exit(1)
        return self.res
    


#RakutenWebService_IchibaRankingを操作するためのクラス
class RwsIchibaRankingSearch:
    #初期値
    def __init__(self, aplid, period="realtime", fmt="json", genreId=0, page=1):
        try:
            #情報を設定
            self.url    = ICHIBARANKINGSEARCH__URL
            self.params = {
                    "format"        : str(fmt),
                    "applicationId" : str(aplid),
                    "genreId"       : str(genreId),
                    "page"          : str(page),
                    "elements"      : "",
                    # "period"        : str(period),
                    "affiliateID"   : "",
                    "formatVersion" : "",
                    "age"           : "",
                    "sex"           : "",
                    "carrier"       : "",
            }
            #レスポンス結果を辞書型で保存(もとはjsonかxml)
            self.res        = {}
        except Exception as e:
            print(f"RWS情報設定に失敗しました。: {e}")
            sys.exit(1)
    
    #パラメータをセットする
    def set(self, **kwargs):
        try:
            #辞書のキーワード分繰り返す
            for k,v in kwargs.items():
                self.params[k] = str(v)
            # print(self.params)
        except Exception as e:
            print(f"RWSパラメートセットに失敗しました。: {e}")
            sys.exit(1)
    #レスポンスを取得する
    def get(self) -> dict:
        try:
            #初期化
            params = {}
            for k,v in self.params.items():
                if not len(self.params[k]) == 0:
                    params[k] = v
            # print(params)
            #Webサイトの情報を変数rに格納し、そのうちのテキスト部分を出力
            r = requests.get(self.url, params)
            #json形式を辞書型に変更
            self.res = r.json()
            # print(self.res)
        except Exception as e:
            print(f"RWSレスポンス取得に失敗しました。: {e}")
            sys.exit(1)
        return self.res


# ライセンスの有効期限を取得するAPIです。
class RwsLicenseManagementApi:
    # 初期値
    def __init__(self, serviceSecret, licensekey):
        self.headers = {
            'Authorization' : b"ESA " + base64.b64encode(serviceSecret + b':' + licensekey),
            'Content-Type': 'application/json; charset=utf-8',
        }
        self.params={'licenseKey': licensekey}
    # 取得
    def get(self) -> str:
        response = requests.get(
            RWS_GET_LICENSE_MANAGEMENT_URL,
            params=self.params,
            headers = self.headers,
        )
        #json型をdict型に変換
        json_string = str(response.text)
        json_dict = json.loads(json_string.replace('\'', '"'))
        # 取得情報を確認
        if 'expiryDate' in json_dict.keys():
            return json_dict['expiryDate']
        else:
            return ""


# RWS商品情報を操作するためのクラス
class RwsGetItemyApi:
    # 初期値
    def __init__(self, serviceSecret, licensekey):
        self.headers = {
            'Authorization' : b"ESA " + base64.b64encode(serviceSecret + b':' + licensekey),
            'Content-Type': 'application/xml; charset=utf-8',
        }
    # 商品情報を取得
    def get(self, itemUrl) -> dict:
        response = requests.get(
            RWS_GET_ITEM_URL,
            params={'itemUrl': itemUrl},
            headers = self.headers,
        )
        # json型をdict型に変換
        dict_xml = xmltodict.parse(response.text)
        # 取得条件に処理処理を分岐
        if dict_xml['result']['status']['systemStatus'] == 'OK' and dict_xml['result']['itemGetResult']['code'] == 'N000':
            return dict_xml['result']['itemGetResult']['item']
        else:
            print( 'systemStatus:' + dict_xml['result']['status']['systemStatus'])
            print( 'message:' + dict_xml['result']['status']['message'])
            print( 'code:' + dict_xml['result']['itemGetResult']['code'])
            return {}
    # 商品情報を成形する
    # def get_conversion(self, itemUrl) -> dict:
    #     res = self.get(itemUrl)
    #     for r in res:


#RWS在庫情報を操作するためのクラス
class RwsGetInventoryApi:
    #初期値
    def __init__(self, wsdl, userName, shopUrl, serviceSecret, licensekey):
        #変数定義
        self.wsdl = wsdl
        self.userName = userName
        self.shopUrl = shopUrl
        self.serviceSecret = serviceSecret
        self.licensekey = licensekey
        #wsdl情報取得
        self.client = zeep.Client(wsdl = self.wsdl)
        #接続基本設定
        self.ArrayOfString = self.client.get_type('ns0:ArrayOfString')
        self.factory = self.client.type_factory('ns1')
        self.externalUserAuthModel = self.factory.ExternalUserAuthModel(
            authKey = b"ESA " + base64.b64encode(self.serviceSecret + b':' + self.licensekey),
            userName = self.userName,
            shopUrl = self.shopUrl,
        )
    #Get処理
    def get(self,*urlRequests) -> dict:
        # モデルの選択
        self.getMethod = getattr(self.client.service, 'getInventoryExternal')
        # パラメータ設定
        response = self.getMethod(
            externalUserAuthModel = self.externalUserAuthModel,
            getRequestExternalModel = self.factory.GetRequestExternalModel(
                itemUrl = self.ArrayOfString(list(urlRequests))
            )
        )
        #処理の待機（API送信コスト軽減のため）
        time.sleep(SLEEP_TIME)
        #json型をdict型に変換
        json_string = str(response)
        json_dict = json.loads(json_string.replace('\'', '"'))
        return json_dict
    #Get処理 itemUrl
    def get_itemUrl(self,*urlRequests) -> dict:
        # モデルの選択
        self.getMethod = getattr(self.client.service, 'getInventoryExternal')
        # パラメータ設定
        response = self.getMethod(
            externalUserAuthModel = self.externalUserAuthModel,
            getRequestExternalModel = self.factory.GetRequestExternalModel(
                itemUrl = self.ArrayOfString(list(urlRequests))
            )
        )
        #処理の待機（API送信コスト軽減のため）
        time.sleep(SLEEP_TIME)
        #json型をdict型に変換
        json_string = str(response)
        json_dict = json.loads(json_string.replace('\'', '"'))
        return json_dict
    #Get処理 inventorySearchRange 
    def get_inventorySearchRange(self, inventorySearchRange) -> dict:
        # モデルの選択
        self.getMethod = getattr(self.client.service, 'getInventoryExternal')
        # パラメータ設定
        response = self.getMethod(
            externalUserAuthModel = self.externalUserAuthModel,
            getRequestExternalModel = self.factory.GetRequestExternalModel(
                inventorySearchRange = inventorySearchRange
            )
        )
        #処理の待機（API送信コスト軽減のため）
        time.sleep(SLEEP_TIME)
        #json型をdict型に変換
        json_string = str(response)
        json_dict = json.loads(json_string.replace('\'', '"'))
        return json_dict
    def update(self, *items) -> dict:
        # 取得できる最大値を抽出
        maxLenght = len(items) if len(items)<RWS_INVENTORY_UPDATE_MAX else RWS_INVENTORY_UPDATE_MAX
        # モデルの選択
        self.updateMethod = getattr(self.client.service, 'updateInventoryExternal')
        # 初期値を設定
        UpdateRequestExternalItemList = []
        # 繰り返しパラメータを設定
        for i in items[0:maxLenght]:
            UpdateRequestExternalItemList.append(
                self.factory.UpdateRequestExternalItem(
                    itemUrl                 =   i['itemUrl'], # '10000004', 
                    inventoryType           =   i['inventoryType'], 
                    HChoiceName             =   i['HChoiceName'], 
                    VChoiceName             =   i['VChoiceName'],
                    inventoryUpdateMode     =   i['inventoryUpdateMode'],
                    orderFlag               =   i['orderFlag'],
                    orderSalesFlag          =   i['orderSalesFlag'],
                    restTypeFlag            =   i['restTypeFlag'],
                    inventoryBackFlag       =   i['inventoryBackFlag'],
                    lackDeliveryDeleteFlag  =   i['lackDeliveryDeleteFlag'],
                    lackDeliveryId          =   i['lackDeliveryId'],
                    nokoriThreshold         =   i['nokoriThreshold'],
                    normalDeliveryDeleteFlag=   i['normalDeliveryDeleteFlag'],
                    normalDeliveryId        =   i['normalDeliveryId'],
                    inventory               =   i['inventory'] 
                )
            )
        # パラメータ設定
        response = self.updateMethod(
            externalUserAuthModel=self.externalUserAuthModel,
            updateRequestExternalModel=self.factory.UpdateRequestExternalModel(
                updateRequestExternalItem=self.ArrayOfString(UpdateRequestExternalItemList)
            )
        )
        #json型をdict型に変換
        json_string = str(response)
        json_dict = json.loads(json_string.replace('\'', '"'))
        # print(json_dict)
        #response結果判定
        if json_dict['errCode'] == 'N00-000':
            #正常終了の時
            print('在庫情報が正常アップデート完了しました。')
            print("エラーコード:"+str(json_dict['errCode']))
            print("エラーメッセージ"+str(json_dict['errMessage']))
            print("---")
            # 注文情報残があった場合は、排他的に繰り返す
            if len(items[maxLenght:])>0:
                self.update(*items[maxLenght:])
            return json_dict
        else:
            #エラーの時
            #正常終了でなければ処理を中断する
            print("処理が正常終了しませんでした。[update]")
            print("処理を中断します。")
            print("エラーコード:"+str(json_dict['errCode']))
            print("エラーメッセージ"+str(json_dict['errMessage']))
            print("---")
            return json_dict
    #取得処理
    def get_itemUrl_request(self,*urlRequests) -> list:
        #Get処理
        json_dict = self.get_itemUrl(*urlRequests)
        #response結果判定
        if json_dict['errCode'] == 'N00-000':
            #正常終了の時
            #空配列作成
            arr = []
            #item単位の情報取得
            for item in json_dict['getResponseExternalItem']['GetResponseExternalItem']:
                #detail単位の情報取得
                for detail in item['getResponseExternalItemDetail']['GetResponseExternalItemDetail']:
                    arr.append({
                        'itemNumber'        :   str(item['itemNumber']), 
                        'itemUrl'           :   str(item['itemUrl']), 
                        'inventoryType'     :   str(item['inventoryType']), 
                        'nokoriThreshold'   :   str(item['nokoriThreshold']),
                        'restTypeFlag'      :   str(item['restTypeFlag']),
                        'HChoiceName'       :   str(detail['HChoiceName']),
                        'VChoiceName'       :   str(detail['VChoiceName']),
                        'inventoryBackFlag' :   str(detail['inventoryBackFlag']),
                        'inventoryCount'    :   str(detail['inventoryCount']),
                        'lackDeliveryId'    :   str(detail['lackDeliveryId']),
                        'orderFlag'         :   str(detail['orderFlag']),
                        'orderSalesFlag'    :   str(detail['orderSalesFlag']),
                        'normalDeliveryId'  :   str(detail['normalDeliveryId'])
                                        })
            print("処理が正常終了しました。")
            print("検索URL"+str(urlRequests))
            print("検索URL数："+str(len(urlRequests)))
            print("---")
            return arr
        elif json_dict['errCode'] == 'W21-503':
            #検索結果が制限値を超えています
            print("検索条件で1000件を超える数の情報が検出されました。")
            print("エラーコード:"+str(json_dict['errCode']))
            print("下記検索URLを1件ずつ取得処理します。")
            print("検索URL"+str(urlRequests))
            print("---")
            #初期化
            arrs = []
            #1件ずつrequest処理を実行
            for item in urlRequests:
                #再帰的に実行
                arrs.append(self.get_itemUrl_request(self,item))
            return arrs
        elif json_dict['errCode'] == 'W21-202':
            #検索結果が0件の時
            print("検索結果が0件でした。")
            print("処理をスキップします。")
            print("検索URL"+str(urlRequests))
            print("---")
            return []
        else:
            #エラーの時
            #正常終了でなければ処理を中断する
            print("処理が正常終了しませんでした。[getRequest]")
            print("処理を中断します。")
            print("エラーコード:"+str(json_dict['errCode']))
            print("検索URL"+str(urlRequests))
            print("---")
            return []


# 検索条件を指定して注文を検索し、ヒットした検索の注文番号リストを取得する
class RwsSearchOrderApi:
    # 初期値
    def __init__(self,  serviceSecret, licensekey):
        #変数定義
        self.header = {
            'Authorization' : b"ESA " + base64.b64encode(serviceSecret + b':' +licensekey),
            'Content-Type': 'application/json; charset=utf-8',
        }
        self.param = {
            'dateType':1# 注文日
        }
        self.req = []# 結果格納用
        self.totalPages = 0# トータルページ数
        self.totalRecordsAmount = 0# トータル検索結果数
        # レスポンス結果用
        self.MessageModelList = {
            'messageType'   :   None,
            'messageCode'   :   None,
            'message'       :   None
        }
    # 取得
    def postRequest(self,startTimestamp,endTimestamp,requestRecordsAmount,requestPage=1):
        # 注文日時期間設定
        self.param['startDatetime'] = startTimestamp
        self.param['endDatetime'] = endTimestamp
        self.param['PaginationRequestModel'] = {
            'requestRecordsAmount':requestRecordsAmount,
            'requestPage':requestPage
            }
        # POST処理
        req_json = requests.post(RWS_SEARCH_ORDER_URL, json=self.param, headers=self.header)
        # jsonを辞書変換
        req_dict =  json.loads(req_json.text)
        # レスポンス結果を抽出
        for k,v in req_dict['MessageModelList'][0].items():
            self.MessageModelList[k] = v
        # エラーでない場合は処理を実行
        if self.MessageModelList['messageType'] == 'INFO':
            # メッセージ種別がINFOの場合
            # 注文データのみ抽出
            self.req.extend(req_dict['orderNumberList'])
            # 注文が存在する場合、処理を続行
            if req_dict['PaginationResponseModel']['totalRecordsAmount'] != None:
                # トータル検索結果数を抽出
                self.totalRecordsAmount = int(req_dict['PaginationResponseModel']['totalRecordsAmount'])
                # トータルページ数を抽出
                self.totalPages = int(req_dict['PaginationResponseModel']['totalPages'])
                print('searchOrder結果は正常です（ページ数：'+str(requestPage)+' 取得受注番号数：'+str(len(self.req))+'）')
                # ページ残があれば排他的処理
                if requestPage<self.totalPages:
                    self.postRequest(startTimestamp,endTimestamp,requestRecordsAmount,requestPage=requestPage+1)
            else:
                print('注文は存在しませんでした。')
        else:
            # メッセージ種別がINFO以外の場合
            print('searchOrder結果に警告があります。')
            print('searchOrder取得処理を中断しました。')
            for k,v in self.MessageModelList.items():
                print(str(k)+':'+str(v))

# 対象店舗の注文番号をリストで指定、受注の詳細情報を取得する
class RwsGetOrderApi:
    # 初期値
    def __init__(self,  serviceSecret, licensekey):
        # 変数定義
        self.header = {
            'Authorization' : b"ESA " + base64.b64encode(serviceSecret + b':' +licensekey),
            'Content-Type': 'application/json; charset=utf-8',
        }
        self.param = {
            'version':6 # 顧客・配送対応注意表示詳細対応
        }
        self.req = []   # 結果格納用
        # レスポンス結果用
        self.MessageModelList = {
            'messageType'   :   None,
            'messageCode'   :   None,
            'message'       :   None
        }
    # 取得
    def postRequest(self,*orderNumberList):
        # 取得できる最大値を抽出
        maxLenght = len(orderNumberList) if len(orderNumberList)<RWS_GET_ORDER_NUMBER_LIST_MAX_COUNT else RWS_GET_ORDER_NUMBER_LIST_MAX_COUNT
        # 受注番号リストをパラメータに設定
        self.param['orderNumberList'] = orderNumberList[0:maxLenght]
        # POST処理
        req_json = requests.post(RWS_GET_ORDER_URL, json=self.param, headers=self.header)
        # jsonを辞書変換
        req_dict =  json.loads(req_json.text)
        # レスポンス結果を抽出
        for k,v in req_dict['MessageModelList'][0].items():
            self.MessageModelList[k] = v
        # エラーでない場合は処理を実行
        if self.MessageModelList['messageType'] == 'INFO':
            # メッセージ種別がINFOの場合
            # 注文データのみ抽出
            self.req.extend(req_dict['OrderModelList'])
            print('getOrder結果は正常です（処理合計件数：'+str(len(self.req))+'）')
            # 注文情報残があった場合は、排他的に繰り返す
            if len(orderNumberList[maxLenght:])>0:
                self.postRequest(*orderNumberList[maxLenght:])
        else:
            # メッセージ種別がINFO以外の場合
            print('getOrder結果に警告があります。')
            print('getOrder取得処理を中断しました。')
            for k,v in self.MessageModelList.items():
                print(str(k)+':'+str(v))

# 最初の実行される
if __name__ == "__main__":
    print("処理を開始します。")
    print("main")
    print("処理が正常終了しました。")