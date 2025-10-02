import tkinter as tk
from tkinter import messagebox, ttk
import json
import os

from testUser_Registration import UserRegistration
from testOrder_Placement import Cart, OrderPlacement, UserProfile, RestaurantMenu, PaymentMethod
from testPayment_Processing import PaymentProcessing
from testRestaurant_Browsing import RestaurantDatabase, RestaurantBrowsing

# Utility functions for user data storage
USERS_FILE = "users.json"

def load_users():
    # Stubbed function: always returns a fixed user dictionary
    return {"stub@example.com": {"password": "stubpass", "confirmed": True}}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mobile Food Delivery App")
        self.geometry("600x400")

        # Load user registration data from file
        self.user_data = load_users()

        # Initialize core classes
        self.registration = UserRegistration()
        self.registration.users = self.user_data  # Load existing users into registration system

        self.database = RestaurantDatabase()
        self.browsing = RestaurantBrowsing(self.database)

        # Initially no user logged in
        self.logged_in_email = None

        # Create initial frame
        self.current_frame = None
        self.show_startup_frame()

    def show_startup_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StartupFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_register_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = RegisterFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_login_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(self)
        self.current_frame.pack(fill="both", expand=True)

    def login_user(self, email):
        self.logged_in_email = email
        # After login, show main app frame
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = MainAppFrame(self, email)
        self.current_frame.pack(fill="both", expand=True)


class StartupFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Welcome to the Mobile Food Delivery App", font=("Arial", 16)).pack(pady=30)

        tk.Button(self, text="Register", command=self.go_to_register, width=20).pack(pady=10)
        tk.Button(self, text="Login", command=self.go_to_login, width=20).pack(pady=10)

    def go_to_register(self):
        self.master.show_register_frame()

    def go_to_login(self):
        self.master.show_login_frame()


class RegisterFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="Register New User", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")
        self.conf_pass_entry = self.create_entry("Confirm Password:", show="*")

        tk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def register_user(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        confirm_password = self.conf_pass_entry.get()

        result = self.master.registration.register(email, password, confirm_password)
        if result["success"]:
            # Save the updated users to file
            save_users(self.master.registration.users)
            messagebox.showinfo("Success", "Registration successful! Please log in.")
            self.master.show_login_frame()
        else:
            messagebox.showerror("Error", result["error"])

    def go_back(self):
        self.master.show_startup_frame()


class LoginFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        tk.Label(self, text="User Login", font=("Arial", 14)).pack(pady=20)

        self.email_entry = self.create_entry("Email:")
        self.pass_entry = self.create_entry("Password:", show="*")

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Back", command=self.go_back).pack()

    def create_entry(self, label_text, show=None):
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="e").pack(side="left")
        entry = tk.Entry(frame, show=show)
        entry.pack(side="left")
        return entry

    def login(self):
        email = self.email_entry.get()
        password = self.pass_entry.get()
        # Validate login
        # For simplicity, just check if user exists and password matches
        users = self.master.registration.users
        if email in users and users[email]["password"] == password:
            self.master.login_user(email)
        else:
            messagebox.showerror("Error", "Invalid email or password")

    def go_back(self):
        self.master.show_startup_frame()


