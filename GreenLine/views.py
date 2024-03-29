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
            params['msg'] = '未登録のドライバー電話番号です'
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
            files = File.objects.filter(phone__contains=request.POST['phone'])
            if files and files.count() > 0 :
                params['files'] = files
            else :
                params['msg'] = '該当するPDFファイルがありません'
            params['form'] = form
        else :
            params['msg'] = '入力に誤りがあります'
    return render(request, 'main.html', params)

@csrf_exempt
def show_file(request) :
    phone = request.POST.get('phone')
    file = File.objects.filter(phone=phone)
    if not file or file.count() <= 0 :
        return HttpResponse("PDFファイルが見つかりません")
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
        return HttpResponse("PDFファイルが見つかりません")

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
            new = request.POST['new']
            confirm = request.POST['confirm']
            if new == confirm :
                employee.password = new
                employee.save()
                request.session['msg'] = 'パスワードを変更しました、再度ログインしてください'
                del request.session['employee']
                return redirect('login')
            else :
                params['msg'] = '新パスワード(確認)が間違っています'
        else :
            params['msg'] = '入力に誤りがあります'
    return render(request, 'change_password.html', params)

@csrf_exempt
def admin_login(request) :
    params = {
        'title' : 'Admin Login',
        'msg' : '',
        'form' : LoginForm(),
        'mode_admin' : True,
    }
    if 'msg' in request.session :
        params['msg'] = request.session['msg']
        del request.session['msg']
    if request.method != 'POST' :
        return render(request, 'login.html', params)
    obj = Employee()
    form = LoginForm(data=request.POST, instance=obj)
    if form.is_valid() :
        data = Employee.objects.filter(phone=request.POST['phone'])
        if data.count() <= 0 :
            params['msg'] = '未登録の管理者電話番号です'
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
        'title' : 'Admin Main',
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
def employee(request, id, edit) :
    print(id, edit)
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    target = Employee.objects.filter(id=id).first()
    params = {
        'title' : 'Employee',
        'msg' : '',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'id' : id,
        'edit' : edit,
        'form' : EmployeeForm(instance=target)
    }
    if request.POST :
        form = EmployeeForm(data=request.POST)
        if edit == 1 :
            if form.is_valid() :
                params['msg'] = 'この内容で更新してよいですか？'
                params['form'] = form
            else :
                params['msg'] = '入力に誤りがあります'
        elif edit == 3 :
            target.phone = request.POST['phone']
            target.name = request.POST['name']
            target.kana = request.POST['kana']
            target.password = request.POST['password']
            print(request.POST['organization'])
            target.organization = Organization.objects.filter(id=request.POST['organization']).first()
            target.save()
            return redirect('show_employees')
    else :
        if edit == 2 :
            params['msg'] = '本当に削除しますか？'
        elif edit == 4 :
            target = Employee.objects.filter(id=id)
            target.delete()
            return redirect('show_employees')
    return render(request, 'employee.html', params)

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
        'form' : AddEmployeeForm(),
    }
    if request.POST :
        form = AddEmployeeForm(data=request.POST)
        if form.is_valid() :
            if not request.session['add_employee_confirm'] :
                if Employee.objects.filter(phone=request.POST['phone']).count() > 0 :
                    if request.POST['auth'] :
                        params['msg'] = '既に登録されている管理者電話番号です'
                    else :
                        params['msg'] = '既に登録されているドライバー電話番号です'
                else :
                    request.session['add_employee_confirm'] = True
                    params['msg'] = 'この内容で登録します、よろしいですか？'
                    data = request.POST.copy()
                    data.update({'dummy':request.POST['phone']})
                    form = AddEmployeeForm(data=data)
            else :
                form.instance.password = request.POST['phone']
                form.instance.save()
                del request.session['add_employee_confirm']
                return redirect('show_employees')
        else :
            params['msg'] = '入力に誤りがあります'
        params['form'] = form
        params['password'] = request.POST['phone']
    else :
        request.session['add_employee_confirm'] = False
        params['msg'] = 'ドライバーもしくは管理者を登録できます'
        params['password'] = ""
    return render(request, 'add_employee.html', params)

@csrf_exempt
def add_file(request) :
    employee = get_employee(request, True)
    if not employee :
        return redirect('admin_login')
    params = {
        'title' : 'Upload',
        'msg' : 'PDFファイルをアップロードできます',
        'name' : employee.name,
        'organizaion' : employee.organization.name,
        'form' : UploadForm(),
    }
    if request.POST :
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid() :
            form.save()
            return redirect('show_files')
        else :
            params['msg'] = '入力に誤りがあります'
    return render(request, 'add_file.html', params)

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

@csrf_exempt
def del_file(request, id) :
    for file in File.objects.filter(id=id) :
        file.delete()
    return redirect('show_files')

def get_employee(request, auth_flg) :
    if not 'employee' in request.session :
        return None
    employee = Employee.objects.filter(id=request.session['employee']).first()
    if not employee :
        return None
    if auth_flg and not employee.auth :
        return None
    return employee
