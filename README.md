# Seastate

## Summary
Facade of multiple APIs to collect sea state by location and timeframe

**Features**
- Closest active station is selected for each measurement
- Reaches into secondary historical archives when required
- Available measurements: Tide, wind, water temp, air temp, air pressure, conductivity and swell information
- Returns pandas dataframe compatible lists

## Installing
`pip install seastate`

## Examples
### Retrieving raw data
```
sample code with start end

sample code with timedelta
```

### Converting to a dataframe
```
sample code
```

### Retrieving a subset of data sources
```

## For developers:
### Testing
`py test`

### Generating UMLs
`pyreverse -d UML -o png seastate`