from .address import Address
from .credit_card import CreditCard


class Profile:

    def __init__(self, first_name, last_name, email, phone,
                 shipping_address: Address,
                 billing_address: Address,
                 credit_card: CreditCard):
        self.first_name = first_name
        self.last_name = last_name
        self.name = " ".join([first_name, last_name])
        self.email = email
        self.phone = phone
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.credit_card = credit_card
