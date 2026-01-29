#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Import standard libraries
from urllib.parse import urljoin
import warnings
import logging
import urllib3
import json
import time
import re

# Import third-party libraries
from bs4 import BeautifulSoup
import requests
import pandas

# Import internal libraries
from shared.decorators import performance


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.simplefilter(action="ignore", category=FutureWarning)


class KLSEScreener:

    def __init__(self):
        self.url = "https://www.klsescreener.com/v2"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    def fetch_html(self, url: str, match: str = ".+", extract_links: str | None = None) -> list:
        """Fetch html from website.
        """
        logging.debug(f"Fetching html from {url} with match={match} and extract_links={extract_links}")
        response = requests.get(url=url, headers=self.headers)
        response.raise_for_status()
        dataframes = pandas.read_html(io=response.text, match=match, extract_links=extract_links)
        # Post-process dataframes
        for dataframe in dataframes:
            # If all values in a column are NaN, drop the column
            dataframe.dropna(axis=1, how="all", inplace=True)
        return dataframes

    def fetch_json(self, url: str, timeout: int = 20) -> list:
        """Fetch json from website.
        """
        logging.debug(f"Fetching json from {url}.")
        with requests.Session() as session:
            due_time = time.time() + timeout
            response = session.get(url=url, headers=self.headers)
            while response.status_code == 202:
                time.sleep(1)  # Wait for 1 second before retrying
                response = session.get(url=url, headers=self.headers)
                if time.time() > due_time:
                    raise TimeoutError(f"Timeout after {timeout} seconds while fetching data from {url}.")
        dataframe = pandas.DataFrame(data=response.json())
        return dataframe

    def fetch_text(self, url: str) -> str:
        """Fetch text from website.
        """
        logging.debug(f"Fetching text from {url}.")
        response = requests.get(url=url, headers=self.headers, verify=False)
        response.raise_for_status()
        content = response.text
        return content

    @performance()
    def screener(self) -> pandas.DataFrame:
        """Get the KLSE Screener data.
        """

        def remove_consecutive_duplicates(text):
            return re.sub(r"\b(\w+)\b(\s+\1\b)+", r"\1", text, flags=re.IGNORECASE)

        pattern = r"\b(?:Main Market|Ace Market|Leap Market)|ETF\b"
        dataframe = self.fetch_html(url=f"{self.url}/screener/quote_results")[0]
        dataframe["Name"] = dataframe["Name"].str.strip("[s]").str.strip("")
        dataframe["Market"] = dataframe["Category"].str.extract(f"({pattern})", flags=re.IGNORECASE)
        dataframe["Category"] = dataframe["Category"].str.replace(pattern, "", case=False, regex=True).str.replace(r"[ ,]+", " ", regex=True).str.strip().apply(remove_consecutive_duplicates)
        dataframe["KLSEScreener"] = dataframe["Code"].apply(lambda x: f"{self.url}/stocks/view/{x}")
        dataframe["KLSEScreener Chart"] = dataframe["Code"].apply(lambda x: f"{self.url}/charting/chart/{x}")
        return dataframe

    @performance()
    def warrant_screener(self) -> pandas.DataFrame:
        """Get the KLSE Warrant Screener data.
        """
        dataframe = self.fetch_html(url=f"{self.url}/screener_warrants/quote_results")[0]
        return dataframe

    @performance()
    def bursa_index(self) -> pandas.DataFrame:
        """Get the Bursa Index data.
        """
        context = self.fetch_text(url=f"{self.url}/markets")
        soup = BeautifulSoup(markup=context, features="html.parser")
        node = soup.find(lambda tag: tag.string == "Bursa Index").find_next_sibling()
        dataframe = pandas.DataFrame(data={
            "Index": [a.text for a in node.find_all("a")],
            "Code" : [a.get("href").split("/")[-1] for a in node.find_all("a")],
            "Link" : [urljoin(self.url, a.get("href")) for a in node.find_all("a")],
            "Price": [span.text for span in node.find_all("span", attrs={"class": "last"})],
        })
        dataframe["Chart Link"] = dataframe["Code"].apply(lambda x: f"{self.url}/charting/chart/{x}")

        for row_index, row in dataframe.iterrows():
            df = self.fetch_html(url=row["Link"])[0].dropna().transpose()
            df.columns = df.iloc[0]
            df.drop(labels=df.index[0], inplace=True)
            series = pandas.Series(data=json.loads(s=df.to_json(orient="records"))[0])
            dataframe.loc[row_index, series.index] = series
        return dataframe

    @performance()
    def bursa_index_components(self) -> pandas.DataFrame:
        dataframe = self.bursa_index()
        for row_index, row in dataframe.iterrows():
            if row["Code"].startswith("00"):
                context = self.fetch_text(url=f"{self.url}/markets/bursa/" + row["Code"])
                soup = BeautifulSoup(markup=context, features="html.parser")
                node = soup.find(name="div", attrs={"class": "container"}).find_next_sibling().find_next_sibling()
                dataframe.at[row_index, "Components"] = str([a.text for a in node.find_all("a")])
            elif row["Code"] in ("0200I"):
                df = self.fetch_html(url=row["Link"])[-1]
                dataframe.at[row_index, "Components"] = str(df["Name"].to_list())
        return dataframe

    def _post_process_dataframe(self, dataframe_raw: pandas.DataFrame) -> pandas.DataFrame:
        dataframe = pandas.DataFrame()
        # Iterate each column and insert values and links if available
        for (column, _), series in dataframe_raw.items():
            values = series.apply(lambda x: x[0])
            links = series.apply(lambda x: x[1])
            if values.isna().all():
                dataframe[column] = links
            elif links.isna().all():
                dataframe[column] = values
            else:
                dataframe[f"{column}Link"] = links.apply(lambda x: urljoin(self.url, x) if x else "")
                dataframe[column] = values

        # Remove dummy rows
        number_of_columns = len(dataframe.columns)
        rows_to_drop = []
        for index, row in dataframe.iterrows():
            if len(row.unique()) < (0.5 * number_of_columns):
                rows_to_drop.append(index)
        for index in reversed(rows_to_drop):
            dataframe.drop(labels=index, inplace=True)

        # Remove columns that only contain 'View'.
        dataframe = dataframe.loc[:, ~(dataframe.isin(["", "View"])).all()]

        # Reset index
        dataframe.reset_index(inplace=True)
        return dataframe

    @performance()
    def recent_dividends(self) -> pandas.DataFrame:
        """Get the recent dividends data.
        """
        dataframe = self.fetch_html(url=f"{self.url}/entitlements/dividends", extract_links="all")[0]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def upcoming_dividends(self) -> pandas.DataFrame:
        """Get the upcoming dividends data.
        """
        dataframe = self.fetch_html(url=f"{self.url}/entitlements/dividends", extract_links="all")[1]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def recent_share_issue(self) -> pandas.DataFrame:
        """Get the recent share issue data.
        """
        dataframe = self.fetch_html(url=f"{self.url}/entitlements/shares-issue", extract_links="all")[0]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def upcoming_share_issue(self) -> pandas.DataFrame:
        """Get the upcoming share issue data.
        """
        dataframe = self.fetch_html(url=f"{self.url}/entitlements/shares-issue", extract_links="all")[1]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def recent_quarterly_reports(self) -> pandas.DataFrame:
        """Get the recent quarterly reports data.
        """
        dataframe = self.fetch_html(url=f"{self.url}/financial-reports", extract_links="all")[0]
        dataframe = self._post_process_dataframe(dataframe)
        return dataframe

    @performance()
    def get_stockcodes(self) -> list:
        stockcodes = self.screener()["Code"].dropna().to_list()
        stockcodes.sort(reverse=False)
        return stockcodes

    @performance()
    def get_stocknames(self) -> list:
        stocknames = self.screener()["Name"].dropna().to_list()
        stocknames.sort(reverse=False)
        return stocknames

    @performance()
    def get_categories(self) -> list:
        categories = list(set(self.screener()["Category"].dropna().to_list()))
        categories.sort(reverse=False)
        return categories

    @performance()
    def get_markets(self) -> list:
        markets = list(set(self.screener()["Market"].dropna().to_list()))
        markets.sort(reverse=False)
        return markets
