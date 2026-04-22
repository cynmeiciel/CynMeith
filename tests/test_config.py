import pytest

from cynmeith import Config, ConfigError


def test_config_rejects_missing_required_fields() -> None:
    with pytest.raises(ConfigError, match="missing required field"):
        Config.from_data({})


def test_config_rejects_invalid_field_types() -> None:
    with pytest.raises(ConfigError, match="`width`"):
        Config.from_data(
            {
                "pieces": {},
                "width": 0,
                "height": 8,
                "fen": "8/8/8/8/8/8/8/8",
            }
        )

    with pytest.raises(ConfigError, match="`pieces`"):
        Config.from_data(
            {
                "pieces": [],
                "width": 8,
                "height": 8,
                "fen": "8/8/8/8/8/8/8/8",
            }
        )
