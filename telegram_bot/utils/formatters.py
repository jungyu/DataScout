"""
訊息與資料格式化工具
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Union


def format_task_status(task: Dict[str, Any]) -> str:
    """格式化任務狀態訊息
    
    Args:
        task: 任務狀態字典
    
    Returns:
        格式化後的任務狀態文本
    """
    # 狀態對應的表情符號
    status_emoji = {
        "pending": "⏳",
        "running": "▶️",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫",
        "scheduled": "🗓️"
    }
    
    # 獲取狀態表情
    status = task.get("status", "unknown")
    emoji = status_emoji.get(status, "❓")
    
    # 格式化基本信息
    result = (
        f"*任務 {task.get('id', 'N/A')} 狀態*\n\n"
        f"狀態: {emoji} {status.upper()}\n"
        f"目標: `{task.get('target_url', 'N/A')}`\n"
    )
    
    # 根據狀態添加不同的信息
    if status in ("pending", "running"):
        result += f"進度: {task.get('progress', 0)}%\n"
        
    if "start_time" in task:
        result += f"開始時間: {task.get('start_time')}\n"
        
    if status in ("completed", "failed", "cancelled") and "end_time" in task:
        result += f"結束時間: {task.get('end_time')}\n"
        
        # 計算執行時間
        try:
            start_time = datetime.strptime(task.get('start_time', ""), "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(task.get('end_time', ""), "%Y-%m-%d %H:%M:%S")
            duration = end_time - start_time
            result += f"執行時間: {format_duration(duration.total_seconds())}\n"
        except (ValueError, TypeError):
            pass
    
    # 添加錯誤信息
    if status == "failed" and "error" in task:
        result += f"\n錯誤信息:\n`{task.get('error')}`\n"
    
    # 添加選項信息
    if "options" in task and task["options"]:
        options_str = ", ".join([f"{k}={v}" for k, v in task["options"].items()])
        result += f"\n選項: {options_str}\n"
        
    # 添加結果信息
    if status == "completed" and task.get("has_result", False):
        result += f"\n使用 /result {task.get('id')} 查看結果\n"
    
    return result


def format_task_list(tasks: List[Dict[str, Any]], title: str) -> str:
    """格式化任務列表訊息
    
    Args:
        tasks: 任務列表
        title: 列表標題
    
    Returns:
        格式化後的任務列表文本
    """
    # 狀態對應的表情符號
    status_emoji = {
        "pending": "⏳",
        "running": "▶️",
        "completed": "✅",
        "failed": "❌",
        "cancelled": "🚫",
        "scheduled": "🗓️"
    }
    
    # 格式化標題
    result = f"📋 *{title}*\n\n"
    
    # 格式化每個任務
    for i, task in enumerate(tasks, 1):
        status = task.get("status", "unknown")
        emoji = status_emoji.get(status, "❓")
        
        # 任務基本信息
        task_line = (
            f"{i}. {emoji} *{task.get('id', 'N/A')}*: "
            f"`{truncate_url(task.get('target_url', 'N/A'))}`"
        )
        
        # 添加任務進度
        if status in ("pending", "running") and "progress" in task:
            task_line += f" ({task.get('progress')}%)"
            
        # 添加時間信息
        if "start_time" in task:
            time_str = task.get('start_time', "").split()[0]  # 只取日期部分
            task_line += f" - {time_str}"
            
        result += task_line + "\n"
    
    # 添加說明
    result += "\n使用 /status [任務ID] 查看詳細狀態"
    
    return result


def format_duration(seconds: float) -> str:
    """格式化時間長度
    
    Args:
        seconds: 秒數
    
    Returns:
        格式化後的時間長度文本 (例如: 2小時 30分 15秒)
    """
    if seconds < 60:
        return f"{int(seconds)} 秒"
    
    minutes, seconds = divmod(int(seconds), 60)
    if minutes < 60:
        return f"{minutes} 分 {seconds} 秒"
    
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours} 小時 {minutes} 分 {seconds} 秒"
    
    days, hours = divmod(hours, 24)
    return f"{days} 天 {hours} 小時 {minutes} 分"


def truncate_url(url: str, max_length: int = 30) -> str:
    """截斷 URL 以適合顯示
    
    Args:
        url: 完整 URL
        max_length: 最大長度
    
    Returns:
        截斷後的 URL
    """
    if len(url) <= max_length:
        return url
        
    # 保留協議和域名部分
    parts = url.split("/")
    if len(parts) >= 3:  # 有協議和域名
        domain = "/".join(parts[:3])
        if len(domain) < max_length - 3:
            return domain + "/..."
    
    # 簡單截斷
    return url[:max_length-3] + "..."


def format_json_result(data: Union[Dict, List]) -> str:
    """格式化 JSON 結果
    
    Args:
        data: JSON 資料
    
    Returns:
        格式化後的 JSON 文本
    """
    try:
        return f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```"
    except:
        return f"```\n{str(data)}\n```"


def format_message(text: str, footer: str = None) -> str:
    """格式化通用消息文本
    
    Args:
        text: 主體文本
        footer: 可選的頁腳文本
        
    Returns:
        格式化後的消息文本，準備好使用 Markdown 解析
    """
    # 移除可能存在的多餘空行
    text = "\n".join(line for line in text.splitlines() if line.strip())
    
    if footer:
        # 添加分隔線和頁腳
        return f"{text}\n\n---\n{footer}"
    else:
        return text
