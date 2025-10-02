import unittest
from unittest import mock  # Import the mock module to simulate payment gateway responses.

# PaymentProcessing Class
class PaymentProcessing:
    """
    The PaymentProcessing class handles validation and processing of payments using different payment methods.
    
    Attributes:
        available_gateways (list): A list of supported payment gateways such as 'credit_card' and 'paypal'.
    """
    def __init__(self, gateway=None):
        """
        Initializes the PaymentProcessing class with available payment gateways.
        """
        self.available_gateways = ["credit_card", "paypal"]
        self.gateway = gateway or FakePaymentGateway()

    def validate_payment_method(self, payment_method, payment_details):
        """
        Validates the selected payment method and its associated details.
        
        Args:
            payment_method (str): The selected payment method (e.g., 'credit_card', 'paypal').
            payment_details (dict): The details required for the payment method (e.g., card number, expiry date).
        
        Returns:
            bool: True if the payment method and details are valid, otherwise raises ValueError.
        
        Raises:
            ValueError: If the payment method is not supported or if the payment details are invalid.
        """
        # Check if the payment method is supported.
        if payment_method not in self.available_gateways:
            raise ValueError("Invalid payment method")

        # Validate credit card details if the selected method is 'credit_card'.
        if payment_method == "credit_card":
            if not self.validate_credit_card(payment_details):
                raise ValueError("Invalid credit card details")

        # Validation passed.
        return True

    def validate_credit_card(self, details):
        """
        Validates the credit card details (e.g., card number, expiry date, CVV).
        
        Args:
            details (dict): A dictionary containing 'card_number', 'expiry_date', and 'cvv'.
        
        Returns:
            bool: True if the card details are valid, False otherwise.
        """
        required_fields = ["card_number", "expiry_date", "cvv"]
        for field in required_fields:
            if field not in details or not details[field]:
                return False

        card_number = details.get("card_number", "")
        cvv = details.get("cvv", "")

        # Basic validation: Check if the card number is 16 digits and CVV is 3 digits.
        if len(card_number) != 16 or len(cvv) != 3:
            return False

        # More advanced validations like the Luhn Algorithm for card number can be added here.
        return True

    def process_payment(self, order, payment_method, payment_details):
        """
        Processes the payment for an order, validating the payment method and interacting with the payment gateway.
        
        Args:
            order (dict): The order details, including total amount.
            payment_method (str): The selected payment method.
            payment_details (dict): The details required for the payment method.
        
        Returns:
            str: A message indicating whether the payment was successful or failed.
        """
        if payment_method not in self.available_gateways:
            return "Error: Invalid payment method"
        response = self.gateway.process(payment_method, payment_details, order.get("total_amount", 0))
        if response["status"] == "success":
            return "Payment successful, Order confirmed"
        else:
            return f"Payment failed: {response['message']}"

class FakePaymentGateway:
    """
    Simulates a payment gateway for testing purposes.
    """
    def process(self, payment_method, payment_details, amount):
        # Simulate success for a specific card, failure for another
        if payment_method == "credit_card":
            if payment_details.get("card_number") == "1111222233334444":
                return {"status": "failure", "message": "Card declined"}
            return {"status": "success", "transaction_id": "fake_txn_123"}
        elif payment_method == "paypal":
            return {"status": "success", "transaction_id": "fake_txn_456"}
        return {"status": "failure", "message": "Unsupported payment method"}

# Unit tests for PaymentProcessing class
class TestPaymentProcessing(unittest.TestCase):
    """
    Unit tests for the PaymentProcessing class to ensure payment validation and processing work correctly.
    """
    def setUp(self):
        """
        Sets up the test environment by creating an instance of PaymentProcessing.
        """
        self.payment_processing = PaymentProcessing()

    def test_validate_payment_method_success(self):
        """
        Test case for successful validation of a valid payment method ('credit_card') with valid details.
        """
        payment_details = {"card_number": "1234567812345678", "expiry_date": "12/25", "cvv": "123"}
        result = self.payment_processing.validate_payment_method("credit_card", payment_details)
        self.assertTrue(result)

    def test_validate_payment_method_invalid_gateway(self):
        """
        Test case for validation failure due to an unsupported payment method ('bitcoin').
        """
        payment_details = {"card_number": "1234567812345678", "expiry_date": "12/25", "cvv": "123"}
        with self.assertRaises(ValueError) as context:
            self.payment_processing.validate_payment_method("bitcoin", payment_details)
        self.assertEqual(str(context.exception), "Invalid payment method")

    def test_validate_credit_card_invalid_details(self):
        """
        Test case for validation failure due to invalid credit card details (invalid card number and CVV).
        """
        payment_details = {"card_number": "1234", "expiry_date": "12/25", "cvv": "12"}  # Invalid card number and CVV.
        result = self.payment_processing.validate_credit_card(payment_details)
        self.assertFalse(result)

    def test_process_payment_success(self):
        """
        Test case for successful payment processing using the 'credit_card' method with valid details.
        """
        order = {"total_amount": 100.00}
        payment_details = {"card_number": "1234567812345678", "expiry_date": "12/25", "cvv": "123"}

        # Use mock to simulate a successful payment response from the gateway.
        with mock.patch.object(self.payment_processing.gateway, 'process', return_value={"status": "success"}):
            result = self.payment_processing.process_payment(order, "credit_card", payment_details)
            self.assertEqual(result, "Payment successful, Order confirmed")

    def test_process_payment_failure(self):
        """
        Test case for payment failure due to a declined credit card.
        """
        order = {"total_amount": 100.00}
        payment_details = {"card_number": "1111222233334444", "expiry_date": "12/25", "cvv": "123"}  # Simulate a declined card.

        # Use mock to simulate a failed payment response from the gateway.
        with mock.patch.object(self.payment_processing.gateway, 'process', return_value={"status": "failure", "message": "Card declined"}):
            result = self.payment_processing.process_payment(order, "credit_card", payment_details)
            self.assertEqual(result, "Payment failed: Card declined")

    def test_process_payment_invalid_method(self):
        """
        Test case for payment processing failure due to an invalid payment method ('bitcoin').
        """
        order = {"total_amount": 100.00}
        payment_details = {"card_number": "1234567812345678", "expiry_date": "12/25", "cvv": "123"}

        # No need for mocking, the method will raise an error directly.
        result = self.payment_processing.process_payment(order, "bitcoin", payment_details)
        self.assertIn("Error: Invalid payment method", result)

    def test_successful_credit_card_payment(self):
        order = {"total_amount": 50.00}
        payment_details = {"card_number": "1234567812345678"}
        result = self.payment_processing.process_payment(order, "credit_card", payment_details)
        self.assertEqual(result, "Payment successful, Order confirmed")

    def test_declined_credit_card_payment(self):
        order = {"total_amount": 50.00}
        payment_details = {"card_number": "1111222233334444"}
        result = self.payment_processing.process_payment(order, "credit_card", payment_details)
        self.assertEqual(result, "Payment failed: Card declined")

    def test_unsupported_payment_method(self):
        order = {"total_amount": 50.00}
        payment_details = {}
        result = self.payment_processing.process_payment(order, "bitcoin", payment_details)
        self.assertEqual(result, "Error: Invalid payment method")

if __name__ == "__main__":
    unittest.main()  # Run the unit tests.
