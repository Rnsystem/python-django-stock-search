from django.contrib.auth.forms import AuthenticationForm 
# from .models import DeliveriesDB

# 参考文献
# https://www.techpit.jp/courses/27/curriculums/28/sections/241/parts/835
class LoginForm(AuthenticationForm):
    """ログオンフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'    #　※１
            field.widget.attrs['placeholder'] = field.label #　※２
            # 　※１：全てのフォームの部品のclass属性に「form-control」を指定（bootstrapのフォームデザインを利用するため）
            # 　※２：全てのフォームの部品にpaceholderを定義して、入力フォームにフォーム名が表示されるように指定。


# class DeliveriesDBForm(forms.ModelForm):
#     class Meta:
#         # どのモデルをフォームにするか指定
#         model = DeliveriesDB
#         # そのフォームの中から表示するフィールドを指定
#         fields = ('stores', 'delivery_id', 'delivery_no', 'delivery_name', 'delivery_days', 'delivery_memo')