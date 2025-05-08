from typing import Dict, Any, Optional, Callable
from extractors.base_extractor import BaseNewsExtractor
from dateutil import parser

class NewsListExtractor(BaseNewsExtractor):
    def extract_news_item(
        self,
        element,
        selectors: Dict[str, str],
        base_url: Optional[str] = None,
        field_cleaners: Optional[Dict[str, Callable[[str], str]]] = None,
    ) -> Dict[str, Any]:
        item = self.extract_news_data(element, selectors, base_url)
        # summary 處理
        if "summary" in selectors:
            summary_el = element.query_selector(selectors["summary"])
            summary = summary_el.text_content().strip() if summary_el else ""
            if field_cleaners and "summary" in field_cleaners:
                summary = field_cleaners["summary"](summary)
            item["summary"] = summary
        # 日期格式標準化
        if "date" in selectors:
            date_el = element.query_selector(selectors["date"])
            date_str = date_el.text_content().strip() if date_el else ""
            if field_cleaners and "date" in field_cleaners:
                date_str = field_cleaners["date"](date_str)
            else:
                date_str = self.parse_date(date_str)
            item["date"] = date_str
        # URL 拼接與清理
        if "url" in selectors:
            url_el = element.query_selector(selectors["url"])
            url = url_el.get_attribute("href") if url_el else ""
            if url and base_url and url.startswith("/"):
                url = f"{base_url}{url}"
            if field_cleaners and "url" in field_cleaners:
                url = field_cleaners["url"](url)
            item["url"] = url
        return self.standardize_news_item(item)

    def parse_date(self, date_str: str) -> str:
        from dateutil import parser
        import re
        try:
            zh_date = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
            if zh_date:
                y, m, d = zh_date.groups()
                return f"{y}-{int(m):02d}-{int(d):02d}"
            date_str = date_str.replace("/", "-").replace("年", "-").replace("月", "-").replace("日", "")
            return parser.parse(date_str).isoformat()
        except Exception:
            return date_str

class NewsContentExtractor(BaseNewsExtractor):
    def extract_article_content(
        self,
        page,
        selectors: Dict[str, str],
        base_url: Optional[str] = None,
        field_cleaners: Optional[Dict[str, Callable[[str], str]]] = None,
    ) -> Dict[str, Any]:
        article = {}
        if "title" in selectors:
            el = page.query_selector(selectors["title"])
            title = el.text_content().strip() if el else ""
            if field_cleaners and "title" in field_cleaners:
                title = field_cleaners["title"](title)
            article["title"] = title
        if "date" in selectors:
            el = page.query_selector(selectors["date"])
            date_str = el.text_content().strip() if el else ""
            if field_cleaners and "date" in field_cleaners:
                date_str = field_cleaners["date"](date_str)
            else:
                date_str = self.parse_date(date_str)
            article["date"] = date_str
        if "author" in selectors:
            el = page.query_selector(selectors["author"])
            author = el.text_content().strip() if el else ""
            if field_cleaners and "author" in field_cleaners:
                author = field_cleaners["author"](author)
            article["author"] = author
        if "content" in selectors:
            content_els = page.query_selector_all(selectors["content"])
            paragraphs = [el.text_content().strip() for el in content_els if el]
            content = "\n".join(paragraphs)
            if field_cleaners and "content" in field_cleaners:
                content = field_cleaners["content"](content)
            article["content"] = content
        if "image" in selectors:
            el = page.query_selector(selectors["image"])
            image_url = el.get_attribute("src") if el else ""
            if image_url and base_url and image_url.startswith("/"):
                image_url = f"{base_url}{image_url}"
            if field_cleaners and "image" in field_cleaners:
                image_url = field_cleaners["image"](image_url)
            article["image"] = image_url
        return self.standardize_news_item(article)

    def parse_date(self, date_str: str) -> str:
        from dateutil import parser
        import re
        try:
            zh_date = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
            if zh_date:
                y, m, d = zh_date.groups()
                return f"{y}-{int(m):02d}-{int(d):02d}"
            date_str = date_str.replace("/", "-").replace("年", "-").replace("月", "-").replace("日", "")
            return parser.parse(date_str).isoformat()
        except Exception:
            return date_str
