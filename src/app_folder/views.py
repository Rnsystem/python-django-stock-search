from django.shortcuts import render
from django.views import View 
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import(LoginView, LogoutView)
# 検索処理用
from django.db.models import Q
# DB呼び出し
from .models import NewsDB
from .models import MallsDB
from .models import StoresDB
from .models import ExecuteLogsDB
from .models import InventoriesDB
from .models import ItemsDB
from .models import IchibaGenresDB
from .models import IchibaItemsDB
from .models import IchibaRankingsDB
from .models import IchibaItemsDailyDB
from .models import IchibaItemsMonthlyDB
from .models import DeliveriesDB
# form呼び出し
from .forms import LoginForm
# グラフ呼び出し
from . import graph
# 参考文献
# https://yu-nix.com/archives/django-detail-view/#%E3%81%9D%E3%81%AE%E4%BB%96%E3%81%AEDetailView%E3%81%AE%E6%A9%9F%E8%83%BD


# ログイン操作
class Login(LoginView):
    """ログインページ"""
    form_class = LoginForm
    template_name = 'accounts/login.html'
class Logout(LoginRequiredMixin, LogoutView):
    """ログアウトページ"""
    template_name = 'accounts/login.html'
# news
class NewsListView(ListView):  
    template_name = 'news/news_list.html'
    model = NewsDB
    context_object_name = 'news'
    ordering = '-sys_datetime_created'
    paginate_by = 5 # 1ページに表示したい件数
class NewsDetailView(DetailView):  
    template_name = 'news/news_detail.html'
    model = NewsDB
    context_object_name = 'news'
# settings
class SettingsMallsListView(ListView):  
    template_name = 'settings/settings_malls_list.html'
    model = MallsDB
    context_object_name = 'malls'
class SettingsStoresListView(ListView):  
    template_name = 'settings/settings_stores_list.html'
    model = StoresDB
    context_object_name = 'stores'
    # コンテキスト定義（オーバーライド）
    def get_context_data(self, **kwargs):
        # GETリクエストパラメータにkeywordがあれば、それでフィルタする
        keyword = self.kwargs['pk']
        stores_query = StoresDB.objects.filter(malls=keyword)
        malls_all = MallsDB.objects.all()
        context = super().get_context_data(**kwargs)
        context['malls'] = malls_all
        context['stores'] = stores_query
        return context
class SettingsStoresDetailView(DetailView): 
    template_name = 'settings/settings_stores_detail.html'
    model = StoresDB
    context_object_name = 'store'
    # コンテキスト定義（オーバーライド）
    def post(self, request, *args, **kwargs):
        # 実行履歴を作成
        pk = str(kwargs['pk'])
        store_query = StoresDB.objects.filter(pk=pk)
        if self.request.POST.get('items_update_button') is not None:
            print('items_update_button click')
            # ExecuteLogsDB新規作成
            ExecuteLogsDB.objects.create(user=request.user, stores=store_query[0], execute_status=1, execute_type=2)
            return redirect('/apps/settings/stores/'+pk+'/execute/')
        if self.request.POST.get('stocks_update_button') is not None:
            print('stocks_update_button click')
            # ExecuteLogsDB新規作成
            ExecuteLogsDB.objects.create(user=request.user, stores=store_query[0], execute_status=1,execute_type=3)
            return redirect('/apps/settings/stores/'+pk+'/execute/')
        return HttpResponse("ボタンが正常動作しませんでした。システムまで連絡してください。")
    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        malls_all = MallsDB.objects.all()
        store_query = StoresDB.objects.filter(pk=pk)
        stores_query = StoresDB.objects.filter(malls=store_query.first().malls)
        context = super().get_context_data(**kwargs)
        context['malls']    = malls_all
        context['stores']   = stores_query
        post = context.get("object")
        print(post)
        return context
