# config/nikkei_config.py
# -*- coding: utf-8 -*-
"""
Nikkei Asia 站點專用設定與選擇器
"""
from typing import Dict, Any

SITE_CONFIG: Dict[str, Any] = {
    "base_url": "https://asia.nikkei.com",
    "search_url": "https://asia.nikkei.com/search",
    "save_path": "../data",
    "request": {
        "timeout": 60000,
    },
    "max_pages": 1,
    "scroll": {
        "enabled": True,
        "max_scrolls": 6,
        "scroll_delay": 1.2,
        "scroll_distance": 600,
        "wait_for_selector": ".article-card-list__item",
    },
    "pagination": {
        "next_button_selector": ".pagination__next",
        "max_pages": 5,
    },
    "browser": {
        "headless": False,
        "browser_type": "chromium",
        "launch_options": {
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
            ]
        },
        "context_options": {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            ),
            "is_mobile": False,
            "locale": "en-US",
            "timezone_id": "America/New_York",
            "accept_downloads": True,
            "ignore_https_errors": True,
            "has_touch": False,
        },
    },
}

SELECTORS: Dict[str, Any] = {
    "search": {
        "list_item": ".article-card-list__item",
        "title": ".article-card__headline",
        "date": ".article-card__date",
        "summary": ".article-card__summary",
        "url": ".article-card__headline a",
        "count": ".title__search-result",
    },
    "next_page": ".pagination__next",
    "article": {
        "title": "h1.article-header__title",
        "date": ".article-header__date",
        "author": ".article-header__author",
        "content": ".ezrichtext-field p",
        "image": ".article-header__image img",
    },
    "paywall": {
        "login_button": ".login-link",
        "paywall": ".piano-container",
        "cookie_banner": ".cookie-consent, .cookie-banner",
        "cookie_accept": (
            ".cookie-banner__button[data-acceptance-button], "
            ".btn.btn--white-fill.cookie-banner__button"
        ),
        "cookie_close": (
            ".cookie-banner__link--close[data-close-button], "
            ".cookie-banner__link.cookie-banner__link--close"
        ),
        "subscription_banner": ".subscription-prompt",
        "close_button": ".close-button",
    },
}
