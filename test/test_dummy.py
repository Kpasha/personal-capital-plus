import pytest
import pandas as pd

from personalcapital.etl import (
    get_category_map,
    get_accounts
)


def test_basic():
    cmap = get_category_map()
    assert isinstance(cmap, dict)

    accounts = get_accounts()
    assert isinstance(accounts, pd.DataFrame)
