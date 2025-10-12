# User Acceptance Testing for Mobile Food Delivery App
# Testing Order Tracking and Order Scheduling features

import time
import random
from datetime import datetime, timedelta

# Simulated Order Tracking System
class OrderTracker:
    """Simulates real-time order tracking functionality"""
    
    def __init__(self, order_id):
        self.order_id = order_id
        self.status = "Preparing"
        self.status_history = []
        self.last_update = datetime.now()
        self.update_interval = 10  # seconds
        
    def get_current_status(self):
        """Get the current order status"""
        return {
            "order_id": self.order_id,
            "status": self.status,
            "last_updated": self.last_update.strftime("%Y-%m-%d %H:%M:%S"),
            "update_interval": self.update_interval
        }
    
    def update_status(self, new_status):
        """Update order status and record the change"""
        old_status = self.status
        self.status = new_status
        self.last_update = datetime.now()
        self.status_history.append({
            "from": old_status,
            "to": new_status,
            "timestamp": self.last_update
        })
        return True
    
    def simulate_order_progress(self):
        """Simulate automatic order progression"""
        statuses = ["Preparing", "On the Way", "Delivered"]
        current_index = statuses.index(self.status)
        if current_index < len(statuses) - 1:
            self.update_status(statuses[current_index + 1])
            return True
        return False
    
    def check_update_frequency(self):
        """Check if updates happen within 10 seconds"""
        time_diff = (datetime.now() - self.last_update).seconds
        return time_diff <= self.update_interval

# Simulated Order Scheduling System
class OrderScheduler:
    """Simulates order scheduling functionality"""
    
    def __init__(self):
        self.scheduled_orders = []
        self.confirmation_times = []
        
    def schedule_order(self, user_id, items, delivery_time):
        """Schedule a future order"""
        start_time = datetime.now()
        
        # Validate delivery time (must be in the future)
        current_time = datetime.now()
        if delivery_time <= current_time:
            return {
                "success": False,
                "message": "Delivery time must be in the future"
            }
        
        # Create scheduled order
        order = {
            "order_id": f"SCH{random.randint(1000, 9999)}",
            "user_id": user_id,
            "items": items,
            "scheduled_time": delivery_time,
            "created_at": current_time,
            "status": "Scheduled"
        }
        
        self.scheduled_orders.append(order)
        
        # Simulate confirmation process (with slight delay)
        time.sleep(random.uniform(0.5, 1.5))  # Simulate processing time
        
        confirmation_time = datetime.now()
        time_taken = (confirmation_time - start_time).total_seconds()
        self.confirmation_times.append(time_taken)
        
        # Send confirmation
        confirmation = {
            "success": True,
            "order_id": order["order_id"],
            "scheduled_time": delivery_time.strftime("%Y-%m-%d %H:%M"),
            "confirmation_sent_at": confirmation_time.strftime("%Y-%m-%d %H:%M:%S"),
            "time_to_confirm": f"{time_taken:.2f} seconds"
        }
        
        return confirmation
    
    def check_confirmation_time(self):
        """Check if all confirmations were sent within 2 minutes"""
        if not self.confirmation_times:
            return None
        
        max_time = max(self.confirmation_times)
        avg_time = sum(self.confirmation_times) / len(self.confirmation_times)
        
        return {
            "all_within_2min": all(t < 120 for t in self.confirmation_times),
            "max_time": f"{max_time:.2f} seconds",
            "avg_time": f"{avg_time:.2f} seconds",
            "total_orders": len(self.confirmation_times)
        }

# UAT Test Cases
class UATTestCases:
    """User Acceptance Test Cases for Order Tracking and Scheduling"""
    
    @staticmethod
    def test_order_status_update_frequency():
        """TC-OT-001: Verify order status updates every 10 seconds"""
        print("\n=== TC-OT-001: Order Status Update Frequency ===")
        tracker = OrderTracker("ORD12345")
        
        # Initial status
        print(f"Initial status: {tracker.get_current_status()}")
        
        # Simulate updates
        results = []
        for i in range(3):
            time.sleep(2)  # Simulate time passing
            tracker.update_status(f"Update {i+1}")
            is_within_interval = tracker.check_update_frequency()
            results.append(is_within_interval)
            print(f"Update {i+1}: Within 10s interval? {is_within_interval}")
        
        test_passed = all(results)
        print(f"Test Result: {'PASS' if test_passed else 'FAIL'}")
        return test_passed
    
    @staticmethod
    def test_order_status_stages():
        """TC-OT-002: Verify order displays correct stages"""
        print("\n=== TC-OT-002: Order Status Stages ===")
        tracker = OrderTracker("ORD12346")
        
        expected_stages = ["Preparing", "On the Way", "Delivered"]
        actual_stages = []
        
        print(f"Initial status: {tracker.status}")
        actual_stages.append(tracker.status)
        
        # Progress through stages
        for _ in range(2):
            tracker.simulate_order_progress()
            print(f"Updated status: {tracker.status}")
            actual_stages.append(tracker.status)
        
        test_passed = actual_stages == expected_stages
        print(f"Expected stages: {expected_stages}")
        print(f"Actual stages: {actual_stages}")
        print(f"Test Result: {'PASS' if test_passed else 'FAIL'}")
        return test_passed
    
    @staticmethod
    def test_schedule_delivery_time_selection():
        """TC-OS-001: Verify user can select delivery time"""
        print("\n=== TC-OS-001: Delivery Time Selection ===")
        scheduler = OrderScheduler()
        
        # Test future delivery time
        future_time = datetime.now() + timedelta(hours=2)
        result = scheduler.schedule_order(
            user_id="USER123",
            items=["Burger", "Fries"],
            delivery_time=future_time
        )
        
        print(f"Scheduling for: {future_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Order created: {result.get('success')}")
        print(f"Order ID: {result.get('order_id')}")
        
        # Test past delivery time (should fail)
        past_time = datetime.now() - timedelta(hours=1)
        invalid_result = scheduler.schedule_order(
            user_id="USER123",
            items=["Pizza"],
            delivery_time=past_time
        )
        
        print(f"\nAttempting past time scheduling: {invalid_result.get('success')}")
        print(f"Error message: {invalid_result.get('message')}")
        
        test_passed = result['success'] and not invalid_result['success']
        print(f"\nTest Result: {'PASS' if test_passed else 'FAIL'}")
        return test_passed
    
    @staticmethod
    def test_confirmation_within_two_minutes():
        """TC-OS-002: Verify confirmation sent within 2 minutes"""
        print("\n=== TC-OS-002: Confirmation Time Validation ===")
        scheduler = OrderScheduler()
        
        # Schedule multiple orders
        print("Scheduling multiple orders to test confirmation time...")
        for i in range(5):
            future_time = datetime.now() + timedelta(hours=i+1)
            result = scheduler.schedule_order(
                user_id=f"USER{i}",
                items=[f"Item{i}"],
                delivery_time=future_time
            )
            print(f"Order {i+1}: Confirmed in {result['time_to_confirm']}")
        
        # Check confirmation times
        stats = scheduler.check_confirmation_time()
        print(f"\nConfirmation Statistics:")
        print(f"All within 2 minutes: {stats['all_within_2min']}")
        print(f"Maximum time: {stats['max_time']}")
        print(f"Average time: {stats['avg_time']}")
        
        test_passed = stats['all_within_2min']
        print(f"\nTest Result: {'PASS' if test_passed else 'FAIL'}")
        return test_passed

