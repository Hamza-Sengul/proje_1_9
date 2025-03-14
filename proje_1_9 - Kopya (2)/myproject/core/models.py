from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    department = models.CharField(max_length=100, blank=True, null=True)
    
    LEVEL_CHOICES = (
        (1, 'Kademe 1'),
        (2, 'Kademe 2'),
        (3, 'Kademe 3'),
        (4, 'Kademe 4'),
    )
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1, blank=True, null=True)

# Harcama kategorisi modeli (Yönetici tarafından eklenir)
class ExpenseCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

# Temsilcilerin harcamalarını tutan model
class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.category.name} - {self.amount}"


class ExpenseCategoryLog(models.Model):
    OPERATION_CHOICES = (
        ('edit', 'Düzenleme'),
        ('delete', 'Silme'),
    )
    category_name = models.CharField(max_length=100)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    performed_at = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.category_name} - {self.get_operation_display()} - {self.performed_by}"
    
class SubscriptionType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class SubscriptionDuration(models.Model):
    # Örneğin "6 Ay", "12 Ay" gibi seçenekler
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class PaymentType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name 
    

class Customer(models.Model):
    AGREEMENT_STATUS_CHOICES = (
    ('beklemede', 'Beklemede'),
    ('olumlu', 'Olumlu'),
    ('olumsuz', 'Olumsuz'),
)
    
    rep = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            verbose_name="Temsilci")  # Kaydı oluşturan temsilci
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    identification = models.CharField(max_length=100, blank=True, null=True, verbose_name="TC/Vergi No")
    tax_office = models.CharField(max_length=150, blank=True, null=True, verbose_name="Vergi Dairesi")
    address = models.TextField()
    
    subscription_type = models.ForeignKey(SubscriptionType, on_delete=models.SET_NULL, null=True)
    subscription_duration = models.ForeignKey(SubscriptionDuration, on_delete=models.SET_NULL, null=True)
    subscription_start_date = models.DateField()
    payment_type = models.ForeignKey(PaymentType, on_delete=models.SET_NULL, null=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    agreement_status = models.CharField(max_length=10, choices=AGREEMENT_STATUS_CHOICES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} - {self.first_name} {self.last_name}"
    

# Örneğin, çalışan ekleme için:
class Employee(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    # Diğer bilgiler eklenebilir

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Çalışanlara görev ataması yapmak için:
class EmployeeTask(models.Model):
    STATUS_CHOICES = (
        ("atanmadı", "Atanmadı"),
        ("atanmış", "Atanmış"),
        ("tamamlandı", "Tamamlandı"),
    )
    employee = models.ForeignKey("Employee", on_delete=models.CASCADE, related_name="tasks")
    task_description = models.TextField()
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    # Yeni: Görev atama tarihi, admin tarafından seçilecek (date picker ile)
    assignment_date = models.DateField(null=True, blank=True)
    # Durum, dropdown üzerinden seçilecek
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="atanmadı")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.employee} - {self.task_description[:30]}"

# Çalışan belgelerini tutmak için:
def employee_document_upload_path(instance, filename):
    return f"employee_documents/{instance.employee.id}/{filename}"

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="documents")
    document_name = models.CharField(max_length=150)
    file = models.FileField(upload_to=employee_document_upload_path)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.document_name}"

    # Örneğin, hangi belge türleri isteniyorsa, manager tarafından tanımlanabilir.
    # Burada varsayılan olarak; "Sağlık Belgesi", "Sigorta Belgesi", "İkametgah Belgesi" gibi belgeler
    # istenecektir.


class EmployeeTaskLog(models.Model):
    OPERATION_CHOICES = (
        ('create', 'Oluşturma'),
        ('update', 'Güncelleme'),
        ('delete', 'Silme'),
    )
    task = models.ForeignKey(EmployeeTask, on_delete=models.CASCADE, related_name='logs')
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.task} - {self.get_operation_display()} by {self.performed_by}"
    
class Material(models.Model):
    name = models.CharField(max_length=150, verbose_name="Malzeme Adı")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    quantity = models.PositiveIntegerField(verbose_name="Stok Adedi")
    available = models.BooleanField(default=True, verbose_name="Verilebilir mi?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    

class MaterialTransaction(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="transactions")
    rep = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Temsilci")
    # Müşteri, Customer modeline FK ise onu kullanın. Örneğin:
    customer = models.ForeignKey("Customer", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Müşteri")
    quantity = models.PositiveIntegerField(verbose_name="Verilen Adet")
    transaction_date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, verbose_name="Not")

    def __str__(self):
        return f"{self.material.name} - {self.quantity} adet - {self.rep.username}"
    

class Payment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="payments")
    payment_date = models.DateTimeField(auto_now_add=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ödenen Tutar")
    note = models.TextField(blank=True, null=True, verbose_name="Not")
    payment_method = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ödeme Yöntemi")

    def __str__(self):
        return f"{self.customer.username} - {self.paid_amount} TL"


class Complaint(models.Model):
    STATUS_CHOICES = (
        ('beklemede', 'Beklemede'),
        ('cozuldu', 'Çözüldü'),
        ('cozulemedi', 'Çözülemedi'),
    )
    rep = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Temsilci")
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, verbose_name="Müşteri")
    title = models.CharField(max_length=200, verbose_name="Şikayet Başlığı")
    description = models.TextField(verbose_name="Şikayet Açıklaması")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='beklemede')
    cozum_detay = models.TextField(blank=True, null=True, verbose_name="Çözüm/Neden Detayı")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"

class Request(models.Model):
    rep = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="Temsilci")
    customer = models.ForeignKey("Customer", on_delete=models.CASCADE, verbose_name="Müşteri")
    name = models.CharField(max_length=200, verbose_name="İstek Adı")
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Fiyat")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    


class Vehicle(models.Model):
    rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Temsilci"
    )
    brand = models.CharField(max_length=150, verbose_name="Marka")
    model = models.CharField(max_length=150, verbose_name="Model")
    chassis_no = models.CharField(max_length=100, unique=True, verbose_name="Şasi No")
    maintenance_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Bakım Fiyatı")
    last_maintenance_date = models.DateField(verbose_name="Son Bakım Tarihi")
    estimated_maintenance_date = models.DateField(verbose_name="Tahmini Bakım Zamanı")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.chassis_no}"




class SubscriptionExtra(models.Model):
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('canceled', 'İptal'),
    )
    rep = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Temsilci"
    )
    customer = models.ForeignKey(
        "Customer",
        on_delete=models.CASCADE,
        verbose_name="Müşteri"
    )
    name = models.CharField(max_length=150, verbose_name="Extra Adı")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Extra Fiyatı")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.get_status_display()} ({self.customer.username})"


class SubscriptionExtraLog(models.Model):
    OPERATION_CHOICES = (
        ('create', 'Ekstra Ekleme'),
        ('update', 'Ekstra Güncelleme'),
        ('cancel', 'Ekstra İptali'),
    )
    extra = models.ForeignKey(SubscriptionExtra, on_delete=models.CASCADE, related_name="logs")
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    performed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    old_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.extra.name} - {self.get_operation_display()} - {self.performed_by}"
