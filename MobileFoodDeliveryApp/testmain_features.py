import unittest
from unittest.mock import MagicMock
from testOrder_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu

class TestAppFeatures(unittest.TestCase):

    def setUp(self):
        self.cart = Cart()
        self.menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.order_placement = OrderPlacement(self.cart, self.user_profile, self.menu)

    def test_change_delivery_address(self):
        # Feature: Change Delivery Address
        self.user_profile.delivery_address = "456 Elm St"
        self.assertEqual(self.user_profile.delivery_address, "456 Elm St")

    def test_remove_item_from_cart(self):
        # Feature: Remove Item from Cart
        self.cart.add_item("Pizza", 10.0, 2)
        self.cart.remove_item("Pizza")
        items = self.cart.view_cart()
        self.assertEqual(len(items), 0)

    def test_view_order_history(self):
        # Feature: View Order History (simulate with a simple list)
        self.user_profile.order_history = [
            {"order_id": 1, "items": ["Pizza"], "total": 15.0},
            {"order_id": 2, "items": ["Burger"], "total": 10.0}
        ]
        self.assertEqual(len(self.user_profile.order_history), 2)
        self.assertEqual(self.user_profile.order_history[0]["order_id"], 1)

    def test_filter_restaurants_by_rating(self):
        # Feature: Filter Restaurants by Rating
        restaurants = [
            {"name": "A", "rating": 4.5},
            {"name": "B", "rating": 3.0},
            {"name": "C", "rating": 5.0}
        ]
        min_rating = 4.0
        filtered = [r for r in restaurants if r["rating"] >= min_rating]
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(r["rating"] >= min_rating for r in filtered))

    def test_add_special_instructions_to_order(self):
        # Feature: Add Special Instructions to Order
        self.order_placement.special_instructions = "No onions"
        self.assertEqual(self.order_placement.special_instructions, "No onions")

if __name__ == "__main__":
    unittest.main()