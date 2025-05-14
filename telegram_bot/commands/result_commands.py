"""
結果處理相關指令
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from telegram_bot.data.task_manager import TaskManager
from telegram_bot.config import DEFAULT_EXPORT_FORMAT, AVAILABLE_EXPORT_FORMATS
from telegram_bot.utils.formatters import format_json_result

logger = logging.getLogger(__name__)
task_manager = TaskManager()

async def result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /result 指令
    
    獲取任務結果，格式: /result [任務ID]
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested task result")
    
    # 檢查參數
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ 請提供任務ID。\n"
            "用法: /result [任務ID]"
        )
        return
    
    task_id = context.args[0]
    
    # 獲取任務狀態
    task = task_manager.get_task_status(task_id)
    if not task:
        await update.message.reply_text(f"❌ 找不到任務ID: {task_id}")
        return
        
    # 檢查任務是否完成
    if task["status"] != "completed":
        status_msg = {
            "pending": "任務正在等待處理。",
            "running": "任務正在執行中。",
            "failed": "任務已失敗。",
            "cancelled": "任務已被取消。",
            "scheduled": "任務已排程但尚未執行。"
        }.get(task["status"], "任務狀態未知。")
        
        await update.message.reply_text(
            f"⚠️ 無法獲取結果。{status_msg}\n"
            f"當前狀態: {task['status']}"
        )
        return
    
    # 獲取任務結果
    result_data = task_manager.get_task_result(task_id, user.id)
    if not result_data:
        await update.message.reply_text(
            "❌ 無法獲取任務結果。可能是結果不存在或您沒有權限。"
        )
        return
    
    # 格式化結果
    formatted_result = format_json_result(result_data)
    
    # 創建結果查看按鈕
    keyboard = [
        [
            InlineKeyboardButton("JSON 格式", callback_data=f"format:{task_id}:json"),
            InlineKeyboardButton("表格檢視", callback_data=f"format:{task_id}:table")
        ],
        [
            InlineKeyboardButton("匯出 CSV", callback_data=f"export:{task_id}:csv"),
            InlineKeyboardButton("匯出 Excel", callback_data=f"export:{task_id}:excel")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # 發送結果
    await update.message.reply_text(
        f"✅ 任務 {task_id} 結果:\n\n{formatted_result}",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /export 指令
    
    匯出任務結果，格式: /export [任務ID] [格式]
    支援的格式: json, csv, excel
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested task export")
    
    # 檢查參數
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ 請提供任務ID和格式。\n"
            "用法: /export [任務ID] [格式]\n"
            f"支援的格式: {', '.join(AVAILABLE_EXPORT_FORMATS)}"
        )
        return
    
    # 解析參數
    task_id = context.args[0]
    export_format = context.args[1] if len(context.args) > 1 else DEFAULT_EXPORT_FORMAT
    
    # 檢查格式是否支援
    if export_format not in AVAILABLE_EXPORT_FORMATS:
        await update.message.reply_text(
            f"⚠️ 不支援的匯出格式: {export_format}\n"
            f"支援的格式: {', '.join(AVAILABLE_EXPORT_FORMATS)}"
        )
        return
    
    # 匯出任務結果
    export_path = task_manager.export_task_result(task_id, user.id, export_format)
    if not export_path:
        await update.message.reply_text(
            "❌ 無法匯出任務結果。可能是結果不存在、任務未完成或您沒有權限。"
        )
        return
    
    # 發送匯出結果
    await update.message.reply_text(
        f"✅ 任務 {task_id} 已匯出為 {export_format} 格式。\n\n"
        f"檔案路徑: `{export_path}`",
        parse_mode="Markdown"
    )
    
    # 發送檔案 (如果檔案存在)
    if os.path.exists(export_path):
        with open(export_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=f"task_{task_id}.{export_format}",
                caption=f"任務 {task_id} 的 {export_format} 匯出檔案"
            )


def register_result_commands(application):
    """註冊結果處理相關指令"""
    application.add_handler(CommandHandler("result", result))
    application.add_handler(CommandHandler("export", export))
