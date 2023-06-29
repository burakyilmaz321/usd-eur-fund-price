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

   o `/multi?q=CODE[&q=CODE ...][&date=YYYY-MM-DD ...]`: Multiple
     TEFAS funds for multiple dates.

   o `/returns`: Get fund returns for different time periods.

   o `/value?fund=CODE1,CODE2,..&shares=SHARE1,SHARE2,..[&date=YYYY-MM-DD]`: Total portfolio value.

      The endpoint returns the total portfolio value based on the provided fund codes and the
      number of shares, calculated for the given date or for the current day if the date is not
      provided. The lists of fund codes and share quantities must have the same length. If there is
      a mismatch in the lengths of these lists, the request will result in an error.

      Parameters:

         fund: A comma-separated list of fund codes. At least one code must be provided. Multiple
            codes should be listed in the same order as the corresponding number of shares. The
            parameter is mandatory.

         shares: A comma-separated list of the number of shares for each fund code provided. At
            least one share quantity must be provided. Multiple share quantities should be listed
            in the same order as the corresponding fund codes. The parameter is mandatory.

         date: The date for which the portfolio value should be calculated, in YYYY-MM-DD format.
            This parameter is optional. If not provided, the calculation will be made for the
            current day.

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

   o Get multiple funds for multiple dates:
      `/multi?q=YAC&q=TCD&date=2021-12-07&date=2021-12-08`

   o Calculate the latest total portfolio value for funds CODE1 and CODE2 with 10 and 20 shares
     respectively:
      `/value?fund=CODE1,CODE2&shares=10,20`

   o Calculate the total portfolio value for funds CODE1 and CODE2 with 10 and 20 shares
     respectively, as of December 7th, 2021:
     `/value?fund=CODE1,CODE2&shares=10,20&date=2021-12-07`

   o Use it with Google Sheets function IMPORTDATA to get the latest total portfolio value for
     funds CODE1 and CODE2 with 10 and 20 shares respectively:
     `=IMPORTDATA("/value?fund=CODE1,CODE2&shares=10,20")`
</pre>