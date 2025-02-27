# calculator/utils.py
def calculate_payment_history(late_payments, collections, bankruptcies):
    base_score = 100
    if late_payments:
        for days, count in late_payments.items():
            if days == 30:
                base_score -= (count * 15)
            elif days == 60:
                base_score -= (count * 25)
            elif days == 90:
                base_score -= (count * 45)
    base_score -= (collections * 50)
    base_score -= (bankruptcies * 130)
    return max(0, base_score)

def calculate_amounts_owed(credit_utilization, total_balances, num_accounts_with_balances):
    base_score = 100
    if credit_utilization <= 10:
        base_score = 100
    elif credit_utilization <= 20:
        base_score = 90
    elif credit_utilization <= 30:
        base_score = 80
    elif credit_utilization <= 50:
        base_score = 65
    elif credit_utilization <= 70:
        base_score = 40
    else:
        base_score = 30
    base_score -= (num_accounts_with_balances * 5)
    return max(0, base_score)

def calculate_length_of_history(avg_age, oldest, newest):
    base_score = 0
    if avg_age >= 9:
        base_score += 100
    elif avg_age >= 5:
        base_score += 80
    elif avg_age >= 2:
        base_score += 60
    elif avg_age >= 1:
        base_score += 40
    else:
        base_score += 20
    if oldest >= 20:
        base_score += 100
    elif oldest >= 10:
        base_score += 80
    elif oldest >= 5:
        base_score += 60
    else:
        base_score += 40
    return base_score / 2

def calculate_credit_mix(credit_types):
    base_score = 40
    if 'credit_card' in credit_types or 'retail_account' in credit_types:
        base_score += 10
    if 'mortgage' in credit_types or 'auto_loan' in credit_types or 'personal_loan' in credit_types or 'student_loan' in credit_types:
        base_score += 10
    return min(100, base_score)

def calculate_new_credit(inquiries_last_12mo, new_accounts_6mo):
    base_score = 100
    base_score -= (inquiries_last_12mo * 5)
    base_score -= (new_accounts_6mo * 10)
    return max(0, base_score)

def calculate_fico_score(data):
    payment_history = calculate_payment_history(
        data.get('late_payments', {30: 0, 60: 0, 90: 0}),
        data.get('collections', 0),
        data.get('bankruptcies', 0)
    )
    amounts_owed = calculate_amounts_owed(
        data.get('credit_utilization', 0),
        data.get('total_balances', 0),
        data.get('accounts_with_balance', 0)
    )
    length_of_history = calculate_length_of_history(
        data.get('avg_age', 5),
        data.get('oldest', 5),
        data.get('newest', 1)
    )
    credit_mix = calculate_credit_mix(data.get('credit_types', []))
    new_credit = calculate_new_credit(
        data.get('inquiries_last_12mo', 0),
        data.get('new_accounts_6mo', 0)
    )
    weighted_score = (
        (payment_history * 0.35) +
        (amounts_owed * 0.30) +
        (length_of_history * 0.15) +
        (credit_mix * 0.10) +
        (new_credit * 0.10)
    )
    fico_score = 300 + (weighted_score * 5.5)
    # Also return individual component scores
    components = {
        'Payment History': payment_history,
        'Amounts Owed': amounts_owed,
        'Length of History': length_of_history,
        'Credit Mix': credit_mix,
        'New Credit': new_credit
    }
    return round(min(850, max(300, fico_score))), components
