# HareBot

The makings of a checkout bot for BestBuy, Newegg, and other websites.
HareBot uses a combination of Selenium to create an interactive browser session,
BeautifulSoup to parse HTML, and Requests to execute HTTP requests.
I do not plan to maintain this project.

# Running the Bot

Simply install the packages in `requirements.txt` and run `main.py`.
Replace the urls array with whatever item(s) you're interested in. 
The url must end in the SKU number for BestBuy (combo item URLs will not work). 
Do not worry about the existing `Profile` information. 
It is configured with a fake address and Discover test card.

# Additional Information

It will successfully checkout if you put an in stock item URL, 
so replace `rtx_3080_urls` with an in stock item url 
and `checkout_profile.email` with a valid email address, then run it 
and look for an order confirmation email.

Only BestBuy works completely from querying stock to performing checkout.
It was a fairly intensive effort to disect their website for the appropriate
sequence of API calls to construct a successful checkout. 
The other `sites` are experimental.

I have not successfully checked out with the bot, 
though it has seen stock appear at BestBuy.
At the time, the bot was misconfigured and it failed to checkout.
I have since attempted to remedy what I think was the issue 
(not repeatedly hitting the `/addToCart` URL and checking for success),
so put in your information and let 'er rip!