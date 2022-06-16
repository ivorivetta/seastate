# ocean_sdk

## Summary
Facade of weather APIs for collecting ocean state by location and timeframe

**Notable features**
- Time offset feature allows building of time coherent datasets, defaut is local timezone of measurement
- Closest active measurement station is selected by default, filters can be used to select certain agencies
- request-cache implemented with appropriate timeouts for each datasource
- Forecasting available for Tide
- Available datasources: Tide, wind, water temp ...

**Requested Features**
- Automatically reach into historical archives for older datasets

## Installing
`pip install ocean_sdk`

## Examples
### Retrieving raw data
```
sample code with start end

sample code with timedelta
```

### Retrieving a dataframe
```
sample code
```

### Retrieving a subset of data sources
```

## For developers:
### Testing
`py test`

### Generating UMLs
`pyreverse -d UML -o png ocean_sdk`