from model.address import Address
from model.credit_card import CreditCard
from model.profile import Profile
from sites.bestbuy import BestBuy

rtx_3080_urls = [
    "https://www.bestbuy.com/site/evga-geforce-rtx-3080-xc3-ultra-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6432400.p?skuId=6432400"
    "https://www.bestbuy.com/site/gigabyte-geforce-rtx-3080-gaming-oc-10g-gddr6x-pci-express-4-0-graphics-card-black/6430620.p?skuId=6430620",
    "https://www.bestbuy.com/site/gigabyte-geforce-rtx-3080-vision-oc-10g-gddr6x-pci-express-4-0-graphics-card-white/6436219.p?skuId=6436219",
    "https://www.bestbuy.com/site/gigabyte-geforce-rtx-3080-aorus-master-10g-gddr6x-pci-express-4-0-graphics-card-black/6436223.p?skuId=6436223",
    "https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440",
    "https://www.bestbuy.com/site/asus-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-strix-graphics-card-black/6432445.p?skuId=6432445",
    "https://www.bestbuy.com/site/msi-geforce-rtx-3080-ventus-3x-10g-oc-bv-gddr6x-pci-express-4-0-graphic-card-black-silver/6430175.p?skuId=6430175",
    "https://www.bestbuy.com/site/evga-geforce-rtx-3080-ftw3-ultra-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6436196.p?skuId=6436196",
    "https://www.bestbuy.com/site/pny-geforce-rtx-3080-10gb-xlr8-gaming-epic-x-rgb-triple-fan-graphics-card/6432658.p?skuId=6432658",
    "https://www.bestbuy.com/site/pny-geforce-rtx-3080-10gb-xlr8-gaming-epic-x-rgb-triple-fan-graphics-card/6432655.p?skuId=6432655",
    "https://www.bestbuy.com/site/evga-geforce-rtx-3080-ftw3-gaming-10gb-gddr6x-pci-express-4-0-graphics-card/6436191.p?skuId=6436191",
    "https://www.bestbuy.com/site/evga-geforce-rtx-3080-xc3-black-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6432399.p?skuId=6432399",
    "https://www.bestbuy.com/site/gigabyte-geforce-rtx-3080-eagle-oc-10g-gddr6x-pci-express-4-0-graphics-card-black/6430621.p?skuId=6430621",
    "https://www.bestbuy.com/site/evga-geforce-rtx-3080-xc3-ultra-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6436195.p?skuId=6436195",
    "https://www.bestbuy.com/site/evga-geforce-rtx-3080-xc3-gaming-10gb-gddr6-pci-express-4-0-graphics-card/6436194.p?skuId=6436194",
    # "https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149"
]

if __name__ in '__main__':
    my_address = Address(
        address_line_1="191 College Court",
        address_line_2="",
        city="Woodhaven",
        state_code="NY",
        zipcode="11421",
        country="USA"
    )
    my_credit_card = CreditCard(
        first_name="Chet",
        last_name="Bet",
        card_type="DISCOVER",
        card_number="6011950004545190",
        expiration_month="05",
        expiration_year="2025",
        cvv="431"
    )
    checkout_profile = Profile(
        first_name="aName",
        last_name="aLastName",
        email="anEmail@gmail.com", # substitute your email for the test!
        phone="4408595932",
        shipping_address=my_address,
        billing_address=my_address,
        credit_card=my_credit_card
    )

    bestbuy = BestBuy(product_urls=rtx_3080_urls, profile=checkout_profile)
    bestbuy.get_item()