class SettingsStoresUpdateView(UpdateView): 
    template_name = 'settings/settings_stores_update.html'
    model = StoresDB
    context_object_name = 'store'
    fields = [
        'is_exe', 'url', 'api_No', 'api_ID', 'api_Key', 'shop_Name', 'shop_URL', 'shop_Code', 
        'shop_No', 'shop_ID', 'shop_Password', 'user_Name', 'user_No', 'user_ID', 'user_Password']
    # 編集完了後に読み出される関数（オーバーライド）
    def get_success_url(self):
        return reverse('app_folder:settings_stores_detail', kwargs={'pk': self.object.pk})
    # 編集画面（form）を呼び出す関数（オーバーライド
    def get_form(self):
        form = super(SettingsStoresUpdateView, self).get_form()
        form.fields['is_exe'].label = '連動ステータス'
        form.fields['url'].label = '店舗URL'
        form.fields['api_No'].label = 'API管理番号'
        form.fields['api_ID'].label = 'API管理ID'
        form.fields['api_Key'].label = 'API管理キー'
        form.fields['shop_Name'].label = 'ショップ名'
        form.fields['shop_URL'].label = 'ショップURL'
        form.fields['shop_No'].label = 'ショップ管理番号'
        form.fields['shop_ID'].label = 'ショップ管理ID'
        form.fields['shop_Password'].label = 'ショップ管理パスワード'
        form.fields['user_Name'].label = 'ユーザ名'
        form.fields['user_No'].label = 'ユーザ管理番号'
        form.fields['user_ID'].label = 'ユーザ管理ID'
        form.fields['user_Password'].label = 'ユーザ管理パスワード'
        return form
    # コンテキスト定義（オーバーライド）
    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        malls_all = MallsDB.objects.all()
        store_query = StoresDB.objects.filter(pk=pk)
        stores_query = StoresDB.objects.filter(malls=store_query.first().malls)
        context = super().get_context_data(**kwargs)
        context['malls']    = malls_all
        context['stores']   = stores_query
        return context
class SettingsStoresExecuteView(DetailView):
    template_name = 'settings/settings_stores_detail_execute.html'
    model = StoresDB
    context_object_name = 'store'
    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        malls_all = MallsDB.objects.all()
        store_query = StoresDB.objects.filter(pk=pk)
        stores_query = StoresDB.objects.filter(malls=store_query.first().malls)
        context = super().get_context_data(**kwargs)
        context['malls']    = malls_all
        context['stores']   = stores_query
        post = context.get("object")
        print(post)
        return context
class SettingsDeliveriesListView(ListView):
    template_name = 'settings/settings_deliveries_list.html'
    model = DeliveriesDB
    def get_context_data(self, **kwargs):
        stores_uuid = self.kwargs['stores']
        malls_all = MallsDB.objects.all()
        store_query = StoresDB.objects.filter(pk=stores_uuid)
        stores_query = StoresDB.objects.filter(malls=store_query.first().malls)
        print(store_query.first().name)
        deliveries_query = DeliveriesDB.objects.filter(stores=stores_uuid)
        context = super().get_context_data(**kwargs)
        context['malls']    = malls_all
        context['stores']   = stores_query
        context['store_uuid']   = stores_uuid
        context['store_name']   = store_query.first().name
        context['deliveries']   = deliveries_query
        post = context.get("object")
        return context
class SettingsDeliveriesCreateView(CreateView):  
    template_name = 'settings/settings_Deliveries_create.html'
    model = DeliveriesDB
    context_object_name = 'deliveries'
    fields = ('stores', 'delivery_id', 'delivery_no', 'delivery_name', 'delivery_days', 'delivery_memo')
    # 編集完了後に読み出される関数（オーバーライド）
    def get_success_url(self):
        return reverse('app_folder:settings_deliveries_list', kwargs={'stores': self.object.stores.pk})
    # CreateView初期値設定
    def get_initial(self, *args, **kwargs):
        print(self.kwargs['stores'])
        initial = super().get_initial()
        initial["stores"] = self.kwargs['stores']
        return initial
    def get_context_data(self, **kwargs):
        stores_uuid = self.kwargs['stores']
        malls_all = MallsDB.objects.all()
        store_query = StoresDB.objects.filter(pk=stores_uuid)
        stores_query = StoresDB.objects.filter(malls=store_query.first().malls)
        deliveries_query = DeliveriesDB.objects.filter(stores=stores_uuid)
        context = super().get_context_data(**kwargs)
        context['malls']    = malls_all
        context['stores']   = stores_query
        context['store_uuid']   = stores_uuid
        context['store_name']   = store_query.first().name
        context['deliveries']   = deliveries_query
        post = context.get("object")
        return context
