# stdDev() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-stddev.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`stdDev()`](functions-stddev.html "stdDev\(\)")

Calculates the standard deviation for a field over a set of events. The result is returned in a field named _stddev

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-stddev.html#query-functions-stddev-as)|  string| optional[a] | `_stddev`|  Name of output field.   
[_`field`_](functions-stddev.html#query-functions-stddev-field)[b]| string| required |  |  Field to extract a number from and calculate standard deviation over.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-stddev.html#query-functions-stddev-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-stddev.html#query-functions-stddev-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     stdDev("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     stdDev(field="value")
> 
> These examples show basic structure only.

### [`stdDev()`](functions-stddev.html "stdDev\(\)") Syntax Examples

Find the standard deviation of bytes send in http responses 

logscale
    
    
    stdDevBytes := stdDev(field=bytes_sent)

### [`stdDev()`](functions-stddev.html "stdDev\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Standard Deviation of Bytes Sent

**Calculate standard deviation of Bytes sent using the[`stdDev()`](functions-stddev.html "stdDev\(\)") function **

##### Query

logscale
    
    
    stdDevBytes := stdDev(field=bytes_sent)

##### Introduction

In this example, the [`stdDev()`](functions-stddev.html "stdDev\(\)") is used to calculate how much the number of bytes sent varies from the mean value. 

Example incoming data might look like this: 

@timestamp| endpoint| bytes_sent| status_code  
---|---|---|---  
1686837825000| /api/users| 1450| 200  
1686837826000| /api/products| 8920| 200  
1686837827000| /api/orders| 1670| 200  
1686837828000| /api/payment| 12900| 500  
1686837829000| /api/users| 1560| 200  
1686837830000| /api/items| 780| 200  
1686837831000| /api/orders| 9340| 200  
1686837832000| /api/checkout| 9230| 200  
1686837833000| /api/products| 1340| 200  
1686837834000| /api/users| 4450| 200  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         stdDevBytes := stdDev(field=bytes_sent)

Calculates the standard deviation of values in the bytes_sent field and assigns the result to a new field named stdDevBytes. 

The [`stdDev()`](functions-stddev.html "stdDev\(\)") function measures how widely the values are dispersed from their average value. 

  3. Event Result set.




##### Summary and Results

The query is used to understand the variability in the size of data being transferred. 

This query is useful, for example, to identify unusual patterns in data transfer sizes, establish normal ranges for network traffic, or detect anomalies in data transmission. 

Sample output from the incoming example data: 

stdDevBytes  
---  
4289.32  
  
Note that the result is a single value representing the standard deviation. A higher value indicates greater variation in the data. 

The unit of measurement is the same as the input field (bytes in this case).
