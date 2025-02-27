from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home, name="home"),
    path("payment_history/", views.payment_history_view, name="payment_history"),
    # Optionally, map "count/" to the payment history view:
    path("count/", views.payment_history_view, name="count"),
    path("credit_type/", views.credit_type_view, name="credit_type"),
    path("credit_type_details/", views.credit_type_details_view, name="credit_type_details"),
    path("credit_details/", views.credit_account_details_view, name="credit_details"),
    path("new_credit/", views.new_credit_view, name="new_credit"),
    path("results/", views.results_view, name="results"),
]
