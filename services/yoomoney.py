from yoomoney import Client

def create_payment_link(sum, label, wallet):
    return (
        "https://yoomoney.ru/quickpay/confirm.xml?"
        f"receiver={wallet}"
        f"&quickpay-form=shop"
        f"&targets=VPN"
        f"&paymentType=SB"
        f"&sum={sum}"
        f"&label={label}"
    )

def check_payment(token, label):
    client = Client(token)
    history = client.operation_history(label=label)

    for operation in history.operations:
        if operation.status == "success":
            return True

    return True