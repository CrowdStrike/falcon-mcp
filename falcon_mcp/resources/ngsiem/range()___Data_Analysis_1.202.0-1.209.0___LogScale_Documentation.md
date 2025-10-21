# range() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-range.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`range()`](functions-range.html "range\(\)")

Finds numeric range between the smallest and largest numbers for the specified field over a set of events. Result is returned in a field named _range. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-range.html#query-functions-range-as)|  string| optional[a] | `_range`|  Name of output field.   
[_`field`_](functions-range.html#query-functions-range-field)[b]| string| required |  |  Field to extract a number from.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-range.html#query-functions-range-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-range.html#query-functions-range-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     range("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     range(field="value")
> 
> These examples show basic structure only.

### [`range()`](functions-range.html "range\(\)") Examples

Click + next to an example below to get the full details.

####  Find Range Between Smallest And Largest Numbers in Field

**Find numeric range between the smallest and largest numbers in specified field using the[`range()`](functions-range.html "range\(\)") function **

##### Query

logscale
    
    
    range(responsetime)

##### Introduction

In this example, the [`range()`](functions-range.html "range\(\)") function is used to find the range of the values in the field responsetime. 

Example incoming event data might look like this: 

timestamp| endpoint| responsetime  
---|---|---  
2025-04-30T07:00:00Z| /api/users| 0.125  
2025-04-30T07:00:01Z| /api/login| 2.543  
2025-04-30T07:00:02Z| /api/data| 0.891  
2025-04-30T07:00:03Z| /api/users| 1.234  
2025-04-30T07:00:04Z| /api/search| 3.456  
2025-04-30T07:00:05Z| /api/login| 0.567  
2025-04-30T07:00:06Z| /api/data| 1.789  
2025-04-30T07:00:07Z| /api/users| 0.234  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         range(responsetime)

Finds the range of the values in the field responsetime, and returns the result in a field named _range. The [`range()`](functions-range.html "range\(\)") function always returns a single number (the difference between maximum and minimum). 

  3. Event Result set.




##### Summary and Results

The query is used to calculate the difference between the highest and lowest values in the field responsetime across a set of events. Finding the range of responsetime in LogScale is particularly useful for performance analysis to identify performance inconsistancies. A small range indicates consistent performance, while a large range suggests reliability issues. 

The [`range()`](functions-range.html "range\(\)") function is commonly used with [`groupBy()`](functions-groupby.html "groupBy\(\)") for comparative analysis. See [ Find Range of CPU Usage by Host](https://library.humio.com/examples/examples-range-groupby-cpu.html). 

Sample output from the incoming example data: 

_range  
---  
3.331  
  
####  Find Range of CPU Usage by Host

**Find numeric range between the smallest and largest numbers in specified field using the[`range()`](functions-range.html "range\(\)") function with [`groupBy()`](functions-groupby.html "groupBy\(\)") **

##### Query

logscale
    
    
    groupBy([host], function=range(cpu_usage))

##### Introduction

In this example, the [`range()`](functions-range.html "range\(\)") function is used to find the CPU usage by host by finding the range of the values in the field cpu_usage. 

Example incoming event data might look like this: 

timestamp| host| cpu_usage  
---|---|---  
2025-04-30T07:00:00Z| host1.com| 50  
2025-04-30T07:01:00Z| host1.com| 75  
2025-04-30T07:02:00Z| host1.com| 95  
2025-04-30T07:03:00Z| host1.com| 65  
2025-04-30T07:00:00Z| host2.com| 50  
2025-04-30T07:01:00Z| host2.com| 70  
2025-04-30T07:02:00Z| host2.com| 55  
2025-04-30T07:03:00Z| host2.com| 65  
2025-04-30T07:00:00Z| host3.com| 25  
2025-04-30T07:01:00Z| host3.com| 100  
2025-04-30T07:02:00Z| host3.com| 45  
2025-04-30T07:03:00Z| host3.com| 80  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy([host], function=range(cpu_usage))

Groups events by host name in the field host ([host]), then calculates the range (the difference) between highest CPU usage value and lowest CPU usage value for each host, returning the results in a new field named _range. 

The [`range()`](functions-range.html "range\(\)") function always returns a single number (the difference between maximum and minimum). 

  3. Event Result set.




##### Summary and Results

The query is used to find the CPU usage by host. The smaller the range (0-20), the more stable is the system. 

Sample output from the incoming example data: 

host| _range  
---|---  
host1.com| 45  
host2.com| 20  
host3.com| 75
