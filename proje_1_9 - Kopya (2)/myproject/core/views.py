from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django import forms
from django.db.models import Q
from .models import User, ExpenseCategory, Expense, ExpenseCategoryLog, EmployeeTaskLog

# Inline temsilci ekleme formu (önceki adımda tanımlanan)
class TemsilciForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Şifre")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'department', 'password', 'level']

def home(request):
    return render(request, 'home.html')

class AdminLoginView(LoginView):
    template_name = 'admin_login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_superuser:
            form.add_error(None, "Bu giriş sayfası sadece yöneticiler içindir!")
            return self.form_invalid(form)
        login(self.request, user)
        return redirect('admin_panel')

class TemsilciLoginView(LoginView):
    template_name = 'temsilci_login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser:
            form.add_error(None, "Bu giriş sayfası temsilciler içindir!")
            return self.form_invalid(form)
        login(self.request, user)
        return redirect('temsilci_panel')

@login_required
def admin_panel(request):
    if not request.user.is_superuser:
        return redirect('home')
    return render(request, 'admin_panel.html')

@login_required
def temsilci_panel(request):
    if request.user.is_superuser:
        return redirect('home')
    return render(request, 'temsilci_panel.html')

@login_required
def add_temsilci(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        form = TemsilciForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_staff = False
            user.save()
            return redirect('admin_panel')
    else:
        form = TemsilciForm()
    
    return render(request, 'add_temsilci.html', {'form': form})

# Detaylı filtreleme ile temsilci listesini gösteren view (sadece admin erişebilir)
@login_required
def list_temsilci(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    # Superuser olmayan (temsilci) kullanıcıları alıyoruz.
    temsilciler = User.objects.filter(is_superuser=False)
    
    # GET parametrelerinden filtreleme değerlerini alıyoruz.
    username    = request.GET.get('username', '')
    first_name  = request.GET.get('first_name', '')
    last_name   = request.GET.get('last_name', '')
    department  = request.GET.get('department', '')
    level       = request.GET.get('level', '')
    
    if username:
        temsilciler = temsilciler.filter(username__icontains=username)
    if first_name:
        temsilciler = temsilciler.filter(first_name__icontains=first_name)
    if last_name:
        temsilciler = temsilciler.filter(last_name__icontains=last_name)
    if department:
        temsilciler = temsilciler.filter(department__icontains=department)
    if level:
        temsilciler = temsilciler.filter(level=level)
    
    context = {
        'temsilciler': temsilciler,
    }
    return render(request, 'list_temsilci.html', context)

def admin_logout(request):
    logout(request)
    return redirect('home')

def temsilci_logout(request):
    logout(request)
    return redirect('home')



# İsteğe bağlı: Eklenen kategorileri listeleyen sayfa (filtreleme eklenebilir)
@login_required
def list_expense_categories(request):
    if not request.user.is_superuser:
        return redirect('home')
    categories = ExpenseCategory.objects.all()
    return render(request, "list_expense_categories.html", {"categories": categories})

# 2. Temsilci: Harcama Girişi  
@login_required
def add_expense(request):
    if request.user.is_superuser:
        return redirect('home')
    if request.method == "POST":
        category_id = request.POST.get("category")
        amount = request.POST.get("amount")
        description = request.POST.get("description", "")
        if category_id and amount:
            try:
                category = ExpenseCategory.objects.get(id=category_id)
                Expense.objects.create(user=request.user, category=category, amount=amount, description=description)
                return redirect("list_expenses_rep")
            except ExpenseCategory.DoesNotExist:
                pass  # Hatalı kategori id girildiğinde yapılacak
    context = {"categories": ExpenseCategory.objects.all()}
    return render(request, "add_expense.html", context)

# 3. Yönetici: Temsilcilerin Harcamalarını Detaylı Filtreleme ile Listeleme  
@login_required
def list_expenses_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    expenses = Expense.objects.all().order_by("-created_at")
    # Filtreleme parametreleri: temsilci kullanıcı adı, kategori, tarih aralığı
    username    = request.GET.get('username', '')
    category_id = request.GET.get('category', '')
    date_from   = request.GET.get('date_from', '')
    date_to     = request.GET.get('date_to', '')
    
    if username:
        expenses = expenses.filter(user__username__icontains=username)
    if category_id:
        expenses = expenses.filter(category__id=category_id)
    if date_from:
        expenses = expenses.filter(created_at__gte=date_from)
    if date_to:
        expenses = expenses.filter(created_at__lte=date_to)
    
    context = {
        'expenses': expenses,
        'categories': ExpenseCategory.objects.all(),
    }
    return render(request, "list_expenses_admin.html", context)

# 4. Temsilci: Kendi Harcamalarını Filtreleme ile Listeleme  
@login_required
def list_expenses_rep(request):
    if request.user.is_superuser:
        return redirect('home')
    expenses = Expense.objects.filter(user=request.user).order_by("-created_at")
    # Filtreleme parametreleri: kategori, tarih aralığı
    category_id = request.GET.get('category', '')
    date_from   = request.GET.get('date_from', '')
    date_to     = request.GET.get('date_to', '')
    
    if category_id:
        expenses = expenses.filter(category__id=category_id)
    if date_from:
        expenses = expenses.filter(created_at__gte=date_from)
    if date_to:
        expenses = expenses.filter(created_at__lte=date_to)
    
    context = {
        'expenses': expenses,
        'categories': ExpenseCategory.objects.all(),
    }
    return render(request, "list_expenses_rep.html", context)




# Harcama kategorisi ekleme (önceki adımda oluşturduğunuz view)
@login_required
def add_expense_category(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        if name:
            ExpenseCategory.objects.create(name=name, description=description)
            return redirect('list_expense_categories')
    return render(request, "add_expense_category.html")

@login_required
def list_expense_categories(request):
    if not request.user.is_superuser:
        return redirect('home')
    categories = ExpenseCategory.objects.all()
    return render(request, "list_expense_categories.html", {"categories": categories})

# Inline form for düzenleme
class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'description']

# Harcama kategorisi düzenleme
@login_required
def edit_expense_category(request, category_id):
    try:
        category = ExpenseCategory.objects.get(id=category_id)
    except ExpenseCategory.DoesNotExist:
        return redirect('list_expense_categories')
    
    if request.method == "POST":
        form = ExpenseCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            # Log kaydı oluşturma
            ExpenseCategoryLog.objects.create(
                category_name=category.name,
                operation='edit',
                performed_by=request.user,
                details="Kategori düzenlendi."
            )
            return redirect('list_expense_categories')
    else:
        form = ExpenseCategoryForm(instance=category)
    
    return render(request, "edit_expense_category.html", {"form": form, "category": category})

# Harcama kategorisi silme
@login_required
def delete_expense_category(request, category_id):
    try:
        category = ExpenseCategory.objects.get(id=category_id)
    except ExpenseCategory.DoesNotExist:
        return redirect('list_expense_categories')
    
    if request.method == "POST":
        # Silme işleminden önce log kaydı
        ExpenseCategoryLog.objects.create(
            category_name=category.name,
            operation='delete',
            performed_by=request.user,
            details="Kategori silindi."
        )
        category.delete()
        return redirect('list_expense_categories')
    
    return render(request, "delete_expense_category.html", {"category": category})

# Yönetici panelinde log kayıtlarını listeleyen view
@login_required
def expense_category_logs(request):
    if not request.user.is_superuser:
        return redirect('home')
    logs = ExpenseCategoryLog.objects.all().order_by("-performed_at")
    return render(request, "expense_category_logs.html", {"logs": logs})


# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Customer, SubscriptionType, SubscriptionDuration, PaymentType

# Inline CustomerForm: rep alanı otomatik atanacak, bu yüzden formda yer almaz.
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'username',
            'first_name',
            'last_name',
            'identification',
            'tax_office',
            'address',
            'subscription_type',
            'subscription_duration',
            'subscription_start_date',
            'payment_type',
            'amount',
            'description',
            'agreement_status',
        ]
        widgets = {
            'subscription_start_date': forms.DateInput(attrs={'type': 'date'}),
        }

@login_required
def add_customer(request):
    # Yalnızca temsilciler (superuser olmayan ve level>=2) müşteri ekleyebilsin.
    if request.user.is_superuser or request.user.level < 2:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.rep = request.user
            customer.save()
            return redirect('list_customers_rep')
    else:
        form = CustomerForm()
    return render(request, "add_customer.html", {"form": form})

@login_required
def list_customers_rep(request):
    # Yalnızca 2. kademe ve üzeri temsilciler kendi müşterilerini görebilir.
    if request.user.is_superuser or request.user.level < 2:
        return redirect('home')

    # Giriş yapan temsilciye ait müşterileri alıyoruz.
    customers = Customer.objects.filter(rep=request.user).order_by("-created_at")
    
    # Filtreleme: müşteri kullanıcı adı, ad, abonelik türü, anlaşma durumu
    username = request.GET.get('username', '')
    first_name = request.GET.get('first_name', '')
    subscription_type = request.GET.get('subscription_type', '')
    agreement_status = request.GET.get('agreement_status', '')
    
    if username:
        customers = customers.filter(username__icontains=username)
    if first_name:
        customers = customers.filter(first_name__icontains=first_name)
    if subscription_type:
        try:
            subscription_type_id = int(subscription_type)
            customers = customers.filter(subscription_type__id=subscription_type_id)
        except ValueError:
            pass  # Geçersiz değer gönderildiyse filtrelemeyi atla.
    if agreement_status:
        customers = customers.filter(agreement_status=agreement_status)
    
    context = {
        'customers': customers,
        'subscription_types': SubscriptionType.objects.all(),
    }
    return render(request, "list_customers_rep.html", context)

@login_required
def list_customers_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    customers = Customer.objects.all().order_by("-created_at")
    
    # Filtreleme: temsilci kullanıcı adı, müşteri kullanıcı adı, abonelik türü, anlaşma durumu
    rep_username = request.GET.get('rep_username', '')
    customer_username = request.GET.get('customer_username', '')
    subscription_type = request.GET.get('subscription_type', '')
    agreement_status = request.GET.get('agreement_status', '')
    
    if rep_username:
        customers = customers.filter(rep__username__icontains=rep_username)
    if customer_username:
        customers = customers.filter(username__icontains=customer_username)
    if subscription_type:
        customers = customers.filter(subscription_type__id=subscription_type)
    if agreement_status:
        customers = customers.filter(agreement_status=agreement_status)
    
    context = {
        'customers': customers,
        'subscription_types': SubscriptionType.objects.all(),
    }
    return render(request, "list_customers_admin.html", context)

class SubscriptionTypeForm(forms.ModelForm):
    class Meta:
        model = SubscriptionType
        fields = ['name', 'description']

@login_required
def add_subscription_type(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == 'POST':
        form = SubscriptionTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_subscription_types')
    else:
        form = SubscriptionTypeForm()
    return render(request, 'add_subscription_type.html', {'form': form})

@login_required
def list_subscription_types(request):
    if not request.user.is_superuser:
        return redirect('home')
    types = SubscriptionType.objects.all()
    return render(request, 'list_subscription_types.html', {'subscription_types': types})


# Abonelik Süresi Ekleme Formu ve View
class SubscriptionDurationForm(forms.ModelForm):
    class Meta:
        model = SubscriptionDuration
        fields = ['name']

@login_required
def add_subscription_duration(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == 'POST':
        form = SubscriptionDurationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_subscription_durations')
    else:
        form = SubscriptionDurationForm()
    return render(request, 'add_subscription_duration.html', {'form': form})

@login_required
def list_subscription_durations(request):
    if not request.user.is_superuser:
        return redirect('home')
    durations = SubscriptionDuration.objects.all()
    return render(request, 'list_subscription_durations.html', {'subscription_durations': durations})


# Ödeme Tipi Ekleme Formu ve View
class PaymentTypeForm(forms.ModelForm):
    class Meta:
        model = PaymentType
        fields = ['name']

@login_required
def add_payment_type(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == 'POST':
        form = PaymentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_payment_types')
    else:
        form = PaymentTypeForm()
    return render(request, 'add_payment_type.html', {'form': form})

@login_required
def list_payment_types(request):
    if not request.user.is_superuser:
        return redirect('home')
    payment_types = PaymentType.objects.all()
    return render(request, 'list_payment_types.html', {'payment_types': payment_types})


@login_required
def list_pending_customers(request):
    # Sadece 2. kademe ve üzeri temsilciler (superuser olmayanlar) kendi müşterileri üzerinde işlem yapabilsin.
    if request.user.is_superuser or request.user.level < 2:
        return redirect('home')
    pending_customers = Customer.objects.filter(rep=request.user, agreement_status='beklemede').order_by("-created_at")
    context = {'pending_customers': pending_customers}
    return render(request, 'list_pending_customers.html', context)

# Bekleyen müşteriler için anlaşma durumunu düzenleme view'i:
@login_required
def edit_customer_agreement(request, customer_id):
    # Sadece kendi eklediği ve anlaşma durumu beklemede olan müşteriler düzenlenebilir.
    customer = get_object_or_404(Customer, id=customer_id, rep=request.user, agreement_status='beklemede')
    if request.method == "POST":
        # İsterseniz CustomerForm yerine anlaşmaya ait alanları içeren ayrı bir form da oluşturabilirsiniz.
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('list_pending_customers')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'edit_customer_agreement.html', {'form': form, 'customer': customer})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Employee, EmployeeTask, EmployeeDocument

# Çalışan ekleme formu
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'salary', 'department']

@login_required
def add_employee(request):
    if not request.user.is_superuser:
        return redirect('home')
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_employees_admin')
    else:
        form = EmployeeForm()
    return render(request, "add_employee.html", {"form": form})

# Çalışanları detaylı filtreleme ile listeleme (Yönetici)
@login_required
def list_employees_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    employees = Employee.objects.all().order_by("-created_at")
    
    # Filtreleme: ad, soyad, departman, maaş aralığı
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    department = request.GET.get('department', '')
    min_salary = request.GET.get('min_salary', '')
    max_salary = request.GET.get('max_salary', '')
    
    if first_name:
        employees = employees.filter(first_name__icontains=first_name)
    if last_name:
        employees = employees.filter(last_name__icontains=last_name)
    if department:
        employees = employees.filter(department__icontains=department)
    if min_salary:
        employees = employees.filter(salary__gte=min_salary)
    if max_salary:
        employees = employees.filter(salary__lte=max_salary)
    
    context = {'employees': employees}
    return render(request, "list_employees_admin.html", context)

# Çalışan görevlerini güncelleme (Görev ataması)
class EmployeeTaskForm(forms.ModelForm):
    class Meta:
        model = EmployeeTask
        fields = ['task_description', 'assignment_date', 'status']
        widgets = {
            'assignment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'task_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Görevin açıklamasını giriniz'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

@login_required
def assign_employee_task(request, employee_id):
    if not request.user.is_superuser:
        return redirect('home')
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == "POST":
        form = EmployeeTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.employee = employee
            task.assigned_by = request.user
            task.save()
            return redirect('list_employees_admin')
    else:
        form = EmployeeTaskForm()
    return render(request, "assign_employee_task.html", {"form": form, "employee": employee})


DEFAULT_DOCUMENT_CHOICES = [
    ('Sağlık Belgesi', 'Sağlık Belgesi'),
    ('Sigorta Belgesi', 'Sigorta Belgesi'),
    ('İkametgah Belgesi', 'İkametgah Belgesi'),
]

class EmployeeDocumentForm(forms.ModelForm):
    DOCUMENT_CHOICES = [
        ('default', 'Varsayılan Belge Seç'),
        ('optional', 'Opsiyonel Belge Ekle'),
    ]
    document_choice = forms.ChoiceField(
        choices=DOCUMENT_CHOICES,
        widget=forms.RadioSelect,
        initial='default',
        label="Belge Türü Seçimi"
    )
    default_document = forms.ChoiceField(
        choices=DEFAULT_DOCUMENT_CHOICES,
        required=False,
        label="Varsayılan Belge Seçiniz"
    )
    optional_document_name = forms.CharField(
        max_length=150,
        required=False,
        label="Opsiyonel Belge Adı"
    )
    
    class Meta:
        model = EmployeeDocument
        fields = ['file']  # Belge dosyası
        
    def clean(self):
        cleaned_data = super().clean()
        document_choice = cleaned_data.get('document_choice')
        default_document = cleaned_data.get('default_document')
        optional_document_name = cleaned_data.get('optional_document_name')
        
        if document_choice == 'default':
            if not default_document:
                raise forms.ValidationError("Lütfen varsayılan belge seçiniz.")
            cleaned_data['document_name'] = default_document
        elif document_choice == 'optional':
            if not optional_document_name:
                raise forms.ValidationError("Lütfen opsiyonel belge için bir belge adı giriniz.")
            cleaned_data['document_name'] = optional_document_name
        else:
            raise forms.ValidationError("Geçersiz belge seçimi.")
        return cleaned_data

@login_required
def add_employee_document(request, employee_id):
    # İlgili çalışan nesnesini alıyoruz.
    employee = get_object_or_404(Employee, id=employee_id)
    if request.method == "POST":
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.employee = employee
            doc.uploaded_by = request.user
            # clean() metodunda 'document_name' alanı ayarlandı.
            doc.document_name = form.cleaned_data.get('document_name')
            doc.save()
            return redirect('list_employee_documents', employee_id=employee.id)
    else:
        form = EmployeeDocumentForm()
    return render(request, "add_employee_document.html", {"form": form, "employee": employee})

@login_required
def list_employee_documents(request, employee_id):
    # Hem yöneticiler hem de temsilciler, çalışan belgelerini görebilir.
    employee = get_object_or_404(Employee, id=employee_id)
    documents = employee.documents.all().order_by("-uploaded_at")
    return render(request, "list_employee_documents.html", {"employee": employee, "documents": documents})


@login_required
def list_employees_for_rep(request):
    # Sadece temsilciler (superuser olmayan) bu view'e erişsin.
    if request.user.is_superuser:
        return redirect('admin_panel')
    # Yönetici tarafından eklenen tüm çalışanları listeleyelim.
    employees = Employee.objects.all().order_by("first_name")
    context = {"employees": employees}
    return render(request, "list_employees_for_rep.html", context)


@login_required
def list_employees_admin(request):
    if not request.user.is_superuser:
        return redirect('home')
    employees = Employee.objects.all().order_by("-created_at")
    
    # Varsayılan (zorunlu) belgeler
    required_documents = ["Sağlık Belgesi", "Sigorta Belgesi", "İkametgah Belgesi"]
    for emp in employees:
        uploaded_doc_names = list(emp.documents.values_list("document_name", flat=True))
        missing = [doc for doc in required_documents if doc not in uploaded_doc_names]
        emp.missing_docs = missing  # Bu bilgiyi template'te kullanacağız.
    
    context = {
        'employees': employees,
        'required_documents': required_documents,
    }
    return render(request, "list_employees_admin.html", context)


@login_required
def admin_view_employee_documents(request, employee_id):
    if not request.user.is_superuser:
        return redirect('home')
    employee = get_object_or_404(Employee, id=employee_id)
    required_documents = ["Sağlık Belgesi", "Sigorta Belgesi", "İkametgah Belgesi"]
    uploaded_doc_names = list(employee.documents.values_list("document_name", flat=True))
    missing = [doc for doc in required_documents if doc not in uploaded_doc_names]
    context = {
         'employee': employee,
         'documents': employee.documents.all().order_by("-uploaded_at"),
         'missing_docs': missing,
         'required_documents': required_documents,
    }
    return render(request, "admin_view_employee_documents.html", context)

@login_required
def admin_view_employee_documents(request, employee_id):
    if not request.user.is_superuser:
        return redirect('home')
    employee = get_object_or_404(Employee, id=employee_id)
    required_documents = ["Sağlık Belgesi", "Sigorta Belgesi", "İkametgah Belgesi"]
    uploaded_doc_names = list(employee.documents.values_list("document_name", flat=True))
    missing = [doc for doc in required_documents if doc not in uploaded_doc_names]
    context = {
         'employee': employee,
         'documents': employee.documents.all().order_by("-uploaded_at"),
         'missing_docs': missing,
         'required_documents': required_documents,
    }
    return render(request, "admin_view_employee_documents.html", context)


# Çalışan görevlerini listeleme (yönetici için)
@login_required
def list_employee_tasks(request):
    if not request.user.is_superuser:
        return redirect('home')
    tasks = EmployeeTask.objects.all().order_by("-created_at")
    return render(request, "list_employee_tasks.html", {"tasks": tasks})

# Çalışan görevi güncelleme
@login_required
def update_employee_task(request, task_id):
    if not request.user.is_superuser:
        return redirect('home')
    task = get_object_or_404(EmployeeTask, id=task_id)
    if request.method == "POST":
        form = EmployeeTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            EmployeeTaskLog.objects.create(
                task=task,
                operation="update",
                performed_by=request.user,
                details="Görev güncellendi."
            )
            return redirect('list_employee_tasks')
    else:
        form = EmployeeTaskForm(instance=task)
    return render(request, "update_employee_task.html", {"form": form, "task": task})

# Çalışan görevi silme
@login_required
def delete_employee_task(request, task_id):
    if not request.user.is_superuser:
        return redirect('home')
    task = get_object_or_404(EmployeeTask, id=task_id)
    if request.method == "POST":
        EmployeeTaskLog.objects.create(
            task=task,
            operation="delete",
            performed_by=request.user,
            details="Görev silindi."
        )
        task.delete()
        return redirect('list_employee_tasks')
    return render(request, "delete_employee_task.html", {"task": task})

# Görev işlemleri log sayfası
@login_required
def list_employee_task_logs(request):
    if not request.user.is_superuser:
        return redirect('home')
    logs = EmployeeTaskLog.objects.all().order_by("-timestamp")
    return render(request, "list_employee_task_logs.html", {"logs": logs})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django import forms
from .models import Material, MaterialTransaction
# Eğer Customer modeli varsa import edin: from .models import Customer

# Inline MaterialForm
class InlineMaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['name', 'price', 'quantity', 'available']


@login_required
def add_material(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == "POST":
        form = InlineMaterialForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_materials')
    else:
        form = InlineMaterialForm()
    
    return render(request, "add_material.html", {"form": form})


@login_required
def list_materials(request):
    if not request.user.is_superuser:
        return redirect('home')

    materials = Material.objects.all().order_by("-created_at")
    return render(request, "list_materials.html", {"materials": materials})


@login_required
def update_material(request, material_id):
    if not request.user.is_superuser:
        return redirect('home')

    material = get_object_or_404(Material, id=material_id)
    if request.method == "POST":
        form = InlineMaterialForm(request.POST, instance=material)
        if form.is_valid():
            form.save()
            return redirect('list_materials')
    else:
        form = InlineMaterialForm(instance=material)
    
    return render(request, "update_material.html", {"form": form, "material": material})


@login_required
def delete_material(request, material_id):
    if not request.user.is_superuser:
        return redirect('home')

    material = get_object_or_404(Material, id=material_id)
    if request.method == "POST":
        material.delete()
        return redirect('list_materials')
    return render(request, "delete_material.html", {"material": material})


# Inline Transaction Form
class InlineMaterialTransactionForm(forms.ModelForm):
    class Meta:
        model = MaterialTransaction
        fields = ['material', 'customer', 'quantity', 'note']


@login_required
def add_material_transaction(request):
    # Yalnızca 2. kademe ve üzeri temsilciler
    if request.user.is_superuser or request.user.level < 2:
        return redirect('home')

    if request.method == "POST":
        form = InlineMaterialTransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.rep = request.user
            transaction.save()
            return redirect('list_material_transactions_for_rep')
    else:
        form = InlineMaterialTransactionForm()
    
    return render(request, "add_material_transaction.html", {"form": form})


@login_required
def list_material_transactions_admin(request):
    # Yalnızca yönetici tüm işlemleri görebilir
    if not request.user.is_superuser:
        return redirect('home')
    
    transactions = MaterialTransaction.objects.all().order_by("-transaction_date")
    return render(request, "list_material_transactions_admin.html", {"transactions": transactions})


@login_required
def list_material_transactions_for_rep(request):
    # 2. kademe ve üzeri temsilciler kendi işlemlerini görebilir
    if request.user.is_superuser or request.user.level < 2:
        return redirect('home')
    
    transactions = MaterialTransaction.objects.filter(rep=request.user).order_by("-transaction_date")
    return render(request, "list_material_transactions_for_rep.html", {"transactions": transactions})





from datetime import date, timedelta

from datetime import date, timedelta

def analyze_customer_payment(customer):
    """
    Müşterinin abonelik ödemelerini analiz eder.
    - Eğer subscription_duration.name == "1 Ay" ise, süresiz aylık yaklaşım.
      (her ay bir taksit, abonelik durmaz/iptal edilmezse sonsuza dek sürer)
    - Yoksa, "6 Ay", "12 Ay" vb. ise sınırlı süreli taksit yaklaşımı.
    """
    # Ortak veriler
    subscription_duration_str = customer.subscription_duration.name  # "1 Ay", "6 Ay"
    start_date = customer.subscription_start_date
    total_amount = customer.amount  # Müşterinin 'amount' alanı
    payments = customer.payments.all()
    total_paid = sum(p.paid_amount for p in payments)
    today = date.today()

    # Eğer start_date ileride ise (henüz başlamadıysa):
    if start_date > today:
        return {
            "total_amount": total_amount,
            "total_paid": total_paid,
            "remaining_amount": total_amount,  # ödemeler henüz başlamadı
            "is_late": False,
            "next_payment_date": start_date,  # ilk ödeme start_date baz alınabilir
            "missed_months": 0,
            "message": "Abonelik henüz başlamadı.",
        }

    # 1) Ayırt et: "1 Ay" → Süresiz aylık, diğer → sınırlı
    if subscription_duration_str.strip().lower() == "1 ay":
        # SÜRESİZ AYLIK YAKLAŞIM

        # Aylık ücret: customer.amount olduğunu varsayıyoruz
        monthly_cost = total_amount  # Her ay ödenmesi beklenen ücret

        # Kaç ay geçti?
        days_diff = (today - start_date).days
        months_passed = days_diff // 30  # Yaklaşık her 30 günde 1 ay

        if months_passed < 0:
            months_passed = 0

        # Bu güne kadar ödenmesi gereken toplam
        required_total = months_passed * monthly_cost

        # Gecikme var mı?
        if total_paid < required_total:
            # Kaç aylık gecikme?
            missed_amount = required_total - total_paid
            missed_months = int(missed_amount // monthly_cost)
            if missed_months < 1 and missed_amount > 0:
                missed_months = 1  # kısmi bir aylık borç
            is_late = True if missed_months >= 1 else False
        else:
            missed_months = 0
            is_late = False

        remaining_amount = 0  # Süresiz olduğundan tam "kalan" yok, ama o anki gecikme => missed_months
        # Bir sonraki ödeme tarihi: start_date + months_passed * 30
        next_payment_date = start_date + timedelta(days=(months_passed+1)*30)

        return {
            "total_amount": f"Süresiz (Her ay {monthly_cost} TL)",
            "total_paid": total_paid,
            "remaining_amount": remaining_amount,  # Süresiz -> o anda biriken borç var
            "is_late": is_late,
            "next_payment_date": next_payment_date,
            "missed_months": missed_months,
            "message": f"Aylık ödenmesi gereken: {monthly_cost} TL / Gecikmiş ay: {missed_months}",
        }
    else:
        # SINIRLI SÜRELİ YAKLAŞIM, ÖRN: "6 Ay" = 6 taksit
        try:
            period_count = int(subscription_duration_str.split()[0])  # "6" -> 6
        except:
            period_count = 1

        if period_count <= 0:
            period_count = 1

        # Periyot başına ücret
        per_period_amount = total_amount / period_count

        # Kaç gün geçti
        days_passed = (today - start_date).days
        if days_passed < 0:
            days_passed = 0

        # Kaç periyot ödenmiş olmalı?
        # Basit mantık: her periyot 30 gün -> n = days_passed // 30
        months_passed = days_passed // 30
        if months_passed > period_count:
            months_passed = period_count  # maksimum

        # required_total = months_passed * per_period_amount
        required_total = months_passed * per_period_amount

        # Gecikme var mı?
        missed_amount = max(0, required_total - total_paid)
        missed_months = int(missed_amount // per_period_amount)
        if missed_months < 1 and missed_amount > 0:
            missed_months = 1
        is_late = missed_months >= 1

        # Kalan tutar
        remaining_amount = max(0, total_amount - total_paid)

        # Bir sonraki ödeme periyot index
        periyot_odendi = int(total_paid // per_period_amount)
        if periyot_odendi > period_count:
            periyot_odendi = period_count
        next_period_index = periyot_odendi + 1
        if next_period_index > period_count:
            next_period_index = period_count

        next_payment_date = None
        if periyot_odendi < period_count:
            offset_days = (next_period_index - 1)*30
            next_payment_date = start_date + timedelta(days=offset_days)

        return {
            "total_amount": total_amount,
            "total_paid": total_paid,
            "remaining_amount": remaining_amount,
            "is_late": is_late,
            "next_payment_date": next_payment_date,
            "missed_months": missed_months,
            "message": f"Taksitli ({period_count} Ay). Geciken periyot: {missed_months}",
        }





from django import forms
from .models import Payment

class InlinePaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['customer', 'paid_amount', 'payment_method', 'note']


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment, Customer
 # Yukarıda tanımladığımız form

@login_required
def add_payment(request):
    # ...
    if request.method == 'POST':
        form = InlinePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.save()
            return redirect('list_payments_rep')
    else:
        form = InlinePaymentForm()

    # Tüm müşterileri alalım (temsilcinin):
    customers = Customer.objects.filter(rep=request.user)
    return render(request, "add_payment.html", {
        "form": form,
        "customers": customers
    })


@login_required
def list_payments_rep(request):
    # 2. kademe temsilci
    if request.user.is_superuser or (request.user.level and request.user.level < 2):
        return redirect('home')

    customers = Customer.objects.filter(rep=request.user)

    # Filtre parametreleri
    q_username = request.GET.get('q_username', '').strip()
    q_first_name = request.GET.get('q_first_name', '').strip()
    q_last_name = request.GET.get('q_last_name', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    late_flag = request.GET.get('late', '')
    q_status = request.GET.get('status', '')
    q_min_rem = request.GET.get('min_remaining', '')
    q_max_rem = request.GET.get('max_remaining', '')

    if q_username:
        customers = customers.filter(username__icontains=q_username)
    if q_first_name:
        customers = customers.filter(first_name__icontains=q_first_name)
    if q_last_name:
        customers = customers.filter(last_name__icontains=q_last_name)
    if q_status:
        customers = customers.filter(agreement_status=q_status)

    customer_list = []
    for cust in customers:
        analysis = analyze_customer_payment(cust)
        payments = cust.payments.all().order_by("-payment_date")
        if date_from:
            payments = payments.filter(payment_date__date__gte=date_from)
        if date_to:
            payments = payments.filter(payment_date__date__lte=date_to)
        if late_flag == "1" and not analysis["is_late"]:
            continue
        rem = analysis["remaining_amount"]
        if q_min_rem:
            try:
                minval = float(q_min_rem)
                if rem < minval:
                    continue
            except:
                pass
        if q_max_rem:
            try:
                maxval = float(q_max_rem)
                if rem > maxval:
                    continue
            except:
                pass

        customer_list.append({
            "customer": cust,
            "analysis": analysis,
            "payments": payments,
        })

    return render(request, "list_payments_rep.html", {
        "customer_list": customer_list
    })





@login_required
def list_payments_admin(request):
    """
    Yönetici: Tüm müşterilerdeki tahsilatları gösterir.
    Daha detaylı filtre: Müşteri arama, tarih aralığı, gecikme, abonelik durumu, kalan tutar aralığı
    """
    if not request.user.is_superuser:
        return redirect('home')

    customers = Customer.objects.all()

    # Filtre parametreleri
    # 1) Müşteri arama (username, first_name, last_name)
    q_username = request.GET.get('q_username', '').strip()
    q_first_name = request.GET.get('q_first_name', '').strip()
    q_last_name = request.GET.get('q_last_name', '').strip()

    # 2) Tarih aralığı (date_from, date_to) -> Payment.payment_date
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # 3) Gecikme (late=1)
    late_flag = request.GET.get('late', '')

    # 4) Abonelik Durumu (agreement_status) = 'olumlu', 'beklemede', 'olumsuz'
    q_status = request.GET.get('status', '')

    # 5) Kalan Tutar aralığı (min_remaining, max_remaining)
    q_min_rem = request.GET.get('min_remaining', '')
    q_max_rem = request.GET.get('max_remaining', '')

    # Uygula
    if q_username:
        customers = customers.filter(username__icontains=q_username)
    if q_first_name:
        customers = customers.filter(first_name__icontains=q_first_name)
    if q_last_name:
        customers = customers.filter(last_name__icontains=q_last_name)
    if q_status:
        customers = customers.filter(agreement_status=q_status)

    # Aşağıda, her müşteri için analyze + Payment filtresi
    customer_list = []
    for cust in customers:
        # Dinamik hesap
        analysis = analyze_customer_payment(cust)

        # Payment kayıtları
        payments = cust.payments.all().order_by("-payment_date")
        if date_from:
            payments = payments.filter(payment_date__date__gte=date_from)
        if date_to:
            payments = payments.filter(payment_date__date__lte=date_to)

        # Gecikme
        if late_flag == "1" and not analysis["is_late"]:
            continue

        # Kalan tutar aralığı
        # analysis["remaining_amount"] ile kıyaslayalım
        remaining_amount = analysis["remaining_amount"]

        if q_min_rem:
            try:
                val_min = float(q_min_rem)
                if remaining_amount < val_min:
                    continue
            except:
                pass
        if q_max_rem:
            try:
                val_max = float(q_max_rem)
                if remaining_amount > val_max:
                    continue
            except:
                pass

        customer_list.append({
            "customer": cust,
            "analysis": analysis,
            "payments": payments,
        })

    return render(request, "list_payments_admin.html", {
        "customer_list": customer_list
    })



@login_required
def change_subscription_status(request, customer_id, new_status):
    customer = get_object_or_404(Customer, id=customer_id)
    # Örneğin: 'agreement_status' => 'olumlu', 'beklemede', 'olumsuz'
    if new_status == 'durdur':
        customer.agreement_status = 'beklemede'
    elif new_status == 'iptal':
        customer.agreement_status = 'olumsuz'
    elif new_status == 'devam':
        customer.agreement_status = 'olumlu'
    customer.save()

    # Yönlendirme Hatası: Daha önce -> return redirect('add_payment')
    # Bunu istemiyoruz. 
    # İstediğimiz: Temsilci isek -> list_payments_rep, Yönetici isek -> list_payments_admin
    if request.user.is_superuser:
        return redirect('list_payments_admin')
    else:
        return redirect('list_payments_rep')



# core/views.py
from django import forms
from .models import Complaint, Request

class InlineComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['customer', 'title', 'description']

class InlineComplaintUpdateForm(forms.ModelForm):
    """
    Şikayetin durumunu güncellerken cozum_detay girilebilsin.
    """
    class Meta:
        model = Complaint
        fields = ['status', 'cozum_detay']

class InlineRequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['customer', 'name', 'price', 'description']


@login_required
def add_complaint(request):
    # Temsilci level 2+ veya yönetici
    if request.user.is_superuser == False and (request.user.level and request.user.level < 2):
        return redirect('home')

    if request.method == 'POST':
        form = InlineComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.rep = request.user
            complaint.status = 'beklemede'
            complaint.save()
            return redirect('list_complaints_rep' if not request.user.is_superuser else 'list_complaints_admin')
    else:
        form = InlineComplaintForm()
    
    # Müşteri seçimi form.customer.queryset => temsilcinin müşterileri? opsiyona göre
    return render(request, "add_complaint.html", {"form": form})


@login_required
def list_complaints_rep(request):
    # Temsilci (level 2+) 
    if request.user.is_superuser or (request.user.level and request.user.level < 2):
        return redirect('home')

    # Filtre parametreleri
    q_status = request.GET.get('status', '')       # "beklemede", "cozuldu", "cozulemedi"
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    q_title = request.GET.get('title', '')

    complaints = Complaint.objects.filter(rep=request.user).order_by("-created_at")
    if q_status:
        complaints = complaints.filter(status=q_status)
    if q_title:
        complaints = complaints.filter(title__icontains=q_title)
    if date_from:
        complaints = complaints.filter(created_at__date__gte=date_from)
    if date_to:
        complaints = complaints.filter(created_at__date__lte=date_to)

    return render(request, "list_complaints_rep.html", {"complaints": complaints})

@login_required
def list_complaints_admin(request):
    if not request.user.is_superuser:
        return redirect('home')

    q_status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    q_title = request.GET.get('title', '')
    q_rep = request.GET.get('rep', '')

    complaints = Complaint.objects.all().order_by("-created_at")
    if q_status:
        complaints = complaints.filter(status=q_status)
    if q_title:
        complaints = complaints.filter(title__icontains=q_title)
    if date_from:
        complaints = complaints.filter(created_at__date__gte=date_from)
    if date_to:
        complaints = complaints.filter(created_at__date__lte=date_to)
    if q_rep:
        complaints = complaints.filter(rep__username__icontains=q_rep)

    return render(request, "list_complaints_admin.html", {"complaints": complaints})

@login_required
def update_complaint(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    # Yetki kontrol (ya superuser ya da rep == request.user)
    if not request.user.is_superuser:
        if complaint.rep != request.user:
            return redirect('home')

    if request.method == 'POST':
        form = InlineComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            # Yönlendirme: Temsilci mi Yönetici mi?
            return redirect('list_complaints_admin' if request.user.is_superuser else 'list_complaints_rep')
    else:
        form = InlineComplaintUpdateForm(instance=complaint)

    return render(request, "update_complaint.html", {
        "form": form,
        "complaint": complaint
    })


@login_required
def add_request(request):
    # Temsilci level 2+ veya admin
    if request.user.is_superuser == False and (request.user.level and request.user.level < 2):
        return redirect('home')

    if request.method == 'POST':
        form = InlineRequestForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.rep = request.user
            req.save()
            return redirect('list_requests_rep' if not request.user.is_superuser else 'list_requests_admin')
    else:
        form = InlineRequestForm()
    return render(request, "add_request.html", {"form": form})


@login_required
def list_requests_rep(request):
    if request.user.is_superuser or (request.user.level and request.user.level < 2):
        return redirect('home')

    q_name = request.GET.get('name', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    reqs = Request.objects.filter(rep=request.user).order_by("-created_at")
    if q_name:
        reqs = reqs.filter(name__icontains=q_name)
    if date_from:
        reqs = reqs.filter(created_at__date__gte=date_from)
    if date_to:
        reqs = reqs.filter(created_at__date__lte=date_to)

    return render(request, "list_requests_rep.html", {"reqs": reqs})


@login_required
def list_requests_admin(request):
    if not request.user.is_superuser:
        return redirect('home')

    q_name = request.GET.get('name', '')
    q_rep = request.GET.get('rep', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    reqs = Request.objects.all().order_by("-created_at")
    if q_name:
        reqs = reqs.filter(name__icontains=q_name)
    if q_rep:
        reqs = reqs.filter(rep__username__icontains=q_rep)
    if date_from:
        reqs = reqs.filter(created_at__date__gte=date_from)
    if date_to:
        reqs = reqs.filter(created_at__date__lte=date_to)

    return render(request, "list_requests_admin.html", {"reqs": reqs})


from django import forms
from .models import Vehicle

class InlineVehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'brand',
            'model',
            'chassis_no',
            'maintenance_price',
            'last_maintenance_date',
            'estimated_maintenance_date'
        ]

@login_required
def add_vehicle(request):
    # 2. kademe temsilci veya yönetici ekleyebilir
    if not request.user.is_superuser and (request.user.level and request.user.level < 2):
        return redirect('home')

    if request.method == 'POST':
        form = InlineVehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.rep = request.user
            vehicle.save()
            # Temsilci -> list_vehicles_rep; Yönetici -> list_vehicles_admin
            if request.user.is_superuser:
                return redirect('list_vehicles_admin')
            else:
                return redirect('list_vehicles_rep')
    else:
        form = InlineVehicleForm()

    return render(request, "add_vehicle.html", {"form": form})


@login_required
def list_vehicles_rep(request):
    # 2. kademe temsilci
    if request.user.is_superuser or (request.user.level and request.user.level < 2):
        return redirect('home')

    vehicles = Vehicle.objects.filter(rep=request.user).order_by("-created_at")

    # Filtre parametreleri
    q_brand = request.GET.get('brand', '').strip()
    q_model = request.GET.get('model', '').strip()
    q_chassis = request.GET.get('chassis_no', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q_brand:
        vehicles = vehicles.filter(brand__icontains=q_brand)
    if q_model:
        vehicles = vehicles.filter(model__icontains=q_model)
    if q_chassis:
        vehicles = vehicles.filter(chassis_no__icontains=q_chassis)

    if date_from:
        vehicles = vehicles.filter(created_at__date__gte=date_from)
    if date_to:
        vehicles = vehicles.filter(created_at__date__lte=date_to)

    return render(request, "list_vehicles_rep.html", {"vehicles": vehicles})

@login_required
def list_vehicles_admin(request):
    if not request.user.is_superuser:
        return redirect('home')

    vehicles = Vehicle.objects.all().order_by("-created_at")

    # Filtre parametreleri
    q_brand = request.GET.get('brand', '').strip()
    q_model = request.GET.get('model', '').strip()
    q_chassis = request.GET.get('chassis_no', '').strip()
    q_rep = request.GET.get('rep', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q_brand:
        vehicles = vehicles.filter(brand__icontains=q_brand)
    if q_model:
        vehicles = vehicles.filter(model__icontains=q_model)
    if q_chassis:
        vehicles = vehicles.filter(chassis_no__icontains=q_chassis)
    if q_rep:
        vehicles = vehicles.filter(rep__username__icontains=q_rep)

    if date_from:
        vehicles = vehicles.filter(created_at__date__gte=date_from)
    if date_to:
        vehicles = vehicles.filter(created_at__date__lte=date_to)

    return render(request, "list_vehicles_admin.html", {"vehicles": vehicles})


from django import forms
from .models import SubscriptionExtra
from .models import SubscriptionExtra, SubscriptionExtraLog 

class InlineSubscriptionExtraForm(forms.ModelForm):
    class Meta:
        model = SubscriptionExtra
        fields = ['customer', 'name', 'price']


@login_required
def add_subscription_extra(request):
    # 2. kademe temsilci veya yönetici
    if not request.user.is_superuser and (request.user.level and request.user.level < 2):
        return redirect('home')

    if request.method == 'POST':
        form = InlineSubscriptionExtraForm(request.POST)
        if form.is_valid():
            extra = form.save(commit=False)
            extra.rep = request.user
            extra.status = 'active'
            extra.save()
            # Müşteri abonelik fiyatını yükselt
            customer = extra.customer
            old_amount = customer.amount
            new_amount = old_amount + extra.price
            customer.amount = new_amount
            customer.save()

            # Log kaydı
            SubscriptionExtraLog.objects.create(
                extra=extra,
                operation='create',
                performed_by=request.user,
                old_amount=old_amount,
                new_amount=new_amount,
                details=f"Extra eklendi: {extra.name}, +{extra.price}"
            )

            # Yönlendirme
            if request.user.is_superuser:
                return redirect('list_subscription_extras_admin')
            else:
                return redirect('list_subscription_extras_rep')
    else:
        form = InlineSubscriptionExtraForm()
    
    return render(request, "add_subscription_extra.html", {"form": form})

@login_required
def list_subscription_extras_rep(request):
    # 2. kademe temsilci
    if request.user.is_superuser or (request.user.level and request.user.level < 2):
        return redirect('home')

    extras = SubscriptionExtra.objects.filter(rep=request.user).order_by("-created_at")

    # Filtre parametreleri
    q_name = request.GET.get('name', '').strip()
    q_customer = request.GET.get('customer', '').strip()  # customer.username
    q_status = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q_name:
        extras = extras.filter(name__icontains=q_name)
    if q_customer:
        extras = extras.filter(customer__username__icontains=q_customer)
    if q_status:
        extras = extras.filter(status=q_status)
    if date_from:
        extras = extras.filter(created_at__date__gte=date_from)
    if date_to:
        extras = extras.filter(created_at__date__lte=date_to)

    return render(request, "list_subscription_extras_rep.html", {"extras": extras})


@login_required
def list_subscription_extras_admin(request):
    if not request.user.is_superuser:
        return redirect('home')

    extras = SubscriptionExtra.objects.all().order_by("-created_at")

    q_name = request.GET.get('name', '').strip()
    q_customer = request.GET.get('customer', '').strip()
    q_rep = request.GET.get('rep', '').strip()
    q_status = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q_name:
        extras = extras.filter(name__icontains=q_name)
    if q_customer:
        extras = extras.filter(customer__username__icontains=q_customer)
    if q_rep:
        extras = extras.filter(rep__username__icontains=q_rep)
    if q_status:
        extras = extras.filter(status=q_status)
    if date_from:
        extras = extras.filter(created_at__date__gte=date_from)
    if date_to:
        extras = extras.filter(created_at__date__lte=date_to)

    return render(request, "list_subscription_extras_admin.html", {"extras": extras})


@login_required
def cancel_subscription_extra(request, extra_id):
    extra = get_object_or_404(SubscriptionExtra, id=extra_id)
    # Yetki kontrol
    if not request.user.is_superuser:
        # Temsilci kendi eklediği extrayı iptal edebilir
        if extra.rep != request.user:
            return redirect('home')
    
    # Durum kontrol
    if extra.status == 'active':
        customer = extra.customer
        old_amount = customer.amount
        new_amount = old_amount - extra.price
        customer.amount = new_amount
        customer.save()
        
        extra.status = 'canceled'
        extra.save()

        # Log kaydı
        SubscriptionExtraLog.objects.create(
            extra=extra,
            operation='cancel',
            performed_by=request.user,
            old_amount=old_amount,
            new_amount=new_amount,
            details=f"Extra iptal edildi: {extra.name}, -{extra.price}"
        )

    # Yönlendirme
    if request.user.is_superuser:
        return redirect('list_subscription_extras_admin')
    else:
        return redirect('list_subscription_extras_rep')


# core/views.py

from rest_framework import viewsets
from django.contrib.auth import get_user_model
from .models import (
    ExpenseCategory, Expense, ExpenseCategoryLog,
    SubscriptionType, SubscriptionDuration, PaymentType,
    Customer, Employee, EmployeeTask, EmployeeDocument, EmployeeTaskLog,
    Material, MaterialTransaction, Payment, Complaint, Request, Vehicle,
    SubscriptionExtra, SubscriptionExtraLog
)
from .serializers import (
    UserSerializer, ExpenseCategorySerializer, ExpenseSerializer, ExpenseCategoryLogSerializer,
    SubscriptionTypeSerializer, SubscriptionDurationSerializer, PaymentTypeSerializer,
    CustomerSerializer, EmployeeSerializer, EmployeeTaskSerializer, EmployeeDocumentSerializer,
    EmployeeTaskLogSerializer, MaterialSerializer, MaterialTransactionSerializer,
    PaymentSerializer, ComplaintSerializer, RequestSerializer, VehicleSerializer,
    SubscriptionExtraSerializer, SubscriptionExtraLogSerializer
)

User = get_user_model()

# Örnek: User ViewSet
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer

class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

class ExpenseCategoryLogViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategoryLog.objects.all()
    serializer_class = ExpenseCategoryLogSerializer

class SubscriptionTypeViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionType.objects.all()
    serializer_class = SubscriptionTypeSerializer

class SubscriptionDurationViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionDuration.objects.all()
    serializer_class = SubscriptionDurationSerializer

class PaymentTypeViewSet(viewsets.ModelViewSet):
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer

from rest_framework.permissions import AllowAny

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [AllowAny]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

class EmployeeTaskViewSet(viewsets.ModelViewSet):
    queryset = EmployeeTask.objects.all()
    serializer_class = EmployeeTaskSerializer

class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer

class EmployeeTaskLogViewSet(viewsets.ModelViewSet):
    queryset = EmployeeTaskLog.objects.all()
    serializer_class = EmployeeTaskLogSerializer

class MaterialViewSet(viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer

class MaterialTransactionViewSet(viewsets.ModelViewSet):
    queryset = MaterialTransaction.objects.all()
    serializer_class = MaterialTransactionSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all()
    serializer_class = ComplaintSerializer

class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer

class SubscriptionExtraViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionExtra.objects.all()
    serializer_class = SubscriptionExtraSerializer

class SubscriptionExtraLogViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionExtraLog.objects.all()
    serializer_class = SubscriptionExtraLogSerializer


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

logger = logging.getLogger(__name__)

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info(f"Authorization header: {request.headers.get('Authorization')}")
        logger.info(f"Authenticated user: {request.user}")
        user = request.user
        data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
        }
        return Response(data)