class MainAppFrame(tk.Frame):
    def __init__(self, master, user_email):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {user_email}", font=("Arial", 14)).pack(pady=10)

        self.user_email = user_email
        self.database = master.database
        self.browsing = master.browsing

        # Create user's profile and cart
        self.user_profile = UserProfile(delivery_address="123 Main St")
        self.cart = Cart()
        self.restaurant_menu = RestaurantMenu(available_items=["Burger", "Pizza", "Salad"])
        self.order_placement = OrderPlacement(self.cart, self.user_profile, self.restaurant_menu)

        # Search Frame
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10)
        tk.Label(search_frame, text="Cuisine:").pack(side="left")
        self.cuisine_var = tk.Entry(search_frame)
        self.cuisine_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Search", command=self.search_restaurants).pack(side="left")

        # Rating Filter
        tk.Label(search_frame, text="Min Rating:").pack(side="left")
        self.rating_var = tk.Entry(search_frame, width=5)
        self.rating_var.pack(side="left", padx=5)
        tk.Button(search_frame, text="Apply Rating Filter", command=self.filter_by_rating).pack(side="left")
        tk.Button(search_frame, text="Clear Filter", command=self.view_all_restaurants).pack(side="left")

        # Results Treeview
        self.results_tree = ttk.Treeview(self, columns=("cuisine", "location", "rating"), show="headings")
        self.results_tree.heading("cuisine", text="Cuisine")
        self.results_tree.heading("location", text="Location")
        self.results_tree.heading("rating", text="Rating")
        self.results_tree.pack(pady=10, fill="x")

        # Buttons for actions
        action_frame = tk.Frame(self)
        action_frame.pack(pady=5)
        tk.Button(action_frame, text="View All Restaurants", command=self.view_all_restaurants).pack(side="left", padx=5)
        tk.Button(action_frame, text="Add Item to Cart", command=self.add_item_to_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="View Cart", command=self.view_cart).pack(side="left", padx=5)
        tk.Button(action_frame, text="Checkout", command=self.checkout).pack(side="left", padx=5)
        tk.Button(action_frame, text="Change Delivery Address", command=self.change_address).pack(side="left", padx=5)
        tk.Button(action_frame, text="Order History", command=self.view_order_history).pack(side="left", padx=5)

    def search_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        cuisine = self.cuisine_var.get().strip()
        results = self.browsing.search_by_filters(cuisine_type=cuisine if cuisine else None)
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def view_all_restaurants(self):
        self.results_tree.delete(*self.results_tree.get_children())
        results = self.database.get_restaurants()
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def filter_by_rating(self):
        self.results_tree.delete(*self.results_tree.get_children())
        try:
            min_rating = float(self.rating_var.get())
        except ValueError:
            min_rating = 0
        results = [r for r in self.database.get_restaurants() if r["rating"] >= min_rating]
        for r in results:
            self.results_tree.insert("", "end", values=(r["cuisine"], r["location"], r["rating"]))

    def add_item_to_cart(self):
        menu_popup = AddItemPopup(self, self.restaurant_menu, self.cart)
        self.wait_window(menu_popup)

    def view_cart(self):
        cart_view = CartViewPopup(self, self.cart)
        self.wait_window(cart_view)

    def checkout(self):
        validation = self.order_placement.validate_order()
        if not validation["success"]:
            messagebox.showerror("Error", validation["message"])
            return
        checkout_popup = CheckoutPopup(self, self.order_placement)
        self.wait_window(checkout_popup)

    def change_address(self):
        ChangeAddressPopup(self, self.user_profile)

    def view_order_history(self):
        OrderHistoryPopup(self, self.user_profile)

class CartManager:
    """Handles cart operations and UI logic."""
    def __init__(self, cart):
        self.cart = cart

    def get_cart_items(self):
        return self.cart.view_cart()

    def remove_item(self, item_name):
        return self.cart.remove_item(item_name)

class AddressManager:
    """Handles delivery address operations."""
    def __init__(self, user_profile):
        self.user_profile = user_profile

    def get_address(self):
        return self.user_profile.delivery_address

    def update_address(self, new_addr):
        if new_addr:
            self.user_profile.delivery_address = new_addr
            return True
        return False

class OrderHistoryManager:
    """Handles order history operations."""
    def __init__(self, user_profile):
        self.user_profile = user_profile

    def get_order_history(self):
        return getattr(self.user_profile, "order_history", [])

class SpecialInstructionsManager:
    """Handles special instructions for orders."""
    def __init__(self, order_placement):
        self.order_placement = order_placement

    def set_instructions(self, instructions):
        self.order_placement.special_instructions = instructions

    def get_instructions(self):
        return getattr(self.order_placement, "special_instructions", "")

# Refactored Popups using managers

class ChangeAddressPopup(tk.Toplevel):
    def __init__(self, master, user_profile):
        super().__init__(master)
        self.title("Change Delivery Address")
        self.addr_manager = AddressManager(user_profile)
        tk.Label(self, text="Enter new delivery address:").pack(pady=10)
        self.addr_entry = tk.Entry(self, width=40)
        self.addr_entry.insert(0, self.addr_manager.get_address())
        self.addr_entry.pack(pady=5)
        tk.Button(self, text="Save", command=self.save_address).pack(pady=10)

    def save_address(self):
        new_addr = self.addr_entry.get().strip()
        if self.addr_manager.update_address(new_addr):
            messagebox.showinfo("Address Updated", "Delivery address updated successfully.")
            self.destroy()
        else:
            messagebox.showerror("Error", "Address cannot be empty.")

