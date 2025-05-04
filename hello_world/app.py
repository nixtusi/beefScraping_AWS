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

    try:
        if isinstance(event, dict) and "body" in event:
            data = json.loads(event["body"])
        else:
            data = event
    except Exception as e:
        return {"statusCode": 400, "body": f"Invalid JSON: {str(e)}"}

    number = data.get("number")
    password = data.get("password")
    api_key = data.get("api_key")

    if api_key != "mysecretkey123":
        return {"statusCode": 403, "body": "Invalid API key."}

    # パス設定
    chromedriver_path = "/tmp/chromedriver"
    headless_chromium_path = "/tmp/headless-chromium"

    # S3からバイナリをダウンロード
    s3 = boto3.client("s3")
    try:
        print("⬇️ Downloading Chrome binaries...")
        s3.download_file("my-kobe-univ-lambda", "chromedriver", chromedriver_path)
        s3.download_file("my-kobe-univ-lambda", "headless-chromium", headless_chromium_path)
        os.chmod(chromedriver_path, 0o755)
        os.chmod(headless_chromium_path, 0o755)
    except Exception as e:
        return {"statusCode": 500, "body": f"Error downloading browser binaries: {str(e)}"}

    # Chromeオプション設定
    options = webdriver.ChromeOptions()
    options.binary_location = headless_chromium_path
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--single-process")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-features=VizDisplayCompositor")

    tasks = []

    try:
        print("🧭 Launching Chrome...")
        driver = webdriver.Chrome(service=Service(chromedriver_path), options=options)

        base_url = "https://beefplus.center.kobe-u.ac.jp"
        login_url = "/saml/loginyu?disco=true"
        task_url = "/lms/task"

        # ログイン
        driver.get(base_url + login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "username")))
        driver.find_element(By.ID, "username").send_keys(number)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "kc-login").click()
        time.sleep(2)

        # 課題一覧ページへ
        driver.get(base_url + task_url)
        time.sleep(2)

        soup = bs4(driver.page_source, "html.parser")
        blocks = soup.find_all("div", class_="sortTaskBlock")

        for block in blocks:
            try:
                course = block.find("div", class_="tasklist-course").get_text(strip=True)
                content = block.find("div", class_="tasklist-contents").get_text(strip=True)
                title_tag = block.find("div", class_="tasklist-title").find("a")
                title = title_tag.get_text(strip=True)
                url = base_url + title_tag["href"]
                deadline = block.find("span", class_="deadline").get_text(strip=True)

                tasks.append({
                    "course": course,
                    "content": content,
                    "title": title,
                    "deadline": deadline,
                    "url": url
                })
            except Exception as e:
                print(f"⚠️ Skipping a task block due to error: {e}")

        return {
            "statusCode": 200,
            "body": json.dumps({"tasks": tasks}, ensure_ascii=False)
        }

    except Exception as e:
        return {"statusCode": 500, "body": f"Error during scraping: {str(e)}"}

    finally:
        if "driver" in locals():
            try:
                driver.quit()
                print("🛑 Chrome closed")
            except Exception as quit_error:
                print(f"⚠️ Error during driver.quit(): {quit_error}")
