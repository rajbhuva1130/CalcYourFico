# calculator/views.py
from django.shortcuts import render, redirect
from django.forms import formset_factory
from .forms import (
    PaymentHistoryForm, CreditTypeCountForm, CreditTypeDetailForm,
    CreditCardDetailForm, LoanDetailForm, NewCreditForm
)
from .utils import calculate_fico_score

def home(request):
    return render(request, "calculator/index.html")

# Step 1: Payment History Data
def payment_history_view(request):
    if request.method == 'POST':
        form = PaymentHistoryForm(request.POST)
        if form.is_valid():
            request.session['payment_history'] = form.cleaned_data
            return redirect('credit_type')
    else:
        form = PaymentHistoryForm()
    return render(request, "calculator/payment_history.html", {"form": form})

# Step 2: Credit Type Count
def credit_type_view(request):
    if request.method == 'POST':
        form = CreditTypeCountForm(request.POST)
        if form.is_valid():
            request.session['num_credit_types'] = form.cleaned_data['num_credit_types']
            return redirect('credit_type_details')
    else:
        form = CreditTypeCountForm()
    return render(request, "calculator/credit_type.html", {"form": form})

# Step 3: Credit Type Details (dynamic formset)
def credit_type_details_view(request):
    num = request.session.get('num_credit_types', 1)
    CreditTypeFormSet = formset_factory(CreditTypeDetailForm, extra=num)
    if request.method == 'POST':
        formset = CreditTypeFormSet(request.POST, prefix='ct')
        if formset.is_valid():
            # Save the list of credit types and account counts
            credit_types_details = [form.cleaned_data for form in formset]
            request.session['credit_types_details'] = credit_types_details
            return redirect('credit_details')
    else:
        formset = CreditTypeFormSet(prefix='ct')
    return render(request, "calculator/credit_type_details.html", {"formset": formset})

# Step 4: Credit Account Details for each credit type
def credit_account_details_view(request):
    # Retrieve the credit types details from session.
    credit_types_details = request.session.get('credit_types_details', [])
    account_formsets = {}
    revolving_types = ['credit_card', 'retail_account']
    loan_types = ['mortgage', 'auto_loan', 'personal_loan', 'student_loan']
    
    # For each credit type provided, create a formset.
    for idx, detail in enumerate(credit_types_details):
        ctype = detail.get('credit_type')
        count = detail.get('account_count')
        if ctype in revolving_types:
            FormSet = formset_factory(CreditCardDetailForm, extra=count)
        else:
            FormSet = formset_factory(LoanDetailForm, extra=count)
        prefix = f'accounts_{idx}'
        if request.method == 'POST':
            account_formsets[prefix] = FormSet(request.POST, prefix=prefix)
        else:
            account_formsets[prefix] = FormSet(prefix=prefix)
    
    if request.method == 'POST':
        valid = all(fs.is_valid() for fs in account_formsets.values())
        if valid:
            # Save the account details for each credit type.
            credit_account_details = {}
            for prefix, fs in account_formsets.items():
                credit_account_details[prefix] = [form.cleaned_data for form in fs]
            request.session['credit_account_details'] = credit_account_details
            return redirect('new_credit')
    
    # Zip the credit types details with their corresponding formset for easier template iteration.

    zipped = []
    for idx, detail in enumerate(credit_types_details):
        prefix = f'accounts_{idx}'
        zipped.append((detail, account_formsets[prefix]))
    return render(request, "calculator/credit_details.html", {"zipped": zipped})


# Step 5: New Credit Data
def new_credit_view(request):
    if request.method == 'POST':
        form = NewCreditForm(request.POST)
        if form.is_valid():
            request.session['new_credit'] = form.cleaned_data
            return redirect('results')
    else:
        form = NewCreditForm()
    return render(request, "calculator/new_credit.html", {"form": form})

