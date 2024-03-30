from io import BufferedReader

import pytest

import os

# Working directory set up by Pycharm is different that the one set by pytest, so we use this as a base to import files
TEST_DIR = os.path.join(os.path.dirname(__file__))


class Utils:
    @staticmethod
    def get_fixture(fixture_name: str):
        return BufferedReader(open(f"{TEST_DIR}/fixtures/{fixture_name}", "rb"))


@pytest.fixture
def utils():
    return Utils