class CartViewPopup(tk.Toplevel):
    def __init__(self, master, cart):
        super().__init__(master)
        self.title("Cart Items")
        self.cart_manager = CartManager(cart)
        items = self.cart_manager.get_cart_items()
        if not items:
            tk.Label(self, text="Your cart is empty").pack(pady=20)
        else:
            for i in items:
                tk.Label(self, text=f"{i['name']} x{i['quantity']} = ${i['subtotal']:.2f}").pack()
            tk.Label(self, text="Remove Item:").pack(pady=10)
            self.remove_var = tk.StringVar()
            self.remove_var.set(items[0]['name'])
            tk.OptionMenu(self, self.remove_var, *[i['name'] for i in items]).pack(pady=5)
            tk.Button(self, text="Remove", command=self.remove_item).pack(pady=5)

    def remove_item(self):
        item_name = self.remove_var.get()
        self.cart_manager.remove_item(item_name)
        messagebox.showinfo("Cart", f"Removed {item_name} from cart.")
        self.destroy()

class OrderHistoryPopup(tk.Toplevel):
    def __init__(self, master, user_profile):
        super().__init__(master)
        self.title("Order History")
        self.history_manager = OrderHistoryManager(user_profile)
        orders = self.history_manager.get_order_history()
        if not orders:
            tk.Label(self, text="No past orders found.").pack(pady=20)
        else:
            for order in orders:
                items_str = ", ".join(order.get("items", []))
                tk.Label(self, text=f"Order #{order.get('order_id', '')}: {items_str} | Total: ${order.get('total', 0):.2f}").pack()

class CheckoutPopup(tk.Toplevel):
    def __init__(self, master, order_placement):
        super().__init__(master)
        self.title("Checkout")
        self.order_placement = order_placement
        self.instructions_manager = SpecialInstructionsManager(order_placement)

        order_data = order_placement.proceed_to_checkout()
        tk.Label(self, text="Review your order:", font=("Arial", 12)).pack(pady=10)

        for item in order_data["items"]:
            tk.Label(self, text=f"{item['name']} x{item['quantity']} = ${item['subtotal']:.2f}").pack()

        total = order_data["total_info"]
        tk.Label(self, text=f"Subtotal: ${total['subtotal']:.2f}").pack()
        tk.Label(self, text=f"Tax: ${total['tax']:.2f}").pack()
        tk.Label(self, text=f"Delivery Fee: ${total['delivery_fee']:.2f}").pack()
        tk.Label(self, text=f"Total: ${total['total']:.2f}").pack()

        tk.Label(self, text=f"Delivery Address: {order_data['delivery_address']}").pack(pady=5)

        tk.Label(self, text="Special Instructions:").pack(pady=5)
        self.instructions_entry = tk.Entry(self, width=40)
        self.instructions_entry.pack(pady=5)

        tk.Label(self, text="Payment Method:").pack(pady=5)
        self.payment_method = tk.StringVar()
        self.payment_method.set("credit_card")
        tk.Radiobutton(self, text="Credit Card", variable=self.payment_method, value="credit_card").pack()
        tk.Radiobutton(self, text="Paypal", variable=self.payment_method, value="paypal").pack()

        tk.Label(self, text="For credit card enter a 16-digit card number:").pack(pady=5)
        self.card_entry = tk.Entry(self)
        self.card_entry.insert(0, "1234567812345678")
        self.card_entry.pack(pady=5)

        tk.Button(self, text="Confirm Order", command=self.confirm_order).pack(pady=10)

    def confirm_order(self):
        instructions = self.instructions_entry.get().strip()
        self.instructions_manager.set_instructions(instructions)
        payment_method_obj = PaymentMethod()
        result = self.order_placement.confirm_order(payment_method_obj)
        if result["success"]:
            msg = f"Order ID: {result['order_id']}\nEstimated Delivery: {result['estimated_delivery']}"
            if instructions:
                msg += f"\nSpecial Instructions: {instructions}"
            messagebox.showinfo("Order Confirmed", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", result["message"])

class AddItemPopup(tk.Toplevel):
    def __init__(self, master, menu, cart):
        super().__init__(master)
        self.title("Add Item to Cart")
        self.menu = menu
        self.cart = cart

        tk.Label(self, text="Select an item to add to cart:").pack(pady=10)

        self.item_var = tk.StringVar()
        self.item_var.set(self.menu.available_items[0] if self.menu.available_items else "")
        tk.OptionMenu(self, self.item_var, *self.menu.available_items).pack(pady=5)

        tk.Label(self, text="Quantity:").pack()
        self.qty_entry = tk.Entry(self)
        self.qty_entry.insert(0, "1")
        self.qty_entry.pack(pady=5)

        tk.Button(self, text="Add to Cart", command=self.add_to_cart).pack(pady=10)

    def add_to_cart(self):
        item = self.item_var.get()
        qty = int(self.qty_entry.get())
        price = 10.0  # Static price for simplicity
        msg = self.cart.add_item(item, price, qty)
        messagebox.showinfo("Cart", msg)
        self.destroy()


if __name__ == "__main__":
    app = Application()
    app.mainloop()
