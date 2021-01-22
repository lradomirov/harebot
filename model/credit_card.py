class CreditCard:

    def __init__(self, first_name, last_name, card_type, card_number, expiration_month, expiration_year, cvv):
        self.card_holder_first_name = first_name
        self.card_holder_last_name = last_name
        self.card_holder_name = " ".join([first_name, last_name])
        self.card_type = card_type
        self.card_number = card_number
        self.expiration_year = expiration_year
        self.expiration_month = expiration_month
        self.cvv = cvv
