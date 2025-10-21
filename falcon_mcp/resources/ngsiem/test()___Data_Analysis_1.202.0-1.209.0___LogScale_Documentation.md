# test() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-test.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

Content was updated:Oct 1, 2024

## [`test()`](functions-test.html "test\(\)")

Evaluates an arbitrary expression as a boolean value and filters events when the expression returns true. Not only can Falcon LogScale make comparisons between one field and one value, but it can also compare more fields and their respective values, using the [`test()`](functions-test.html "test\(\)") function. 

### Note

In [`test()`](functions-test.html "test\(\)") unquoted strings are interpreted as field names. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`expression`_](functions-test.html#query-functions-test-expression)[a]| expression| required |  |  The expression to test.   
[a] The parameter name [_`expression`_](functions-test.html#query-functions-test-expression) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`expression`_](functions-test.html#query-functions-test-expression) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     test("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     test(expression="value")
> 
> These examples show basic structure only.

Hide negatable operation for this function

Show negatable operation for this function

> Negatable Function Operation
> 
> This function is negatable, implying the inverse of the result. For example:
> 
> logscale Syntax
>     
>     
>     !test()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not test()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`test()`](functions-test.html "test\(\)") Examples

Click + next to an example below to get the full details.

#### Check if Field Contains Specific Value

**Check if field contains specific value using[`test()`](functions-test.html "test\(\)") function **

##### Query

logscale
    
    
    test(myField == "myValue")

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function is used to check if a field contains a specific value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(myField == "myValue")

Returns all events where field myField holds the specific value myOtherField. Notice the use of double-quotes. If the string had been `test(myField == myOtherField)`, then it would have returned results where the fields contained the same values and not a specific value. 

  3. Event Result set.




##### Summary and Results

The query is used to check if a field contains a specific value. The function syntax with [`test()`](functions-test.html "test\(\)") does not support fields with space. For example, `test("f o o" == "bar")` compares the two values, not a field named f o o. 

The syntax form, `myField = myValue` is the preferred method for performance reasons. 

#### Check if Fields Contain Same Value

**Search for more fields with same length using the test() function with length()**

##### Query

logscale
    
    
    test(length(userid) == length(method))

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function is used with [`length()`](functions-length.html "length\(\)") to search for events where the userid field and method field have the same length. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(length(userid) == length(method))

Returns all events where field userid has the same length as the method field. This could for example be events with `Chad` and _`POST`_ , and `Peter` and _`PATCH`_. 

  3. Event Result set.




##### Summary and Results

The query is used to compare more fields and their respective values. 

#### Compare More Fields and Filter for Specific Events

**Compare more fields and filter for events that are not twice as large using a negation statement**

##### Query

logscale
    
    
    test(field1 != 2 * field2)

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function is used to filter for events where the value of field1 is not exactly twice as large as the value in field2. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(field1 != 2 * field2)

Filters for events where the value of the field field1 is not exactly twice as large as the value in field field2. 

  3. Event Result set.




##### Summary and Results

The query is used to compare more fields and filter for specific events that are not of a certain size. 

#### Compare More Fields and Their Respective Values

**Compare more fields and their respective values**

##### Query

logscale
    
    
    test(field1 < field2)

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function is used to check if the value of field1 is less than the value in field2. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(field1 < field2)

Evaluates if the value of the field field1 is less than the value in field field2. 

  3. Event Result set.




##### Summary and Results

The query is used to compare more fields and their respective values. 

#### Evaluate Arbitrary Expression as Boolean Value

**Evaluate an arbitrary expression as a boolean value and filter events when expression returns true**

##### Query

logscale
    
    
    test(foo < bar)

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function evaluates the arbitrary expression `<` as a boolean value (true/false) and filters events when the expression returns true. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(foo < bar)

Evaluates if the value of the field foo is less than the value of the field bar. 

  3. Event Result set.




##### Summary and Results

The query is used to evaluate arbitrary expressions as boolean values in a query. This is used to filter events where the expression returns true. The difference between using the [`test()`](functions-test.html "test\(\)") function instead of the [`match()`](functions-match.html "match\(\)") function is that [`test()`](functions-test.html "test\(\)") returns a boolean value and [`match()`](functions-match.html "match\(\)") returns a string. 

#### Evaluate Arbitrary Field Values for CPU Time Within Repository

**Evaluate and compare field values for CPU time within a repository**

##### Query

logscale
    
    
    test(cputime < 7500)

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function evaluates the arbitrary expression `<` as a boolean value (true/false) and filters events when the expression returns true. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(cputime < 7500)

Evaluates if the value of the field cputime is less than the value `7500` in a repository. 

  3. Event Result set.




##### Summary and Results

The query is used to evaluate arbitrary expressions as boolean values in a query. This is used to filter events where the expression returns true. The difference between using the [`test()`](functions-test.html "test\(\)") function instead of the [`match()`](functions-match.html "match\(\)") function is that [`test()`](functions-test.html "test\(\)") returns a boolean value and [`match()`](functions-match.html "match\(\)") returns a string. Searching for CPU times is useful when troubleshooting performance issues in a system. 

#### Evaluate Field Values Within Repository

**Compare field values within the Falcon LogScale repository**

##### Query

logscale
    
    
    test(cputime < 7500)

##### Introduction

In this example, the [`test()`](functions-test.html "test\(\)") function evaluates the arbitrary expression `<` as a boolean value (true/false) and filters events when the expression returns true. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(cputime < 7500)

Evaluates if the value of the field cputime is less than `7500`. 

  3. Event Result set.




##### Summary and Results

The query is used to compare a field value within the Falcon LogScale repository. 

#### Search Relative Time to Query Execution

**Writing a query that is executed against a time range relative to when the query is executed using the[`start()`](functions-start.html "start\(\)") function **

##### Query

logscale
    
    
    test(@timestamp < (start() + (30*24*60*60*1000)))

##### Introduction

In this example, the` start()` function is used to test if the [@timestamp](searching-data-event-fields.html#searching-data-event-fields-metadata-timestamp) field is less than (earlier than) the start time plus `30` days. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         test(@timestamp < (start() + (30*24*60*60*1000)))

Tests whether the @timestamp for an event is less than the start time of the query. The query start time is returned by the [`start()`](functions-start.html "start\(\)") function. 

To work out the relative time, we add the explicit number of milliseconds by calculating the number of milliseconds in the specified number of days, in this case, `30`. 

Time calculation breakdown is as follows: 

30 (days) 

× 24 (hours) 

× 60 (minutes) 

× 60 (seconds) 

× 1000 (milliseconds) 

= 2,592,000,000 milliseconds (30 days) 

  3. Event Result set.




##### Summary and Results

The query is used to filter events that occurred within the first 30 days after the start time. 

The query is a practical way of querying with a relative time from the query execution. The 30 days (and calculation) used in the example could be updated with any time calculation to achieve the required result.
