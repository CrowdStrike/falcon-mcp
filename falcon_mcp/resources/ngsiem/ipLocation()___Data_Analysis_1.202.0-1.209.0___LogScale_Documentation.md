# ipLocation() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-iplocation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`ipLocation()`](functions-iplocation.html "ipLocation\(\)")

The [`ipLocation()`](functions-iplocation.html "ipLocation\(\)") function adds geolocation data for IPv4 or IPv6 addresses. It adds the following 4 fields (attributes) to the events (ip prefix is default): ip.country, ip.city, ip.lon, and ip.lat. 

LogScale includes GeoLite2 data created by [MaxMind](https://www.maxmind.com/en/home). By default, the database is automatically updated if the cluster is running with a valid LogScale license. 

### Note

Updates to the MaxMind database are checked every 5 minutes. 

Only the paid version of the MaxMind database includes city information as well as country information. Some IP addresses only show country information regardless of the MaxMind database version used, in case the city information is unknown. 

### Note

For self-hosted customers, in order to use your own MaxMind database, place it in the LogScale data directory as `IpLocationDb.mmdb` and run LogScale with environment variable [`AUTO_UPDATE_IP_LOCATION_DB`](https://library.humio.com/falcon-logscale-self-hosted/envar-auto_update_ip_location_db.html) set to false. Ensure that the database includes city information (for example, GeoLite2 City). For more information, see [MaxMind Configuration](https://library.humio.com/deployment/configuration-maxmind.html). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-iplocation.html#query-functions-iplocation-as)|  string| optional[a] |  |  Name the prefix to add to fields added by the ipLocation function. Defaults to `.` (the name of the field from which to get the IP address).   
[_`field`_](functions-iplocation.html#query-functions-iplocation-field)[b]| string| optional[[a]](functions-iplocation.html#ftn.table-functions-iplocation-optparamfn) | `ip`|  The field from which to get the IP address.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-iplocation.html#query-functions-iplocation-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-iplocation.html#query-functions-iplocation-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     ipLocation("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     ipLocation(field="value")
> 
> These examples show basic structure only.

### [`ipLocation()`](functions-iplocation.html "ipLocation\(\)") Syntax Examples

Based on the field ip, the attributes ip.country, ip.city, ip.lon and ip.lat are added to the event. The default field is ip. 

logscale
    
    
    ipLocation()

Based on the field address, the attributes address.country, address.city, address.lon and address.lat are added to the event. The [_`field`_](functions-iplocation.html#query-functions-iplocation-field) parameter is used in the following example: 

logscale
    
    
    ipLocation(field=address)

Based on the field ip, the attributes address.country, address.city, address.lon and address.lat are added to the event. The [_`as`_](functions-iplocation.html#query-functions-iplocation-as) parameter is used in the following example: 

logscale
    
    
    ipLocation(as=address)

### [`ipLocation()`](functions-iplocation.html "ipLocation\(\)") Examples

Click + next to an example below to get the full details.

#### Retrieve Location Data From Specified Field

**Retrieve location data from a specified field using the[`ipLocation()`](functions-iplocation.html "ipLocation\(\)") function **

##### Query

logscale
    
    
    ipLocation(field=@rawstring)

##### Introduction

In this example, the [`ipLocation()`](functions-iplocation.html "ipLocation\(\)") function is used with the [_`field`_](functions-iplocation.html#query-functions-iplocation-field) parameter to retrieve location data from the @rawstring field. The default prefix value in the [_`field`_](functions-iplocation.html#query-functions-iplocation-field) parameter is `ip`, but with the [_`field`_](functions-iplocation.html#query-functions-iplocation-field) parameter 

defined as @rawstring, then the prefix will be `@rawstring`. 

Example incoming data might look like this: 

@rawstring  
---  
165.225.194.1  
1.2.3.4  
4.3.2.1  
8.8.8.8  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         ipLocation(field=@rawstring)

Retrieves location data from the @rawstring field, and adds the fields @rawstring.country, @rawstring.city, @rawstring.lon, and @rawstring.lat to the event. 

  3. Event Result set.




##### Summary and Results

The query is used to retrieve location data from the @rawstring field also adding more geolocation information to the events, such as Country, City, Longitude, and Latitude. The function automatically enriches the events with standardized location data, which enables consistent geographic analysis across the logs. This is, for example, useful for detection of suspicious access patterns from unexpected locations. 

Sample output from the incoming example data: 

@rawstring| @rawstring.city| @rawstring.country| @rawstring.lat| @rawstring.lon  
---|---|---|---|---  
165.225.194.1| Copenhagen| DK| 55.674| 12.5696  
1.2.3.4| <no value>| AU| -33.494| 143.2104  
4.3.2.1| <no value>| US| 37.751| -97.822  
8.8.8.8| <no value>| US| 37.751| -97.822
