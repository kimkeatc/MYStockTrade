#!/usr/bin/env python

# -*- coding: utf-8 -*-

# Import standard libraries
from enum import Enum, unique


@unique
class Resolution(Enum):
    MINUTE_1  = "1"
    MINUTE_5  = "5"
    MINUTE_15 = "15"
    MINUTE_30 = "30"
    HOUR_1    = "60"
    HOUR_4    = "240"
    DAILY     = "1D"
    WEEKLY    = "1W"
    MONTH_1   = "1M"
    MONTH_3   = "3M"
    MONTH_6   = "6M"
    YEAR_1    = "1Y"
    YEAR_5    = "5Y"
    YEAR_10   = "10Y"
