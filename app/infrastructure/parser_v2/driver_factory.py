import asyncio
import gc
import psutil
from typing import Optional
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)


class DriverFactory:
    """
    Единый инстанс браузера на воркер.
    Для каждой задачи создаётся новый context и page.
    """

    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _lock = asyncio.Lock()

    def __init__(self, headless: bool = True):
        self.headless = headless
        self._context: Optional[BrowserContext] = None

    @classmethod
    async def init_browser(cls, headless: bool = True):
        async with cls._lock:
            if not cls._playwright:
                cls._playwright = await async_playwright().start()
            if not cls._browser:
                cls._browser = await cls._playwright.chromium.launch(
                    headless=False,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-software-rasterizer",
                        "--disable-extensions",
                        "--disable-background-networking",
                        "--disable-sync",
                        "--disable-translate",
                        "--disable-features=IsolateOrigins,site-per-process",
                        "--disable-blink-features=AutomationControlled",
                        "--window-size=1600,900",
                        "--js-flags=--expose-gc",
                        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
                        "--lang=ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    ],
                )

    async def create(self) -> Page:
        """Создаёт новый контекст и страницу в рамках уже существующего браузера."""
        await self.init_browser(self.headless)
        self._context = await self._browser.new_context(
            viewport={"width": 1600, "height": 900},
            record_har_path=None,
            record_video_dir=None,
            accept_downloads=False,
        )
        page = await self._context.new_page()

        async def route_handler(route):
            if route.request.resource_type in ["image", "media", "font"]:
                await route.abort()
            else:
                await route.continue_()

        try:
            await page.route("**/*", route_handler)
        except Exception:
            pass

        setattr(page, "_pw_factory", self)
        return page

    async def stop(self) -> None:
        try:
            if self._context:
                await self._context.clear_cookies()
                await self._context.close()
        except Exception:
            pass
        finally:
            gc.collect()
            self._context = None

    @classmethod
    async def shutdown_browser(cls):
        try:
            if cls._browser:
                try:
                    await cls._browser.close()
                except Exception:
                    pass

            if cls._playwright:
                try:
                    await cls._playwright.stop()
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            for proc in psutil.process_iter(["name", "cmdline"]):
                try:
                    name = proc.info.get("name") or ""
                    cmdline = proc.info.get("cmdline") or []
                    if "node" in name and "playwright" in " ".join(cmdline):
                        proc.kill()
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    continue
                except Exception:
                    continue

            cls._browser = None
            cls._playwright = None
            gc.collect()
