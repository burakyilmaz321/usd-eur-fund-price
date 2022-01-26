<pre>
USD/TRY, EUR/TRY AND TEFAS FUND PRICE SERVICE
---------------------------------------------

DESCRIPTION
    This is a service that offers the USD/TRY or EUR/TRY exchange rates,
    and TEFAS fund prices. It provides the latest prices and rates, as
    well as the ones for a specific date.


ENDPOINTS
   o `/usd[?date=YYYY-MM-DD]`: USD/TRY exchange rate. Returns the
     latest rate if `date` parameter is not given.

   o `/eur[?date=YYYY-MM-DD]`: EUR/TRY exchange rate. Returns the
     latest rate if `date` parameter is not given.

   o `/fon?q=CODE[&date=YYYY-MM-DD]`: TEFAS fund price. Parameter `q`
     is the code of the desired fund. Returns the latest price if
     `date` parameter is not given.

   o `/all[?date=YYYY-MM-DD]`: All TEFAS fund price. Returns the
     latest prices if `date` parameter is not given.

USAGE
   o Get latest USD/TRY rate:
      `/usd`

   o Get USD/TRY rate at December 7th, 2021:
      `/usd?date=2021-12-07`

   o Get latest EUR/TRY rate:
      `/eur`

   o Get EUR/TRY rate at December 7th, 2021:
      `/eur?date=2021-12-07`

   o Get latest TCD fund price:
      `/fon?q=TCD`

   o Get TCD fund price at December 7th, 2021:
      `/fon?q=TCD&date=2021-12-07`

   o Use it with Google Sheets function IMPORTDATA:
      =IMPORTDATA("/fon?q=TCD")

   o Get all fund prices for today:
      `/all`

   o Get all fund prices at December 7th, 2021:
      `/all?date=2021-12-07`
</pre>