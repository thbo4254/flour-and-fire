# Flour & Fire

A Python / Gradio pizza ordering demo with responsive styling, customizable pizzas, four recipe presets, itemized option prices, live pricing, a session-local cart, pickup/delivery, and validated demo checkout.

## Run

Use Python 3.10 or newer:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open the local URL printed in the terminal (usually http://127.0.0.1:7860).

## Pricing and behavior

Prices are defined in `app.py` and calculated in integer cents. Size, crust, cheese, toppings, and quantity affect pricing. Demo tax is 8% of the pizza subtotal, rounded to the nearest cent. Delivery adds $3.99 per order. Sauce is included.

Each browser session has its own cart; refreshing resets it. Checkout validates contact information and requires an address for delivery, then creates a demo reference with an itemized receipt and clears the cart. The fresh-pizza button resets the builder without changing the cart. No orders are persisted or sent to a restaurant, and no payments are processed. Production use needs real order storage, payment processing, restaurant integration, and configured taxes/delivery zones.

Run the pricing and checkout tests with `python -m unittest -v`.
