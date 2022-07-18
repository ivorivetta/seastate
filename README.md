# Seastate

## Summary
Collect ocean measurement data based on location and timeframe

**Features**
- Closest active station is selected for each measurement
- Reaches into secondary historical archives when required
- Returns pandas dataframe compatible lists
- Available measurements: Tide, wind, water temp, air temp, air pressure, conductivity and swell information
- Datasources: NOAA NDBC, NOAA Tides and Currents

## Installing
`pip install seastate`

## Quick start
```
from seastate.seastate import SeaState
from datetime import datetime

# make SeaState object for specific location
san_diego = SeaState(32,-117)

# retrieve measurements for today
san_diego_today = san_diego.measurements_from_date_range(datetime.today())

san_diego_today['tide'] -> [{t: time, v: value, s: stdev]
san_diego_today['wind']-> [{t: time, v: value, d: direction, g: gust}]
san_diego_today['water_temp']-> [{t: time, v: value}]
san_diego_today['air_temp']-> [{t: time, v: value}]
san_diego_today['air_press']-> [{t: time, v: value}]
san_diego_today['wave']-> [{t: time, v: Wave Height, dpd: Dominant Period, mwd: dpd Direction}]
san_diego_today['conductivity']-> [{t: time, v: value}] 
```
Measurement details for NDBC are [here](https://www.ndbc.noaa.gov/measdes.shtml) and for Tides and Currents [here](https://api.tidesandcurrents.noaa.gov/api/prod/responseHelp.html)

## Measurement x API breakdown
| Measurement | T&C | NDBC |
| ---: | :---: | :---: |
|tide | y | y |
|wind | y | y |
|water_temp | y | y |
|air_temp | y | y |
|air_press | y | y |
|wave |  | y |
|conductivity | y |  |

## More Examples
### Measurements for past 30 days
```
from seastate.seastate import SeaState
from datetime import datetime, timedelta

start = datetime.today()-timedelta(days=30)
end = datetime.today()
san_diego_past_30 = san_diego.measurements_from_date_range(start,end)
```
### Hourly Slices
```
san_diego_past_30_hourly = san_diego.hourly(start,end) # this returns a single reading per hour
# experimental feature
# no guarantee between APIs that readings will align or exist in all cases
```
