"""A self-contained Gradio pizza ordering demo. Run: python app.py."""
from html import escape
import math
from uuid import uuid4
import gradio as gr

SIZES = {'Small · 10 inch': 1000, 'Medium · 12 inch': 1300, 'Large · 14 inch': 1600, 'Party · 16 inch': 1900}
CRUSTS = {'Classic hand-tossed': 0, 'Thin & crispy': 0, 'Stuffed crust': 300, 'Gluten-free style': 250}
SAUCES = ['Tomato basil', 'Garlic cream', 'Smoky BBQ', 'No sauce']
CHEESES = {'Mozzarella': 0, 'Extra mozzarella': 200, 'Plant-based cheese': 250, 'No cheese': 0}
TOPPINGS = {'Pepperoni': 150, 'Italian sausage': 150, 'Grilled chicken': 200, 'Smoked ham': 150, 'Mushrooms': 100, 'Red onion': 100, 'Bell peppers': 100, 'Black olives': 100, 'Pineapple': 100, 'Jalapeños': 100, 'Fresh basil': 100}
DEFAULT = ['Medium · 12 inch', 'Classic hand-tossed', 'Tomato basil', 'Mozzarella', [], 1, '']

PRESETS = {
    'Classic cheese': ('Tomato basil', 'Mozzarella', []),
    'Pepperoni favorite': ('Tomato basil', 'Mozzarella', ['Pepperoni']),
    'Garden party': ('Tomato basil', 'Mozzarella', ['Mushrooms', 'Red onion', 'Bell peppers', 'Black olives']),
    'BBQ chicken': ('Smoky BBQ', 'Mozzarella', ['Grilled chicken', 'Red onion']),
}

def recipe(name):
    sauce, cheese, toppings = PRESETS[name]
    return sauce, cheese, list(toppings)

def money(cents):
    return f'${cents / 100:,.2f}'

def pizza(size, crust, sauce, cheese, toppings, quantity, notes):
    if size not in SIZES or crust not in CRUSTS or sauce not in SAUCES or cheese not in CHEESES:
        raise gr.Error('Please select valid pizza options.')
    toppings = list(dict.fromkeys(toppings or []))
    if any(t not in TOPPINGS for t in toppings):
        raise gr.Error('Please select toppings from the menu.')
    if quantity is None or not math.isfinite(quantity) or quantity != int(quantity) or not 1 <= quantity <= 10:
        raise gr.Error('Choose a whole quantity from 1 to 10.')
    return dict(size=size, crust=crust, sauce=sauce, cheese=cheese, toppings=toppings, quantity=int(quantity), notes=(notes or '').strip()[:300], price=SIZES[size] + CRUSTS[crust] + CHEESES[cheese] + sum(TOPPINGS[t] for t in toppings))

def cheese_present(p):
    return p['cheese'] != 'No cheese'

def preview(*args):
    p = pizza(*args)
    toppings = ', '.join(p['toppings']) or ('Simply cheese. A classic for a reason.' if cheese_present(p) else 'Your crust. Your sauce. Beautifully simple.')
    return f'''<div class="pizza-preview"><div class="pizza-art">🍕</div><span class="eyebrow">MADE YOUR WAY</span><h2>Your next favorite pizza.</h2><p>{escape(toppings)}</p><div class="price-line"><span>{p['quantity']} × {escape(p['size'])}</span><strong>{money(p['price'] * p['quantity'])}</strong></div><small>{money(p['price'])} per pizza · before tax</small></div>'''

def totals(cart, method):
    subtotal = sum(p['price'] * p['quantity'] for p in cart)
    tax = (subtotal * 8 + 50) // 100
    delivery = 399 if cart and method == 'Delivery' else 0
    return subtotal, tax, delivery, subtotal + tax + delivery

def cart_view(cart, method):
    if not cart:
        return '<div class="empty-cart"><span>🛍️</span><h3>A little empty. A lot of potential.</h3><p>Build something delicious and add it to your order.</p></div>'
    rows = []
    for i, p in enumerate(cart, 1):
        details = ' · '.join([p['crust'], p['sauce'], p['cheese'], ', '.join(p['toppings']) or 'No toppings'])
        note = f"<p><em>{escape(p['notes'])}</em></p>" if p['notes'] else ''
        rows.append(f"<div class='cart-item'><b>{i}. {p['quantity']} × {escape(p['size'])}</b><strong>{money(p['price'] * p['quantity'])}</strong><p>{escape(details)}</p>{note}</div>")
    sub, tax, fee, total = totals(cart, method)
    return '<div class="cart-content">' + ''.join(rows) + f'<div class="bill"><p>Subtotal <b>{money(sub)}</b></p><p>Demo tax (8%) <b>{money(tax)}</b></p><p>Delivery <b>{money(fee)}</b></p><p class="total">Total <b>{money(total)}</b></p></div></div>'

