"""本地通达信离线数据 Web 路由。"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from easy_tdx.web.schemas import DataFrameResponse

router = APIRouter(tags=["offline"])


def _clean_record(obj: Any) -> dict[str, Any]:
    if hasattr(obj, "__dataclass_fields__"):
        row = asdict(obj)
    elif isinstance(obj, dict):
        row = dict(obj)
    else:
        row = dict(vars(obj))
    return {k: v for k, v in row.items() if not k.startswith("_")}


@router.get("/offline/status")
async def offline_status(
    vipdoc: str | None = Query(None, description="可选：显式指定 vipdoc 目录"),
) -> dict[str, Any]:
    """检测本机通达信目录与 vipdoc 是否可用。"""
    from easy_tdx.offline import detect_tdx_home, resolve_vipdoc

    home = detect_tdx_home()
    result: dict[str, Any] = {
        "tdx_home": str(home) if home else None,
        "auto_detected": home is not None,
        "vipdoc": None,
        "vipdoc_exists": False,
    }
    try:
        vp = resolve_vipdoc(vipdoc)
        result["vipdoc"] = str(vp)
        result["vipdoc_exists"] = vp.is_dir()
    except Exception as exc:
        result["error"] = str(exc)
    return result


@router.get("/offline/daily", response_model=DataFrameResponse)
async def offline_daily(
    market: str = Query(..., pattern=r"^(SZ|SH)$"),
    code: str = Query(..., min_length=6, max_length=6),
    vipdoc: str | None = Query(None, description="可选：显式指定 vipdoc 目录"),
    count: int = Query(500, ge=1, le=5000),
) -> DataFrameResponse:
    """直接读取本地通达信 .day 日线文件。"""
    from easy_tdx.offline import find_daily_bar_file, read_daily_bars

    try:
        market_value = 1 if market == "SH" else 0
        path = find_daily_bar_file(market_value, code, vipdoc=vipdoc)
        records = read_daily_bars(path)
        rows = []
        for bar in records[-count:]:
            row = _clean_record(bar)
            row["date"] = f"{bar.year:04d}-{bar.month:02d}-{bar.day:02d}"
            rows.append(row)
        return DataFrameResponse(data=rows, count=len(rows))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/offline/customer-blocks", response_model=DataFrameResponse)
async def offline_customer_blocks(
    block_dir: str = Query(..., description="通达信自定义板块目录，如 T0002/blocknew"),
) -> DataFrameResponse:
    """读取通达信自定义板块（blocknew.cfg + *.blk）。"""
    from easy_tdx.offline import read_customer_blocks

    try:
        blocks = read_customer_blocks(Path(block_dir))
        rows = [
            {
                "blockname": item.blockname,
                "block_type": item.block_type,
                "count": len(item.codes),
                "codes": item.codes,
            }
            for item in blocks
        ]
        return DataFrameResponse(data=rows, count=len(rows))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
