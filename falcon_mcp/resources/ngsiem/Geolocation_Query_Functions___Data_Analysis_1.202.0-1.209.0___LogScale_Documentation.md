# Geolocation Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-geolocation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Geolocation Query Functions

LogScale's Geolocation related functions format or convert geographical data points. 

**Table: Event and Geolocation Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`geography:distance([as], lat1, lat2, lon1, lon2)`](functions-geography-distance.html "geography:distance\(\)")|  |  |  Calculates the distance between two geographical coordinates along an ideal earth surface.   
[`geohash([as], [lat], [lon], [precision])`](functions-geohash.html "geohash\(\)")|  |  |  Calculates a geohash value given two fields representing latitude and longitude.   
[`ipLocation([as], [field])`](functions-iplocation.html "ipLocation\(\)")| [_`field`_](functions-iplocation.html#query-functions-iplocation-field)|  |  Determines country, city, longitude, and latitude for given IP address.
