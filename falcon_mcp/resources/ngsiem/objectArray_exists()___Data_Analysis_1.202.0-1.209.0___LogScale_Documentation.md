# objectArray:exists() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-objectarray-exists.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)")

The function filters events based on array contents. It checks if an array contains at least one element that meets a specified condition. 

[`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") is useful when [`array:contains()`](functions-array-contains.html "array:contains\(\)") is not flexible enough, for example, when users want to compare the elements of the array to the values of other fields, or when they want to use query functions in the condition. 

Although [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") can be used on both flat arrays and structured arrays, for best performance, LogScale recommends using [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") only for nested arrays (for example JSON structures). For flat arrays, the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function is a recommended equivalent. For a list of functions that can be used on flat arrays, see [Array Query Functions](functions-array.html "Array Query Functions"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-objectarray-exists.html#query-functions-objectarray-exists-array)[a]| string| required |  |  Name of the array in which to search for matching elements. Must follow valid [Array Syntax](syntax-array.html "Array Syntax") for arrays. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[_`condition`_](functions-objectarray-exists.html#query-functions-objectarray-exists-condition)|  non-aggregate pipeline| required |  |  A non-aggregate pipeline. If an event passes through the pipeline, the event is included, otherwise it is excluded.   
[_`var`_](functions-objectarray-exists.html#query-functions-objectarray-exists-var)|  string| optional[b] | `input array name.`|  Name of the variable to be used in the [_`condition`_](functions-objectarray-exists.html#query-functions-objectarray-exists-condition) argument.   
[a] The parameter name [_`array`_](functions-objectarray-exists.html#query-functions-objectarray-exists-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-objectarray-exists.html#query-functions-objectarray-exists-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     objectArray:exists("value",condition=)
> 
> and:
> 
> logscale Syntax
>     
>     
>     objectArray:exists(array="value",condition=)
> 
> These examples show basic structure only.

Note that for nested arrays, the [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function must be used instead of the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function. 

### [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") Examples

Click + next to an example below to get the full details.

#### Check For Existence of Simple Values in Nested Array Using [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)")

**Check for the existence of simple values in nested array using[`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function with [`array:exists()`](functions-array-exists.html "array:exists\(\)") as filter function **

##### Query

logscale
    
    
    kvParse()
    | objectArray:exists(
    array="a[]",
    condition=array:exists(array="a.field.b[]", var=x, condition=test(x==2)))

##### Introduction

In this example, the [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function is used with the _`condition`_ argument and [`array:exists()`](functions-array-exists.html "array:exists\(\)") function to check if given values are in the array. 

The `objectArray:exist()` part handles the structured part of the example, whereas the [`array:exists()`](functions-array-exists.html "array:exists\(\)") is used within the condition to loop through the nested array. In a nested array, the outermost call must be [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)"), the inner one could in theory be either function, but LogScale recommends using [`array:exists()`](functions-array-exists.html "array:exists\(\)"). 

Example incoming data might look like this: 

a[0].field.b[0]| a[0].field.b[1]| a[1].field.b[0]| a[2].field.b[0]  
---|---|---|---  
1| <no value>| <no value>| <no value>  
1| 2| <no value>| <no value>  
<no value>| <no value>| 3| <no value>  
1| 2| 3| 4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | objectArray:exists(
         array="a[]",
         condition=array:exists(array="a.field.b[]", var=x, condition=test(x==2)))

Filters for elements in the array a[] that meet the given condition, then checks if there exists a value in the a.field.b[] array that equals `2`. 

  4. Event Result set.




##### Summary and Results

The query is used to test for the existence of simple values in nested arrays. The query outputs the events that passed the filtering condition. 

Sample output from the incoming example data: 

a[0].field.b[0]| a[0].field.b[1]| a[1].field.b[0]| a[2].field.b[0]  
---|---|---|---  
1| 2| <no value>| <no value>  
1| 2| 3| 4  
  
#### Check for AWS Resources in Vendor Array

**Filter events based on specific AWS resource ARNs using the[`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function **

##### Query

logscale
    
    
    objectArray:exists(array="Vendor.resources[]", condition={Vendor.resources.ARN="arn:aws:*"})

##### Introduction

In this example, the [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function is used to filter events where an AWS resource ARN exists within a vendor's resource array that matches a specific pattern. 

Example incoming data might look like this: 

@timestamp| Vendor.resources  
---|---  
2023-06-15T10:00:00Z, [{"ARN": "arn:aws:s3:::bucket1", "Type": "S3"}, {"ARN": "arn:aws:ec2:instance1", "Type": "EC2"}]|   
2023-06-15T10:01:00Z, [{"ARN": "arn:azure:vm1", "Type": "VM"}, {"ARN": "arn:azure:storage1", "Type": "Storage"}]|   
2023-06-15T10:02:00Z, [{"ARN": "arn:aws:lambda:function1", "Type": "Lambda"}, {"ARN": "arn:aws:s3:::bucket2", "Type": "S3"}]|   
2023-06-15T10:03:00Z, [{"ARN": "arn:gcp:instance1", "Type": "VM"}, {"ARN": "arn:gcp:storage1", "Type": "Storage"}]|   
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:exists(array="Vendor.resources[]", condition={Vendor.resources.ARN="arn:aws:*"})

Filters events by checking if any element in the Vendor.resources array contains an ARN field that matches the pattern `arn:aws:*`. The [_`array`_](functions-objectarray-exists.html#query-functions-objectarray-exists-array) parameter specifies the array to search through, and the [_`condition`_](functions-objectarray-exists.html#query-functions-objectarray-exists-condition) parameter defines the matching criteria. 

  3. Event Result set.




##### Summary and Results

The query is used to identify events that contain AWS resources by checking the ARN patterns in the resource array. The [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function filters events based on array content matching specific conditions. 

This query is useful, for example, to monitor AWS-specific resources in a multi-cloud environment, audit AWS resource usage, or filter out non-AWS resources from the analysis. 

Sample output from the incoming example data: 

@timestamp| Vendor.resources  
---|---  
2023-06-15T10:00:00Z, [{"ARN": "arn:aws:s3:::bucket1", "Type": "S3"}, {"ARN": "arn:aws:ec2:instance1", "Type": "EC2"}]|   
2023-06-15T10:02:00Z, [{"ARN": "arn:aws:lambda:function1", "Type": "Lambda"}, {"ARN": "arn:aws:s3:::bucket2", "Type": "S3"}]|   
  
Note that only events containing AWS ARNs (starting with "arn:aws:") are included in the results, while events with Azure and GCP resources are filtered out.
