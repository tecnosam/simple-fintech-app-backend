from hashlib import md5

import time

from requests import get, post

from app.utils.settings import (
    PAYSTACK_SECRET_KEY
)


BASE_URL = "https://api.paystack.co"

AUTH_HEADERS = {'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}'}


def generate_transaction_reference(*args):

    hash_object = md5(str(time.time()).encode())

    for arg in args:

        hash_object.update(str(arg).encode('utf-8'))

    return str(hash_object.hexdigest())


def initiate_transaction(email, amount):

    url = f"{BASE_URL}/transaction/initialize"

    print(email, amount)

    response = post(
        url,
        headers=AUTH_HEADERS,
        json={
            'email': email,
            'amount': amount
        },
        timeout=1
    )

    if response.ok:

        response = response.json()

        if not response['status']:
            print(response)
            return None

        return response['data']

    print(response.text)
    return None


def get_bank_list():

    url = f"{BASE_URL}/bank"

    response = get(
        url,
        params={"currency": 'NGN'},
        headers=AUTH_HEADERS
    )

    return response.json()


def verify_bank_account(bank_code, account_number):

    url = f"{BASE_URL}/bank/resolve"

    response = get(
        url,
        params={
            "bank_code": bank_code,
            "account_number": account_number
        },
        headers=AUTH_HEADERS
    )

    return response.json()


def generate_recipient_code(
    name: str,
    account_number: str,
    bank_code: str,
):

    url = f"{BASE_URL}/transferrecipient"
    payload = {
        "type": "nuban",
        "name": name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": "NGN"
    }

    response = post(
        url,
        json=payload,
        headers=AUTH_HEADERS
    )

    res_data = response.json()

    return res_data['recipient_code']


def initiate_bank_transfer(
    recipient_code,
    amount,
    reference
):

    url = f"{BASE_URL}/transfer"

    payload = {
        "source": "balance",
        "amount": str(amount),
        "reference": reference,
        "recipient": recipient_code,
        "reason": "Transfer to Bank Account"
    }

    response = post(
        url,
        json=payload,
        headers=AUTH_HEADERS
    )

    return response.json()
