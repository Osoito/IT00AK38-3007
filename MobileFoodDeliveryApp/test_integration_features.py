import unittest
from testOrder_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu

class TestIntegrationFeatures(unittest.TestCase):
    def setUp(self):
        self.user_profile = UserProfile(delivery_address="111 Old St")
        self.cart = Cart()
        self.menu = RestaurantMenu(available_items=["Burger", "Pizza"])
        self.order_placement = OrderPlacement(self.cart, self.user_profile, self.menu)

    def test_change_address_updates_order_placement(self):
        # Change address via AddressManager
        from main import AddressManager
        addr_manager = AddressManager(self.user_profile)
        addr_manager.update_address("222 New Ave")
        self.assertEqual(self.user_profile.delivery_address, "222 New Ave")
        # OrderPlacement should use updated address
        checkout_data = self.order_placement.proceed_to_checkout()
        self.assertEqual(checkout_data["delivery_address"], "222 New Ave")

    def test_remove_item_affects_order_total(self):
        # Add and remove items via CartManager
        from main import CartManager
        self.cart.add_item("Burger", 8.0, 2)
        self.cart.add_item("Pizza", 12.0, 1)
        cart_manager = CartManager(self.cart)
        cart_manager.remove_item("Burger")
        items = cart_manager.get_cart_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "Pizza")
        # OrderPlacement total should reflect only Pizza
        checkout_data = self.order_placement.proceed_to_checkout()
        self.assertEqual(checkout_data["total_info"]["subtotal"], 12.0)

    def test_order_history_records_orders(self):
        # Simulate placing an order and updating history
        from main import OrderHistoryManager
        self.cart.add_item("Burger", 8.0, 1)
        self.user_profile.order_history.append({
            "order_id": 1,
            "items": ["Burger"],
            "total": 8.0
        })
        history_manager = OrderHistoryManager(self.user_profile)
        history = history_manager.get_order_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["items"], ["Burger"])

    def test_special_instructions_flow(self):
        # Set instructions via SpecialInstructionsManager and verify in OrderPlacement
        from main import SpecialInstructionsManager
        instructions_manager = SpecialInstructionsManager(self.order_placement)
        instructions_manager.set_instructions("Extra napkins, please.")
        self.assertEqual(self.order_placement.special_instructions, "Extra napkins, please.")
        self.assertEqual(instructions_manager.get_instructions(), "Extra napkins, please.")

    def test_filter_restaurants_by_rating_integration(self):
        # Simulate RestaurantDatabase and RestaurantBrowsing
        class DummyDatabase:
            def get_restaurants(self):
                return [
                    {"cuisine": "Italian", "location": "Downtown", "rating": 4.7},
                    {"cuisine": "Chinese", "location": "Uptown", "rating": 3.5},
                    {"cuisine": "Mexican", "location": "Midtown", "rating": 4.2},
                ]
        class DummyBrowsing:
            def __init__(self, db):
                self.db = db
            def search_by_filters(self, cuisine_type=None, min_rating=None):
                results = self.db.get_restaurants()
                if min_rating is not None:
                    results = [r for r in results if r["rating"] >= min_rating]
                if cuisine_type:
                    results = [r for r in results if r["cuisine"] == cuisine_type]
                return results

        db = DummyDatabase()
        browsing = DummyBrowsing(db)
        filtered = browsing.search_by_filters(min_rating=4.5)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["cuisine"], "Italian")

if __name__ == "__main__":
    unittest.main()