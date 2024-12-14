import os
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from cs50 import SQL

db = SQL("sqlite:///tracker.db")

# Set logging level to WARNING to suppress debug messages
logging.getLogger('selenium').setLevel(logging.WARNING)

def webscrap():
    chromedriver_path = r"G:\CSE\chromedriver"
    if chromedriver_path not in os.environ['PATH']:
        os.environ['PATH'] += os.pathsep + chromedriver_path
    
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.techinterviewhandbook.org/grind75/?mode=all&grouping=topics")
        driver.implicitly_wait(10)  # Increase wait time
        
        # Use WebDriverWait to wait for the elements to be present
        try:
            scraps = WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".text-indigo-600.text-base.hover\\:underline"))
            )
            for scrap in scraps:
                neetcode = f"neetcode.io/solutions/{scrap.get_attribute('innerHTML').replace(' ', '-').lower()}"
                ###db.execute("INSERT INTO Leetcode(Title, Leetcode, Neetcode) VALUES (?, ?, ?)",
                 ###          scrap.get_attribute("innerHTML"), scrap.get_attribute("href"), neetcode)

        except TimeoutException:
            print("Timed out waiting for problems to load")
        
    except NoSuchElementException as e:
        print(f"Element not found: {e}")
    finally:
        driver.quit()

def problemselect():
    global problems
    problems=db.execute("SELECT Title,Leetcode,Neetcode FROM Leetcode WHERE COMPLETION=0 LIMIT 2")

problemselect()

    
