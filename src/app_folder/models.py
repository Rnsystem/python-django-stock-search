from django.db import models
# uuid使用のため読み出し
import uuid
# ユーザモデルの読み出し
from django.contrib.auth.models import User

# tmp：ワークテーブル
# tbl：トランザクションテーブル
# mst：マスタテーブル

# Years
class YearsDB(models.Model):
    class Meta:
        db_table = 'mst_years' # DB内で使用するテーブル名
        verbose_name_plural = 'mst_years' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    name = models.CharField( max_length=128, null=True, blank=True, help_text='管理名')
    datetime_start = models.DateTimeField(help_text='開始日時')
    datetime_end = models.DateTimeField(help_text='終了日時')

# Months
class MonthsDB(models.Model):
    class Meta:
        db_table = 'mst_months' # DB内で使用するテーブル名
        verbose_name_plural = 'mst_months' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    years = models.ForeignKey(YearsDB, verbose_name='yearsID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_months_years') # 外部キー　CASCADE：親が消されたら削除する
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    name = models.CharField( max_length=128, null=True, blank=True, help_text='管理名')
    datetime_start = models.DateTimeField(help_text='開始日時')
    datetime_end = models.DateTimeField(help_text='終了日時')

# Days
class DaysDB(models.Model):
    class Meta:
        db_table = 'mst_days' # DB内で使用するテーブル名
        verbose_name_plural = 'mst_days' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    months = models.ForeignKey(MonthsDB, verbose_name='monthsID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_days_months') # 外部キー　CASCADE：親が消されたら削除する
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    name = models.CharField( max_length=128, null=True, blank=True, help_text='管理名')
    datetime_start = models.DateTimeField(help_text='開始日時')
    datetime_end = models.DateTimeField(help_text='終了日時')

# news
class NewsDB(models.Model):
    class Meta:
        db_table = 'tbl_news' # DB内で使用するテーブル名
        verbose_name_plural = 'tbl_news' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    posting_datetime = models.DateTimeField(help_text='投稿日時')
    posting_user = models.CharField( max_length=64, null=True, blank=True, help_text='投稿者')
    title = models.CharField( max_length=128, null=True, blank=True, help_text='タイトル')
    exposition = models.CharField( max_length=1024, null=True, blank=True, help_text='説明文')

# malls
class MallsDB(models.Model):
    class Meta:
        db_table = 'mst_malls' # DB内で使用するテーブル名
        verbose_name_plural = 'mst_malls' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    name = models.CharField( max_length=128, null=True, blank=True, help_text='モール名')
    url = models.CharField( max_length=256, null=True, blank=True, help_text='モールurl')

# stores
class StoresDB(models.Model):
    IS_EXE_CHOICES = (
        (False, '停止'),
        (True, '連動')
    )
    class Meta:
        db_table = 'mst_stores' # DB内で使用するテーブル名
        verbose_name_plural = 'mst_stores' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    malls = models.ForeignKey(MallsDB, on_delete=models.CASCADE, related_name='related_stores_malls') # 外部キー　CASCADE：親が消されたら削除する
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    name = models.CharField( max_length=128, null=True, blank=True, help_text='ストア名')
    url = models.CharField( max_length=256, null=True, blank=True, help_text='url')
    is_exe = models.BooleanField(default=False,null=False,help_text='連動ならTRUE',choices=IS_EXE_CHOICES)
    api_No = models.CharField( max_length=256, null=True, blank=True, help_text='API管理番号')
    api_ID = models.CharField( max_length=256, null=True, blank=True, help_text='API ID')
    api_Key = models.CharField( max_length=256, null=True, blank=True, help_text='APIライセンスキー')
    shop_Name = models.CharField( max_length=128, null=True, blank=True, help_text='ショップ名')
    shop_No = models.CharField( max_length=128, null=True, blank=True, help_text='ショップ管理番号')
    shop_Code = models.CharField( max_length=128, null=True, blank=True, help_text='ショップコード')
    shop_ID = models.CharField( max_length=128, null=True, blank=True, help_text='ショップID')
    shop_Password = models.CharField( max_length=128, null=True, blank=True, help_text='ショップパスワード')
    user_Name = models.CharField( max_length=128, null=True, blank=True, help_text='ユーザ名')
    user_No = models.CharField( max_length=128, null=True, blank=True, help_text='ユーザ管理番号')
    user_ID = models.CharField( max_length=128, null=True, blank=True, help_text='ユーザID')
    user_Password = models.CharField( max_length=128, null=True, blank=True, help_text='ユーザパスワード')
    shop_URL = models.CharField( max_length=128, null=True, blank=True, help_text='ショップURL')
    # テーブルの名前を定義（外部から呼び出される時に使用される名前）
    def __str__(self):
        return self.malls.name + ' ' + self.name

