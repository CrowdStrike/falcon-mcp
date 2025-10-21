# splitString() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-splitstring.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`splitString()`](functions-splitstring.html "splitString\(\)")

Splits a string using a regular expression into an array of values. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-splitstring.html#query-functions-splitstring-as)|  string| optional[a] | `_splitstring`|  Emit selected attribute using this name.   
[_`by`_](functions-splitstring.html#query-functions-splitstring-by)|  string| required |  |  String or regular expression to split by.   
[_`field`_](functions-splitstring.html#query-functions-splitstring-field)[b]| string| optional[[a]](functions-splitstring.html#ftn.table-functions-splitstring-optparamfn) | `@rawstring`|  Field that needs splitting.   
[_`index`_](functions-splitstring.html#query-functions-splitstring-index)|  number| optional[[a]](functions-splitstring.html#ftn.table-functions-splitstring-optparamfn) |  |  Emit only this index after splitting. Can be negative; -1 designates the last element.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-splitstring.html#query-functions-splitstring-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-splitstring.html#query-functions-splitstring-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     splitString("value",by="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     splitString(field="value",by="value")
> 
> These examples show basic structure only.

### [`splitString()`](functions-splitstring.html "splitString\(\)") Syntax Examples

Assuming an event has the @rawstring="2007-01-01 test bar" you can split the string into fields part[0], part[1], and part[2]: 

logscale Syntax
    
    
    ...
    | part := splitString(field=@rawstring, by=" ")

Assuming an event has [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring): 

accesslog
    
    
    2007-01-01 test bar

You can split pick out the date part using: 

logscale Syntax
    
    
    ...
    | date := splitString(field=@rawstring, by=" ", index=0)

Assuming an event has [@rawstring](searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring): 
    
    
    <2007-01-01>test;bar

You can split the string into attributes part[0], part[1], and part[2]. In this case, the splitting string is a regex specifying any one of the characters <, >, or ;

logscale Syntax
    
    
    ...
    | part := splitString(field=@rawstring, by="[<>;]")

Split an event into multiple events by newlines. The first function [`splitString()`](functions-splitstring.html "splitString\(\)") creates @rawstring[0], @rawstring[1], ... for each line, and the following [`split()`](functions-split.html "split\(\)") creates the multiple events from the array of rawstrings. 

logscale Syntax
    
    
    ...
    | splitString(by="\n", as=@rawstring)
    | split(@rawstring)

Split the value of a string field into individual characters: 

logscale
    
    
    characters := splitString(my_field, by="(?!\A)(?=.)")

Split the value of a string using case-insensitive regex: 

logscale
    
    
    characters := splitString(my_field, by="(?i)(e
    | encoded
    | enc)")

Split the string using a multi-character separator. This can be used for system logs that use the multi-character separator to allow a character such as comma or colon that might otherwise be used as a separator. Because the value to the _`by`_ is a regular expression, you should use a regular expression group as the value. For example: 

logscale
    
    
    splitString(by="(\*\
    | \*)")

Splits incoming data by the string `*|*` and would correctly split the string `image.png*|*PNG*|*0755*|*john` into: 

Field| Value  
---|---  
_splitstring[0]| image.png  
_splitstring[1]| PNG  
_splitstring[2]| 0755  
_splitstring[3]| john  
  
### Note

Special characters (including asterisk and pipe) also need to be escaped. 

### [`splitString()`](functions-splitstring.html "splitString\(\)") Examples

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
