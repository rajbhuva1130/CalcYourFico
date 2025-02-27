# calculator/forms.py
from django import forms

CREDIT_TYPE_CHOICES = [
    ('mortgage', 'Mortgage'),
    ('auto_loan', 'Auto Loan'),
    ('credit_card', 'Credit Card'),
    ('personal_loan', 'Personal Loan'),
    ('retail_account', 'Retail Account'),
    ('student_loan', 'Student Loan'),
]

# --- Step 1: Payment History Data ---
class PaymentHistoryForm(forms.Form):
    late_payment_30 = forms.IntegerField(label="Number of 30-day late payments", min_value=0, initial=0)
    late_payment_60 = forms.IntegerField(label="Number of 60-day late payments", min_value=0, initial=0)
    late_payment_90 = forms.IntegerField(label="Number of 90-day late payments", min_value=0, initial=0)
    collections = forms.IntegerField(label="Number of accounts in collections", min_value=0, initial=0)
    bankruptcies = forms.IntegerField(label="Number of bankruptcies", min_value=0, initial=0)

# --- Step 2: Credit Type Count ---
class CreditTypeCountForm(forms.Form):
    num_credit_types = forms.IntegerField(
        label="How many different types of credit do you have? (Valid types: mortgage, auto_loan, credit_card, personal_loan, retail_account, student_loan)",
        min_value=1
    )

# --- Step 3: Credit Type Details ---
class CreditTypeDetailForm(forms.Form):
    credit_type = forms.ChoiceField(choices=CREDIT_TYPE_CHOICES, label="Enter credit type")
    account_count = forms.IntegerField(label="How many accounts for this credit type?", min_value=1)

# --- Step 4a: Account Details for Revolving Accounts ---
class CreditCardDetailForm(forms.Form):
    account_age = forms.FloatField(label="Account age (in months)", min_value=0)
    balance = forms.FloatField(label="Current balance ($)", min_value=0)
    credit_limit = forms.FloatField(label="Credit limit ($)", min_value=0)

# --- Step 4b: Account Details for Loan Accounts ---
class LoanDetailForm(forms.Form):
    account_age = forms.FloatField(label="Account age (in months)", min_value=0)
    loan_amount = forms.FloatField(label="Original loan amount ($)", min_value=0)
    current_balance = forms.FloatField(label="Current balance ($)", min_value=0)
    monthly_payment = forms.FloatField(label="Monthly payment ($)", min_value=0)

# --- Step 5: New Credit Data ---
class NewCreditForm(forms.Form):
    inquiries_last_12mo = forms.IntegerField(label="Number of hard inquiries in last 12 months", min_value=0, initial=0)
    new_accounts_6mo = forms.IntegerField(label="Number of accounts opened in last 6 months", min_value=0, initial=0)
