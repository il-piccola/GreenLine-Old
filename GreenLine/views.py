import os
from django.shortcuts import render, redirect
from django.http import FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .forms import *

@csrf_exempt
def login(request) :
    params = {
        'title' : 'Login',
        'msg' : '',
        'form' : LoginForm(),
        'mode_admin' : False,
    }
    if 'msg' in request.session :
        params['msg'] = request.session['msg']
        del request.session['msg']
    if (request.method != 'POST') :
        return render(request, 'login.html', params)
    obj = Employee()
    form = LoginForm(data=request.POST, instance=obj)
    if form.is_valid() :
        data = Employee.objects.filter(phone=request.POST['phone'])
        if data.count() <= 0 :
            params['msg'] = '未登録の電話番号です'
        elif data.first().password != request.POST['password'] :
            params['msg'] = 'パスワードが間違っています'
        else :
            request.session['employee'] = data.first().id
            return redirect('main')
    else :
        params['msg'] = '入力に誤りがあります'
    params['form'] = form
    return render(request, 'login.html', params)

@csrf_exempt
def main(request) :
    employee = get_employee(request, False)
    if not employee :
        return redirect('login')
    params = {
        'title' : 'Main',
        'msg' : '',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'form' : MainForm(),
    }
    if (request.method != 'POST') :
        return render(request, 'main.html', params)
    else :
        form = MainForm(data=request.POST)
        if form.is_valid() :
            files = File.objects.filter(phone=request.POST['phone'])
            if File and File.objects.count() > 0 :
                files = File.objects.filter(phone=request.POST['phone'])
                print(files.count())
                # print(files.first().get_path())
                params['files'] = files
            else :
                params['msg'] = '該当するファイルがありません'
            params['form'] = form
        else :
            params['msg'] = '入力に誤りがあります'
    return render(request, 'main.html', params)

@csrf_exempt
def show_file(request) :
    phone = request.POST.get('phone')
    file = File.objects.filter(phone=phone)
    if not file or file.count() <= 0 :
        return HttpResponse("ファイルが見つかりません")
    try :
        path = File.first().get_path()
        ext = os.path.splitext(path)[1][1:]
        content_type = 'application/pdf'
        if ext == "xlsx" :
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        elif ext == "xls" :
            content_type = 'application/vnd.ms-excel'
        with open(file=path, mode='rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = 'inline;filename="'+ f.name + '"'
            return response
    except FileNotFoundError :
        return HttpResponse("ファイルが見つかりません")

@csrf_exempt
def change_password(request) :
    employee = get_employee(request, False)
    if not employee :
        return redirect('login')
    params = {
        'title' : 'Password',
        'msg' : 'パスワードを変更できます',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'form' : PasswordForm(),
    }
    if (request.method != 'POST') :
        return render(request, 'change_password.html', params)
    else :
        form = PasswordForm(data=request.POST)
        if form.is_valid() :
            old = request.POST['old']
            new = request.POST['new']
            confirm = request.POST['confirm']
            if employee.password == old and new == confirm :
                employee.password = new
                employee.save()
                request.session['msg'] = 'パスワードを変更しました'
                del request.session['employee']
                return redirect('login')
            elif employee.password != old :
                params['msg'] = '旧パスワードが間違っています'
            elif new != confirm :
                params['msg'] = '新パスワード(確認)が間違っています'
            params['form'] = form
        else :
            params['msg'] = '入力に誤りがあります'
    return render(request, 'change_password.html', params)

@csrf_exempt
def admin_login(request) :
    params = {
        'title' : 'Administor Login',
        'msg' : '',
        'form' : LoginForm(),
        'mode_admin' : True,
    }
    if 'msg' in request.session :
        params['msg'] = request.session['msg']
        del request.session['msg']
    if (request.method != 'POST') :
        return render(request, 'login.html', params)
    obj = Employee()
    form = LoginForm(data=request.POST, instance=obj)
    if form.is_valid() :
        data = Employee.objects.filter(phone=request.POST['phone'])
        if data.count() <= 0 :
            params['msg'] = '未登録の電話番号です'
        elif data.first().password != request.POST['password'] :
            params['msg'] = 'パスワードが間違っています'
        elif not data.first().auth :
            params['msg'] = '管理者権限がありません'
        else :
            request.session['employee'] = data.first().id
            return redirect('admin_main')
    else :
        params['msg'] = '入力に誤りがあります'
    params['form'] = form
    return render(request, 'login.html', params)

@csrf_exempt
def admin_main(request) :
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    params = {
        'title' : 'Administrator Main',
        'msg' : '',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
    }
    return render(request, 'admin_main.html', params)

@csrf_exempt
def show_employees(request) :
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    params = {
        'title' : 'Employees',
        'msg' : '',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'list' : Employee.objects.all(),
    }
    return render(request, 'show_employees.html', params)

@csrf_exempt
def add_employee(request) :
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    params = {
        'title' : 'New Employee',
        'msg' : '',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'form' : EmployeeForm(),
    }
    if request.POST :
        form = EmployeeForm(data=request.POST)
        if form.is_valid() :
            if not form.confirm :
                if Employee.objects.filter(phone=request.POST['phone']).count() > 0 :
                    params['msg'] = '既に登録されている電話番号です'
                else :
                    form.confirm = True
                    params['msg'] = 'この内容で登録します、よろしいですか？'
        else :
            params['msg'] = '入力に誤りがあります'
        params['form'] = form
    else :
        params['msg'] = '従業員を登録できます'
    return render(request, 'add_employee.html', params)

@csrf_exempt
def add_file(request) :
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    pass

@csrf_exempt
def show_files(request) :
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    params = {
        'title' : 'Files',
        'msg' : '',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'list' : File.objects.all(),
    }
    return render(request, 'show_files.html', params)

def get_employee(request, auth_flg) :
    if not 'employee' in request.session :
        return None
    employee = Employee.objects.filter(id=request.session['employee']).first()
    if not employee :
        return None
    if auth_flg and not employee.auth :
        return None
    return employee
