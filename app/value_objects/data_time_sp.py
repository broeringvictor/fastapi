import datetime
from zoneinfo import ZoneInfo


def _get_default_tz() -> ZoneInfo:
    # No Windows, o banco de timezones pode não
    # estar disponível sem o pacote `tzdata`.
    try:
        return ZoneInfo("America/Sao_Paulo")
    except Exception:
        return ZoneInfo("UTC")


def tz_sp_now() -> datetime.datetime:
    """Retorna o datetime atual em São Paulo"""
    tz = _get_default_tz()
    return datetime.datetime.now(tz)