# ExecuteLogs
class ExecuteLogsDB(models.Model):
    EXECUTE_STATUS_CHOICES = (
        (0, '未選択'),
        (1, '待機'),
        (2, '処理中'),
        (3, '完了'),
        (99, 'エラー')
    )
    EXECUTE_TYPE_CHOICES = (
        (0, '未選択'),
        (1, '受注'),
        (2, '商品'),
        (3, '在庫'),
        (99, 'エラー')
    )
    class Meta:
        db_table = 'tbl_executelogs' # DB内で使用するテーブル名
        verbose_name_plural = 'tbl_executelogs' # Admionサイトで表示するテーブル名
    sys_datetime_created = models.DateTimeField(auto_now_add=True, verbose_name='作成日時', help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, verbose_name='更新日時', help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, verbose_name='UUID', unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    user = models.ForeignKey(User, verbose_name='実行者', on_delete=models.CASCADE, null=True,blank=True, related_name='related_executelogs_user')
    stores = models.ForeignKey(StoresDB, verbose_name='ストアID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_executelogs_stores') # 外部キー　CASCADE：親が消されたら削除する
    execute_datetime_start = models.DateTimeField(help_text='実行開始日時', null=True,blank=True)
    execute_datetime_end = models.DateTimeField(help_text='実行終了日時', null=True,blank=True)
    execute_status = models.PositiveSmallIntegerField(default=0, verbose_name='処理状況', null=True, blank=True, help_text='処理状況',choices=EXECUTE_STATUS_CHOICES)
    execute_type = models.PositiveSmallIntegerField(default=0, verbose_name='処理タイプ', null=True, blank=True, help_text='処理タイプ',choices=EXECUTE_TYPE_CHOICES)
    memo = models.CharField(max_length=256, verbose_name='備考', null=True, blank=True, help_text='備考')

# Deliveries(delivery)
class DeliveriesDB(models.Model):
    class Meta:
        db_table = 'mst_deliveries' # DB内で使用するテーブル名
        verbose_name_plural = 'mst_deliveries' # Admionサイトで表示するテーブル名
        # 複合ユニーク制約
        constraints = [
            models.UniqueConstraint(fields=['stores', 'delivery_id'], name='unique_delivery')
        ]
        # ソート順指定
        ordering = ['delivery_id']
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    stores = models.ForeignKey(StoresDB, verbose_name='ストアID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_deliveries_stores') # 外部キー　CASCADE：親が消されたら削除する
    # 納期管理情報
    delivery_id = models.PositiveSmallIntegerField(verbose_name='管理ID', null=True, blank=True, help_text='管理ID')
    delivery_no = models.PositiveSmallIntegerField(verbose_name='管理番号', null=True, blank=True, help_text='管理番号')
    delivery_name = models.CharField(max_length=128, verbose_name='お届けの目安', null=True, blank=True, help_text='お届けの目安')
    delivery_days = models.PositiveSmallIntegerField(default=0, verbose_name='お届け日数', null=True, blank=True, help_text='お届け日数')
    delivery_memo = models.CharField(max_length=256, verbose_name='備考', null=True, blank=True, help_text='備考')
    # テーブルの名前を定義（外部から呼び出される時に使用される名前）
    def __str__(self):
        return self.delivery_name

# IchibaGenres(IchibaGenres)
class IchibaGenresDB(models.Model):
    class Meta:
        db_table = 'tmp_ichibaGenres' # DB内で使用するテーブル名
        verbose_name_plural = 'tmp_ichibaGenres' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    malls = models.ForeignKey(MallsDB, verbose_name='モールID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_tmp_ichibaGenres_malls') # 外部キー　CASCADE：親が消されたら削除する
    ichibaGenres_parent = models.ForeignKey('self', verbose_name='ichibaGenres_parent', on_delete=models.PROTECT, null=True,blank=True, related_name='related_tmp_ichibaGenres_ichibaGenres_parent') # 外部キー　CASCADE：親が消されたら削除する
    # ジャンル情報
    genreId = models.CharField(max_length=8, verbose_name='genreId', null=True, blank=True, help_text='genreId')
    genreName = models.CharField(max_length=128, verbose_name='genreName', null=True, blank=True, help_text='genreName')
    genreLevel = models.PositiveSmallIntegerField(verbose_name='genreLevel', null=True, blank=True, help_text='genreLevel')
    parentGenreId = models.CharField(max_length=8, verbose_name='parentGenreId', null=True, blank=True, help_text='parentGenreId')

# IchibaItems(IchibaItems)
class IchibaItemsDB(models.Model):
    class Meta:
        db_table = 'tmp_ichibaItems' # DB内で使用するテーブル名
        verbose_name_plural = 'tmp_ichibaItems' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    stores = models.ForeignKey(StoresDB, verbose_name='ストアID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItems_stores') # 外部キー　CASCADE：親が消されたら削除する
    ichibaGenres = models.ForeignKey(IchibaGenresDB, verbose_name='楽天市場ジャンルID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItems_ichibaGenres') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報
    itemUrl = models.CharField(max_length=256, verbose_name='商品Url', null=True, blank=True, help_text='商品Url', unique=True)
    itemCode = models.CharField(max_length=64, verbose_name='商品コード', null=True, blank=True, help_text='商品コード')
    itemNumber = models.CharField(max_length=32, verbose_name='商品番号', null=True, blank=True, help_text='商品番号')
    imageUrl = models.TextField(max_length=1024, verbose_name='画像Url', null=True, blank=True, help_text='画像Url')
    itemPrice = models.PositiveSmallIntegerField(verbose_name='itemPrice', null=True, blank=True, help_text='itemPrice')
    reviewAverage = models.FloatField(verbose_name='reviewAverage', null=True, blank=True, help_text='reviewAverage')
    reviewCount = models.PositiveSmallIntegerField(verbose_name='reviewCount', null=True, blank=True, help_text='reviewCount')
    genreId = models.CharField(max_length=8, verbose_name='genreId', null=True, blank=True, help_text='genreId')


# IchibaItemGenres(ichibaItemGenres)
class IchibaItemGenresDB(models.Model):
    class Meta:
        db_table = 'tmp_ichibaItemGenres' # DB内で使用するテーブル名
        verbose_name_plural = 'tmp_ichibaItemGenres' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    stores = models.ForeignKey(StoresDB, verbose_name='ストアID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItemGenres_stores') # 外部キー　CASCADE：親が消されたら削除する
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品ID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItemGenres_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    ichibaGenres = models.ForeignKey(IchibaGenresDB, verbose_name='楽天市場ジャンルID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItemGenres_ichibaGenres') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報


# IchibaItemsDaily(IchibaItems)
class IchibaItemsDailyDB(models.Model):
    class Meta:
        db_table = 'tbl_ichibaItems_daily' # DB内で使用するテーブル名
        verbose_name_plural = 'tbl_ichibaItems_daily' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品ID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItems_daily_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報
    daily = models.DateTimeField(verbose_name='デイリー(YYYY/MM/DD)', null=False, blank=True, help_text='デイリー(YYYY/MM/DD)')
    itemPrice = models.PositiveSmallIntegerField(verbose_name='itemPrice', null=True, blank=True, help_text='itemPrice')
    reviewAverage = models.FloatField(verbose_name='reviewAverage', null=True, blank=True, help_text='reviewAverage')
    reviewCount = models.PositiveSmallIntegerField(verbose_name='reviewCount', null=True, blank=True, help_text='reviewCount')
    summaryCount = models.PositiveSmallIntegerField(verbose_name='summaryCount', null=True, blank=True, help_text='summaryCount')

# IchibaItemsMonthly(IchibaItems)
class IchibaItemsMonthlyDB(models.Model):
    class Meta:
        db_table = 'tbl_ichibaItems_monthly' # DB内で使用するテーブル名
        verbose_name_plural = 'tbl_ichibaItems_monthly' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品ID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItems_monthly_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報
    monthly = models.DateTimeField(verbose_name='マンスリー(YYYY/MM)', null=False, blank=True, help_text='マンスリー(YYYY/MM)')
    itemPrice = models.PositiveSmallIntegerField(verbose_name='itemPrice', null=True, blank=True, help_text='itemPrice')
    reviewAverage = models.FloatField(verbose_name='reviewAverage', null=True, blank=True, help_text='reviewAverage')
    reviewCount = models.PositiveSmallIntegerField(verbose_name='reviewCount', null=True, blank=True, help_text='reviewCount')
    summaryCount = models.PositiveSmallIntegerField(verbose_name='summaryCount', null=True, blank=True, help_text='summaryCount')

# IchibaItemsLogs(IchibaItems)
class IchibaItemsLogsDB(models.Model):
    class Meta:
        db_table = 'tbl_ichibaItems_logs' # DB内で使用するテーブル名
        verbose_name_plural = 'tbl_ichibaItems_logs' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品ID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItems_logs_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    executelogs = models.ForeignKey(ExecuteLogsDB, verbose_name='実行ログID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaItems_logs_executelogs') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報
    affiliateRate = models.PositiveSmallIntegerField(verbose_name='affiliateRate', null=True, blank=True, help_text='affiliateRate')
    affiliateUrl = models.CharField(max_length=256, verbose_name='affiliateUrl', null=True, blank=True, help_text='affiliateUrl')
    asurakuArea = models.TextField(max_length=512, verbose_name='asurakuArea', null=True, blank=True, help_text='asurakuArea')
    asurakuClosingTime = models.CharField(max_length=8, verbose_name='asurakuClosingTime', null=True, blank=True, help_text='asurakuClosingTime')
    asurakuFlag = models.PositiveSmallIntegerField(verbose_name='asurakuFlag', null=True, blank=True, help_text='asurakuFlag')
    availability = models.PositiveSmallIntegerField(verbose_name='availability', null=True, blank=True, help_text='availability')
    catchcopy = models.TextField(max_length=256, verbose_name='catchcopy', null=True, blank=True, help_text='catchcopy')
    creditCardFlag = models.PositiveSmallIntegerField(verbose_name='creditCardFlag', null=True, blank=True, help_text='creditCardFlag')
    endTime = models.CharField(max_length=32, verbose_name='endTime', null=True, blank=True, help_text='endTime')
    genreId = models.CharField(max_length=8, verbose_name='genreId', null=True, blank=True, help_text='genreId')
    giftFlag = models.PositiveSmallIntegerField(verbose_name='giftFlag', null=True, blank=True, help_text='giftFlag')
    imageFlag = models.PositiveSmallIntegerField(verbose_name='imageFlag', null=True, blank=True, help_text='imageFlag')
    itemCaption = models.TextField(max_length=4056, verbose_name='itemCaption', null=True, blank=True, help_text='itemCaption')
    itemCode = models.CharField(max_length=64, verbose_name='itemCode', null=True, blank=True, help_text='itemCode')
    itemName = models.CharField(max_length=256, verbose_name='itemName', null=True, blank=True, help_text='itemName')
    itemPrice = models.PositiveSmallIntegerField(verbose_name='itemPrice', null=True, blank=True, help_text='itemPrice')
    itemUrl = models.CharField(max_length=128, verbose_name='itemUrl', null=True, blank=True, help_text='itemUrl')
    mediumImageUrls = models.TextField(max_length=1024, verbose_name='mediumImageUrls', null=True, blank=True, help_text='mediumImageUrls')
    pointRate = models.PositiveSmallIntegerField(verbose_name='pointRate', null=True, blank=True, help_text='pointRate')
    pointRateEndTime = models.CharField(max_length=32, verbose_name='pointRateEndTime', null=True, blank=True, help_text='pointRateEndTime')
    pointRateStartTime = models.CharField(max_length=32, verbose_name='pointRateStartTime', null=True, blank=True, help_text='pointRateStartTime')
    postageFlag = models.PositiveSmallIntegerField(verbose_name='postageFlag', null=True, blank=True, help_text='postageFlag')
    reviewAverage = models.FloatField(verbose_name='reviewAverage', null=True, blank=True, help_text='reviewAverage')
    reviewCount = models.PositiveSmallIntegerField(verbose_name='reviewCount', null=True, blank=True, help_text='reviewCount')
    shipOverseasArea = models.TextField(max_length=256, verbose_name='shipOverseasArea', null=True, blank=True, help_text='shipOverseasArea')
    shipOverseasFlag = models.PositiveSmallIntegerField(verbose_name='shipOverseasFlag', null=True, blank=True, help_text='shipOverseasFlag')
    shopAffiliateUrl = models.CharField(max_length=128, verbose_name='shopAffiliateUrl', null=True, blank=True, help_text='shopAffiliateUrl')
    shopCode = models.CharField(max_length=32, verbose_name='shopCode', null=True, blank=True, help_text='shopCode')
    shopName = models.CharField(max_length=64, verbose_name='shopName', null=True, blank=True, help_text='shopName')
    shopOfTheYearFlag = models.PositiveSmallIntegerField(verbose_name='shopOfTheYearFlag', null=True, blank=True, help_text='shopOfTheYearFlag')
    shopUrl = models.CharField(max_length=128, verbose_name='shopUrl', null=True, blank=True, help_text='shopUrl')
    smallImageUrls = models.TextField(max_length=512, verbose_name='smallImageUrls', null=True, blank=True, help_text='smallImageUrls')
    startTime = models.CharField(max_length=32, verbose_name='startTime', null=True, blank=True, help_text='startTime')
    tagIds = models.TextField(max_length=512, verbose_name='tagIds', null=True, blank=True, help_text='tagIds')
    taxFlag = models.PositiveSmallIntegerField(verbose_name='taxFlag', null=True, blank=True, help_text='taxFlag')
    carrier = models.PositiveSmallIntegerField(verbose_name='carrier', null=True, blank=True, help_text='carrier')
    count = models.PositiveSmallIntegerField(verbose_name='count', null=True, blank=True, help_text='count')
    first = models.PositiveSmallIntegerField(verbose_name='first', null=True, blank=True, help_text='first')
    hits = models.PositiveSmallIntegerField(verbose_name='hits', null=True, blank=True, help_text='hits')
    last = models.PositiveSmallIntegerField(verbose_name='last', null=True, blank=True, help_text='last')
    page = models.PositiveSmallIntegerField(verbose_name='page', null=True, blank=True, help_text='page')
    pageCount = models.PositiveSmallIntegerField(verbose_name='pageCount', null=True, blank=True, help_text='pageCount')
    sort = models.PositiveSmallIntegerField(verbose_name='sort', null=True, blank=True, help_text='sort')

# IchibaRankings(IchibaRankings)
class IchibaRankingsDB(models.Model):
    class Meta:
        db_table = 'tbl_ichibaRankings' # DB内で使用するテーブル名
        verbose_name_plural = 'tbl_ichibaRankings' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    stores = models.ForeignKey(StoresDB, verbose_name='ストアID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaRankings_stores') # 外部キー　CASCADE：親が消されたら削除する
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品ID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaRankings_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    ichibaGenres = models.ForeignKey(IchibaGenresDB, verbose_name='楽天市場ジャンルID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaRankings_ichibaGenres') # 外部キー　CASCADE：親が消されたら削除する
    ichibaRankingGenres = models.ForeignKey(IchibaGenresDB, verbose_name='楽天市場ランキングジャンルID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaRankings_ichibaRankingGenres') # 外部キー　CASCADE：親が消されたら削除する
    ichibaItemGenres = models.ForeignKey(IchibaItemGenresDB, verbose_name='楽天市場商品ジャンルID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_ichibaRankings_ichibaItemGenres') # 外部キー　CASCADE：親が消されたら削除する
    # ランキング情報
    title = models.CharField(max_length=256, verbose_name='title', null=True, blank=True, help_text='title')
    lastBuildDate = models.DateTimeField(null=True, auto_now=False, auto_now_add=False, help_text='lastBuildDate')
#    affiliateRate = models.PositiveSmallIntegerField(verbose_name='affiliateRate', null=True, blank=True, help_text='affiliateRate')
#    affiliateUrl = models.CharField(max_length=256, verbose_name='affiliateUrl', null=True, blank=True, help_text='affiliateUrl')
#    availability = models.PositiveSmallIntegerField(verbose_name='availability', null=True, blank=True, help_text='availability')
#    carrier = models.PositiveSmallIntegerField(verbose_name='carrier', null=True, blank=True, help_text='carrier')carrier
#    catchcopy = models.TextField(max_length=256, verbose_name='catchcopy', null=True, blank=True, help_text='catchcopy')
#    startTime = models.CharField(max_length=32, verbose_name='startTime', null=True, blank=True, help_text='startTime')
#    endTime = models.CharField(max_length=32, verbose_name='endTime', null=True, blank=True, help_text='endTime')
    genreId = models.CharField(max_length=8, verbose_name='genreId', null=True, blank=True, help_text='genreId')
#    itemCaption = models.TextField(max_length=4056, verbose_name='itemCaption', null=True, blank=True, help_text='itemCaption')
    itemCode = models.CharField(max_length=64, verbose_name='itemCode', null=True, blank=True, help_text='itemCode')
#    itemName = models.CharField(max_length=256, verbose_name='itemName', null=True, blank=True, help_text='itemName')
#    itemPrice = models.PositiveSmallIntegerField(verbose_name='itemPrice', null=True, blank=True, help_text='itemPrice')
#    itemUrl = models.CharField(max_length=256, verbose_name='itemUrl', null=True, blank=True, help_text='itemUrl')
#    pointRate = models.PositiveSmallIntegerField(verbose_name='pointRate', null=True, blank=True, help_text='pointRate')
#    pointRateStartTime = models.CharField(max_length=32, verbose_name='pointRateStartTime', null=True, blank=True, help_text='pointRateStartTime')
#    pointRateEndTime = models.CharField(max_length=32, verbose_name='pointRateEndTime', null=True, blank=True, help_text='pointRateEndTime')
#    postageFlag = models.PositiveSmallIntegerField(verbose_name='postageFlag', null=True, blank=True, help_text='postageFlag')
    rank = models.PositiveSmallIntegerField(verbose_name='rank', null=True, blank=True, help_text='rank')
#    reviewAverage = models.FloatField(verbose_name='reviewAverage', null=True, blank=True, help_text='reviewAverage')
#    reviewCount = models.PositiveSmallIntegerField(verbose_name='reviewCount', null=True, blank=True, help_text='reviewCount')
#    shipOverseasFlag = models.PositiveSmallIntegerField(verbose_name='shipOverseasFlag', null=True, blank=True, help_text='shipOverseasFlag')
#    shopAffiliateUrl = models.CharField(max_length=128, verbose_name='shopAffiliateUrl', null=True, blank=True, help_text='shopAffiliateUrl')
    shopCode = models.CharField(max_length=32, verbose_name='shopCode', null=True, blank=True, help_text='shopCode')
#    shopName = models.CharField(max_length=64, verbose_name='shopName', null=True, blank=True, help_text='shopName')
#    shopOfTheYearFlag = models.PositiveSmallIntegerField(verbose_name='shopOfTheYearFlag', null=True, blank=True, help_text='shopOfTheYearFlag')
#    shopUrl = models.CharField(max_length=128, verbose_name='shopUrl', null=True, blank=True, help_text='shopUrl')

# inventories(inventory)
class InventoriesDB(models.Model):
    class Meta:
        db_table = 'tmp_inventories' # DB内で使用するテーブル名
        verbose_name_plural = 'tmp_inventories' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    executelogs = models.ForeignKey(ExecuteLogsDB, verbose_name='実行ログID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_inventories_executelogs') # 外部キー　CASCADE：親が消されたら削除する
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品API', on_delete=models.CASCADE, null=True,blank=True, related_name='related_inventories_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    deliveries = models.ForeignKey(DeliveriesDB, verbose_name='DeliveriesUUID_通常納期ID', on_delete=models.CASCADE, null=True,blank=True, related_name='related_inventories_deliveries') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報
    itemID = models.CharField(max_length=256, verbose_name='商品管理ID', null=True, blank=True, help_text='商品管理ID')
    itemUrl = models.CharField(max_length=256, verbose_name='商品管理URL', null=True, blank=True, help_text='商品管理URL')
    itemNumber = models.CharField(max_length=256, verbose_name='商品管理番号', null=True, blank=True, help_text='商品管理番号')
    inventoryType = models.PositiveSmallIntegerField(verbose_name='在庫タイプ', null=True, blank=True, help_text='在庫タイプ')
    # SKU
    sku = models.CharField(max_length=256, verbose_name='sku', null=True, blank=True, help_text='sku')
    skuNo = models.CharField(max_length=256, verbose_name='sku管理番号', null=True, blank=True, help_text='sku管理番号')
    janCode = models.CharField(max_length=32, verbose_name='JANコード', null=True, blank=True, help_text='JANコード')
    horizontalName = models.CharField(max_length=128, verbose_name='横軸管理名', null=True, blank=True, help_text='横軸管理名')
    verticalName = models.CharField(max_length=128, verbose_name='縦軸管理名', null=True, blank=True, help_text='縦軸管理名')
    horizontalCode = models.CharField(max_length=128, verbose_name='横軸管理コード', null=True, blank=True, help_text='横軸管理コード')
    verticalCode = models.CharField(max_length=128, verbose_name='縦軸管理コード', null=True, blank=True, help_text='縦軸管理コード')    
    # 納期情報
    normalDeliveryId = models.PositiveSmallIntegerField(verbose_name='通常納期ID', null=True, blank=True, help_text='通常納期ID')
    lackDeliveryId = models.PositiveSmallIntegerField(verbose_name='在庫切れ時納期ID', null=True, blank=True, help_text='在庫切れ時納期ID')
    # 在庫情報
    inventoryCount = models.PositiveSmallIntegerField(default=0, verbose_name='在庫数', null=True, blank=True, help_text='在庫数')

# ItemsDB(ItemsDB)
class ItemsDB(models.Model):
    class Meta:
        db_table = 'tmp_items' # DB内で使用するテーブル名
        verbose_name_plural = 'tmp_items' # Admionサイトで表示するテーブル名
    # 共通管理情報
    sys_datetime_created = models.DateTimeField(auto_now_add=True, help_text='作成日時')
    sys_datetime_modified = models.DateTimeField(auto_now=True, help_text='更新日時')
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False, help_text='uuid')
    # 外部キー
    ichibaItems = models.ForeignKey(IchibaItemsDB, verbose_name='楽天市場商品API', on_delete=models.CASCADE, null=True,blank=True, related_name='related_items_ichibaItems') # 外部キー　CASCADE：親が消されたら削除する
    # 商品情報
    itemUrl = models.CharField(max_length=256, verbose_name='商品管理番号', null=True, blank=True, help_text='商品管理番号')
    itemNumber = models.CharField(max_length=32, verbose_name='商品番号', null=True, blank=True, help_text='商品番号')
    itemName = models.CharField(max_length=256, verbose_name='商品名', null=True, blank=True, help_text='商品名')
    itemPrice = models.PositiveSmallIntegerField(verbose_name='販売価格', null=True, blank=True, help_text='販売価格')
    genreId = models.PositiveSmallIntegerField(verbose_name='全商品ディレクトリID', null=True, blank=True, help_text='全商品ディレクトリID')
    catalogId = models.CharField(max_length=30, verbose_name='カタログID', null=True, blank=True, help_text='カタログID')
    catalogIdExemptionReason = models.PositiveSmallIntegerField(verbose_name='カタログIDなしの理由', null=True, blank=True, help_text='カタログIDなしの理由')
    whiteBgImageUrl = models.CharField(max_length=256, verbose_name='白背景画像URL', null=True, blank=True, help_text='白背景画像URL')
    # images = 
    descriptionForPC = models.TextField(max_length=10240, verbose_name='PC用商品説明文', null=True, blank=True, help_text='PC用商品説明文')
    descriptionForSmartPhone = models.TextField(max_length=10240, verbose_name='スマートフォン用商品説明文', null=True, blank=True, help_text='スマートフォン用商品説明文')
    movieUrl = models.CharField(max_length=2048, verbose_name='動画URL', null=True, blank=True, help_text='動画URL')
    # options = 
    # tagIds = 
    catchCopyForPC = models.CharField(max_length=174, verbose_name='PC用キャッチコピー', null=True, blank=True, help_text='PC用キャッチコピー')
    catchCopyForMobile = models.CharField(max_length=60, verbose_name='モバイル用キャッチコピー', null=True, blank=True, help_text='モバイル用キャッチコピー')
    descriptionBySalesMethod = models.TextField(max_length=10240, verbose_name='PC用販売説明文', null=True, blank=True, help_text='PC用販売説明文')
    isSaleButton = models.BooleanField(null=True, verbose_name='注文ボタン',help_text='注文ボタン')
    isDocumentButton = models.BooleanField(null=True, verbose_name='資料請求ボタン',help_text='資料請求ボタン')
    isInquiryButton = models.BooleanField(null=True, verbose_name='商品問い合わせボタン',help_text='商品問い合わせボタン')
    isStockNoticeButton = models.BooleanField(null=True, verbose_name='再入荷のお知らせボタン',help_text='再入荷のお知らせボタン')
    displayMakerContents = models.BooleanField(null=True, verbose_name='メーカー提供コンテンツ表示',help_text='メーカー提供コンテンツ表示')
    itemLayout = models.PositiveSmallIntegerField(verbose_name='商品情報レイアウト', null=True, blank=True, help_text='商品情報レイアウト')
    isIncludedTax = models.BooleanField(null=True, verbose_name='消費税',help_text='消費税')
    isIncludedPostage = models.BooleanField(null=True, verbose_name='送料',help_text='送料')
    isIncludedCashOnDeliveryPostage = models.BooleanField(null=True, verbose_name='代引き手数料',help_text='代引き手数料')
    displayPrice = models.PositiveSmallIntegerField(verbose_name='表示価格', null=True, blank=True, help_text='表示価格')
    orderLimit = models.PositiveSmallIntegerField(verbose_name='注文受付数', null=True, blank=True, help_text='注文受付数')
    postage = models.PositiveSmallIntegerField(verbose_name='個別送料', null=True, blank=True, help_text='個別送料')
    isNoshiEnable = models.BooleanField(null=True, verbose_name='のし対応',help_text='のし対応')
    isTimeSale = models.BooleanField(null=True, verbose_name='期間限定販売フラグ',help_text='期間限定販売フラグ')
    timeSaleStartDateTime = models.DateTimeField(verbose_name='期間限定販売開始日',help_text='期間限定販売開始日', null=True,blank=True)
    timeSaleEndDateTime = models.DateTimeField(verbose_name='期間限定販売終了日',help_text='期間限定販売終了日', null=True,blank=True)
    isUnavailableForSearch = models.BooleanField(null=True, verbose_name='サーチ非表示',help_text='サーチ非表示')
    # isAvailableForMobile = 
    isDepot = models.BooleanField(null=True, verbose_name='倉庫指定',help_text='倉庫指定')
    detailSellType = models.PositiveSmallIntegerField(verbose_name='詳細販売種別', null=True, blank=True, help_text='詳細販売種別')
    # point = 
    # itemInventory = 
    asurakuDeliveryId = models.CharField(max_length=10, verbose_name='あす楽配送管理番号', null=True, blank=True, help_text='あす楽配送管理番号')
    deliverySetId = models.PositiveSmallIntegerField(verbose_name='配送方法セット管理番号', null=True, blank=True, help_text='配送方法セット管理番号')
    sizeChartLinkCode = models.CharField(max_length=5, verbose_name='サイズ表リンクコード', null=True, blank=True, help_text='サイズ表リンクコード')
    reviewDisp = models.PositiveSmallIntegerField(verbose_name='レビュー表示', null=True, blank=True, help_text='レビュー表示')
    displayPriceId = models.PositiveSmallIntegerField(verbose_name='二重価格文言ID', null=True, blank=True, help_text='二重価格文言ID')
    # categories = 
    itemWeight = models.PositiveSmallIntegerField(verbose_name='表示優先度', null=True, blank=True, help_text='表示優先度')
    layoutCommonId = models.PositiveSmallIntegerField(verbose_name='ヘッダー・フッター・レフトナビのテンプレートID', null=True, blank=True, help_text='ヘッダー・フッター・レフトナビのテンプレートID')
    layoutMapId = models.PositiveSmallIntegerField(verbose_name='表示項目の並び順のテンプレートID', null=True, blank=True, help_text='表示項目の並び順のテンプレートID')
    textSmallId = models.PositiveSmallIntegerField(verbose_name='共通説明文（小）のテンプレートID', null=True, blank=True, help_text='共通説明文（小）のテンプレートID')
    lossLeaderId = models.PositiveSmallIntegerField(verbose_name='目玉商品のテンプレートID', null=True, blank=True, help_text='目玉商品のテンプレートID')
    textLargeId = models.PositiveSmallIntegerField(verbose_name='共通説明文（大）のテンプレートID', null=True, blank=True, help_text='共通説明文（大）のテンプレートID')
    isSingleItemShipping = models.BooleanField(null=True, verbose_name='単品配送設定',help_text='単品配送設定')




