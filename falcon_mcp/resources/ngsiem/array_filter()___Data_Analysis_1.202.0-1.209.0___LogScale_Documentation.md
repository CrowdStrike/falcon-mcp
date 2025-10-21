# array:filter() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-filter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:filter()`](functions-array-filter.html "array:filter\(\)")

Filters events from the input array using the function provided in the array. 

The order is maintained in the output array. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-filter.html#query-functions-array-filter-array)[a]| string| required |  |  A string in the format of a valid array followed by `[]`. A valid array can either be an identifier, a valid array followed by `.` and an identifier, or a valid array followed by an array index surrounded by square brackets. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]` .   
[_`asArray`_](functions-array-filter.html#query-functions-array-filter-asarray)|  string| optional[b] |  |  The output array. Defaults to the value passed to the [_`array`_](functions-array-filter.html#query-functions-array-filter-array) parameter.   
[_`function`_](functions-array-filter.html#query-functions-array-filter-function)|  non-aggregate function| required |  |  The function to use for filtering events in the array.   
[_`var`_](functions-array-filter.html#query-functions-array-filter-var)|  string| optional[[b]](functions-array-filter.html#ftn.table-functions-array-filter-optparamfn) | `input array name`|  Name of the variable to be used in the [_`function`_](functions-array-filter.html#query-functions-array-filter-function) argument.   
[a] The parameter name [_`array`_](functions-array-filter.html#query-functions-array-filter-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-filter.html#query-functions-array-filter-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:filter("value",function="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:filter(array="value",function="value")
> 
> These examples show basic structure only.

### [`array:filter()`](functions-array-filter.html "array:filter\(\)") Examples

Click + next to an example below to get the full details.

#### Deduplicate Compound Field Data With [`array:union()`](functions-array-union.html "array:union\(\)") and [`split()`](functions-split.html "split\(\)")

****

##### Query

logscale
    
    
    splitString(field=userAgent,by=" ",as=agents)
    |array:filter(array="agents[]", function={bname=/\//}, var="bname")
    |array:union(array=agents,as=browsers)
    | split(browsers)

##### Introduction

Deduplicating fields of information where there are multiple occurrences of a value in a single field, maybe separated by a single character can be achieved in a variety of ways. This solution uses [`array:union()`](functions-array-union.html "array:union\(\)") and `split` create a unique array and then split the content out to a unique list. 

For example, when examining the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) and looking for the browsers or user agents that have used your instance, the `UserAgent` data will contain the browser and toolkits used to support them, for example: 

Raw Events

Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36  
---  
  
The actual names are the `Name/Version` pairs showing compatibility with different browser standards. Resolving this into a simplified list requires splitting up the list, simplifying (to remove duplicates), filtering, and then summarizing the final list. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         splitString(field=userAgent,by=" ",as=agents)

First we split up the userAgent field using a call to [`splitString()`](functions-splitstring.html "splitString\(\)") and place the output into the array field agents

This will create individual array entries into the agents array for each event: 

agents[0]| agents[1]| agents[2]| agents[3]| agents[4]| agents[5]| agents[6]| agents[7]| agents[8]| agents[9]| agents[10]| agents[11]| agents[12]  
---|---|---|---|---|---|---|---|---|---|---|---|---  
Mozilla/5.0| (Macintosh;| Intel| Mac| OS| X| 10_15_7)| AppleWebKit/537.36| (KHTML,| like| Gecko)| Chrome/116.0.0.0| Safari/537.36  
  
  3. logscale
         
         |array:filter(array="agents[]", function={bname=/\//}, var="bname")

  4. logscale
         
         |array:union(array=agents,as=browsers)

Using [`array:union()`](functions-array-union.html "array:union\(\)") we aggregate the list of user agents across all the events to create a list of unique entries. This will eliminate duplicates where the value of the user agent is the same value. 

The event data now looks like this: 

browsers[0]| browsers[1]| browsers[2]  
---|---|---  
Gecko/20100101| Safari/537.36| AppleWebKit/605.1.15  
  
An array of the individual values. 

  5. logscale
         
         | split(browsers)

Using the [`split()`](functions-split.html "split\(\)") will split the array into individual events, turning: 

browsers[0]| browsers[1]| browsers[2]  
---|---|---  
Gecko/20100101| Safari/537.36| AppleWebKit/605.1.15  
  
into: 

_index| row[1]  
---|---  
0| Gecko/20100101  
1| Safari/537.36  
2| AppleWebKit/605.1.15  
  
  6. Event Result set.




##### Summary and Results

The resulting output from the query is a list of events with each event containing a matching _index and browser. This can be useful if you want to perform further processing on a list of events rather than an array of values. 

#### Filter an Array on a Given Condition

**Filter the elements of a flat array on a given condition using the array filter function[`array:filter()`](functions-array-filter.html "array:filter\(\)") **

##### Query

logscale
    
    
    array:filter(array="mailto[]", var="addr", function={addr=ba*@example.com}, asArray="out[]")

##### Introduction

It is possible to filter an array on a given condition using the array filter function [`array:filter()`](functions-array-filter.html "array:filter\(\)"). The [`array:filter()`](functions-array-filter.html "array:filter\(\)") creates a new array with elements matching the specified conditions and does not change the original array. The new array will retain the original order. 

Example incoming data might look like this: 

logscale
    
    
    mailto[0]=foo@example.com
    mailto[1]=bar@example.com
    mailto[2]=baz@example.com

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:filter(array="mailto[]", var="addr", function={addr=ba*@example.com}, asArray="out[]")

Filters the mailto[] array to include only elements that contain the value `ba*@example.com`, this is achieved by testing the value of each element of the array, set by the [_`var`_](functions-array-filter.html#query-functions-array-filter-var) parameter as `addr`, returning a new array that only contains elements that meet the specified condition. The expression in the [_`function`_](functions-array-filter.html#query-functions-array-filter-function) argument should contain the field declared in the _`addr`_ parameter. 

  3. Event Result set.




##### Summary and Results

The query is used to filter values from the input array using the function provided in the array and return a new array with the results meeting the specified condition. 

Sample output from the incoming example data: 

logscale
    
    
    out[0]=bar@example.com
    out[1]=baz@example.com
