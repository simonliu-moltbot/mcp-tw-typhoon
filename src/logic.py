import requests
from bs4 import BeautifulSoup
import sys
import re
from typing import List, Dict, Optional, Any

DGPA_URL = "https://www.dgpa.gov.tw/typh/daily/nds.html"

def fetch_suspension_status() -> Dict[str, Any]:
    """
    Fetch the suspension status from DGPA.
    Returns a dictionary with 'updated_at' and 'cities'.
    """
    try:
        sys.stderr.write(f"Fetching {DGPA_URL}...\n")
        response = requests.get(DGPA_URL, timeout=10)
        response.encoding = 'utf-8' # Ensure correct encoding
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find update time
        # Usually text like "更新時間：2026/02/08 20:01:11"
        updated_at = "Unknown"
        body_text = soup.get_text()
        match = re.search(r"更新時間：(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})", body_text)
        if match:
            updated_at = match.group(1)
            
        # Parse table
        cities = []
        # The table structure is tricky. It might be:
        # Region | City | Status
        # But looking at the text dump:
        # 區域 縣市名稱 是否停止上班上課情形
        # 北部地區 基隆市 尚未宣布消息
        
        # Let's try to find the table rows
        # The table usually has class "Table_Body" or simple <table>
        tables = soup.find_all('table')
        if not tables:
            return {"error": "No table found", "updated_at": updated_at}
            
        # Assume the main table is the one with city names
        target_table = None
        for t in tables:
            if "縣市名稱" in t.get_text():
                target_table = t
                break
        
        if not target_table:
            return {"error": "Status table not found", "updated_at": updated_at}

        rows = target_table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            # We expect 3 columns: Region, City, Status
            # Or 2 columns if rowspan is used for Region
            # But BeautifulSoup handles finding all cells.
            
            # Simple heuristic: find a cell that looks like a city name
            # and the next cell is status.
            
            # Clean text
            texts = [c.get_text(strip=True) for c in cols]
            
            if not texts:
                continue
                
            # Check if this row has city data
            # Cities end with "市" or "縣" usually
            city = None
            status = None
            
            for i, text in enumerate(texts):
                if text.endswith("縣") or text.endswith("市"):
                    city = text
                    # The status is usually the next column
                    if i + 1 < len(texts):
                        status = texts[i+1]
                    break
            
            if city and status and city != "縣市名稱":
                cities.append({
                    "city": city,
                    "status": status
                })
                
        return {
            "updated_at": updated_at,
            "cities": cities
        }

    except Exception as e:
        sys.stderr.write(f"Error fetching suspension status: {e}\n")
        return {"error": str(e)}

def check_city_suspension(city_name: str) -> str:
    """
    Check suspension status for a specific city.
    """
    # Normalize input: 台 -> 臺
    if city_name:
        city_name = city_name.replace("台", "臺")
    
    data = fetch_suspension_status()
    if "error" in data:
        return f"Error: {data['error']}"
        
    cities = data.get("cities", [])
    
    # Fuzzy match city name
    target = None
    for c in cities:
        if city_name in c["city"] or c["city"] in city_name:
            target = c
            break
            
    if target:
        return f"【{target['city']}】{target['status']} (更新時間: {data['updated_at']})"
    else:
        # If not found, maybe list all?
        return f"找不到 '{city_name}' 的資料。目前資料包含: " + ", ".join([c['city'] for c in cities[:5]]) + "..."
