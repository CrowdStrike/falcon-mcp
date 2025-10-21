# array:union() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-union.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:union()`](functions-array-union.html "array:union\(\)")

### Important

This function is considered experimental and under active development and should not be used in production. 

The function must be enabled using the feature flag ArrayFunctions. See [Enabling & Disabling Feature Flags](https://library.humio.com/deployment/configuration-enabling-features.html). 

Determines the set union of array values over input events. 

Used to compute the values that occur in any of the events supplied to this function. The output order of the values is not defined. If no arrays are found, the output is empty. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-union.html#query-functions-array-union-array)[a]| string| required |  |  The prefix of the array in LogScale, for example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents`.   
[_`as`_](functions-array-union.html#query-functions-array-union-as)|  string| optional[b] | `_union`|  The name of the output array.   
[a] The parameter name [_`array`_](functions-array-union.html#query-functions-array-union-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-union.html#query-functions-array-union-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:union("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:union(array="value")
> 
> These examples show basic structure only.

### [`array:union()`](functions-array-union.html "array:union\(\)") Examples

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

#### Find Union of Array Over multiple Events

**Find union of an array over multiple events using the[`array:union()`](functions-array-union.html "array:union\(\)") function **

##### Query

logscale
    
    
    array:union(mailto, as=unique_mails)

##### Introduction

Arrays are handy when you want to work with multiple values of the same data type. The [`array:union()`](functions-array-union.html "array:union\(\)") function is used to find distinct values of an array over multiple events. One important feature of UNION is, that it removes duplicate rows from the combined data meaning if there are repetitions, then only one element occurrence should be in the union. 

Example incoming data might look like this: 

mailto[0]| mailto[1]  
---|---  
foo@example.com| bar@example.com  
bar@example.com|   
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         array:union(mailto, as=unique_mails)

Searches in the mailto array across multiple events and returns the union of element values in a new array, where the unique emails will appear only once. In this case creating a unique list of email addresses in a single array. 

  3. Event Result set.




##### Summary and Results

The query is used to search for and eliminate duplicates of e-mail addresses in arrays/combined datasets. 

Sample output from the incoming example data: 

unique_mails[0]| unique_mails[1]  
---|---  
bar@example.com| foo@example.com
