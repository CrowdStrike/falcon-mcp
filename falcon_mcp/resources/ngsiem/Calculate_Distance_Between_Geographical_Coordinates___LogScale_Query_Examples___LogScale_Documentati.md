# Calculate Distance Between Geographical Coordinates | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-geographydistance-haversine.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Distance Between Geographical Coordinates

Calculate the distance between two geographical coordinates using the [`geography:distance()`](https://library.humio.com/data-analysis/functions-geography-distance.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    londonLat := 51.507222
    | londonLon := -0.1275
    | tokyoLat := 35.689722
    | tokyoLon := 139.692222
    | distance := geography:distance(lat1=londonLat, lon1=londonLon, lat2=tokyoLat, lon2=tokyoLon)

### Introduction

The [`geography:distance()`](https://library.humio.com/data-analysis/functions-geography-distance.html) function can be used to calculate the distance between two geographical coordinates (`lat1`, `lon1`) and (`lat2`, `lon2`) along an ideal earth surface. 

It uses the Haversine approximation, which is accurate to about 0.5%, to calculate the great-circle distance between the two points. Note that it does not take the altitude into account. 

In this example, the [`geography:distance()`](https://library.humio.com/data-analysis/functions-geography-distance.html) function is used to calculate the distance in meters between London and Tokyo using geographical coordinates. 

Note that the values of latitude and longitude coordinates must be expressed in decimal degrees. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         londonLat := 51.507222
         | londonLon := -0.1275
         | tokyoLat := 35.689722
         | tokyoLon := 139.692222
         | distance := geography:distance(lat1=londonLat, lon1=londonLon, lat2=tokyoLat, lon2=tokyoLon)

Calculates the distance between two points on Earth (in this example, London and Tokyo) given their latitude and longitude, and returns the result in a field named distance. By default, the distance is returned in meters. 

Using the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function, it is possible to convert the result to kilometers for easier interpretation by adding the following to the query: `| eval(_distanceKm = distance / 1000)`. This will return the results in a field named _distanceKm. 

  3. Event Result set.




### Summary and Results

The query is used to calculate the distance between two geographical coordinates (`lat1`, `lon1`) and (`lat2`, `lon2`) along an ideal earth surface. 

In this example, the parameters [_`lat1`_](https://library.humio.com/data-analysis/functions-geography-distance.html#query-functions-geography-distance-lat1) and [_`lon1`_](https://library.humio.com/data-analysis/functions-geography-distance.html#query-functions-geography-distance-lon1) are the coordinates of the first point (London), and the parameters [_`lat2`_](https://library.humio.com/data-analysis/functions-geography-distance.html#query-functions-geography-distance-lat2) and [_`lon2`_](https://library.humio.com/data-analysis/functions-geography-distance.html#query-functions-geography-distance-lon2) are the coordinates of the second point (Tokyo). 

Sample output from the incoming example data: 

distance| londonLat| londonLon| tokyoLat| tokyoLon  
---|---|---|---|---  
9558729.514524894| 51.507222| -0.1275| 35.689722| 139.692222  
  
Sample output from the incoming example data when converted to kilometers: 

londonLat| londonLon| tokyoLat| tokyoLon| _distanceKm  
---|---|---|---|---  
51.507222| -0.1275| 35.689722| 139.692222| 9558.73 km  
  
Geographical calculations can be useful in log analysis involving location data, network traffic analysis across global infrastructure, or any scenario where geographical distance is relevant.
