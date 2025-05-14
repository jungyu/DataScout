"""
爬蟲相關指令處理
"""

import logging
import time
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from telegram_bot.data.task_manager import TaskManager

logger = logging.getLogger(__name__)
task_manager = TaskManager()

async def crawl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /crawl 指令
    
    啟動爬蟲任務，格式: /crawl [URL] [選項]
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated crawl command")
    
    # 檢查參數
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ 請提供目標網址。\n"
            "用法: /crawl [網址] [選項]\n\n"
            "例如: /crawl https://example.com headless=true"
        )
        return
    
    # 解析參數
    target_url = context.args[0]
    options = {}
    
    # 解析選項 (格式: key=value)
    for arg in context.args[1:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
            options[key] = value
    
    # 建立任務
    try:
        # 檢查用戶任務數量上限
        user_tasks = task_manager.get_user_tasks(user.id)
        if len(user_tasks) >= task_manager.max_tasks_per_user:
            await update.message.reply_text(
                f"⚠️ 您已達到最大任務數量限制 ({task_manager.max_tasks_per_user})。\n"
                "請等待現有任務完成或使用 /cancel 取消任務。"
            )
            return
            
        # 創建任務
        task_id = task_manager.create_task(
            user_id=user.id,
            target_url=target_url,
            options=options
        )
        
        # 回應用戶
        await update.message.reply_text(
            f"✅ 已啟動爬蟲任務 (ID: `{task_id}`)\n"
            f"目標: `{target_url}`\n"
            f"選項: {', '.join([f'{k}={v}' for k, v in options.items()])} \n\n"
            f"使用 /status {task_id} 檢查任務狀態",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error creating crawl task: {str(e)}")
        await update.message.reply_text(f"❌ 建立任務失敗: {str(e)}")


async def schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /schedule 指令
    
    排程爬蟲任務，格式: /schedule [URL] [選項] [時間]
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated schedule command")
    
    # 檢查參數
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ 請提供目標網址和排程時間。\n"
            "用法: /schedule [網址] [選項] [時間]\n\n"
            "例如: /schedule https://example.com headless=true 2023-01-01T12:00"
        )
        return
    
    # 解析參數 (最後一個參數是時間)
    target_url = context.args[0]
    schedule_time = context.args[-1]
    
    # 解析選項 (中間的參數)
    options = {}
    for arg in context.args[1:-1]:
        if "=" in arg:
            key, value = arg.split("=", 1)
            options[key] = value
    
    # 建立排程任務
    try:
        task_id = task_manager.schedule_task(
            user_id=user.id,
            target_url=target_url,
            options=options,
            schedule_time=schedule_time
        )
        
        await update.message.reply_text(
            f"✅ 已排程爬蟲任務 (ID: `{task_id}`)\n"
            f"目標: `{target_url}`\n"
            f"排程時間: {schedule_time}\n"
            f"選項: {', '.join([f'{k}={v}' for k, v in options.items()])} \n\n"
            f"使用 /status {task_id} 檢查任務狀態",
            parse_mode="Markdown"
        )
        
    except ValueError as e:
        await update.message.reply_text(f"❌ 排程格式錯誤: {str(e)}")
    except Exception as e:
        logger.error(f"Error scheduling task: {str(e)}")
        await update.message.reply_text(f"❌ 建立排程任務失敗: {str(e)}")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /cancel 指令
    
    取消爬蟲任務，格式: /cancel [任務ID]
    """
    user = update.effective_user
    logger.info(f"User {user.id} initiated cancel command")
    
    # 檢查參數
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ 請提供任務ID。\n"
            "用法: /cancel [任務ID]"
        )
        return
    
    task_id = context.args[0]
    
    # 取消任務
    try:
        result = task_manager.cancel_task(task_id, user.id)
        if result:
            await update.message.reply_text(f"✅ 任務 {task_id} 已取消")
        else:
            await update.message.reply_text(
                f"❌ 無法取消任務 {task_id}。可能任務不存在或您沒有權限。"
            )
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        await update.message.reply_text(f"❌ 取消任務失敗: {str(e)}")


def register_crawl_commands(application):
    """註冊爬蟲相關指令"""
    application.add_handler(CommandHandler("crawl", crawl))
    application.add_handler(CommandHandler("schedule", schedule))
    application.add_handler(CommandHandler("cancel", cancel))