# Alpha Testing Simulation
def run_alpha_testing():
    """Execute Alpha Testing internally"""
    print("\n" + "="*50)
    print("ALPHA TESTING SESSION")
    print("="*50)
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Environment: Development")
    print("Tester: Internal Team")
    
    results = {
        "TC-OT-001": UATTestCases.test_order_status_update_frequency(),
        "TC-OT-002": UATTestCases.test_order_status_stages(),
        "TC-OS-001": UATTestCases.test_schedule_delivery_time_selection(),
        "TC-OS-002": UATTestCases.test_confirmation_within_two_minutes()
    }
    
    print("\n" + "="*50)
    print("ALPHA TESTING SUMMARY")
    print("="*50)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Total Test Cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {(passed/total)*100:.1f}%")
    
    for test_id, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_id}: {status}")
    
    return results

# Beta Testing Simulation with User Scenarios
def run_beta_testing():
    """Execute Beta Testing with simulated users"""
    print("\n" + "="*50)
    print("BETA TESTING SESSION")
    print("="*50)
    print("Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("Environment: Staging (Production-like)")
    print("Testers: 5 External Users")
    
    # Simulate different user scenarios
    print("\n--- User A: Real-time Order Tracking ---")
    tracker_a = OrderTracker("BETA001")
    print(f"User A places order: {tracker_a.order_id}")
    print(f"Initial status shown: {tracker_a.status}")
    
    # Simulate user checking status multiple times
    for i in range(3):
        time.sleep(1)
        if i == 1:
            tracker_a.simulate_order_progress()
        status = tracker_a.get_current_status()
        print(f"Check {i+1}: Status = {status['status']}, Last updated = {status['last_updated']}")
    
    print("\n--- User B: Schedule Lunch Order ---")
    scheduler = OrderScheduler()
    lunch_time = datetime.now() + timedelta(hours=3)
    result = scheduler.schedule_order(
        user_id="BETA_USER_B",
        items=["Sandwich", "Salad", "Juice"],
        delivery_time=lunch_time
    )
    print(f"Scheduled for: {lunch_time.strftime('%H:%M')}")
    print(f"Confirmation received: {result['success']}")
    print(f"Time to confirm: {result['time_to_confirm']}")
    
    print("\n--- User C: Multiple Scheduled Orders ---")
    for day in range(3):
        delivery_time = datetime.now() + timedelta(days=day+1, hours=12)
        result = scheduler.schedule_order(
            user_id="BETA_USER_C",
            items=[f"Daily Special Day {day+1}"],
            delivery_time=delivery_time
        )
        print(f"Day {day+1} order: Confirmed in {result['time_to_confirm']}")
    
    # Collect user feedback
    print("\n" + "="*50)
    print("USER FEEDBACK SUMMARY")
    print("="*50)
    
    feedback = {
        "User A": "Order tracking works well, updates are timely",
        "User B": "Scheduling is easy, confirmation was quick",
        "User C": "Multiple orders scheduled successfully",
        "User D": "Would like more frequent status updates",
        "User E": "Want to modify scheduled orders after confirmation"
    }
    
    for user, comment in feedback.items():
        print(f"{user}: {comment}")
    
    return feedback

# Main execution
if __name__ == "__main__":
    print("MOBILE FOOD DELIVERY APP - USER ACCEPTANCE TESTING")
    print("="*60)
    
    # Run Alpha Testing
    alpha_results = run_alpha_testing()
    
    # Wait a moment between testing phases
    time.sleep(2)
    
    # Run Beta Testing
    beta_feedback = run_beta_testing()
    
    print("\n" + "="*60)
    print("UAT TESTING COMPLETED")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")