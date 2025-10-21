# geography:distance() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-geography-distance.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`geography:distance()`](functions-geography-distance.html "geography:distance\(\)")

This query function will calculate the distance, in meters, between two geographical coordinates (`lat1`, `lon1`) and (`lat2`, `lon2`) along an ideal earth surface. 

It uses the Haversine approximation, which is accurate to about 0.5%. It does not take the altitude into account. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-geography-distance.html#query-functions-geography-distance-as)|  string| optional[a] | `_distance`|  The name of the field that is produced by the function.   
[_`lat1`_](functions-geography-distance.html#query-functions-geography-distance-lat1)|  string| required |  |  The field to use for latitude of first point.   
[_`lat2`_](functions-geography-distance.html#query-functions-geography-distance-lat2)|  string| required |  |  The field to use for latitude of second point.   
[_`lon1`_](functions-geography-distance.html#query-functions-geography-distance-lon1)|  string| required |  |  The field to use for longitude of first point.   
[_`lon2`_](functions-geography-distance.html#query-functions-geography-distance-lon2)|  string| required |  |  The field to use for longitude of second point.   
[a] Optional parameters use their default value unless explicitly set.  
  
### Note

The values of latititude and longitude coordinates must be expressed in decimal degrees. 

### [`geography:distance()`](functions-geography-distance.html "geography:distance\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Distance Between Geographical Coordinates

**Calculate the distance between two geographical coordinates using the[`geography:distance()`](functions-geography-distance.html "geography:distance\(\)") function **

##### Query

logscale
    
    
    londonLat := 51.507222
    | londonLon := -0.1275
    | tokyoLat := 35.689722
    | tokyoLon := 139.692222
    | distance := geography:distance(lat1=londonLat, lon1=londonLon, lat2=tokyoLat, lon2=tokyoLon)

##### Introduction

In this example, the [`geography:distance()`](functions-geography-distance.html "geography:distance\(\)") function is used to calculate the distance in meters between London and Tokyo using geographical coordinates. 

Note that the values of latitude and longitude coordinates must be expressed in decimal degrees. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         londonLat := 51.507222
         | londonLon := -0.1275
         | tokyoLat := 35.689722
         | tokyoLon := 139.692222
         | distance := geography:distance(lat1=londonLat, lon1=londonLon, lat2=tokyoLat, lon2=tokyoLon)

Calculates the distance between two points on Earth (in this example, London and Tokyo) given their latitude and longitude, and returns the result in a field named distance. By default, the distance is returned in meters. 

Using the [`eval()`](functions-eval.html "eval\(\)") function, it is possible to convert the result to kilometers for easier interpretation by adding the following to the query: `| eval(_distanceKm = distance / 1000)`. This will return the results in a field named _distanceKm. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate the distance between two geographical coordinates (`lat1`, `lon1`) and (`lat2`, `lon2`) along an ideal earth surface. 

In this example, the parameters [_`lat1`_](functions-geography-distance.html#query-functions-geography-distance-lat1) and [_`lon1`_](functions-geography-distance.html#query-functions-geography-distance-lon1) are the coordinates of the first point (London), and the parameters [_`lat2`_](functions-geography-distance.html#query-functions-geography-distance-lat2) and [_`lon2`_](functions-geography-distance.html#query-functions-geography-distance-lon2) are the coordinates of the second point (Tokyo). 

Sample output from the incoming example data: 

distance| londonLat| londonLon| tokyoLat| tokyoLon  
---|---|---|---|---  
9558729.514524894| 51.507222| -0.1275| 35.689722| 139.692222  
  
Sample output from the incoming example data when converted to kilometers: 

londonLat| londonLon| tokyoLat| tokyoLon| _distanceKm  
---|---|---|---|---  
51.507222| -0.1275| 35.689722| 139.692222| 9558.73 km  
  
Geographical calculations can be useful in log analysis involving location data, network traffic analysis across global infrastructure, or any scenario where geographical distance is relevant.
