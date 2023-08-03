from .models import Payment
from python_daraja import payment as dj_payment


def confirm_incomplete_transactions():
    payments = Payment.objects.filter(is_complete=False)
    for payment in payments:
        details =dj_payment.query_stk_push(checkout_request_id=payment.checkout_id)
        # TODO: (kim) -> Check Transaction status from json body
        payment.metadata = details
        payment.is_complete = True
        payment.bill.is_paid = True
        payment.bill.save()
        payment.save()
        