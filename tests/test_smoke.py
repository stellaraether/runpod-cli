"""Smoke tests for runpod_cli."""

import runpod_cli


def test_version():
    """Package has a version."""
    assert runpod_cli.__version__


def test_config_loads():
    """Config can be instantiated."""
    from runpod_cli.config import Config

    config = Config()
    assert config._data is not None
