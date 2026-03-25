import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def setup_driver():
    chrome_options = Options()
    # EC2 & Anti-Bot Settings
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    # Native Selenium 4+ Manager will download chromedriver automatically
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    return driver

def fetch_shows(url):
    driver = setup_driver()
    result = {
        "status": "success",
        "shows": []
    }
    
    try:
        driver.get(url)
        
        # Check for immediate bot blocks/captchas
        page_source_lower = driver.page_source.lower()
        if "access denied" in page_source_lower or "checking if the site connection is secure" in page_source_lower or "cloudflare" in page_source_lower:
            result["status"] = "blocked"
            return result

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "venue-list"))
            )
        except Exception:
            page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            if "verify you are human" in page_text or "access denied" in page_text:
                result["status"] = "blocked"
                return result
            result["status"] = "page_load_error"
            return result
            
        time.sleep(3) 
        soup = BeautifulSoup(driver.page_source, "html.parser")
        venues = soup.find_all("li", class_="list")
        
        for venue in venues:
            venue_name_tag = venue.find("a", class_="__venue-name")
            if not venue_name_tag:
                continue
                
            venue_name = venue_name_tag.text.strip()
            is_imax = "IMAX" in venue.text.upper()
            movie_format = "IMAX" if is_imax else "Standard"

            pills = venue.find_all("a", class_=lambda x: x and "showtime-pill" in x)
            for pill in pills:
                show_time = pill.text.strip()
                if not show_time:
                    continue
                
                status = "Available"
                pill_class_str = " ".join(pill.get("class", []))
                
                if "_soldout" in pill_class_str:
                    status = "Sold Out"
                elif "_fastfilling" in pill_class_str:
                    status = "Fast Filling"
                elif "none" in pill_class_str: 
                    status = "Disabled"
                
                result["shows"].append({
                    "venue": venue_name,
                    "time": show_time,
                    "format": movie_format,
                    "status": status,
                    "date": "Today" 
                })
                
    except Exception as e:
        print(f"Extraction encountered an issue: {e}")
        result["status"] = "error"
    finally:
        driver.quit()
        
    return result
