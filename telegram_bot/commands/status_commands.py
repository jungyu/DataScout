"""
狀態查詢相關指令處理
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram_bot.data.task_manager import TaskManager
from telegram_bot.utils.formatters import format_task_status, format_task_list

logger = logging.getLogger(__name__)
task_manager = TaskManager()

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /status 指令
    
    查詢爬蟲任務狀態，格式: /status [任務ID]
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested task status")
    
    # 檢查參數
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ 請提供任務ID。\n"
            "用法: /status [任務ID]"
        )
        return
    
    task_id = context.args[0]
    task_status = task_manager.get_task_status(task_id)
    
    # 檢查任務是否存在
    if not task_status:
        await update.message.reply_text(f"❌ 找不到任務ID: {task_id}")
        return
    
    # 檢查是否為該用戶的任務
    if task_status.get("user_id") != user.id:
        # 檢查是否為管理員
        if not task_manager.is_admin(user.id):
            await update.message.reply_text("⚠️ 您沒有權限查看此任務。")
            return
    
    # 格式化任務狀態
    status_text = format_task_status(task_status)
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /list 指令
    
    列出用戶所有進行中的任務
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested task list")
    
    # 獲取用戶任務
    user_tasks = task_manager.get_user_tasks(user.id)
    
    if not user_tasks:
        await update.message.reply_text("📝 您目前沒有進行中的任務。")
        return
    
    # 過濾活躍任務
    active_tasks = [task for task in user_tasks 
                   if task["status"] not in ("completed", "failed", "cancelled")]
    
    # 格式化任務列表
    if active_tasks:
        tasks_text = format_task_list(active_tasks, "進行中的任務")
        await update.message.reply_text(tasks_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("📝 您目前沒有進行中的任務。")


async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /history 指令
    
    顯示用戶的歷史任務記錄
    """
    user = update.effective_user
    logger.info(f"User {user.id} requested task history")
    
    # 獲取用戶任務歷史
    user_tasks = task_manager.get_user_tasks(user.id)
    
    if not user_tasks:
        await update.message.reply_text("📝 您沒有任務記錄。")
        return
    
    # 過濾已完成、失敗或取消的任務
    finished_tasks = [task for task in user_tasks 
                     if task["status"] in ("completed", "failed", "cancelled")]
    
    # 根據時間排序 (最新的在前)
    finished_tasks.sort(key=lambda x: x.get("end_time", ""), reverse=True)
    
    # 格式化任務列表
    if finished_tasks:
        # 限制顯示最近10個任務
        recent_tasks = finished_tasks[:10]
        tasks_text = format_task_list(recent_tasks, "最近的任務")
        await update.message.reply_text(tasks_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("📝 您沒有已完成的任務。")


def register_status_commands(application):
    """註冊狀態查詢相關指令"""
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("history", history))
