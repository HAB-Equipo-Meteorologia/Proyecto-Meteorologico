import pytest
from backend.src.etl_scripts import pipeline


@pytest.mark.asyncio
async def test_fetch_latest():
    result = await pipeline.run_etl_latest(origin='test')

    assert result is not None
    assert len(result) > 0