def cart_outputs(cart, method):
    choices = [(f"{i + 1}. {p['quantity']} × {p['size']}", str(i)) for i, p in enumerate(cart)]
    return cart, cart_view(cart, method), gr.update(choices=choices, value=None)

def add(cart, method, *args):
    if len(cart) >= 20:
        raise gr.Error('Your cart can hold up to 20 different pizzas.')
    return cart_outputs([*cart, pizza(*args)], method)

def remove(cart, method, selected):
    if selected not in {str(i) for i in range(len(cart))}:
        raise gr.Error('Select a pizza to remove first.')
    return cart_outputs([p for i, p in enumerate(cart) if str(i) != selected], method)

def checkout(cart, method, name, phone, address):
    if not cart:
        raise gr.Error('Add a pizza before placing your demo order.')
    if not name.strip() or len([c for c in phone if c.isdigit()]) < 7:
        raise gr.Error('Enter your name and a valid contact phone number.')
    if method == 'Delivery' and not address.strip():
        raise gr.Error('Enter your delivery address.')
    total = totals(cart, method)[-1]
    receipt = f"<div class='receipt'><h3>✓ Demo order created!</h3><p>Thanks, {escape(name.strip())}. Your reference is <b>F&amp;F-{uuid4().hex[:6].upper()}</b>.</p><p>{sum(p['quantity'] for p in cart)} pizza(s) · {escape(method)} · <b>{money(total)}</b></p>{cart_view(cart, method)}<p>This is a demo confirmation. No restaurant was contacted and no payment was taken.</p></div>"
    return *cart_outputs([], method), receipt

CSS = '''
.gradio-container {max-width:1180px !important; margin:auto; background:#faf7f0 !important;}
footer {display:none !important} .brandbar {display:flex;justify-content:space-between;align-items:center;padding:22px 0;border-bottom:1px solid #dedbd0;color:#253f32}
.brand {font-size:24px;font-weight:850;letter-spacing:-1px}.brandbar small {letter-spacing:2px;font-size:10px}
.hero {padding:42px 0 28px;max-width:760px}.eyebrow {color:#b45131;font-size:11px;font-weight:800;letter-spacing:2px}
.hero h1 {font-family:Georgia,serif;font-size:clamp(40px,6vw,68px);line-height:1.04;letter-spacing:-2px;color:#253f32;margin:15px 0}.hero h1 em{color:#bd5638}.hero p{font-size:16px;color:#697066;line-height:1.6}
.pizza-preview {background:#eee9da;border-radius:20px;text-align:center;padding:24px;color:#253f32}.pizza-art{font-size:115px;line-height:1.4;filter:drop-shadow(0 15px 12px #7a52262b)}
.pizza-preview h2{font:28px Georgia,serif;margin:12px 0}.pizza-preview p{min-height:42px;color:#6a7165}.price-line{display:flex;align-items:center;justify-content:space-between;border-top:1px solid #d1cdbd;padding:18px 0 8px;text-align:left}.price-line strong{font-size:28px}.pizza-preview small{color:#74776d}
.empty-cart{text-align:center;padding:32px 16px;color:#687263}.empty-cart span{font-size:32px}.empty-cart h3{color:#253f32;font:20px Georgia,serif}.empty-cart p{font-size:13px}
.cart-item{border-bottom:1px solid #dedbd0;padding:15px 0}.cart-item>strong{float:right}.cart-item p{font-size:12px;color:#697066;margin:8px 0}.bill p{display:flex;justify-content:space-between;margin:12px 0}.bill .total{border-top:1px solid #dedbd0;padding-top:16px;font-size:22px;color:#253f32}.receipt{background:#e8f1e5;padding:20px;border-radius:12px;color:#253f32}.footnote{text-align:center;color:#7d8175;font-size:12px;padding:28px 0}
'''

