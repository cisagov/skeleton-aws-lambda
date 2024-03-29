#!/usr/bin/env pytest -vs
"""Tests for example-aws-lambda."""

# Standard Python Libraries
from datetime import datetime, timezone
import logging
import os
import sys
from unittest.mock import patch

# Third-Party Libraries
import pytest

# cisagov Libraries
from eal import example_aws_lambda as eal

log_levels = (
    "debug",
    "info",
    "warning",
    "error",
    "critical",
    pytest.param("critical2", marks=pytest.mark.xfail),
)

# define sources of version strings
RELEASE_TAG = os.getenv("RELEASE_TAG")
PROJECT_VERSION = eal.__version__

TEST_REGION = "pytest-local"


def test_stdout_version(capsys):
    """Verify that version string sent to stdout agrees with the module version."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            eal.main()
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


def test_running_as_module(capsys):
    """Verify that the __main__.py file loads correctly."""
    with pytest.raises(SystemExit):
        with patch.object(sys, "argv", ["bogus", "--version"]):
            # F401 is a "Module imported but unused" warning. This import
            # emulates how this project would be run as a module. The only thing
            # being done by __main__ is importing the main entrypoint of the
            # package and running it, so there is nothing to use from this
            # import. As a result, we can safely ignore this warning.
            # cisagov Libraries
            import eal.__main__  # noqa: F401
    captured = capsys.readouterr()
    assert (
        captured.out == f"{PROJECT_VERSION}\n"
    ), "standard output by '--version' should agree with module.__version__"


@pytest.mark.skipif(
    RELEASE_TAG in [None, ""], reason="this is not a release (RELEASE_TAG not set)"
)
def test_release_version():
    """Verify that release tag version agrees with the module version."""
    assert (
        RELEASE_TAG == f"v{PROJECT_VERSION}"
    ), "RELEASE_TAG does not match the project version"


@pytest.mark.parametrize("level", log_levels)
def test_log_levels(level):
    """Validate commandline log-level arguments."""
    test_message = "pytest-log_levels"
    with patch.object(
        sys,
        "argv",
        [
            "bogus",
            f"--region={TEST_REGION}",
            f"--message={test_message}",
            f"--log-level={level}",
        ],
    ):
        with patch.object(logging.root, "handlers", []):
            assert (
                logging.root.hasHandlers() is False
            ), "root logger should not have handlers yet"
            return_code = eal.main()
            assert (
                logging.root.hasHandlers() is True
            ), "root logger should now have a handler"
            assert (
                logging.getLevelName(logging.root.getEffectiveLevel()) == level.upper()
            ), f"root logger level should be set to {level.upper()}"
            assert return_code == 0, "main() should return success"


def test_lambda_function_run(capsys):
    """Verify that the core function works."""
    test_message = "pytest-lambda-functionality"
    test_time = datetime.now(timezone.utc)
    eal.setup_logging("warning")
    eal.do_lambda_functionality(TEST_REGION, test_time, test_message)
    captured = capsys.readouterr()
    output_lines = captured.out.split("\n")
    assert len(output_lines) == 5, "unexpected output length"
    assert (
        output_lines[0] == f"Region: {TEST_REGION}"
    ), "region did not match what was provided"
    assert (
        output_lines[1] == f"Invocation Time: {test_time}"
    ), "invocation time did not match what was provided"
    assert (
        output_lines[3] == f"Provided Message: {test_message}"
    ), "message did not match what was provided"


def test_commandline_run(capsys):
    """Verify that the script works from the commandline."""
    test_message = "pytest-cli_functionality"
    with patch.object(
        sys, "argv", ["bogus", f"--region={TEST_REGION}", f"--message={test_message}"]
    ):
        eal.main()
    captured = capsys.readouterr()
    output_lines = (captured.out).split("\n")
    assert len(output_lines) == 5, "unexpected output length"
    assert (
        output_lines[0] == f"Region: {TEST_REGION}"
    ), "region did not match what was provided"
    assert (
        output_lines[3] == f"Provided Message: {test_message}"
    ), "message did not match what was provided"
