#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Import standard libraries
import threading
import datetime
import logging
import ast

# Import third-party libraries
from lxml import etree
import requests
import pandas
import numpy

# Import internal libraries
from klsescreener.resolution import Resolution
from shared.decorators import performance
from klsescreener import KLSEScreener


class Stock(KLSEScreener):

    __slots__ = [
        "_dataframe_1d",
        "_html_content",
        "_tree",
        "cdt",  # Current date time
        "cts",  # Current timestamp
        "headers",
    ]

    def __init__(self, code: int | str):
        super().__init__()
        self.code = code
        self.code_url = self.code
        self.cdt = datetime.datetime.today()
        self.cts = datetime.datetime.now().timestamp()

        self._html_content = self.fetch_text(url=self.code_url)
        self._tree = etree.HTML(text=self._html_content)

        self.name = None
        self.long_name = None
        self.background = None
        self.website = None

        self.listing_timestamp = None
        self.listing_datetime = None
        self.listing_date = None

        self._dataframe_1d = None
        if self.listing_timestamp is not None:
            self._dataframe_1d = self.historical_data_1D(stimestamp=self.listing_timestamp, etimestamp=self.cts)
        self.listing_open_price = None
        self.last_traded_date = None
        self.listed_days = None

        self.ath_price = None
        self.ath_timestamp = None
        self.ath_date = None
        self.ath_days = None

        self.atl_price = None
        self.atl_timestamp = None
        self.atl_date = None
        self.atl_days = None

    @property
    def ath_date(self):
        return self._ath_date

    @ath_date.setter
    def ath_date(self, date: None):
        if date is None and self.ath_price:
            self._ath_date = self._dataframe_1d[self._dataframe_1d["h"] == self.ath_price].iloc[0, :]["d"].date()
        else:
            self._ath_date = timestamp

    @property
    def ath_days(self):
        return self._ath_days

    @ath_days.setter
    def ath_days(self, days: None):
        if days is None and self.ath_timestamp:
            self._ath_days = (self.cdt - datetime.datetime.fromtimestamp(self._ath_timestamp)).days
        else:
            self._ath_days = days

    @property
    def ath_price(self):
        return self._ath_price

    @ath_price.setter
    def ath_price(self, price: float | int | None):
        if price is None and not self._dataframe_1d.empty:
            self._ath_price = self._dataframe_1d["h"].max()
        else:
            self._ath_price = price

    @property
    def ath_timestamp(self):
        return self._ath_timestamp

    @ath_timestamp.setter
    def ath_timestamp(self, timestamp: int | None):
        if timestamp is None and self.ath_price:
            self._ath_timestamp = self._dataframe_1d[self._dataframe_1d["h"] == self.ath_price].iloc[0, :]["d"].timestamp()
        else:
            self._ath_timestamp = timestamp

    @property
    def atl_date(self):
        return self._atl_date

    @atl_date.setter
    def atl_date(self, date: None):
        if date is None and self.atl_price:
            self._atl_date = self._dataframe_1d[self._dataframe_1d["l"] == self.atl_price].iloc[0, :]["d"].date()
        else:
            self._atl_date = timestamp

    @property
    def atl_days(self):
        return self._atl_days

    @atl_days.setter
    def atl_days(self, days: None):
        if days is None and self.atl_timestamp:
            self._atl_days = (self.cdt - datetime.datetime.fromtimestamp(self._atl_timestamp)).days
        else:
            self._atl_days = days

    @property
    def atl_price(self):
        return self._atl_price

    @atl_price.setter
    def atl_price(self, price: float | int | None):
        if price is None and not self._dataframe_1d.empty:
            self._atl_price = self._dataframe_1d["l"].min()
        else:
            self._atl_price = price

    @property
    def atl_timestamp(self):
        return self._atl_timestamp

    @atl_timestamp.setter
    def atl_timestamp(self, timestamp: int | None):
        if timestamp is None and self.atl_price:
            self._atl_timestamp = self._dataframe_1d[self._dataframe_1d["l"] == self.atl_price].iloc[0, :]["d"].timestamp()
        else:
            self._atl_timestamp = timestamp

    @property
    def background(self):
        return self._background

    @background.setter
    def background(self, text: str | None):
        if text is None:
            try:
                self._background = self._tree.xpath(_path="/html/body/div/div[1]/div[3]/div[1]/div/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div/div/div[1]")[0].text.strip()
            except Exception:
                pass
        else:
            self._backgrounde = ""

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code: str):
        if isinstance(code, int):
            self._code = f"{code:04d}"
        else:
            self._code = code

    @property
    def code_url(self):
        return self._code_url

    @code_url.setter
    def code_url(self, code: str):
        self._code_url = f"{self.url}/stocks/view/{self.code}"

    @property
    def last_traded_date(self):
        return self._last_traded_date

    @last_traded_date.setter
    def last_traded_date(self, date: None):
        if date is None and not self._dataframe_1d.empty:
            self._last_traded_date = self._dataframe_1d.iloc[0, :]["Date"]
        else:
            self._last_traded_date = date

    @property
    def listed_days(self):
        return self._listed_days

    @listed_days.setter
    def listed_days(self, days: int | None):
        if days is None and not self._dataframe_1d.empty:
            self._listed_days = (self.cdt - self._dataframe_1d.iloc[-1, :]["d"]).days
        else:
            self._listed_days = days

    @property
    def listing_date(self):
        return self._listing_date

    @listing_date.setter
    def listing_date(self, date: int | None):
        if date is None and self.listing_datetime:
            self._listing_date = str(self.listing_datetime.date())
        else:
            self._listing_date = date

    @property
    def listing_datetime(self):
        return self._listing_datetime

    @listing_datetime.setter
    def listing_datetime(self, date: None):
        if date is None and self.listing_timestamp:
            self._listing_datetime = datetime.datetime.fromtimestamp(timestamp=self.listing_timestamp)
        else:
            self._listing_datetime = date

    @property
    def listing_open_price(self):
        return self._listing_open_price

    @listing_open_price.setter
    def listing_open_price(self, price: float | int | None):
        if price is None and not self._dataframe_1d.empty:
            self._listing_open_price = self._dataframe_1d.iloc[-1, :]["o"]
        else:
            self._listing_open_price = price

    @property
    def listing_timestamp(self):
        return self._listing_timestamp

    @listing_timestamp.setter
    def listing_timestamp(self, timestamp: int | None):
        if timestamp is None:
            self._listing_timestamp = self.get_listing_date(return_timestamp=True)
        else:
            self._listing_timestamp = timestamp

    @property
    def long_name(self):
        return self._long_name

    @long_name.setter
    def long_name(self, name: str | None):
        if name is None:
            try:
                self._long_name = self._tree.xpath(_path="/html/body/div/div[1]/div[3]/div[1]/div/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/span")[0].text.strip()
            except Exception:
                pass
        else:
            self._long_name = ""

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str | None):
        if name is None:
            try:
                self._name = self._tree.xpath(_path="/html/body/div/div[1]/div[3]/div[1]/div/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/h2")[0].text.strip()
            except Exception:
                pass
        else:
            self._name = ""

    @property
    def website(self):
        return self._website

    @website.setter
    def website(self, text: str | None):
        if text is None:
            try:
                self._website = self._tree.xpath(_path="/html/body/div/div[1]/div[3]/div[1]/div/div[3]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div/div/div[1]/p[2]/a")[0].text.strip()
            except Exception:
                pass
        else:
            self._website = ""

    @performance()
    def info(self, transpose: bool = False, return_json: bool = False, extended_info: bool = False) -> pandas.DataFrame | dict:
        dataframe = self.fetch_html(url=self.code_url)[0].dropna()

        # Adding more stock information if is true
        if extended_info is True:

            dataframe = pandas.concat(objs=[dataframe, pandas.DataFrame([
                ["Long Name", self.long_name],
                ["Background", self.background],
                ["Last Trading Date", self.last_traded_date],
                ["All Time High", self.ath_price],
                ["All Time High (Timestamp)", self.ath_timestamp],
                ["All Time High (Date)", self.ath_date],
                ["All Time High (Days)", self.ath_days],
                ["All Time Low", self.atl_price],
                ["All Time Low (Timestamp)", self.atl_timestamp],
                ["All Time Low (Date)", self.atl_date],
                ["All Time Low (Days)", self.atl_days],
                ["Website", self.website],
                ["Listed Timestamp", self.listing_timestamp],
                ["Listed Date", self.listing_date],
                ["Listed Days", self.listed_days],
                ["Listed Open Price", self.listing_open_price],
            ])])

            dataframe.reset_index(drop=True, inplace=True)

        if transpose is True or return_json is True:
            dataframe = dataframe.T
            dataframe.columns = dataframe.iloc[0]
            dataframe = dataframe[1:]
            if return_json is True:
                return ast.literal_eval(dataframe.to_json(orient="records"))[0]
        return dataframe

    @performance()
    def quarter_reports(self) -> pandas.DataFrame:
        dataframe = self.fetch_html(url=self.code_url, match="Financial Year", extract_links="all")[0].iloc[:, :13]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def annual_reports(self) -> pandas.DataFrame:
        dataframe = self.fetch_html(url=self.code_url, match="Financial Year", extract_links="all")[1]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def dividend_reports(self) -> pandas.DataFrame:
        dataframe = self.fetch_html(url=self.code_url, match="Financial Year", extract_links="all")[2].iloc[:, :8]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def capital_changes(self) -> pandas.DataFrame:
        dataframe = self.fetch_html(url=self.code_url, match="Ratio", extract_links="all")[0]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def warrants(self) -> pandas.DataFrame:
        dataframe = self.fetch_html(url=self.code_url, extract_links="all")[-2]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def shareholding_changes(self) -> pandas.DataFrame:
        dataframe = self.fetch_html(url=self.code_url, match="Date Change")[0]
        return dataframe

    def historical_data(self, resolution: str, stimestamp: int, etimestamp: int, countback: int = 99999999) -> pandas.DataFrame:
        url = f"{self.url}/trading_view/history?symbol={self.code}&resolution={resolution}&from={stimestamp}&to={etimestamp}&countback={countback}&currencyCode=MYR"
        logging.debug(f"Fetching historical data for stockcode \"{self.code}\" with resolution {resolution} from {datetime.datetime.fromtimestamp(stimestamp)} ({stimestamp}) to {datetime.datetime.fromtimestamp(etimestamp)} ({etimestamp}). {url}")
        dataframe = self.fetch_json(url=url)

        # Post-process the dataframe
        dataframe.insert(loc=0, column="d", value=pandas.to_datetime(dataframe["t"], unit="s") + pandas.to_timedelta("8 hours"))
        dataframe.insert(loc=0, column="Time", value=dataframe["d"].dt.time)
        dataframe.insert(loc=0, column="Date", value=dataframe["d"].dt.date)
        dataframe.insert(loc=0, column="Day", value=dataframe["d"].dt.day_name())
        dataframe.insert(loc=0, column="Month", value=dataframe["d"].dt.month)
        dataframe.insert(loc=0, column="Year", value=dataframe["d"].dt.year)
        dataframe.insert(loc=0, column="Resolution", value=resolution)
        dataframe.drop(columns=["s", "from", "to", "exact_from", "server", "ip", "qt"], axis=1, inplace=True)
        dataframe.sort_values(by=["t"], ascending=False, inplace=True)
        dataframe.reset_index(drop=True, inplace=True)
        logging.debug(f"Fetched {len(dataframe)} rows of historical data for stockcode \"{self.code}\" with resolution {resolution} from {datetime.datetime.fromtimestamp(stimestamp)} ({stimestamp}) to {datetime.datetime.fromtimestamp(etimestamp)} ({etimestamp}).")
        return dataframe

    @performance()
    def historical_data_1m(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MINUTE_1.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_5m(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MINUTE_5.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_15m(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MINUTE_15.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_30m(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MINUTE_30.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_1H(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.HOUR_1.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_4H(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.HOUR_4.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_1D(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.DAILY.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_1W(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.WEEKLY.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_1M(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MONTH_1.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_3M(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MONTH_3.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_6M(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.MONTH_6.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_1Y(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.YEAR_1.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_5Y(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.YEAR_5.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def historical_data_10Y(self, stimestamp: int = int((datetime.datetime.now() - datetime.timedelta(days=360)).timestamp()), etimestamp: int = int(datetime.datetime.now().timestamp())) -> pandas.DataFrame:
        dataframe = self.historical_data(resolution=Resolution.YEAR_10.value, stimestamp=stimestamp, etimestamp=etimestamp)
        return dataframe

    @performance()
    def get_listing_date(self, fmt: str = "", return_timestamp: bool = False) -> datetime.date | str | int:

        try:
            dataframe = self.quarter_reports()
        except requests.exceptions.HTTPError:
            logging.warning(f"Failed to fetch quarter reports for {self.code_url}.")
            return ""

        if dataframe.empty:
            logging.warning(f"No quarter reports found for {self.code_url}.")
            return ""

        # First quarter report
        date = dataframe["Announced"].to_list()[-1]
        if date == "No financial reports found yet.":
            logging.warning(f"No financial reports from {self.code_url}")
            return ""

        timestamp = datetime.datetime.strptime(date, "%Y-%m-%d")
        dataframe = self.historical_data_1D(
            stimestamp=int((timestamp - datetime.timedelta(days=30)).timestamp()),
            etimestamp=int((timestamp + datetime.timedelta(days=360)).timestamp()),
        )
        date = dataframe["d"].iloc[-1].to_pydatetime().date()
        if return_timestamp is True:
            return int(datetime.datetime.combine(date=date, time=datetime.datetime.min.time()).timestamp())
        if fmt != "":
            date = date.strftime(format=fmt)
        return date


@performance(log=print)
def generate_dashboard(thread_count: int = 16):
    """Extended table with more information
    """

    @performance(log=logging.info)
    def sThread(dataframe: pandas.DataFrame, sub_dataframe: pandas.DataFrame):
        for index, row in sub_dataframe.iterrows():
            info = Stock(code=row["Code"]).info(extended_info=True).T
            info.columns = info.iloc[0]
            info = info[1:]
            dataframe.loc[dataframe["Code"] == row["Code"], info.columns] = info.iloc[0].values

    dataframe = KLSEScreener().screener()
    dataframes = numpy.array_split(ary=dataframe, indices_or_sections=thread_count, axis=0)

    threads = []
    for df in dataframes:
        threads.append(threading.Thread(target=sThread, args=[dataframe, df]))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    return dataframe


if __name__ == "__main__":
    timestamp = datetime.datetime.now().strftime("%y%m%d_%H%M%S")
    #dashboard = generate_dashboard()
    #dashboard.to_excel(f"dashboard_{timestamp}.xlsx", index=False)
