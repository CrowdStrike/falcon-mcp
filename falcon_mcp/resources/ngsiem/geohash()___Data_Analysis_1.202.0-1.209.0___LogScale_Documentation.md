# geohash() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-geohash.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`geohash()`](functions-geohash.html "geohash\(\)")

Calculates a geohash value given two fields representing latitude and longitude. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-geohash.html#query-functions-geohash-as)|  string| optional[a] | `_geohash`|  The name of the field that is produced by the function.   
[_`lat`_](functions-geohash.html#query-functions-geohash-lat)|  string| optional[[a]](functions-geohash.html#ftn.table-functions-geohash-optparamfn) | `ip.lat`|  The field to use for latitude.   
[_`lon`_](functions-geohash.html#query-functions-geohash-lon)|  string| optional[[a]](functions-geohash.html#ftn.table-functions-geohash-optparamfn) | `ip.lon`|  The field to use for longitude.   
[_`precision`_](functions-geohash.html#query-functions-geohash-precision)|  number| optional[[a]](functions-geohash.html#ftn.table-functions-geohash-optparamfn) | `12`|  The precision to use in the calculation. Usually 12 is enough.   
[a] Optional parameters use their default value unless explicitly set.  
  
Calculate the geohash value of a set of coordinates. 

logscale
    
    
    geohash(lat=myLatField, lon=myLonField)

### [`geohash()`](functions-geohash.html "geohash\(\)") Examples

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
