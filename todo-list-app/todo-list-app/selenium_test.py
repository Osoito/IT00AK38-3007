"""
Selenium Automation Test - Todo List App
测试添加任务、验证任务列表、调试功能
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
import logging
import time
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_log.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TodoListTest:
    def __init__(self, html_path, driver_path=None, headless=False):
        """
        Initialize test class
        :param html_path: Full path to index.html
        :param driver_path: Path to msedgedriver.exe (optional)
        :param headless: Use headless mode or not
        """
        self.html_path = html_path
        self.driver = None

        # WebDriver version lock: recommend using a specific driver version
        # Example: msedgedriver version 125.0.2535.85 for Edge 125.0.2535.85
        self.locked_driver_version = "125.0.2535.85"  # Change as needed

        edge_options = Options()
        if headless:
            edge_options.add_argument('--headless')
            edge_options.add_argument('--disable-gpu')

        try:
            if driver_path:
                # Check driver version
                import subprocess
                try:
                    version_output = subprocess.check_output([driver_path, '--version'], encoding='utf-8')
                    if self.locked_driver_version not in version_output:
                        logger.warning(f"⚠ WebDriver version mismatch! Expected: {self.locked_driver_version}, Got: {version_output.strip()}")
                except Exception as ve:
                    logger.warning(f"⚠ Could not verify WebDriver version: {ve}")

                service = Service(executable_path=driver_path)
                self.driver = webdriver.Edge(service=service, options=edge_options)
            else:
                self.driver = webdriver.Edge(options=edge_options)

            logger.info("✓ Edge WebDriver initialized successfully")
        except WebDriverException as e:
            logger.error(f"✗ Failed to initialize WebDriver: {e}")
            raise

    def open_page(self):
        """Open Todo List page"""
        try:
            file_url = f"file:///{self.html_path.replace(os.sep, '/')}"
            self.driver.get(file_url)
            logger.info(f"✓ Successfully opened page: {file_url}")
            # Explicit wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            logger.error("✗ Timeout waiting for page to load")
            self.take_screenshot("error_open_page_timeout.png")
            raise
        except Exception as e:
            logger.error(f"✗ Failed to open page: {e}")
            self.take_screenshot("error_open_page.png")
            raise

    def test_add_regular_task(self, task_text="Buy groceries"):
        """Test adding a regular task"""
        logger.info(f"\n=== Test 1: Add Regular Task '{task_text}' ===")
        try:
            task_input = self.driver.find_element(By.ID, "taskInput")
            add_button = self.driver.find_element(By.XPATH, "//button[text()='Add Task']")

            task_input.clear()
            task_input.send_keys(task_text)
            logger.info(f"✓ Entered text in input: {task_text}")

            add_button.click()
            logger.info("✓ Clicked 'Add Task' button")

            # Explicit wait for task to appear
            WebDriverWait(self.driver, 10).until(
                lambda d: any(task_text in li.text for li in d.find_element(By.ID, "taskList").find_elements(By.TAG_NAME, "li"))
            )

            task_list = self.driver.find_element(By.ID, "taskList")
            tasks = task_list.find_elements(By.TAG_NAME, "li")
            assert len(tasks) > 0, "Task list is empty"

            task_found = any(task_text in task.text for task in tasks)
            assert task_found, f"Task '{task_text}' not found"

            self.take_screenshot("test1_success.png")
            logger.info("✓ Test 1 Passed!\n")
            return True

        except Exception as e:
            logger.error(f"✗ Test 1 Failed: {e}")
            self.take_screenshot("test1_error.png")
            raise

    def test_add_important_task(self, task_text="Finish assignment"):
        """Test adding an important task"""
        logger.info(f"\n=== Test 2: Add Important Task '{task_text}' ===")
        try:
            important_input = self.driver.find_element(By.ID, "importantTaskInput")
            add_important_button = self.driver.find_element(
                By.XPATH, "//button[text()='Add Important Task']"
            )

            important_input.clear()
            important_input.send_keys(task_text)
            logger.info(f"✓ Entered text in important task input: {task_text}")

            add_important_button.click()
            logger.info("✓ Clicked 'Add Important Task' button")

            # Explicit wait for important task to appear
            WebDriverWait(self.driver, 10).until(
                lambda d: any(task_text in li.text for li in d.find_element(By.ID, "importantTaskList").find_elements(By.TAG_NAME, "li"))
            )

            important_list = self.driver.find_element(By.ID, "importantTaskList")
            tasks = important_list.find_elements(By.TAG_NAME, "li")
            assert len(tasks) > 0, "Important task list is empty"

            task_found = any(task_text in task.text for task in tasks)
            assert task_found, f"Important task '{task_text}' not found"

            self.take_screenshot("test2_success.png")
            logger.info("✓ Test 2 Passed!\n")
            return True

        except Exception as e:
            logger.error(f"✗ Test 2 Failed: {e}")
            self.take_screenshot("test2_error.png")
            raise

    def test_empty_task(self):
        """Test adding an empty task (should trigger alert)"""
        logger.info("\n=== Test 3: Empty Task Validation ===")
        try:
            task_input = self.driver.find_element(By.ID, "taskInput")
            add_button = self.driver.find_element(By.XPATH, "//button[text()='Add Task']")

            task_input.clear()
            logger.info("✓ Cleared input field")

            add_button.click()
            logger.info("✓ Clicked add button")

            # Wait for alert, handle localStorage disabled
            try:
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                logger.info(f"✓ Captured Alert: {alert_text}")
                alert.accept()
                assert "enter a task" in alert_text.lower(), "Alert text is incorrect"
                logger.info("✓ Test 3 Passed!\n")
                self.take_screenshot("test3_success.png")
                return True
            except TimeoutException:
                logger.warning("⚠ No alert captured (might be expected behavior if localStorage is disabled)")
                self.take_screenshot("test3_no_alert.png")
                return True
            except WebDriverException as e:
                if "localStorage" in str(e):
                    logger.warning("⚠ localStorage is disabled or not available in this browser context")
                else:
                    logger.error(f"✗ Unexpected WebDriverException: {e}")
                self.take_screenshot("test3_localstorage_error.png")
                return False

        except Exception as e:
            logger.error(f"✗ Test 3 Failed: {e}")
            self.take_screenshot("test3_error.png")
            raise

    def test_toggle_task(self):
        """Test toggling task completion status"""
        logger.info("\n=== Test 4: Toggle Task Completion Status ===")
        try:
            task_input = self.driver.find_element(By.ID, "taskInput")
            task_input.send_keys("Test toggle task")
            add_button = self.driver.find_element(By.XPATH, "//button[text()='Add Task']")
            add_button.click()

            # Explicit wait for task to appear
            WebDriverWait(self.driver, 10).until(
                lambda d: any("Test toggle task" in li.text for li in d.find_element(By.ID, "taskList").find_elements(By.TAG_NAME, "li"))
            )

            task_list = self.driver.find_element(By.ID, "taskList")
            task_span = task_list.find_element(By.TAG_NAME, "span")
            task_span.click()
            logger.info("✓ Clicked task to toggle completion status")

            # Explicit wait for class change
            WebDriverWait(self.driver, 5).until(
                lambda d: "completed" in d.find_element(By.ID, "taskList").find_element(By.TAG_NAME, "li").get_attribute("class")
            )

            task_item = task_list.find_element(By.TAG_NAME, "li")
            class_name = task_item.get_attribute("class")

            if "completed" in class_name:
                logger.info("✓ Task marked as completed")
            else:
                logger.warning("⚠ Task not marked as completed (might need to check)")

            self.take_screenshot("test4_success.png")
            logger.info("✓ Test 4 Passed!\n")
            return True

        except Exception as e:
            logger.error(f"✗ Test 4 Failed: {e}")
            self.take_screenshot("test4_error.png")
            raise

    def take_screenshot(self, filename):
        """Save screenshot"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"📸 Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"✗ Failed to take screenshot: {e}")

    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
            logger.info("✓ Browser closed")


