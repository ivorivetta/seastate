# Seastate

## Summary
Collect sea state by location and timeframe

**Features**
- Closest active station is selected for each measurement
- Reaches into secondary historical archives when required
- Returns pandas dataframe compatible lists
- Available measurements: Tide, wind, water temp, air temp, air pressure, conductivity and swell information
- Datasources: NOAA NDBC, NOAA Tides and Currents

## Installing
`pip install seastate`

## Examples
### Retrieving raw data
```
from seastate.seastate import SeaState
from datetime import datetime, timedelta

# make SeaState object for specific location
san_diego = SeaState(32,-117)

# retrieve measurements for today
start = datetime.today()
san_diego_today = san_diego.measurements_from_date_range(start)

# retrieve measurements for past 30 days
start = datetime.today()-timedelta(days=30)
end = datetime.today()
san_diego_past_30 = san_diego.measurements_from_date_range(start,end)

```
