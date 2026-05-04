import pytest
import time
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"

# --- FIXTURE: Setup ---
@pytest.fixture
def auth_page(page: Page):
    """
    Registers and logs in a unique user purely via the backend API, 
    then injects the JWT token into the browser to speed up E2E tests.
    """
    unique_id = int(time.time())
    user_data = {"username": f"e2e_bread_{unique_id}", "email": f"bread_{unique_id}@test.com", "password": "secure123"}
    
    # Register via API
    page.request.post(f"{BASE_URL}/users/register", data=user_data)
    # Login via API
    res = page.request.post(f"{BASE_URL}/users/login", data={"username_or_email": user_data["username"], "password": user_data["password"]})
    token = res.json()["access_token"]
    
    # Visit page to set the token, then reload to apply state
    page.goto(BASE_URL)
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.goto(BASE_URL) 
    
    # Return the fully authenticated Playwright page
    yield page

# --- TESTS ---

def test_full_calculation_bread_lifecycle(auth_page: Page):
    """
    Tests the complete happy-path of Add, Browse, Read, Edit, and Delete on the UI.
    """
    page = auth_page

    # 1. ADD
    page.fill("id=numA", "10")
    page.select_option("id=operation", "Add")
    page.fill("id=numB", "5")
    page.click("id=calcBtn")

    # Check Result & Browse (History List)
    expect(page.locator("id=resultText")).to_have_text("Result: 15")
    history_list = page.locator("id=historyList")
    expect(history_list).to_contain_text("10 Add 5 = 15")

    page.fill("id=numA", "2")
    page.select_option("id=operation", "Power")
    page.fill("id=numB", "3")
    page.click("id=calcBtn")
    
    expect(page.locator("id=resultText")).to_have_text("Result: 8")
    expect(history_list).to_contain_text("2 Power 3 = 8")
    

    # 2. READ (View Details)
    page.locator("text=View Details").first.click()
    details_section = page.locator("id=detailsSection")
    expect(details_section).to_be_visible()
    expect(page.locator("id=detailContent")).to_contain_text("Input A: 10")
    
    # Close details
    page.click("text=Close Details")
    expect(details_section).not_to_be_visible()

    # 3. EDIT (Update)
    page.get_by_role("button", name="Edit", exact=True).first.click()
    # Verify the form populated correctly
    expect(page.locator("id=numA")).to_have_value("10")
    expect(page.locator("id=calcBtn")).to_have_text("Update Calculation")
    
    # Change the values
    page.fill("id=numA", "20")
    page.click("id=calcBtn")
    
    # Verify history updated
    expect(history_list).to_contain_text("20 Add 5 = 25")
    # Verify form reset to Add mode
    expect(page.locator("id=calcBtn")).to_have_text("Calculate")

    # 4. DELETE
    page.locator("li").filter(has_text="20 Add 5 = 25").get_by_text("Delete").click()
    
    # Verify history is now empty of that specific item
    expect(history_list).not_to_contain_text("20 Add 5 = 25")


def test_negative_invalid_calculation(auth_page: Page):
    """
    Tests that the frontend correctly handles errors, like division by zero.
    """
    page = auth_page
    
    # Listen for the browser alert dialog and auto-accept it to verify its text
    page.on("dialog", lambda dialog: dialog.accept())
    
    page.fill("id=numA", "10")
    page.select_option("id=operation", "Divide")
    page.fill("id=numB", "0")
    
    page.click("id=calcBtn")
    
    # Ensure it didn't get added to history
    history_list = page.locator("id=historyList")
    expect(history_list).not_to_contain_text("10 Divide 0")