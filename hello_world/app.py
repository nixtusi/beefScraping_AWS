import os
import time
import json
import boto3
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs4

def lambda_handler(event, context):
    print("🚀 Lambda handler started")
    print("📦 Raw event:", event)

    # JSONの取り出し（関数URL用とAPI Gateway用に対応）
    try:
        if isinstance(event, dict) and "body" in event:
            data = json.loads(event["body"])
        else:
            data = event  # 関数URLから直接来た場合
    except Exception as e:
        print(f"❌ JSON parsing error: {e}")
        return {"statusCode": 400, "body": f"Invalid JSON: {str(e)}"}

    number = data.get("number")
    password = data.get("password")
    api_key = data.get("api_key")

    print(f"🔑 API key received: {api_key}")
    print(f"👤 User number: {number}")

    if api_key != "mysecretkey123":
        return {"statusCode": 403, "body": "Invalid API key."}

    # パス設定
    chromedriver_path = "/tmp/chromedriver"
    headless_chromium_path = "/tmp/headless-chromium"
    s3 = boto3.client("s3")

    try:
        print("⬇️ Downloading Chrome binaries...")
        s3.download_file("my-kobe-univ-lambda", "chromedriver", chromedriver_path)
        s3.download_file("my-kobe-univ-lambda", "headless-chromium", headless_chromium_path)
        os.chmod(chromedriver_path, 0o755)
        os.chmod(headless_chromium_path, 0o755)
    except Exception as e:
        print(f"❌ Download error: {e}")
        return {"statusCode": 500, "body": f"Error downloading browser binaries: {str(e)}"}

    options = webdriver.ChromeOptions()
    options.binary_location = headless_chromium_path
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    tasks = []

    try:
        print("🧭 Launching headless Chrome...")
        driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

        base_url = "https://beefplus.center.kobe-u.ac.jp"
        login_url = "/saml/loginyu?disco=true"
        task_url = "/lms/task"

        print("🌐 Opening login page...")
        driver.get(base_url + login_url)

        print("🔐 Waiting for login form...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(number)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "kc-login").click()

        time.sleep(2)  # ログイン後のリダイレクト待ち

        print("📄 Accessing task page...")
        driver.get(base_url + task_url)
        time.sleep(2)

        soup = bs4(driver.page_source, "html.parser")
        courses = soup.find_all("div", class_="course")
        deadlines = soup.find_all("span", class_="deadline")

        for c, d in zip(courses, deadlines):
            tasks.append({
                "course": c.get_text(strip=True),
                "deadline": d.get_text(strip=True)
            })

        print(f"✅ {len(tasks)} tasks scraped")
        return {
            "statusCode": 200,
            "body": json.dumps({"tasks": tasks}, ensure_ascii=False)
        }

    except Exception as e:
        print(f"💥 Scraping error: {str(e)}")
        return {"statusCode": 500, "body": f"Error during scraping: {str(e)}"}

    finally:
        if 'driver' in locals():
            try:
                driver.quit()
                print("🛑 Chrome closed")
            except Exception as quit_error:
                print(f"⚠️ Chrome quit error: {quit_error}")
