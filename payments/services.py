import requests
from django.utils.crypto import get_random_string
from .models import Bill, Payment
from python_daraja import payment
import datetime


def trigger_stk_push(phone_number: int, amount: int, callback_url: str, account_ref: str, description: str) -> dict:
    """

    :param phone_number: Customer Phone Number
    :param amount: Amount to be paid
    :param callback_url: Your callback URL configured in the dashboard
    :param account_ref: Account Reference (e.g. Company Name/Business Name)
    :param description: Transaction Description
    :return: Python Dictionary with transaction info
    """

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {payment._get_access_token()}'
    }

    payload = {
        "BusinessShortCode": payment.SHORT_CODE,
        "Password": payment._get_password(),
        "Timestamp": datetime.datetime.now().strftime('%Y%m%d%H%M%S'),
        "TransactionType": payment._get_trans_type(),
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": payment.SHORT_CODE,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_ref,
        "TransactionDesc": description
    }

    response = requests.request("POST", 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest',
                                headers=headers, json=payload)
    return dict(response.json())


def build_payment_request(bill: Bill):
    details = trigger_stk_push(
        phone_number=bill.tenant.phone_number,
        amount=bill.amount,
        callback_url='https://thinkopal.com/',
        description='Payment',
        account_ref=get_random_string(10)
        )
    print(details)
    Payment.objects.create(bill=bill,merchent_id=details['MerchantRequestID'], checkout_id=details['CheckoutRequestID'])
    return
