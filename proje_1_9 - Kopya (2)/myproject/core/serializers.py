# core/serializers.py

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ExpenseCategory, Expense, ExpenseCategoryLog,
    SubscriptionType, SubscriptionDuration, PaymentType,
    Customer, Employee, EmployeeTask, EmployeeDocument, EmployeeTaskLog,
    Material, MaterialTransaction, Payment, Complaint, Request, Vehicle,
    SubscriptionExtra, SubscriptionExtraLog
)

# 1) Custom User Serializer
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # İhtiyaç duyduğun alanları buraya ekle
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'department', 'level'
        ]


# 2) ExpenseCategory Serializer
class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = '__all__'


# 3) Expense Serializer
class ExpenseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # Eğer istersen user'ı ID olarak POST edebilmek için `user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())` vs. yapabilirsin.

    class Meta:
        model = Expense
        fields = '__all__'


# 4) ExpenseCategoryLog Serializer
class ExpenseCategoryLogSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
    
    class Meta:
        model = ExpenseCategoryLog
        fields = '__all__'


# 5) SubscriptionType Serializer
class SubscriptionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionType
        fields = '__all__'


# 6) SubscriptionDuration Serializer
class SubscriptionDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionDuration
        fields = '__all__'


# 7) PaymentType Serializer
class PaymentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentType
        fields = '__all__'

User = get_user_model()
# 8) Customer Serializer
class CustomerSerializer(serializers.ModelSerializer):
    # Giriş yapan kullanıcıyı rep alanı için yazılabilir hale getirmeden default olarak doldurabilirsiniz.
    rep = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    
    # Yazılabilir alanlar olarak tanımlıyoruz:
    subscription_type = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionType.objects.all(), allow_null=True
    )
    subscription_duration = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionDuration.objects.all(), allow_null=True
    )
    payment_type = serializers.PrimaryKeyRelatedField(
        queryset=PaymentType.objects.all(), allow_null=True
    )
    
    class Meta:
        model = Customer
        fields = '__all__'
    
    def create(self, validated_data):
        # Eğer rep gönderilmemişse, context üzerinden kullanıcıyı ekleyebilirsiniz.
        if 'rep' not in validated_data or not validated_data.get('rep'):
            # Eğer request objesine erişiminiz varsa:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                validated_data['rep'] = request.user
            else:
                # Test amaçlı, örneğin veritabanındaki ilk kullanıcıyı atayabilirsiniz.
                validated_data['rep'] = User.objects.first()
        return super().create(validated_data)


# 9) Employee Serializer
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'


# 10) EmployeeTask Serializer
class EmployeeTaskSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)
    
    class Meta:
        model = EmployeeTask
        fields = '__all__'


# 11) EmployeeDocument Serializer
class EmployeeDocumentSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    uploaded_by = UserSerializer(read_only=True)
    
    class Meta:
        model = EmployeeDocument
        fields = '__all__'


# 12) EmployeeTaskLog Serializer
class EmployeeTaskLogSerializer(serializers.ModelSerializer):
    task = EmployeeTaskSerializer(read_only=True)
    performed_by = UserSerializer(read_only=True)

    class Meta:
        model = EmployeeTaskLog
        fields = '__all__'


# 13) Material Serializer
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


# 14) MaterialTransaction Serializer
class MaterialTransactionSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    rep = UserSerializer(read_only=True)
    # customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = MaterialTransaction
        fields = '__all__'


# 15) Payment Serializer
class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


# 16) Complaint Serializer
class ComplaintSerializer(serializers.ModelSerializer):
    rep = UserSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Complaint
        fields = '__all__'


# 17) Request Serializer
class RequestSerializer(serializers.ModelSerializer):
    rep = UserSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = Request
        fields = '__all__'


# 18) Vehicle Serializer
class VehicleSerializer(serializers.ModelSerializer):
    rep = UserSerializer(read_only=True)

    class Meta:
        model = Vehicle
        fields = '__all__'


# 19) SubscriptionExtra Serializer
class SubscriptionExtraSerializer(serializers.ModelSerializer):
    rep = UserSerializer(read_only=True)
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = SubscriptionExtra
        fields = '__all__'


# 20) SubscriptionExtraLog Serializer
class SubscriptionExtraLogSerializer(serializers.ModelSerializer):
    extra = SubscriptionExtraSerializer(read_only=True)
    performed_by = UserSerializer(read_only=True)

    class Meta:
        model = SubscriptionExtraLog
        fields = '__all__'
