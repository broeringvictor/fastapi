import datetime
from app.value_objects.data_time_sp import tz_sp_now


def test_tz_sp_now_returns_aware_datetime():
    dt = tz_sp_now()
    assert isinstance(dt, datetime.datetime)
    assert dt.tzinfo is not None

    # Verifica se o timezone é SP ou UTC (fallback)
    # Como não podemos garantir o ambiente, verificamos se é um dos dois
    tz_name = str(dt.tzinfo)
    assert "Sao_Paulo" in tz_name or "UTC" in tz_name
