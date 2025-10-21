# array:exists() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-array-exists.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`array:exists()`](functions-array-exists.html "array:exists\(\)")

The function filters events based on array contents. It checks if an array contains at least one element that meets a specified condition. 

The [`array:exists()`](functions-array-exists.html "array:exists\(\)") function is useful when [`array:contains()`](functions-array-contains.html "array:contains\(\)") is not flexible enough, for example, when users want to compare the elements of the array to the values of other fields or when they want to use query functions in the condition. 

### Note

It is recommended to use the [`array:contains()`](functions-array-contains.html "array:contains\(\)") function to check for simple values. See [`array:contains()`](functions-array-contains.html "array:contains\(\)"). 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`array`_](functions-array-exists.html#query-functions-array-exists-array)[a]| string| required |  |  Name of the array in which to search for matching elements. Must follow valid [Array Syntax](syntax-array.html "Array Syntax") for array of scalars. For example, for events with fields `incidents[0], incidents[1], ...` this would be `incidents[]`.   
[_`condition`_](functions-array-exists.html#query-functions-array-exists-condition)|  non-aggregate pipeline| required |  |  A non-aggregate pipeline. If an event passes through the pipeline, the event is included, otherwise it is excluded.   
[_`var`_](functions-array-exists.html#query-functions-array-exists-var)|  string| optional[b] | `input array name.`|  Name of the variable to be used in the _`condition`_ argument.   
[a] The parameter name [_`array`_](functions-array-exists.html#query-functions-array-exists-array) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`array`_](functions-array-exists.html#query-functions-array-exists-array) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     array:exists("value",condition=)
> 
> and:
> 
> logscale Syntax
>     
>     
>     array:exists(array="value",condition=)
> 
> These examples show basic structure only.

The [`array:exists()`](functions-array-exists.html "array:exists\(\)") function can use other filter functions, such as [`in()`](functions-in.html "in\(\)") or [`if()`](functions-if.html "if\(\)"), or pipelines. 

Note that for structured arrays, the [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)") function must be used instead of the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function. For more information, see [`objectArray:exists()`](functions-objectarray-exists.html "objectArray:exists\(\)"). For a complete list of functions for flat arrays, see [Array Query Functions](functions-array.html "Array Query Functions"). 

### [`array:exists()`](functions-array-exists.html "array:exists\(\)") Examples

Click + next to an example below to get the full details.

#### Check For Existence of Element Contained in Given List of Values

**Check for the existence of an element contained in a given list of simple values in a flat array using[`array:exists()`](functions-array-exists.html "array:exists\(\)") function with in() **

##### Query

logscale
    
    
    kvparse()
    | array:exists(array="a[]", condition=in(a, values=[3, 4]))

##### Introduction

In this example, the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function is used with the _`condition`_ argument and the filter function [`in()`](functions-in.html "in\(\)") to check if given values are in the array. 

Example incoming data might look like this: 

a[0]| a[1]  
---|---  
1| 2  
1| 3  
1| 4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvparse()

Parses the string into key value pairs. 

  3. logscale
         
         | array:exists(array="a[]", condition=in(a, values=[3, 4]))

Filters for events where the a[] array contains the values `3` or `4`. 

  4. Event Result set.




##### Summary and Results

The query is used to check for the existence of simple values in a flat array. 

Sample output from the incoming example data: 
    
    
    "a[0]","a[1]"
    "1","3"
    "1","4"

#### Check For Existence of Element Larger Than Given Number

**Check for the existence of an element larger than a given number in a flat array using[`array:exists()`](functions-array-exists.html "array:exists\(\)") function **

##### Query

logscale
    
    
    kvparse()
    | array:exists(array="a[]", condition={a>2})

##### Introduction

In this example, the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function is used with the _`condition`_ argument to check if a given value is in the array. 

### Note

It is recommended to use the [`array:contains()`](functions-array-contains.html "array:contains\(\)") function to check for simple values. See [`array:contains()`](functions-array-contains.html "array:contains\(\)"). 

Example incoming data might look like this: 

a[0]| a[1]  
---|---  
1| 2  
1| 3  
1| 4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvparse()

Parses the string into key value pairs. 

  3. logscale
         
         | array:exists(array="a[]", condition={a>2})

Filters for events where the a[] array contains a value greater than `2`. 

  4. Event Result set.




##### Summary and Results

The query is used to check for the existence of simple values in a flat array. 

Sample output from the incoming example data: 

a[0]| a[1]  
---|---  
1| 3  
1| 4  
  
#### Check For Existence of Element Using Complex Conditions

**Check for the existence of elements using complex conditions in flat array using[`array:exists()`](functions-array-exists.html "array:exists\(\)") function with [`in()`](functions-in.html "in\(\)") and [`if()`](functions-if.html "if\(\)") **

##### Query

logscale
    
    
    kvParse()
    | array:exists(
    array="a[]",
    condition=if(in(a, values=[2,5]), then=true, else=in(a, values=[3, 6]))

##### Introduction

In this example, the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function is used with the _`condition`_ argument and [`if()`](functions-if.html "if\(\)") function along with the [`in()`](functions-in.html "in\(\)") function to check if given values are in the array. 

The example demonstrates how to use the [`kvParse()`](functions-kvparse.html "kvParse\(\)") function along with the [`if()`](functions-if.html "if\(\)") function to create a logical OR-like condition in the expression language. It allows for more complex filtering logic, when a direct logical `OR` operator is not available. 

Example incoming data might look like this: 

a[0]| a[1]  
---|---  
1| 2  
1| 3  
1| 4  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | array:exists(
         array="a[]",
         condition=if(in(a, values=[2,5]), then=true, else=in(a, values=[3, 6]))

Filters for events where the a[] array contains the values `2` or `5`. If not containing these values, it filters for events where the a[] array contains the values `3` or `6`. 

  4. Event Result set.




##### Summary and Results

The query is used to check for the existence of simple values in nested arrays. 

Sample output from the incoming example data: 

a[0]| a[1]  
---|---  
1| 2  
1| 3  
  
#### Check For Existence of Elements Using Filtering Pipeline

**Check for the existence of element in a flat array using the[`array:exists()`](functions-array-exists.html "array:exists\(\)") function with a filtering pipeline **

##### Query

logscale
    
    
    kvParse()
    | array:exists(
    array="a[]",
    var=x,
    condition={ x=3 OR x=4 | test(x>=b) })

##### Introduction

In this example, the [`array:exists()`](functions-array-exists.html "array:exists\(\)") function is used with the _`condition`_ argument and [`test()`](functions-test.html "test\(\)") function to check if given values are in the array. 

Example incoming data might look like this: 

a[0]| a[1]| b  
---|---|---  
1| 2| 4  
1| 3| 4  
1| 4| 3  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. logscale
         
         | array:exists(
         array="a[]",
         var=x,
         condition={ x=3 OR x=4 | test(x>=b) })

Filters for events where the a[] array contains the values `3` or `4` and where x is greater than or equal to the value of the field b in the event. 

  4. Event Result set.




##### Summary and Results

The query is used to compare array entries to both fixed values and field values. The query outputs the event that passed the filtering condition in the pipeline. 

Sample output from the incoming example data: 

a[0]| a[1]| b  
---|---|---  
1| 4| 3  
  
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
