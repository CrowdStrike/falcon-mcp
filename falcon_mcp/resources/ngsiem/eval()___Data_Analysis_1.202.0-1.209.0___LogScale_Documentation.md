# eval() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-eval.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`eval()`](functions-eval.html "eval\(\)")

Creates a new field by evaluating the provided expression. The eval string must always start with an assignment (`f=expr`). The result is stored in a field with that name. 

In an expression, it is possible to supply names of fields, strings and numbers. 

The operators available are `==`, `!=`, as well as `+`, `-`, `*`, and `/` and parenthesized expressions. 

[`eval()`](functions-eval.html "eval\(\)") accepts multiple expressions to be evaluated, separated by a comma, in the form of `field_name = expression`. 

### Note

This function takes no parameters. 

The following are all valid examples: 

logscale
    
    
    eval(a = 3)

logscale
    
    
    eval(a = b, x = y + z)

In the context of an [`eval()`](functions-eval.html "eval\(\)") expression — unlike filters — identifiers always denote field values. For example: 

logscale Syntax
    
    
    eval( is_warning= (loglevel==WARN) )

is most likely wrong; you want to write: 

logscale Syntax
    
    
    (loglevel=="WARN")

The order of evaluation of arguments is left to right. 

The expression: 

logscale Syntax
    
    
    eval(f=expr)

only results in an assignment to `f` when `expr` yields a result — which is not the case when a field in the expression does not exist, or it's not a number. 

This means that fields are not created if the source event is missing a value. 

If `f` already existed as a field on the event and `expr` did not yield any result, then `f` is unchanged. 

### [`eval()`](functions-eval.html "eval\(\)") Examples

Click + next to an example below to get the full details.

#### Create New Fields

**Create new fields by evaluating the provided expression using the[`eval()`](functions-eval.html "eval\(\)") function **

##### Query

logscale
    
    
    eval(c = a + b)

##### Introduction

In this example, the [`eval()`](functions-eval.html "eval\(\)") function is used to add the fields a and b together, creating a new field c containing the results. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         eval(c = a + b)

Adds the values of field a and field b together and returns the sum of these in a new field named c. 

  3. Event Result set.




##### Summary and Results

The query is used to create a new field containing the sum of two other fields. In case the field c already existed, it would just be modified with the new value. The [`eval()`](functions-eval.html "eval\(\)") function is useful when testing and debugging. You can for example use it to test a complex function or expression with different inputs and quickly check the output in the returned values. 

#### Match Field to Timespan

**Match a field to timespan using the[`eval()`](functions-eval.html "eval\(\)") function with [`timeChart()`](functions-timechart.html "timeChart\(\)") **

##### Query

logscale
    
    
    timechart(method, span=5min)
    | eval(_count=_count/5)

##### Introduction

In this example, the [`eval()`](functions-eval.html "eval\(\)") function is used with [`timeChart()`](functions-timechart.html "timeChart\(\)") to match a field to the timespan, dividing the count by 5 to convert from a 5 minute count to a per-minute count. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timechart(method, span=5min)

Creates a timechart based on the values of the method field, and groups data into 5 minute buckets (span=5min). By default, it counts events in each bucket and returns the result in a field named _count. 

  3. logscale
         
         | eval(_count=_count/5)

Divides the count by 5 to convert from a 5-minute count to a per-minute count, and returns the new value in the _count field. 

This approach is useful when you want to display per-minute rates but also want to benefit from the reduced data points and improved performance of larger time buckets. 

  4. Event Result set.




##### Summary and Results

The query is used to match a field to a timespan. It summarizes the count into 5 minutes blocks and then displays those using the [`timeChart()`](functions-timechart.html "timeChart\(\)")_`timespan`_ parameter to display the value in those increments. 

The [`eval()`](functions-eval.html "eval\(\)") function then summarizes the values by dividing the 5 minutes counts by 5 to provide a summarized value for each 5 minutes timespan. You can, for example, use it to test a complex function or expression with different inputs and quickly check the output in the returned values. 

#### Modify Existing Fields

**Modify existing fields by evaluating the provided expression using the[`eval()`](functions-eval.html "eval\(\)") function **

##### Query

logscale
    
    
    eval(responsesize = responsesize / 1024)

##### Introduction

In this example, the [`eval()`](functions-eval.html "eval\(\)") function is used to show the responseSize field in Kibibyte (KiB) instead of bytes. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         eval(responsesize = responsesize / 1024)

Modifies the existing responsesize field by, first, dividing the current value of responsesize by `1024`, then assigning the returned results back to the responsesize field. 

Notice that the original value is overwritten. Any subsequent use of the field responsesize in the query will be working with the new value in kilobytes, not the original value in bytes. 

If you want to preserve the original value, consider creating a new field instead: `eval(responsesizeKB = responsesize / 1024)`. This creates a new field responsesizeKB while leaving the values in the original field responsesize unchanged. 

  3. Event Result set.




##### Summary and Results

The query is used to modify an existing field. In this example, it is used to convert values from one size to another; `bytes` to `KiB`. Converting values to `KiB` is useful when working with binary systems. The transformation is, for example, useful when dealing with network traffic, file sizes, or any other data where you want to represent sizes in a more readable format (KB instead of bytes). 

It is also possible to use the [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)") for converting units. For more information about supported units, see [`unit:convert()`](functions-unit-convert.html "unit:convert\(\)").
