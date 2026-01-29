#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Import standard libraries
from unittest.mock import patch
import datetime

# Import third-party libraries
import pandas
import pytest

# Import internal libraries
from klsescreener.stock import Stock, generate_dashboard
from klsescreener import KLSEScreener


def stockcode():
    return "1818"


@pytest.fixture(params=[stockcode()])
def stock(request):
    """Fixture to create an instance of Stock."""
    return Stock(code=request.param)


def test_info(stock):
    """Test the info method."""
    dataframe = stock.info()
    assert isinstance(dataframe, pandas.DataFrame)


def test_quarter_reports(stock):
    """Test the quarter_reports method."""
    dataframe = stock.quarter_reports()
    assert isinstance(dataframe, pandas.DataFrame)


def test_annual_reports(stock):
    """Test the annual_reports method."""
    dataframe = stock.annual_reports()
    assert isinstance(dataframe, pandas.DataFrame)


def test_dividend_reports(stock):
    """Test the dividend_reports method."""
    dataframe = stock.dividend_reports()
    assert isinstance(dataframe, pandas.DataFrame)


def test_capital_changes(stock):
    """Test the capital_changes method."""
    dataframe = stock.capital_changes()
    assert isinstance(dataframe, pandas.DataFrame)


def test_warrants(stock):
    """Test the warrants method."""
    dataframe = stock.warrants()
    assert isinstance(dataframe, pandas.DataFrame)


def test_shareholding_changes(stock):
    """Test the shareholding_changes method."""
    dataframe = stock.shareholding_changes()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_1m(stock):
    """Test the historical_data_1m method."""
    dataframe = stock.historical_data_1m()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_5m(stock):
    """Test the historical_data_5m method."""
    dataframe = stock.historical_data_5m()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_15m(stock):
    """Test the historical_data_15m method."""
    dataframe = stock.historical_data_15m()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_30m(stock):
    """Test the historical_data_30m method."""
    dataframe = stock.historical_data_30m()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_1H(stock):
    """Test the historical_data_1H method."""
    dataframe = stock.historical_data_1H()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_4H(stock):
    """Test the historical_data_4H method."""
    dataframe = stock.historical_data_4H()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_1D(stock):
    """Test the historical_data_1D method."""
    dataframe = stock.historical_data_1D()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_1W(stock):
    """Test the historical_data_1W method."""
    dataframe = stock.historical_data_1W()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_1M(stock):
    """Test the historical_data_1M method."""
    dataframe = stock.historical_data_1M()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_3M(stock):
    """Test the historical_data_3M method."""
    dataframe = stock.historical_data_3M()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_6M(stock):
    """Test the historical_data_6M method."""
    dataframe = stock.historical_data_6M()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_1Y(stock):
    """Test the historical_data_1Y method."""
    dataframe = stock.historical_data_1Y()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_5Y(stock):
    """Test the historical_data_5Y method."""
    dataframe = stock.historical_data_5Y()
    assert isinstance(dataframe, pandas.DataFrame)


def test_historical_data_10Y(stock):
    """Test the historical_data_10Y method."""
    dataframe = stock.historical_data_10Y()
    assert isinstance(dataframe, pandas.DataFrame)


def test_get_listing_date(stock):
    """Test the get_listing_date method."""
    date = stock.get_listing_date()
    assert isinstance(date, datetime.date)


@patch("klsescreener.stock.KLSEScreener")
def test_generate_dashboard(mock_cls):
    # Build a fake KLSEScreener().screener() return value
    dataframe = KLSEScreener().screener()
    dummy_dataframe = dataframe[dataframe["Code"] == stockcode()]

    # Return dummy dataframe from KLSEScreener().screener()
    mock_cls.return_value.screener.return_value = dummy_dataframe.copy()

    # Call the function
    dataframe = generate_dashboard(thread_count=1)

    assert isinstance(dataframe, pandas.DataFrame)
    assert dataframe.shape[0] == 1
    assert list(dataframe["Code"]) == [stockcode()]
    assert len(dataframe.columns) > len(dummy_dataframe.columns)