def build_app():
    with gr.Blocks(title='Flour & Fire | Pizza your way', analytics_enabled=False) as demo:
        cart = gr.State([])
        gr.HTML('<div class="brandbar"><span class="brand">◒ flour & fire</span><small>GOOD DOUGH. GREAT COMPANY.</small></div><div class="hero"><span class="eyebrow">YOUR SLICE OF HAPPINESS</span><h1>Good pizza.<br><em>Your kind of perfect.</em></h1><p>Start with our dough. Make it your own. From the first topping<br>to the last bite, you’re in charge.</p></div>')
        with gr.Row():
            with gr.Column(scale=6):
                gr.Markdown('### 01 / Make it yours')
                preset = gr.Dropdown(list(PRESETS), value=None, label='Start with a favorite', info='Pick a recipe, then customize it below.')
                with gr.Row():
                    size = gr.Radio([(f'{label} · {money(price)}', label) for label, price in SIZES.items()], value=DEFAULT[0], label='Size · from $10')
                with gr.Row():
                    crust = gr.Dropdown([(f'{label} (+{money(price)})' if price else label, label) for label, price in CRUSTS.items()], value=DEFAULT[1], label='Crust')
                    sauce = gr.Dropdown(SAUCES, value=DEFAULT[2], label='Sauce')
                cheese = gr.Radio([(f'{label} (+{money(price)})' if price else label, label) for label, price in CHEESES.items()], value=DEFAULT[3], label='Cheese')
                gr.Markdown('### 02 / Top it off\nVegetables +$1 · Meats +$1.50 · Chicken +$2 each')
                toppings = gr.CheckboxGroup([(f'{label} +{money(price)}', label) for label, price in TOPPINGS.items()], label='Toppings', value=[])
                gr.Markdown('*Stuffed crust +$3 · Gluten-free style +$2.50 · Extra cheese +$2 · Plant-based +$2.50*')
                with gr.Row():
                    quantity = gr.Slider(1, 10, value=1, step=1, label='Quantity')
                notes = gr.Textbox(label='Kitchen notes', placeholder='Anything we should know?', max_length=300)
                gr.Markdown('*Contains common allergens. Gluten-free style does not guarantee an allergen-free kitchen.*')
                inputs = [size, crust, sauce, cheese, toppings, quantity, notes]
                add_btn = gr.Button('Add to my order  →', variant='primary', size='lg')
                reset_btn = gr.Button('Start a fresh pizza', size='sm')
            with gr.Column(scale=4):
                visual = gr.HTML(preview(*DEFAULT))
                gr.Markdown('### 03 / Your order')
                method = gr.Radio(['Pickup', 'Delivery'], value='Pickup', label='How are you getting your pizza?')
                cart_html = gr.HTML(cart_view([], 'Pickup'))
                with gr.Row():
                    selected = gr.Dropdown([], label='Remove a pizza', interactive=True)
                    remove_btn = gr.Button('Remove', size='sm')
                clear_btn = gr.Button('Clear cart', size='sm')
                with gr.Accordion('Contact & checkout', open=True):
                    name = gr.Textbox(label='Your name', max_length=100)
                    phone = gr.Textbox(label='Phone', max_length=30)
                    address = gr.Textbox(label='Delivery address', visible=False, max_length=300)
                    gr.Markdown('**Demo checkout** · No payment or real order is sent. Delivery is $3.99; demo tax is 8%.')
                    order_btn = gr.Button('Place demo order', variant='primary')
                receipt = gr.HTML()
        gr.HTML('<div class="footnote">flour & fire · A little flour. A lot of love. · Prices in USD.</div>')
        preset.input(recipe, preset, [sauce, cheese, toppings])
        reset_btn.click(lambda: (*DEFAULT, None), outputs=[*inputs, preset])
        gr.on(triggers=[c.change for c in inputs], fn=preview, inputs=inputs, outputs=visual)
        outputs = [cart, cart_html, selected]
        add_btn.click(add, [cart, method, *inputs], outputs)
        remove_btn.click(remove, [cart, method, selected], outputs)
        clear_btn.click(lambda m: cart_outputs([], m), method, outputs)
        method.change(lambda c, m: (cart_view(c, m), gr.update(visible=m == 'Delivery')), [cart, method], [cart_html, address])
        order_btn.click(checkout, [cart, method, name, phone, address], [*outputs, receipt])
    return demo

if __name__ == '__main__':
    build_app().launch(theme=gr.themes.Soft(primary_hue='green', neutral_hue='stone', font=['system-ui', 'sans-serif']), css=CSS)
