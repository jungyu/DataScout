"""
管理員指令處理
"""

import logging
import json
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram_bot.data.task_manager import TaskManager
from telegram_bot.config import ADMIN_USER_IDS
from telegram_bot.utils.formatters import format_task_list

logger = logging.getLogger(__name__)
task_manager = TaskManager()

async def system_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /system 指令
    
    顯示系統狀態，僅限管理員使用
    """
    user = update.effective_user
    
    # 檢查是否為管理員
    if user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⚠️ 此指令僅限管理員使用。")
        return
    
    logger.info(f"Admin {user.id} requested system status")
    
    # 獲取系統狀態
    status = task_manager.get_system_status()
    
    status_text = (
        "🖥️ *系統狀態*\n\n"
        f"活躍任務數: {status['active_tasks']}\n"
        f"排程任務數: {status['scheduled_tasks']}\n"
        f"已完成任務數: {status['completed_tasks']}\n"
        f"失敗任務數: {status['failed_tasks']}\n"
        f"CPU 使用率: {status['cpu_usage']}%\n"
        f"記憶體使用率: {status['memory_usage']}%\n"
        f"系統運行時間: {status['uptime']}\n"
    )
    
    await update.message.reply_text(status_text, parse_mode="Markdown")


async def all_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /alltasks 指令
    
    列出所有用戶的任務，僅限管理員使用
    """
    user = update.effective_user
    
    # 檢查是否為管理員
    if user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⚠️ 此指令僅限管理員使用。")
        return
    
    logger.info(f"Admin {user.id} requested all tasks")
    
    # 獲取所有任務
    all_tasks = task_manager.get_all_tasks()
    
    if not all_tasks:
        await update.message.reply_text("📝 目前沒有任何任務。")
        return
    
    # 按狀態分類任務
    active_tasks = [t for t in all_tasks if t["status"] in ("pending", "running")]
    completed_tasks = [t for t in all_tasks if t["status"] == "completed"]
    failed_tasks = [t for t in all_tasks if t["status"] in ("failed", "cancelled")]
    
    # 發送活躍任務
    if active_tasks:
        tasks_text = format_task_list(active_tasks, "活躍任務")
        await update.message.reply_text(tasks_text, parse_mode="Markdown")
    else:
        await update.message.reply_text("📝 目前沒有活躍任務。")
    
    # 發送最近完成的任務 (最多5個)
    if completed_tasks:
        completed_tasks.sort(key=lambda x: x.get("end_time", ""), reverse=True)
        recent_completed = completed_tasks[:5]
        tasks_text = format_task_list(recent_completed, "最近完成的任務")
        await update.message.reply_text(tasks_text, parse_mode="Markdown")
    
    # 發送最近失敗的任務 (最多5個)
    if failed_tasks:
        failed_tasks.sort(key=lambda x: x.get("end_time", ""), reverse=True)
        recent_failed = failed_tasks[:5]
        tasks_text = format_task_list(recent_failed, "最近失敗的任務")
        await update.message.reply_text(tasks_text, parse_mode="Markdown")


async def kill_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """處理 /kill 指令
    
    強制終止任務，僅限管理員使用
    格式: /kill [任務ID]
    """
    user = update.effective_user
    
    # 檢查是否為管理員
    if user.id not in ADMIN_USER_IDS:
        await update.message.reply_text("⚠️ 此指令僅限管理員使用。")
        return
    
    # 檢查參數
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ 請提供任務ID。\n"
            "用法: /kill [任務ID]"
        )
        return
    
    task_id = context.args[0]
    logger.info(f"Admin {user.id} attempting to kill task {task_id}")
    
    # 強制終止任務
    try:
        result = task_manager.kill_task(task_id)
        if result:
            await update.message.reply_text(f"✅ 任務 {task_id} 已強制終止")
        else:
            await update.message.reply_text(f"❌ 無法終止任務 {task_id}。任務可能不存在。")
    except Exception as e:
        logger.error(f"Error killing task: {str(e)}")
        await update.message.reply_text(f"❌ 終止任務失敗: {str(e)}")


def register_admin_commands(application):
    """註冊管理員指令"""
    application.add_handler(CommandHandler("system", system_status))
    application.add_handler(CommandHandler("alltasks", all_tasks))
    application.add_handler(CommandHandler("kill", kill_task))
