# 🌀 台灣停班停課查詢 (mcp-tw-typhoon)

這是一個 Model Context Protocol (MCP) 伺服器，專門用於查詢台灣各縣市因天然災害（如颱風）而發布的停班停課資訊。
資料來源：[行政院人事行政總處](https://www.dgpa.gov.tw/typh/daily/nds.html)。

## ✨ 功能
- **即時查詢**：獲取最新的停班停課公告。
- **特定縣市**：查詢特定縣市（如「台北市」、「高雄」）的狀態。
- **全台總覽**：列出所有縣市的狀態。

## 🛠 安裝與使用

### 1. 安裝依賴
建議使用虛擬環境：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 設定 Claude Desktop
編輯 `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "tw-typhoon": {
      "command": "/absolute/path/to/projects/mcp-tw-typhoon/.venv/bin/python",
      "args": ["/absolute/path/to/projects/mcp-tw-typhoon/src/server.py"]
    }
  }
}
```

### 3. 設定 Dive (或其他 MCP Client)
- **Type**: `stdio`
- **Command**: `/absolute/path/to/.venv/bin/python`
- **Args**: `/absolute/path/to/src/server.py`

## 📝 範例問句
- "明天台北有沒有放颱風假？"
- "查一下新竹縣有沒有停班停課。"
- "現在全台停班停課的情形如何？"
