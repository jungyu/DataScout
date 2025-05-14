"""
圖像處理模組

處理圖像上傳和分析請求
"""

import os
import logging
import tempfile
from typing import Optional, Union
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from telegram_bot.utils.gemini_client import GeminiClient
from telegram_bot.utils.formatters import format_message

logger = logging.getLogger(__name__)

# 緩存 Gemini 客戶端實例
_gemini_client = None

def get_gemini_client() -> GeminiClient:
    """
    使用懶加載模式獲取 Gemini 客戶端實例
    
    Returns:
        GeminiClient: Gemini API 客戶端實例
    """
    global _gemini_client
    
    if _gemini_client is None:
        _gemini_client = GeminiClient()
        
    return _gemini_client

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理用戶上傳的圖片
    
    Args:
        update: Telegram 更新對象
        context: 回調上下文
    """
    user = update.effective_user
    logger.info(f"用戶 {user.id} 發送了一張圖片")
    
    # 檢查用戶是否有權限使用圖像功能
    from telegram_bot.config import REQUIRE_AUTH, AUTHORIZED_USERS, ADMIN_USER_IDS
    if REQUIRE_AUTH and user.id not in AUTHORIZED_USERS and user.id not in ADMIN_USER_IDS:
        await update.message.reply_text(
            "⚠️ 您沒有權限使用圖像分析功能。請聯繫管理員獲取授權。",
            parse_mode=None
        )
        logger.warning(f"未授權用戶 {user.id} 嘗試使用圖像分析功能")
        return
    
    # 發送處理中的消息
    processing_message = await update.message.reply_text(
        "📸 正在處理圖片，請稍候..."
    )
    
    try:
        # 檢查是否為照片或文件
        is_photo = bool(update.message.photo)
        is_document = bool(update.message.document and 
                         update.message.document.mime_type in 
                         ["image/jpeg", "image/png", "image/webp"])
        
        if not (is_photo or is_document):
            await processing_message.edit_text(
                "❌ 只支持 JPEG、PNG 和 WebP 格式的圖片"
            )
            return
            
        # 獲取文件 ID
        if is_photo:
            # 對於照片，選擇最高解析度的版本
            file_id = update.message.photo[-1].file_id
        else:
            # 對於文檔，直接獲取文件 ID
            file_id = update.message.document.file_id
            
        # 獲取文件對象
        file = await context.bot.get_file(file_id)
        
        # 創建臨時文件
        suffix = Path(file.file_path).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp_path = temp.name
        
        # 下載文件到臨時路徑
        await file.download_to_drive(temp_path)
        
        try:
            # 獲取用戶的自定義提示詞（如果有）
            custom_prompt = update.message.caption if update.message.caption else None
            
            # 預設提示詞
            default_prompt = (
                "請詳細描述這張圖片中的內容，"
                "包括可見的物體、場景、文字和其他重要元素。"
                "如果有文字內容，請完整提取出來。"
                "如果是表格或結構化內容，請整理成易讀的格式。"
            )
            
            prompt = custom_prompt if custom_prompt else default_prompt
            
            # 使用 Gemini API 分析圖片
            client = get_gemini_client()
            analysis_result = await client.analyze_image(temp_path, prompt)
            
            # 創建短 ID 用於按鈕回調
            short_id = hash(file_id) % 10000000  # 建立一個較短的數字 ID
            
            # 存儲在 context.bot_data 中，以便後續使用
            if "file_id_map" not in context.bot_data:
                context.bot_data["file_id_map"] = {}
            context.bot_data["file_id_map"][short_id] = file_id
                
            keyboard = [
                [
                    InlineKeyboardButton("詳細分析", callback_data=f"img_detail:{short_id}"),
                    InlineKeyboardButton("提取文字", callback_data=f"img_text:{short_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # 處理分析結果，使用純文本格式避免解析問題
            header = "🖼 圖像分析結果"
            if custom_prompt:
                header = f"📝 提示詞：「{custom_prompt}」\n\n{header}"
            
            # 使用純文本
            text_response = f"{header}\n\n{analysis_result}"
            
            # 發送分析結果
            await processing_message.edit_text(
                text_response,
                parse_mode=None,  # 不使用解析器
                reply_markup=reply_markup
            )
            
        finally:
            # 清理臨時文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                logger.debug(f"已刪除臨時文件: {temp_path}")
                
    except Exception as e:
        logger.error(f"處理圖片時發生錯誤: {str(e)}", exc_info=True)
        try:
            # 使用安全的方式顯示錯誤訊息
            error_message = str(e)
            if len(error_message) > 200:
                error_message = error_message[:200] + "..."
                
            # 避免 Markdown 特殊字符
            error_message = error_message.replace("*", "\\*").replace("_", "\\_").replace("`", "\\`")
            
            await processing_message.edit_text(
                f"❌ 處理圖片時發生錯誤:\n{error_message}",
                parse_mode=None  # 不使用 Markdown 解析，避免錯誤
            )
        except Exception as edit_error:
            logger.error(f"更新錯誤訊息時發生問題: {str(edit_error)}", exc_info=True)


async def image_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理 /image 指令，提供圖像處理功能的說明
    
    Args:
        update: Telegram 更新對象
        context: 回調上下文
    """
    # 檢查用戶是否有權限使用圖像功能
    user = update.effective_user
    from telegram_bot.config import REQUIRE_AUTH, AUTHORIZED_USERS, ADMIN_USER_IDS
    
    if REQUIRE_AUTH and user.id not in AUTHORIZED_USERS and user.id not in ADMIN_USER_IDS:
        await update.message.reply_text(
            "⚠️ 您沒有權限使用圖像分析功能。請聯繫管理員獲取授權。",
            parse_mode=None
        )
        logger.warning(f"未授權用戶 {user.id} 嘗試查看圖像分析說明")
        return
    
    # 使用純文本格式，避免 HTML/Markdown 解析問題
    help_text = (
        "📸 圖像分析功能使用說明\n\n"
        "您可以發送圖片給我，我將使用 Google Gemini AI 分析圖片內容。\n\n"
        "支援的格式：\n"
        "- JPEG/JPG\n"
        "- PNG\n"
        "- WebP\n\n"
        "使用方法：\n"
        "1. 直接發送或分享圖片\n"
        "2. 可選：添加圖片說明作為自定義提示詞\n\n"
        "互動功能：\n"
        "- 詳細分析：獲取圖片的深度分析\n"
        "- 提取文字：識別並提取圖片中的文字內容\n\n"
        "範例：\n"
        "- 發送圖片並添加說明「辨識這張收據上的金額」\n"
        "- 發送圖片並添加說明「這張圖中有什麼問題？」\n\n"
        "提示：\n"
        "- 圖片質量越高，分析結果越準確\n"
        "- 文字辨識效果取決於文字清晰度\n"
        "- 使用自定義提示詞可以獲得更針對性的分析"
    )
    
    await update.message.reply_text(help_text, parse_mode=None)


