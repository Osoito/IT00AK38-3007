import time
import unittest
from testOrder_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod

class TestSystemPerformance(unittest.TestCase):
    def test_order_flow_performance(self):
        menu = RestaurantMenu(["Pizza", "Burger"])
        user = UserProfile("123 Elm St")
        cart = Cart()
        cart.add_item("Pizza", 10.0, 2)
        order = OrderPlacement(cart, user, menu)
        payment = PaymentMethod()

        start = time.time()
        result = order.confirm_order(payment)
        end = time.time()

        duration = end - start
        print(f"\nPerformance test: executed in {duration:.4f} seconds")

        self.assertLess(duration, 1.0)  # 必须在 1 秒内完成
        self.assertTrue(result["success"])

if __name__ == "__main__":
    unittest.main()
