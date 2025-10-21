# worldMap() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-worldmap.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`worldMap()`](functions-worldmap.html "worldMap\(\)")

A helper function to produce data compatible with the World Map widget. It takes either IP addresses or lat/lon as input and buckets points using a geohashing algorithm. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`ip`_](functions-worldmap.html#query-functions-worldmap-ip)|  string| optional[a] |  |  The field containing the IP address to look up geo-coordinates for.   
[_`lat`_](functions-worldmap.html#query-functions-worldmap-lat)|  string| optional[[a]](functions-worldmap.html#ftn.table-functions-worldmap-optparamfn) |  |  A field containing the latitude to use for geohash bucketing.   
[_`lon`_](functions-worldmap.html#query-functions-worldmap-lon)|  string| optional[[a]](functions-worldmap.html#ftn.table-functions-worldmap-optparamfn) |  |  A field containing the longitude to use for geohash bucketing.   
[_`magnitude`_](functions-worldmap.html#query-functions-worldmap-magnitude)|  aggregate| optional[[a]](functions-worldmap.html#ftn.table-functions-worldmap-optparamfn) | `count(as=_count)`|  A function used to calculate the magnitude (weight) of each bucket. This value is used to determine the size or opacity of the world map markers.   
[_`precision`_](functions-worldmap.html#query-functions-worldmap-precision)|  number| optional[[a]](functions-worldmap.html#ftn.table-functions-worldmap-optparamfn) | `4`|  The precision to use in the calculation of the embedded geohash. Usually 4 is fine for a full globe, 12 is for a small area of zoom.   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`worldMap()`](functions-worldmap.html "worldMap\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Geohash Value of a Set of Coordinates

**Calculate a geohash value given two fields representing latitude and longitude using the [`geohash()`](functions-geohash.html "geohash\(\)") function **

##### Query

logscale
    
    
    londonLat := 51.507222
    | londonLon := -0.1275
    | geohash(lat=londonLat, lon=londonLon)

##### Introduction

In this example, the [`geohash()`](functions-geohash.html "geohash\(\)") function is used to calculate the geohash values for London. Note that the values of latitude and longitude coordinates must be expressed in decimal degrees. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         londonLat := 51.507222
         | londonLon := -0.1275
         | geohash(lat=londonLat, lon=londonLon)

Calculates the geohash value of a set of coordinates extracted from the fields lat=londonLat and lon=londonLon, and returns the result in a field named _geohash. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate the geohash value for London (`lat`, `lon`). A geohash is used for indexing locations on maps and in databases. 

You can use the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function to plot existing geo-coordinates (latitude/longitude) on the World Map by adding this to the query: 

`| worldMap(lat=location.latitude, lon=location.longitude)`

Sample output from the incoming example data: 

_geohash| londonLat| londonLon  
---|---|---  
gcpvj0e5m415| 51.507222| -0.1275  
  
#### Make Data Compatible With World Map Widget - Example 1

**Make data compatible with[World Map](widgets-worldmap.html "World Map") using the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function and magnitude **

##### Query

logscale
    
    
    worldMap(ip=myIpField)

##### Introduction

In this example, the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function takes IP addresses and buckets points using the magnitude, the number of observations in each bucket. 

The [`worldMap()`](functions-worldmap.html "worldMap\(\)") function will automatically bucket the locations to reduce the number of points. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         worldMap(ip=myIpField)

Plots IP addresses on the world map. `ip=myIpField` specifies which field contains IP addresses. The magnitude is the number of observations in each bucket (the default) - the count of IP addresses per location. 

  3. Event Result set.




##### Summary and Results

The query with the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function is used to visualize and present location data, in this case IP addresses and their geo-coordinates, in a [World Map](widgets-worldmap.html "World Map"). 

Visualization of IP addresses on a global map is useful, for example, to show concentration/density of IPs by location, to visualize attack sources, to monitor user access locations, to track network traffic origins, or identify suspicious geographic patterns. 

#### Make Data Compatible With World Map Widget - Example 2

**Make data compatible with[World Map](widgets-worldmap.html "World Map") using the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function and geo-coordinates **

##### Query

logscale
    
    
    worldMap(lat=location.latitude, lon=location.longitude)

##### Introduction

In this example, the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function takes either IP addresses or geo-coordinates (latitude/longitude) as input and buckets points using a geohashing algorithm. 

The [`worldMap()`](functions-worldmap.html "worldMap\(\)") function will automatically bucket the locations to reduce the number of points. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         worldMap(lat=location.latitude, lon=location.longitude)

Plots existing geo-coordinates (latitude/longitude) on the world map. 

  3. Event Result set.




##### Summary and Results

The query with the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function is used to visualize and present location data, in this case IP addresses and their exact geo-coordinates, in a [World Map](widgets-worldmap.html "World Map"). 

Visualization of IP addresses and their exact geo-coordinates on a global map is more accurate and useful in cases where high precision is required, for example for physical asset tracking. 

#### Make Data Compatible With World Map Widget - Example 3

**Make data compatible with[World Map](widgets-worldmap.html "World Map") using the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function and average latency as magnitude of the points **

##### Query

logscale
    
    
    worldMap(ip=myIpField, magnitude=avg(latency))

##### Introduction

In this example, the `worldMap` function is used with the `magnitude` function to calculate the magnitude (weight) of each bucket. This value is used to determine the size or opacity of the world map markers. 

The [`worldMap()`](functions-worldmap.html "worldMap\(\)") function will automatically bucket the locations to reduce the number of points. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         worldMap(ip=myIpField, magnitude=avg(latency))

Plots IP addresses on the world map and uses average latency as magnitude of the points. 

  3. Event Result set.




##### Summary and Results

The query with the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function is used to visualize and present location data, in this example IP addresses and the average latency, in a [World Map](widgets-worldmap.html "World Map"). The query is useful, for example, to identify performance patterns based on latency across different regions, or to identify potential network bottlenecks or performance issues in specific locations. 

Visualization of IP addresses and average latency values on a global map is useful in network monitoring and performance analysis to quickly spot geographical patterns in network latency. Larger average latency values will create bigger/more intense points on the world map.