class SettingsDeliveriesUpdateView(UpdateView):  
    template_name = 'settings/settings_Deliveries_update.html'
    model = DeliveriesDB
    context_object_name = 'deliveries'
    fields = ('stores', 'delivery_id', 'delivery_no', 'delivery_name', 'delivery_days', 'delivery_memo')
    # 編集完了後に読み出される関数（オーバーライド）
    def get_success_url(self):
        return reverse('app_folder:settings_deliveries_list', kwargs={'stores': self.object.stores.pk})
    # 編集画面（form）を呼び出す関数（オーバーライド
    def get_form(self):
        form = super(SettingsDeliveriesUpdateView, self).get_form()
        form.fields['stores'].label = '店舗UUID'
        form.fields['delivery_id'].label = '管理ID'
        form.fields['delivery_no'].label = '管理番号'
        form.fields['delivery_name'].label = 'お届けの目安'
        form.fields['delivery_days'].label = 'お届け日数'
        form.fields['delivery_memo'].label = '備考'
        return form
    # コンテキスト定義（オーバーライド）
    def get_context_data(self, **kwargs):
        stores_uuid = self.kwargs['stores']
        malls_all = MallsDB.objects.all()
        store_query = StoresDB.objects.filter(pk=stores_uuid)
        stores_query = StoresDB.objects.filter(malls=store_query.first().malls)
        deliveries_query = DeliveriesDB.objects.filter(stores=stores_uuid)
        context = super().get_context_data(**kwargs)
        context['malls']    = malls_all
        context['stores']   = stores_query
        context['store_name']   = store_query.first().name
        context['deliveries']   = deliveries_query
        return context

# executelogs
class ExecutelogsListView(ListView):
    template_name = 'executelogs/executelogs_list.html'
    model = ExecuteLogsDB
    context_object_name = 'executelogs'
    ordering = '-sys_datetime_created' # ソート順指定
    paginate_by = 5 # 1ページに表示したい件数
class ExecutelogsDetailView(DetailView):
    template_name = 'executelogs/executelogs_detail.html'
    model = ExecuteLogsDB
    context_object_name = 'executeLog'

# inventories
class InventoriesListView(ListView):
    template_name = 'inventories/inventories_list.html'
    model = InventoriesDB
    context_object_name = 'inventories'
    # ordering = '-sys_datetime_created' # ソート順指定
    paginate_by = 30 # 1ページに表示したい件数
class InventoriesDetailView(DetailView):
    template_name = 'inventories/inventories_detail.html'
    model = InventoriesDB
    context_object_name = 'inventory'

# items
class ItemsListView(ListView):
    template_name = 'items/items_list.html'
    model = IchibaItemsDB
    context_object_name = 'ichibaItems'
    # ordering = '-sys_datetime_created' # ソート順指定
    paginate_by = 30 # 1ページに表示したい件数
    # 検索フォーム用
    def get_queryset(self):
        q_word = self.request.GET.get('query')
        if q_word:
            ichibaItems = IchibaItemsDB.objects.filter(Q(itemCode__icontains=q_word) | Q(imageUrl__icontains=q_word))
        else:
            ichibaItems = IchibaItemsDB.objects.all()
        return ichibaItems

class ItemsDetailView(DetailView):
    template_name = 'items/items_detail.html'
    model = IchibaItemsDB
    context_object_name = 'ichibaItems'
    #変数としてグラフイメージをテンプレートに渡す
    def get_context_data(self, **kwargs):
        pk = self.kwargs['pk']
        ichibaitemsdaily_query = IchibaItemsDailyDB.objects.filter(ichibaItems=pk)
        ichibaitemsdaily_query_sorted = sorted(ichibaitemsdaily_query, key=lambda x: x.daily)
        ichibarankings_query = IchibaRankingsDB.objects.filter(ichibaItems=pk)
        # print('テスト')
        # print(ichibarankings_query[0].rank)
        # print(ichibarankings_query[0].lastBuildDate.strftime('%Y/%m/%d'))
        # print("オブジェクト数")
        # print(len(ichibaitemsdaily_query))
        #グラフオブジェクト .strftime('%Y/%m/%d')
        x     = [x.daily.strftime('%Y/%m/%d') for x in ichibaitemsdaily_query_sorted]  #X軸データ
        y     = [y.reviewCount for y in ichibaitemsdaily_query_sorted]                 #Y軸データ
        y2    = [y.reviewAverage for y in ichibaitemsdaily_query_sorted]               #Y軸データ
        y3     = [y.itemPrice for y in ichibaitemsdaily_query_sorted]                 #Y軸データ
        y4 = []
        # for i in x:
        #     for ichibarankings in ichibarankings_query:
        #         print(ichibarankings.lastBuildDate)
        #         if i == ichibarankings.lastBuildDate.strftime('%Y/%m/%d'):
        #             y4.append(int(ichibarankings.rank))
        #         else:
        #             y4.append(999)
        # print(y4)
        # print(x)
        chart = graph.Plot_Graph(x,y,y2,y3)# グラフ作成
        #変数を渡す
        context = super().get_context_data(**kwargs)
        context['chart'] = chart
        return context
    #get処理
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
