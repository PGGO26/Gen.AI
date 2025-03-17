import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# UIUC Airfoil Database 網址
BASE_URL = "https://m-selig.ae.illinois.edu/ads/"

# 下載頁面內容
response = requests.get(BASE_URL + "coord_database.html")
soup = BeautifulSoup(response.text, "html.parser")

# 找到所有超連結，確保 href 存在
links = soup.find_all("a")
dat_links = [link.get("href") for link in links if link.get("href") and link.get("href").endswith(".dat")]

# 建立存放資料夾
os.makedirs("airfoils", exist_ok=True)

# 下載所有翼型數據
for dat_link in tqdm(dat_links):
    dat_url = BASE_URL + dat_link
    dat_name = dat_link.split("/")[-1]

    # 下載 .dat 文件
    response = requests.get(dat_url)
    with open(f"airfoils/{dat_name}", "wb") as f:
        f.write(response.content)

print(f"下載完成，共 {len(dat_links)} 個翼型數據。")
