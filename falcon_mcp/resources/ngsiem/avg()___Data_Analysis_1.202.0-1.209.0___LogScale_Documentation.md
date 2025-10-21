# avg() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-avg.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`avg()`](functions-avg.html "avg\(\)")

Calculates the average for a field over a set of events. The result is returned in a field named _avg. You can use this field name to pipe the results to other query functions for further processing, as shown in the example below. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-avg.html#query-functions-avg-as)|  string| optional[a] | `_avg`|  The optional name of the output field.   
[_`field`_](functions-avg.html#query-functions-avg-field)[b]| string| required |  |  The field from which to extract a number and calculate the average.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-avg.html#query-functions-avg-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-avg.html#query-functions-avg-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     avg("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     avg(field="value")
> 
> These examples show basic structure only.

### [`avg()`](functions-avg.html "avg\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Average of Field Values in an Array

**Calculate Average of Field Values in a flat array using the[`array:reduceRow()`](functions-array-reducerow.html "array:reduceRow\(\)") function **

##### Query

logscale
    
    
    array:reduceRow("ages[]", var=x, function=avg(x))

##### Introduction

In this example, the [`array:reduceRow()`](functions-array-reducerow.html "array:reduceRow\(\)") function is used to calculate the average age of the field ages and return the result in a field named _reduceRow._avg. 

Example incoming data might look like this: 

ages[0]| ages[1]| ages[2]  
---|---|---  
16| 32| 64  
15| 30| 45  
1| 2| 4  
89| 57| 67  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:reduceRow("ages[]", var=x, function=avg(x))

Produces two events, calculating the average value across the ages[] array for each event. The results are placed into the _avg field for each new event. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate averages for a given array for each event and is a shorthand version of using [`array:eval()`](functions-array-eval.html "array:eval\(\)") specifically for processing each event. 

Sample output from the incoming example data: 

ages[0]| ages[1]| ages[2]| _avg  
---|---|---|---  
16| 32| 64| 37.333  
15| 30| 45| 30  
1| 2| 4| 2.67  
89| 57| 67| 71  
  
Note that the evaluation is per event, for example per row of the overall table of values across the array over all events. To calculate values across the column of values, use [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)"). 

#### Calculate the Mean of CPU Time

**Calculate the sum of all numbers (mean) of the CPU time**

##### Query

logscale
    
    
    avg(field=cputimeNanos)
    | cputime := (_avg/1000000)
    | format("%,.2f", field=_avg, as=_avg)

##### Introduction

CPU time is the exact amount of time that the CPU has spent processing data for a specific program or process. In this example the [`avg()`](functions-avg.html "avg\(\)") function is used to calculate the sum of all numbers; the mean of the CPU Time. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         avg(field=cputimeNanos)

Calculates the mean of the field cputimeNanos. This can be run in the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) system repository to get the average time spent in nanoseconds for different activities. The mean is calculated by summing all of the values in the cputimeNanos field and dividing by the number of values across all events. 

  3. logscale
         
         | cputime := (_avg/1000000)

Calculates the average CPU time to milliseconds to make it easier to read. 

  4. logscale
         
         | format("%,.2f", field=_avg, as=_avg)

Overwrites the field _avg to contain the _avg field to show only two decimals. 

  5. Event Result set.




##### Summary and Results

The query is used to averaging the field containing the CPU value. This value is then piped to the [`format()`](functions-format.html "format\(\)") function, which provides a formatting code — how the field value should be formatted. In this example, it formats the value to two decimal. Calculation of CPU times is useful to determine processing power - for example if troubleshooting a system with high CPU usage. 

Sample output from the incoming example data: 

_avg  
---  
0.14  
  
#### Compute Average Value for Each Array Element With Same Index

**Compute an average value for each array element with the same index across multiple events using the[`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") **

##### Query

logscale
    
    
    maxTimes := array:reduceColumn("ages[]", var=x, function=avg(x))

##### Introduction

In this example, the [`array:reduceColumn()`](functions-array-reducecolumn.html "array:reduceColumn\(\)") function is used to find the maximum time for each array element with same index in a flat array. 

Example incoming data might look like this: 

ages[0]| ages[1]| ages[2]  
---|---|---  
16| 32| 64  
15| 30| 45  
1| 2| 4  
89| 57| 67  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         maxTimes := array:reduceColumn("ages[]", var=x, function=avg(x))

Computes the average for each array element with same index in the array and reduces it to one value, placing the result for each index into a new field _reduceColumn. 

  3. Event Result set.




##### Summary and Results

The query is used to find the maximum time for each array element with same index in a flat array. 

_reduceColumn[0]| _reduceColumn[1]| _reduceColumn[2]| _reduceColumn[3]  
---|---|---|---  
40.3| 40.3| 63.3|