async def handle_image_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    處理圖片按鈕的回調
    
    Args:
        update: Telegram 更新對象
        context: 回調上下文
    """
    query = update.callback_query
    await query.answer()
    
    # 解析回調數據
    data = query.data.split(":")
    action = data[0]
    short_id = int(data[1])
    
    # 從 context.bot_data 獲取完整文件 ID
    if "file_id_map" not in context.bot_data or short_id not in context.bot_data["file_id_map"]:
        await query.edit_message_text(
            f"{query.message.text}\n\n❌ 無效的圖片引用，請重新發送圖片",
            parse_mode=None
        )
        return
    
    file_id = context.bot_data["file_id_map"][short_id]
    
    # 發送處理中的消息
    await query.edit_message_text(
        f"{query.message.text}\n\n⏳ 正在處理請求...",
        parse_mode=None
    )
    
    try:
        # 獲取文件
        file = await context.bot.get_file(file_id)
        
        # 創建臨時文件
        suffix = Path(file.file_path).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            temp_path = temp.name
        
        # 下載文件
        await file.download_to_drive(temp_path)
        
        try:
            client = get_gemini_client()
            
            if action == "img_detail":
                # 詳細分析
                prompt = (
                    "請對這張圖片進行極其詳細的分析，包括：\n"
                    "1. 主要物體和人物\n"
                    "2. 場景和環境描述\n"
                    "3. 色彩和光線特點\n"
                    "4. 可能的拍攝意圖\n"
                    "5. 任何特殊或不尋常的元素"
                )
                
                result = await client.analyze_image(temp_path, prompt)
                
                # 構建純文本響應
                original_text = query.message.text.split("\n\n")[0]
                response_text = f"{original_text}\n\n📋 詳細分析結果\n\n{result}"
                
            elif action == "img_text":
                # 提取文字
                prompt = (
                    "請提取並轉錄這張圖片中的所有文字內容。"
                    "如果是表格，請保持其格式結構。"
                    "如果沒有文字，請明確說明。"
                )
                
                result = await client.analyze_image(temp_path, prompt)
                
                # 構建純文本響應
                original_text = query.message.text.split("\n\n")[0]
                response_text = f"{original_text}\n\n📝 文字提取結果\n\n{result}"
                
            else:
                response_text = f"{query.message.text}\n\n❌ 未知操作"
                
            # 更新消息
            await query.edit_message_text(
                response_text,
                parse_mode=None
            )
            
        finally:
            # 清理臨時文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        logger.error(f"處理圖片回調時發生錯誤: {str(e)}", exc_info=True)
        try:
            # 使用安全的方式顯示錯誤訊息
            error_message = str(e)
            if len(error_message) > 200:
                error_message = error_message[:200] + "..."
                
            # 保留原始訊息的前部分，添加錯誤訊息
            original_text = query.message.text.split("\n\n")[0]
            await query.edit_message_text(
                f"{original_text}\n\n❌ 處理請求時發生錯誤:\n{error_message}",
                parse_mode=None  # 不使用解析器，避免錯誤
            )
        except Exception as edit_error:
            logger.error(f"更新錯誤訊息時發生問題: {str(edit_error)}", exc_info=True)
