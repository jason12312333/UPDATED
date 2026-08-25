"""FastAPI application factory and lifespan management."""

from __future__ import annotations

import logging
import os
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from easy_tdx.web.errors import register_exception_handlers

logger = logging.getLogger(__name__)


def _resolve_web_dist_dir() -> Path | None:
    """定位前端构建产物目录（Vite build 输出的 ``web-ui/dist``）。"""
    env_dir = os.environ.get("EASY_TDX_WEB_DIST")
    if env_dir:
        p = Path(env_dir)
        if p.is_dir():
            return p

    meipass = getattr(sys, "_MEIPASS", None)
    if meipass is not None:
        p = Path(meipass) / "web_dist"
        if p.is_dir():
            return p

    repo_root = Path(__file__).resolve().parents[3]
    p = repo_root / "web-ui" / "dist"
    if p.is_dir():
        return p

    pkg_dist = Path(__file__).resolve().parent / "dist"
    if pkg_dist.is_dir():
        return pkg_dist
    return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """管理标准 TDX、MAC 与扩展市场连接生命周期。"""
    from easy_tdx.client import AsyncTdxClient

    host = app.state.tdx_host
    port = app.state.tdx_port
    timeout = app.state.tdx_timeout

    client = AsyncTdxClient(host=host, port=port, timeout=timeout)
    try:
        await client.connect()
        logger.info("TDX client connected to %s:%s", host, port)
    except Exception:
        logger.warning("TDX client connection failed — endpoints will return 503")
    app.state.tdx_client = client

    mac_client = None
    if getattr(app.state, "enable_mac", True):
        try:
            from easy_tdx.mac.client import AsyncMacClient

            mac_client = AsyncMacClient.from_best_host()
            await mac_client.connect()
            logger.info("MAC client connected")
        except Exception:
            logger.warning("MAC client connection failed — MAC endpoints will return 503")
    app.state.mac_client = mac_client

    ex_client = None
    if getattr(app.state, "enable_ex", True):
        try:
            from easy_tdx.ex.client import AsyncExTdxClient

            ex_client = AsyncExTdxClient.from_best_host()
            await ex_client.connect()
            logger.info("Ex market client connected")
        except Exception:
            logger.warning("Ex market client connection failed — Ex endpoints will return 503")
    app.state.ex_client = ex_client

    yield

    for name, cli in [
        ("Ex market client", ex_client),
        ("MAC client", mac_client),
        ("TDX client", client),
    ]:
        if cli is not None:
            try:
                await cli.close()
                logger.info("%s disconnected", name)
            except Exception:
                pass

    import asyncio

    try:
        from easy_tdx.web.task_runner import shutdown_runner

        await asyncio.to_thread(shutdown_runner)
        logger.info("Backtest task runner shutdown")
    except Exception:
        logger.warning("Backtest task runner shutdown failed", exc_info=True)


def _create_app(
    host: str | None = None,
    port: int | None = None,
    timeout: float | None = None,
    *,
    enable_mac: bool = True,
    enable_ex: bool = True,
) -> FastAPI:
    """创建并配置 FastAPI 应用实例。"""
    from easy_tdx.config import get_best_host, get_port, get_timeout

    if host is None:
        host = get_best_host()
    if port is None:
        port = get_port()
    if timeout is None:
        timeout = get_timeout()

    app = FastAPI(
        title="easy-tdx API",
        description="通达信行情数据 REST + WebSocket API",
        version="1.0.0",
        lifespan=lifespan,
        redoc_url=None,
    )

    from fastapi.openapi.docs import get_redoc_html

    @app.get("/redoc", include_in_schema=False)
    async def redoc_html() -> Any:
        return get_redoc_html(
            openapi_url=app.openapi_url or "/openapi.json",
            title=app.title + " - ReDoc",
            redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@2.2.0/bundles/redoc.standalone.js",
        )

    app.state.tdx_host = host
    app.state.tdx_port = port
    app.state.tdx_timeout = timeout
    app.state.tdx_client = None
    app.state.mac_client = None
    app.state.ex_client = None
    app.state.enable_mac = enable_mac
    app.state.enable_ex = enable_ex

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)

    from easy_tdx.web.routers.announcement import router as announcement_router
    from easy_tdx.web.routers.backtest import router as backtest_router
    from easy_tdx.web.routers.bars import router as bars_router
    from easy_tdx.web.routers.block import router as block_router
    from easy_tdx.web.routers.board_mac import router as board_mac_router
    from easy_tdx.web.routers.chanlun import router as chanlun_router
    from easy_tdx.web.routers.ex_market import router as ex_market_router
    from easy_tdx.web.routers.finance import router as finance_router
    from easy_tdx.web.routers.indicator import router as indicator_router
    from easy_tdx.web.routers.mac_data import router as mac_data_router
    from easy_tdx.web.routers.mac_quotes import router as mac_quotes_router
    from easy_tdx.web.routers.market import router as market_router
    from easy_tdx.web.routers.offline import router as offline_router
    from easy_tdx.web.routers.realtime import router as realtime_router
    from easy_tdx.web.routers.server import router as server_router
    from easy_tdx.web.routers.sina import router as sina_router
    from easy_tdx.web.routers.strategies import router as strategies_router

    for router in [
        market_router,
        bars_router,
        finance_router,
        block_router,
        chanlun_router,
        realtime_router,
        board_mac_router,
        mac_data_router,
        mac_quotes_router,
        ex_market_router,
        indicator_router,
        announcement_router,
        sina_router,
        backtest_router,
        strategies_router,
        server_router,
        offline_router,
    ]:
        app.include_router(router, prefix="/api/v1")

    import mimetypes

    mimetypes.add_type("application/javascript", ".js")
    mimetypes.add_type("application/javascript", ".mjs")
    mimetypes.add_type("text/css", ".css")
    mimetypes.add_type("image/svg+xml", ".svg")

    from fastapi.staticfiles import StaticFiles

    dist_dir = _resolve_web_dist_dir()
    if dist_dir is not None:
        from pathlib import Path as _Path

        from starlette.responses import FileResponse

        class SPAStaticFiles(StaticFiles):
            """StaticFiles + SPA fallback：404 时返回 index.html。"""

            async def get_response(self, path: str, scope):  # type: ignore[no-untyped-def]
                try:
                    return await super().get_response(path, scope)
                except Exception:
                    index = _Path(str(self.directory)) / "index.html"
                    if index.is_file():
                        return FileResponse(str(index))
                    raise

        app.mount("/", SPAStaticFiles(directory=str(dist_dir), html=True), name="web-ui")
        logger.info("Web UI mounted from %s (SPA fallback enabled)", dist_dir)
    else:
        logger.info("Web UI dist not found — serving API only")

    return app
