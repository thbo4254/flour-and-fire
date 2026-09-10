import unittest
import gradio as gr
from app import DEFAULT, pizza, totals, add, remove, checkout, recipe, preview

class OrderingTests(unittest.TestCase):
    def test_custom_price_and_delivery(self):
        p = pizza('Large · 14 inch', 'Stuffed crust', 'Smoky BBQ', 'Extra mozzarella', ['Pepperoni', 'Mushrooms'], 2, '')
        self.assertEqual(p['price'], 2350)
        self.assertEqual(totals([p], 'Delivery'), (4700, 376, 399, 5475))
        self.assertEqual(totals([], 'Delivery'), (0, 0, 0, 0))

    def test_cart_does_not_mutate_original(self):
        original = []
        cart, _, _ = add(original, 'Pickup', *DEFAULT)
        self.assertEqual(original, [])
        self.assertEqual(len(cart), 1)
        self.assertEqual(remove(cart, 'Pickup', '0')[0], [])

    def test_checkout_validation_and_escape(self):
        cart = [pizza(*DEFAULT)]
        with self.assertRaises(gr.Error):
            checkout(cart, 'Delivery', 'Sam', '5551234567', '')
        result = checkout(cart, 'Pickup', '<script>', '5551234567', '')
        self.assertEqual(result[0], [])
        self.assertIn('&lt;script&gt;', result[-1])
        self.assertIn('$14.04', result[-1])

    def test_presets_and_no_cheese_preview(self):
        sauce, cheese, toppings = recipe('BBQ chicken')
        self.assertEqual(sauce, 'Smoky BBQ')
        self.assertEqual(toppings, ['Grilled chicken', 'Red onion'])
        toppings.append('Pepperoni')
        self.assertNotIn('Pepperoni', recipe('BBQ chicken')[2])
        args = DEFAULT.copy()
        args[3] = 'No cheese'
        self.assertNotIn('Simply cheese', preview(*args))

    def test_stale_remove_selection(self):
        with self.assertRaises(gr.Error):
            remove([pizza(*DEFAULT)], 'Pickup', '9')

    def test_invalid_quantity(self):
        for quantity in [0, 11, 1.5, float('nan'), float('inf')]:
            args = DEFAULT.copy()
            args[5] = quantity
            with self.assertRaises(gr.Error):
                pizza(*args)

if __name__ == '__main__':
    unittest.main()
