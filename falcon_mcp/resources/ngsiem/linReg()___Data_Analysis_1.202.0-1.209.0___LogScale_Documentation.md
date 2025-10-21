# linReg() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-linreg.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Apr 8, 2025

## [`linReg()`](functions-linreg.html "linReg\(\)")

The [`linReg()`](functions-linreg.html "linReg\(\)") function calculates a linear relationship between two variables by using least-squares fitting. 

The function creates this relationship between x and y variables: 

logscale
    
    
    y = slope * x + intercept

The result is outputted in fields named _slope and _intercept — unless a different prefix than _ is specified. 

Also outputted is the adjusted R-squared value in a field named _r2 and the number of data points in a field named _n. 

These four key values indicate relationship strength and reliability. 

Note that if all x values are the same or if all y values are the same, then the function cannot calculate results, therefore, nothing is outputted. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`prefix`_](functions-linreg.html#query-functions-linreg-prefix)|  string| optional[a] | `_`|  Prefix for all output field names.   
[_`x`_](functions-linreg.html#query-functions-linreg-x)|  string| required |  |  Specifies the field name that contains the independent variable.   
[_`y`_](functions-linreg.html#query-functions-linreg-y)|  string| required |  |  Specifies the field name that contains the dependent variable.   
[a] Optional parameters use their default value unless explicitly set.  
  
### [`linReg()`](functions-linreg.html "linReg\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Relationship Between X And Y Variables - Example 1 

**Calculate the linear relationship between message size and transmission time using the[`linReg()`](functions-linreg.html "linReg\(\)") function **

##### Query

logscale
    
    
    linReg(x=bytes_sent, y=send_duration)

##### Introduction

In this example, the [`linReg()`](functions-linreg.html "linReg\(\)") function is used to calculate the linear relationship between bytes_sent (`x` variable) and send_duration (`y` variable). The example shows the relationship between message size (bytes sent in a server) and transmission time (time to send the bytes). 

Example incoming data might look like this: 

@timestamp| bytes_sent| send_duration  
---|---|---  
2025-04-07 13:00:00| 1024| 0.15  
2025-04-07 13:00:01| 2048| 0.25  
2025-04-07 13:00:02| 4096| 0.45  
2025-04-07 13:00:03| 8192| 0.85  
2025-04-07 13:00:04| 512| 0.08  
2025-04-07 13:00:05| 16384| 1.65  
2025-04-07 13:00:06| 3072| 0.35  
2025-04-07 13:00:07| 6144| 0.65  
2025-04-07 13:00:08| 10240| 1.05  
2025-04-07 13:00:09| 4608| 0.48  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         linReg(x=bytes_sent, y=send_duration)

Correlates bytes_sent with send_duration, showing the relationship between message size and transmission time (the variables `x` and `y`) and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate a linear relationship between bytes_sent (`x` variable) and send_duration (`y` variable). 

Calculating the relationship between size of data transferred and time taken to send data is useful, for example, in trend analysis, performance monitoring, or anomaly detection. 

Sample output from the incoming example data: 

_slope| _intercept| _r2| _n  
---|---|---|---  
9.823069852941172E-5| 0.04276470588235326| 0.9996897336895081| 10  
  
_slope is the additional time needed per byte sent. 

_intercept is the baseline transmission time. 

_r2 is the statistical accuracy of the linear model. 

_n is the total number of data points analyzed. 

#### Calculate Relationship Between X And Y Variables - Example 2 

**Calculate the linear relationship between server load and total response size using the[`linReg()`](functions-linreg.html "linReg\(\)") function with [`bucket()`](functions-bucket.html "bucket\(\)") **

##### Query

logscale
    
    
    bucket(function=[ sum(bytes_sent, as=x), avg(server_load_pct, as=y) ])
    | linReg(x=x, y=y)

##### Introduction

In this example, the [`linReg()`](functions-linreg.html "linReg\(\)") function is used to calculate the linear relationship between bytes_sent (`x` variable) and server_load_pct (`y` variable). The example shows the relationship between server load percentage and total response size across time. 

Example incoming data might look like this: 

@timestamp| bytes_sent| server_load_pct  
---|---|---  
2024-01-15T09:00:00Z| 156780| 45.2  
2024-01-15T09:05:00Z| 234567| 52.8  
2024-01-15T09:10:00Z| 189234| 48.6  
2024-01-15T09:15:00Z| 345678| 65.3  
2024-01-15T09:20:00Z| 123456| 42.1  
2024-01-15T09:25:00Z| 278901| 58.7  
2024-01-15T09:30:00Z| 198765| 51.4  
2024-01-15T09:35:00Z| 287654| 59.2  
2024-01-15T09:40:00Z| 167890| 46.8  
2024-01-15T09:45:00Z| 298765| 61.5  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(function=[ sum(bytes_sent, as=x), avg(server_load_pct, as=y) ])

Buckets the data points by time, then calculates the sum of bytes sent for each bucket returning the result in a field named x, and calculates the average server load percentage for each bucket returning the result in a field named y. 

  3. logscale
         
         | linReg(x=x, y=y)

Correlates x with y, showing the relationship between the variables `x` and `y` and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate a linear relationship between bytes_sent (`x` variable) and server_load_pct (`y` variable). 

Calculating the relationship between server load percentage and total response size is useful to identify different operational patterns, such as, for example, performance bottlenecks, resource allocation issues, or to identify system optimization opportunities. 

Sample output from the incoming example data: 

_slope| _intercept| _r2| _n  
---|---|---|---  
0.00010617525557193158| 28.934098111407938| 0.991172367336835| 10  
  
_slope is the rate of change between server load and response size. 

_intercept is the baseline relationship value. 

_r2 is the statistical accuracy of the linear model. 

_n is the total number of data points analyzed. 

#### Calculate Relationship Between X And Y Variables - Example 3 

**Calculate the linear relationship between server load and each of several types of request types using the[`linReg()`](functions-linreg.html "linReg\(\)") function with [`bucket()`](functions-bucket.html "bucket\(\)") and [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    bucket(function=[ avg(server_load_pct, as=y), groupBy(request_type, function=count(as=x)) ])
    | groupBy(request_type, function=linReg(x=x, y=y))

##### Introduction

In this example, the [`linReg()`](functions-linreg.html "linReg\(\)") function is used to calculate the linear relationship between request_type (`x` variable) and server_load_pct (`y` variable). The example shows the relationship between server load and each of several types of HTTP request types across time. 

Example incoming data might look like this: 

@timestamp| server_load_pct| request_type  
---|---|---  
2024-01-15T09:00:00.000Z| 45.2| GET  
2024-01-15T09:00:00.000Z| 45.2| POST  
2024-01-15T09:00:00.000Z| 45.2| GET  
2024-01-15T09:05:00.000Z| 52.8| GET  
2024-01-15T09:05:00.000Z| 52.8| PUT  
2024-01-15T09:05:00.000Z| 52.8| POST  
2024-01-15T09:10:00.000Z| 48.6| GET  
2024-01-15T09:10:00.000Z| 48.6| GET  
2024-01-15T09:10:00.000Z| 48.6| DELETE  
2024-01-15T09:15:00.000Z| 65.3| POST  
2024-01-15T09:15:00.000Z| 65.3| POST  
2024-01-15T09:15:00.000Z| 65.3| GET  
2024-01-15T09:20:00.000Z| 42.1| GET  
2024-01-15T09:20:00.000Z| 42.1| PUT  
2024-01-15T09:20:00.000Z| 42.1| GET  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(function=[ avg(server_load_pct, as=y), groupBy(request_type, function=count(as=x)) ])

Buckets the data points by time, then calculates the average server load for each time bucket returning the result in a field named y. It also groups the request types in a field named request_type and makes a count of requests by type in each time bucket returning the result in a field named x. 

  3. logscale
         
         | groupBy(request_type, function=linReg(x=x, y=y))

Correlates x with y, showing the relationship between the variables `x` and `y` for each HTTP request type and outputs the results in fields named _slope (slope value),_intercept (intercept value),_r2 (adjusted R-squared value), and _n (number of data points). These four key values indicate relationship strength and reliability. 

  4. Event Result set.




##### Summary and Results

The query is used to analyze how different HTTP request types affect server load. The analysis helps identify which HTTP request types have the strongest impact on server performance. 

Sample output from the incoming example data: 

request_type| _slope| _intercept| _r2| _n  
---|---|---|---|---  
DELETE| <no value>| <no value>| <no value>| <no value>  
GET| -13.749999999999941| 72.7999999999999| 0.5941824574313592| 5  
POST| 16.29999999999992| 32.70000000000012| 0.7196207242484238| 3  
PUT| <no value>| <no value>| <no value>| <no value>  
  
_slope is the impact rate of request volume on server load. 

_intercept is the baseline server load when there are no requests of a specific type. 

_r2 is the statistical accuracy of the relationship. 

_n is the total number of data points analyzed.
