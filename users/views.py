from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import RegistrationForm  # 导入 RegistrationForm
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
# 用户注册视图
def register_view(request):
    if request.method == 'POST':
        # 使用 request.POST 数据来创建一个表单实例
        form = RegistrationForm(request.POST)

        if form.is_valid():  # 如果表单验证通过
            # 保存用户数据
            user = form.save(commit=False)  # 创建 User 实例，但不立即保存到数据库
            user.set_password(form.cleaned_data['password'])  # 对密码进行加密
            user.save()  # 保存用户数据

            # 自动登录新用户
            login(request, user)

            # 注册成功后，重定向到主页
            return redirect('home')
        else:
            # 如果表单验证失败，返回表单和错误信息
            return render(request, 'users/register.html', {'form': form})
    else:
        # 如果是 GET 请求，创建一个空表单
        form = RegistrationForm()

    # 渲染注册页面，传递表单给模板
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # 确保使用 AuthenticationForm
        if form.is_valid():
            user = form.get_user()  # 获取用户对象
            login(request, user)  # 登录用户
            return redirect('home')  # 登录成功后重定向到主页
        else:
            return render(request, 'users/login.html', {'form': form, 'error': 'Invalid username or password'})
    else:
        form = AuthenticationForm()  # 显示空表单

    return render(request, 'users/login.html', {'form': form})
