import requests
from bs4 import BeautifulSoup
import os
import re
import time

# 1️⃣ 確保 `airfoils/` 目錄存在
os.makedirs("airfoils", exist_ok=True)

# 2️⃣ 取得翼型列表
airfoil_lst_url = "http://airfoiltools.com/search/airfoils"
headers = {"User-Agent": "Mozilla/5.0"}
airfoil_lst_response = requests.get(airfoil_lst_url, headers=headers)
airfoil_lst_soup = BeautifulSoup(airfoil_lst_response.text, "html.parser")

airfoil_lst_table = airfoil_lst_soup.find("table", class_="listtable")

if airfoil_lst_table:
    airfoil_names = [row.text.strip() for row in airfoil_lst_table.find_all("a")]
else:
    print("Table not found.")
    exit()

# 3️⃣ 設定基本網址
base_url = "http://airfoiltools.com"

for airfoil_name in airfoil_names:
    print(f"Processing airfoil: {airfoil_name}")

    # 4️⃣ 過濾非法字元
    safe_airfoil_name = re.sub(r'[\\/*?:"<>|]', "_", airfoil_name)
    filename = f"airfoils/{safe_airfoil_name}.dat"

    # 5️⃣ 下載翼型數據
    airfoil_url = f"{base_url}/airfoil/details?airfoil={airfoil_name}"
    response = requests.get(airfoil_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    pre_tag = soup.find("pre", style="height:100px;overflow:auto;text-align:left;background-color:#ddd")

    if pre_tag:
        airfoil_data = pre_tag.text.strip()
        with open(filename, "w") as f:
            f.write(airfoil_data)
        print(f"✅ Downloaded airfoil shape data: {filename}")
    else:
        print(f"❌ Failed to find airfoil shape data for {airfoil_name}")
        continue  # 跳過這個翼型

    # 6️⃣ 抓取 XFOIL 模擬結果數據
    details_links = None
    for link in soup.find_all("a"):
        href = link.get("href")
        if href and "/polar/details?polar=xf-" in href:
            details_links = f"{base_url}{href}"
            break

    if details_links:
        details_response = requests.get(details_links, headers=headers)
        details_soup = BeautifulSoup(details_response.text, "html.parser")

        xfoil_tag = details_soup.find("pre", style="height:250px;overflow:auto;text-align:left;background-color:#ddd")
        if xfoil_tag:
            xfoil_data = xfoil_tag.text.strip()
            with open(filename, "a") as f:
                f.write("\n\nXFOIL Data:\n")
                f.write(xfoil_data)
            print(f"✅ Downloaded XFOIL data and saved into {filename}")
        else:
            print(f"❌ Failed to find XFOIL data for {airfoil_name}")
    else:
        print(f"❌ No XFOIL polar details found for {airfoil_name}")

    # 7️⃣ 休息 2 秒，避免過快請求被封鎖
    time.sleep(2)

print("\n🎉 All airfoils processed!")
