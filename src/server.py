import sys
import os
import asyncio
from typing import Any, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from mcp.server import Server, NotificationOptions
    from mcp.server.stdio import stdio_server
    import mcp.types as types
    from logic import check_city_suspension, fetch_suspension_status
except ImportError as e:
    sys.stderr.write(f"Error importing dependencies: {e}\n")
    sys.stderr.write("Please run 'pip install -r requirements.txt'\n")
    sys.exit(1)

server = Server("mcp-tw-typhoon")

@server.list_tools()
async def list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="check_suspension",
            description="Check if work and classes are suspended due to natural disasters (e.g., Typhoon) for a specific city in Taiwan. Use this when the user asks 'Is there a typhoon holiday tomorrow?' or 'Is work suspended in Taipei?'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name to check (e.g., '台北市', '新竹縣', '高雄'). If omitted, returns a summary of all announced suspensions."
                    }
                }
            }
        ),
        types.Tool(
            name="list_all_suspensions",
            description="List the suspension status for all cities/counties in Taiwan.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[types.TextContent]:
    try:
        if name == "check_suspension":
            city = arguments.get("city")
            if city:
                result = check_city_suspension(city)
                return [types.TextContent(type="text", text=result)]
            else:
                # No city provided, return summary
                data = fetch_suspension_status()
                if "error" in data:
                    return [types.TextContent(type="text", text=f"Error: {data['error']}")]
                
                updated_at = data.get("updated_at", "Unknown")
                cities = data.get("cities", [])
                
                # Filter for "suspended" or "partial" (anything other than "Normal" or "Pending")
                # But actually, usually people want to know "What is the status?" even if normal.
                # Let's return a summary.
                
                # Check if ANY suspension
                suspended = [c for c in cities if "停止" in c["status"] or "照常" not in c["status"] and "尚未" not in c["status"]]
                
                if suspended:
                    text = f"【停班停課資訊】(更新: {updated_at})\n"
                    for c in suspended:
                        text += f"- {c['city']}: {c['status']}\n"
                    text += "\n其他縣市目前無特別公告或照常上班上課。"
                else:
                    text = f"目前全台無停班停課公告 (更新: {updated_at})。\n大部分縣市狀態為: 尚未宣布消息 或 照常上班上課。"
                
                return [types.TextContent(type="text", text=text)]

        elif name == "list_all_suspensions":
            data = fetch_suspension_status()
            if "error" in data:
                return [types.TextContent(type="text", text=f"Error: {data['error']}")]
            
            updated_at = data.get("updated_at", "Unknown")
            cities = data.get("cities", [])
            
            text = f"全台停班停課情形 (更新: {updated_at}):\n"
            for c in cities:
                text += f"- {c['city']}: {c['status']}\n"
            
            return [types.TextContent(type="text", text=text)]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        sys.stderr.write(f"Error in call_tool: {e}\n")
        return [types.TextContent(type="text", text=f"Error executing tool: {str(e)}")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            o_initialization_options=types.InitializationOptions(
                server_name="mcp-tw-typhoon",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        sys.stderr.write(f"Server crashed: {e}\n")
        sys.exit(1)