# Step 6: Results
def results_view(request):
    # Retrieve data from session
    payment_history = request.session.get('payment_history', {})
    credit_types_details = request.session.get('credit_types_details', [])
    credit_account_details = request.session.get('credit_account_details', {})
    new_credit = request.session.get('new_credit', {})
    
    # Aggregate Payment History data (CLI sample)
    late_payments = {
        30: int(payment_history.get('late_payment_30', 0)),
        60: int(payment_history.get('late_payment_60', 0)),
        90: int(payment_history.get('late_payment_90', 0)),
    }
    collections = int(payment_history.get('collections', 0))
    bankruptcies = int(payment_history.get('bankruptcies', 0))
    
    # Aggregate credit account information.
    total_spend = 0.0
    total_limit = 0.0
    accounts_with_balance = 0
    avg_age_total = 0.0
    total_accounts = 0
    credit_types_used = []
    
    # Loop through each credit type detail and its account details.
    revolving_types = ['credit_card', 'retail_account']
    loan_types = ['mortgage', 'auto_loan', 'personal_loan', 'student_loan']
    
    for idx, detail in enumerate(credit_types_details):
        ctype = detail.get('credit_type')
        credit_types_used.append(ctype)
        prefix = f'accounts_{idx}'
        formset_data = credit_account_details.get(prefix, [])
        for account in formset_data:
            # Account age is provided in months; convert to years.
            age = float(account.get('account_age', 0)) / 12.0
            avg_age_total += age
            total_accounts += 1
            # For revolving accounts, sum up balances and credit limits.
            if ctype in revolving_types:
                bal = float(account.get('balance', 0))
                limit = float(account.get('credit_limit', 0))
                total_spend += bal
                total_limit += limit
                if bal > 0:
                    accounts_with_balance += 1
            else:
                # For loan accounts, add current balance to total balances.
                bal = float(account.get('current_balance', 0))
                total_spend += bal
                # For loans, we do not have a credit limit; use loan_amount as dummy.
                # (In a real scenario you might treat loans differently.)
                limit = float(account.get('loan_amount', 0))
                total_limit += limit
                if bal > 0:
                    accounts_with_balance += 1
    
    avg_age = (avg_age_total / total_accounts) if total_accounts else 0
    # Compute credit utilization for revolving accounts (if any limit exists)
    if total_limit > 0:
        credit_utilization = (total_spend / total_limit) * 100
    else:
        credit_utilization = 0
    
    # Prepare calculation data.
    calc_data = {
        'late_payments': late_payments,
        'collections': collections,
        'bankruptcies': bankruptcies,
        'credit_utilization': credit_utilization,
        'total_balances': total_spend,
        'accounts_with_balance': accounts_with_balance,
        'avg_age': avg_age,
        'oldest': avg_age,  # For simplicity, using avg_age; adjust as needed.
        'newest': avg_age,  # For simplicity.
        'credit_types': credit_types_used,
        'inquiries_last_12mo': int(new_credit.get('inquiries_last_12mo', 0)),
        'new_accounts_6mo': int(new_credit.get('new_accounts_6mo', 0))
    }
    
    fico_score, component_scores = calculate_fico_score(calc_data)
    fico_score_percentage = ((fico_score - 300) / (850 - 300)) * 100

    # Calculate the range
    fico_min = fico_score - 15
    fico_max = fico_score + 15
    
    context = {
        "fico_score": fico_score,
        'fico_min': fico_min,
        'fico_max': fico_max,
        "fico_score_percentage": fico_score_percentage,
        "component_scores": component_scores,
        "credit_utilization": round(credit_utilization, 1),
        "total_spend": total_spend,
        "total_limit": total_limit,
        "accounts_with_balance": accounts_with_balance,
        "total_accounts": total_accounts,
        "avg_age": round(avg_age, 1),
        "credit_types": ", ".join(credit_types_used)
    }
    return render(request, "calculator/results.html", context)
