from .models import Payment
from python_daraja import payment as dj_payment
from django.db import transaction


def confirm_incomplete_transactions():
    payments = Payment.objects.filter(is_complete=False)

    for payment in payments:
        details = dj_payment.query_stk_push(
            checkout_request_id=payment.checkout_id)

        result_code = details['Body']['stkCallback']['ResultCode']
        print(result_code)

        if result_code == 0:
            callback_metadata = details['Body']['stkCallback']['CallbackMetadata']['Item']
            print(callback_metadata)

            payment.metadata = callback_metadata
            payment.is_complete = True
            payment.bill.is_paid = True
            payment.bill.save()
            payment.save()

        else:
            pass


confirm_incomplete_transactions()
