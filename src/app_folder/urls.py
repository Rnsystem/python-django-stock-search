from django.urls import path
from . import views

app_name = 'app_folder'
urlpatterns = [
    # accounts
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    # news（pkはモデルで定義した変数名ではない、予約語の変数） 
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<uuid:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    # settings
    path('settings/malls/', views.SettingsMallsListView.as_view(), name='settings_malls_list'),
    path('settings/malls/<uuid:pk>/', views.SettingsStoresListView.as_view(), name='settings_stores_list'),
    path('settings/stores/<uuid:pk>/', views.SettingsStoresDetailView.as_view(), name='settings_stores_detail'),
    path('settings/stores/<uuid:pk>/update/', views.SettingsStoresUpdateView.as_view(), name='settings_stores_update'),
    path('settings/stores/<uuid:pk>/execute/', views.SettingsStoresExecuteView.as_view(), name='settings_stores_execute'),
    path('settings/stores/<uuid:stores>/deliveries/', views.SettingsDeliveriesListView.as_view(), name='settings_deliveries_list'),
    path('settings/stores/<uuid:stores>/deliveries/<uuid:pk>/update/', views.SettingsDeliveriesUpdateView.as_view(), name='settings_deliveries_update'),
    path("settings/stores/<uuid:stores>/deliveries/create/", views.SettingsDeliveriesCreateView.as_view(), name="settings_deliveries_create"),
    # executelogs
    path('executelogs/', views.ExecutelogsListView.as_view(), name='executelogs_list'),
    path('executelogs/<uuid:pk>/', views.ExecutelogsDetailView.as_view(), name='executelogs_detail'),
    # inventories
    path('inventories/', views.InventoriesListView.as_view(), name='inventories_list'),
    path('inventories/<uuid:pk>/', views.InventoriesDetailView.as_view(), name='inventories_detail'),
    # items
    path('items/', views.ItemsListView.as_view(), name='items_list'),
    path('items/<uuid:pk>/', views.ItemsDetailView.as_view(), name='items_detail'),
]