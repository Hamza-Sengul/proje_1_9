from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from core.views import (
    UserViewSet, ExpenseCategoryViewSet, ExpenseViewSet, ExpenseCategoryLogViewSet,
    SubscriptionTypeViewSet, SubscriptionDurationViewSet, PaymentTypeViewSet,
    CustomerViewSet, EmployeeViewSet, EmployeeTaskViewSet, EmployeeDocumentViewSet,
    EmployeeTaskLogViewSet, MaterialViewSet, MaterialTransactionViewSet,
    PaymentViewSet, ComplaintViewSet, RequestViewSet, VehicleViewSet,
    SubscriptionExtraViewSet, SubscriptionExtraLogViewSet, UserDetailView
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'expense-category-logs', ExpenseCategoryLogViewSet)
router.register(r'subscription-types', SubscriptionTypeViewSet)
router.register(r'subscription-durations', SubscriptionDurationViewSet)
router.register(r'payment-types', PaymentTypeViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'employee-tasks', EmployeeTaskViewSet)
router.register(r'employee-documents', EmployeeDocumentViewSet)
router.register(r'employee-task-logs', EmployeeTaskLogViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'material-transactions', MaterialTransactionViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'complaints', ComplaintViewSet)
router.register(r'requests', RequestViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'subscription-extras', SubscriptionExtraViewSet)
router.register(r'subscription-extra-logs', SubscriptionExtraLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Önce token endpoint'lerini ekleyelim
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Custom kullanıcı detay endpoint'ini router'dan önce ekleyin:
    path('api/users/me/', UserDetailView.as_view(), name='user-detail'),
    # Diğer URL'ler:
    path('', include('core.urls')),
    path('api/', include(router.urls)),
]
