# MYStockTrade
Malaysia Stock Trading

# Uninstall package
```
C:\Users\KLSEScreener> python -m pip uninstall -y MYStockTrade
```

# Install package
```
C:\Users\MYStockTrade> python -m pip install -e .
```

# Build *.whl file
```
C:\Users\MYStockTrade> python -m pip install build
C:\Users\MYStockTrade> python -m build
```

# Install package via *.whl file
```
C:\Users\MYStockTrade> python -m pip install --find-links=.\dist MYStockTrade
```

# Clean up
```
C:\Users\MYStockTrade> RMDIR /S /Q dist build libs\MYStockTrade.egg-info 2>NUL
```

# Verify package
```
C:\Users\MYStockTrade> python -c "import klsescreener; print(dir(klsescreener))"
```

# Run test
```
C:\Users\MYStockTrade> pytest
===================================================================== test session starts =====================================================================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0
rootdir: D:\kimkeatc\workspace\MYStockTrade
configfile: pytest.ini
collected 34 items

libs\klsescreener\tests\test_screener.py ...........                                                                                                     [ 32%]
libs\klsescreener\tests\test_stock.py .......................                                                                                            [100%]

=========================================================================== 34 passed in 220.43s (0:03:40) ====================================================
```