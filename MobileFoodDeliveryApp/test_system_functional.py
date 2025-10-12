import unittest
from testOrder_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod

class TestSystemFunctional(unittest.TestCase):
    def test_full_order_flow(self):
        menu = RestaurantMenu(["Pizza", "Burger"])
        user = UserProfile("123 Elm St")
        cart = Cart()
        cart.add_item("Pizza", 10.0, 2)
        order = OrderPlacement(cart, user, menu)
        payment = PaymentMethod()

        result = order.confirm_order(payment)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Order confirmed")
        print("\nSystem functional test output:", result)

if __name__ == "__main__":
    unittest.main()
