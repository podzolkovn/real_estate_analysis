import asyncio
from typing import Any, Dict, List
from playwright.async_api import Page

from app.core import logger
from app.infrastructure.parser_v2.driver_factory import DriverFactory


class StartParser:
    BASE_URL = (
        "https://krisha.kz/prodazha/kvartiry/almaty/?das[_sys.hasphoto]=1&sort_by=price-asc"
    )

    def __init__(self, headless: bool = True, delay: int = 10):
        self.headless = headless
        self.delay = delay

    async def run(self):
        factory = DriverFactory(headless=self.headless)
        page = await factory.create()
        try:

            await page.goto(self.BASE_URL, timeout=60000)

            max_page = await self._get_max_page(page)
            logger.info(f"Найдено страниц: {max_page}")

            results: List[Dict[str, Any]] = []

            for page_num in range(1, max_page + 1):
                url = f"{self.BASE_URL}&page={page_num}"
                logger.info(f"Парсим страницу: {url}")

                await page.goto(url, timeout=60000)
                await page.wait_for_timeout(2000)

                items = await self._parse_page(page)
                results.extend(items)

                logger.info(f"Страница {page_num} — собрано объявлений: {len(items)}")

                if page_num < max_page:
                    await asyncio.sleep(self.delay)

            return results
        except Exception as e:
            logger.exception("Неожиданная ошибка парсера Kompas")
        finally:
            try:
                await self.close(page)
            except Exception:
                pass
            try:
                await factory.stop()
            except Exception:
                pass
            await asyncio.sleep(0.2)

    @staticmethod
    def _normalize_price(text: str) -> float | None:
        if not text:
            return None

        text = text.lower().replace("₸", "").replace("〒", "").replace("\xa0", "").strip()

        if text.startswith("от "):
            text = text.replace("от ", "").strip()

        if not text.replace(" ", "").isdigit():
            return None

        return float(text.replace(" ", ""))

    @staticmethod
    async def _get_max_page(page: Page) -> int:
        try:
            elems = await page.locator("nav.paginator a.paginator__btn").all()

            pages = []
            for el in elems:
                num = await el.get_attribute("data-page")
                if num and num.isdigit():
                    pages.append(int(num))

            return max(pages) if pages else 1
        except Exception:
            return 1

    async def _parse_page(self, page: Page) -> List[Dict[str, Any]]:
        container = page.locator(
            "body > main > section.a-search-container.main-cols-container "
            "> div > section.a-list.a-search-list.a-list-with-favs"
        )

        cards = container.locator("div.a-card")
        count = await cards.count()

        result = []

        for i in range(count):
            try:
                card = cards.nth(i)
                data = await self._parse_card(card)
                result.append(data)
            except Exception as e:
                logger.info("Ошибка при парсинге карточки:", e)

        return result

    async def _parse_card(self, card) -> Dict[str, Any]:

        title = await card.locator(".a-card__title").inner_text()

        rooms = None
        sq = None

        try:
            parts = title.split("·")
            if len(parts) >= 2:
                rooms_part = parts[0].strip()
                sq_part = parts[1].strip()

                rooms = rooms_part.split("-")[0].replace("комнатная", "").strip()
                sq = sq_part.replace("м²", "").strip()
        except Exception:
            pass

        raw_price = await card.locator(".a-card__price").inner_text()
        price = self._normalize_price(raw_price)

        if price and sq:
            price_per_m = round(float(price) / float(sq), 2)
        else:
            price_per_m = None

        region = await card.locator(".a-card__subtitle").inner_text()
        region = region.strip().split(",")[0]

        views = None
        try:
            views = await card.locator(".a-view-count").inner_text()
        except Exception:
            pass

        owner_type = "Не указано"
        try:
            owner_block = await card.locator(".a-card__owner-label").inner_text()
            owner_type = owner_block.strip()
        except Exception:
            pass

        return {
            "rooms": rooms,
            "area": sq,
            "price": price,
            "price_per_area_metr": price_per_m,
            "region": region,
            "views": views,
            "complex_Label": owner_type,
        }

    @staticmethod
    async def close(page) -> None:
        try:
            ctx = getattr(page, "context", None)
            if ctx:
                try:
                    await ctx.close()
                except Exception:
                    pass
        except Exception:
            pass