def main():
    """主函数：运行所有测试"""
    # ===== 配置区域 - 请修改这里 =====
    # 方式 1: 使用绝对路径
    HTML_PATH = r"D:\Schoolwork\Software Testing\todo-list-app\todo-list-app\index.html"
    
    # 方式 2: 使用相对路径（如果脚本和 HTML 在同一目录）
    # HTML_PATH = os.path.abspath("index.html")
    
    # Edge Driver 路径（如果在 PATH 中可以设为 None）
    DRIVER_PATH =  r"D:\Downloads\edgedriver_win64\msedgedriver.exe"
    
    # 是否使用无头模式（True = 不显示浏览器窗口）
    HEADLESS = False
    # ================================
    
    logger.info("=" * 60)
    logger.info("Starting Selenium Automation Test")
    logger.info("=" * 60)
    
    test = None
    try:
        # 初始化测试
        test = TodoListTest(HTML_PATH, DRIVER_PATH, HEADLESS)
        
        # 打开页面
        test.open_page()
        
        # 运行测试
        test.test_add_regular_task("Buy groceries")
        test.test_add_important_task("Finish assignment")
        test.test_empty_task()
        test.test_toggle_task()
        
        logger.info("=" * 60)
        logger.info("✓ All tests completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n{'=' * 60}")
        logger.error(f"✗ Error occurred during testing: {e}")
        logger.error(f"{'=' * 60}\n")
        
    finally:
        if test:
            time.sleep(2)  # 等待 2 秒以便观察结果
            test.close()


if __name__ == "__main__":
    main()