# Calculate Geohash Value of a Set of Coordinates | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-geohash-calculate.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Geohash Value of a Set of Coordinates

Calculate a geohash value given two fields representing latitude and longitude using the [`geohash()`](https://library.humio.com/data-analysis/functions-geohash.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    londonLat := 51.507222
    | londonLon := -0.1275
    | geohash(lat=londonLat, lon=londonLon)

### Introduction

The [`geohash()`](https://library.humio.com/data-analysis/functions-geohash.html) function is used to calculate a geohash value given two fields representing `latitude` and `longitude`. These fields and their values can be used for geohash bucketing to create a World Map for presentation of the data: `lat`, `lon`, `geohash`, `precision`, `magnitude`

In this example, the [`geohash()`](https://library.humio.com/data-analysis/functions-geohash.html) function is used to calculate the geohash values for London. Note that the values of latitude and longitude coordinates must be expressed in decimal degrees. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         londonLat := 51.507222
         | londonLon := -0.1275
         | geohash(lat=londonLat, lon=londonLon)

Calculates the geohash value of a set of coordinates extracted from the fields lat=londonLat and lon=londonLon, and returns the result in a field named _geohash. 

  3. Event Result set.




### Summary and Results

The query is used to calculate the geohash value for London (`lat`, `lon`). A geohash is used for indexing locations on maps and in databases. 

You can use the [`worldMap()`](https://library.humio.com/data-analysis/functions-worldmap.html) function to plot existing geo-coordinates (latitude/longitude) on the World Map by adding this to the query: 

`| worldMap(lat=location.latitude, lon=location.longitude)`

Sample output from the incoming example data: 

_geohash| londonLat| londonLon  
---|---|---  
gcpvj0e5m415| 51.507222| -0.1275
