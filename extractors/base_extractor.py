from typing import List, Dict, Any, Optional

class BaseNewsExtractor:
    def extract_news_list(self, page, list_selector: str, item_extract_fn) -> List[Dict[str, Any]]:
        news_list = []
        elements = page.query_selector_all(list_selector)
        for element in elements:
            news = item_extract_fn(element)
            if news:
                news_list.append(news)
        return news_list

    def extract_news_data(self, element, field_selectors: Dict[str, str], base_url: Optional[str] = None) -> Optional[Dict[str, Any]]:
        news = {}
        for field, selector in field_selectors.items():
            try:
                el = element.query_selector(selector)
                if el:
                    if field == "url":
                        url = el.get_attribute("href")
                        if url and base_url and url.startswith("/"):
                            url = f"{base_url}{url}"
                        news[field] = url
                    else:
                        news[field] = el.text_content().strip()
            except Exception:
                news[field] = ""
        return news

    def get_page_content(self, page) -> str:
        try:
            return page.content()
        except Exception:
            return ""

    def get_total_count(self, page, count_selector: str) -> int:
        try:
            el = page.query_selector(count_selector)
            if el:
                import re
                text = el.text_content().strip()
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
            return 0
        except Exception:
            return 0

    def standardize_news_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        將原始抓取結果轉為統一格式，並支援 meta_data 欄位
        """
        return {
            "title": item.get("title", ""),
            "date": item.get("date", ""),
            "url": item.get("url", ""),
            "summary": item.get("summary", ""),
            "content": item.get("content", ""),
            "image": item.get("image", ""),
            "author": item.get("author", ""),
            "source": item.get("source", ""),
            "retrieved_at": item.get("retrieved_at", ""),
            "meta_data": item.get("meta_data", {}),
        }
