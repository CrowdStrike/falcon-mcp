# if() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-if.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`if()`](functions-if.html "if\(\)")

This function allows to choose one out of two expressions based on a condition. It provides a functionality similar to the `... ? ... : ...` operator known from some programming languages. 

Unlike a [`case`](syntax-conditional.html#syntax-conditional-case "Case Statements") or `match` statement, the [`if()`](functions-if.html "if\(\)") can be embedded into other functions and expressions. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-if.html#query-functions-if-as)|  string| optional[a] | `_if`|  The name of the output destination field.   
[_`condition`_](functions-if.html#query-functions-if-condition)[b]| expression| required |  |  The conditional expression to evaluate.   
[_`else`_](functions-if.html#query-functions-if-else)|  expression| required |  |  The alternative statement to execute.   
[_`then`_](functions-if.html#query-functions-if-then)|  expression| required |  |  The consequent statement to execute.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`condition`_](functions-if.html#query-functions-if-condition) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`condition`_](functions-if.html#query-functions-if-condition) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     if("value",then="value",else="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     if(condition="value",then="value",else="value")
> 
> These examples show basic structure only.

### [`if()`](functions-if.html "if\(\)") Function Operation

The behavior of: 

logscale
    
    
    if(cond, then=onTrue, else=onFalse, as=y)

is equivalent to a [case expression](syntax-conditional.html#syntax-conditional-case "Case Statements"): 

logscale
    
    
    case {
      test(cond)
    | y := onTrue;
      y := onFalse
    }

In particular: 

  * The interpretation of _`condition`_ is the same as the _`expression`_ argument of [`test()`](functions-test.html "test\(\)"). 

  * The evaluation of _`then`_ / _`else`_ arguments is the same as the evaluation of the right-hand side of `:=`. 




The [`if()`](functions-if.html "if\(\)") function: 

  * is a simplified version of the [case](syntax-conditional.html#syntax-conditional-case "Case Statements") / [match](syntax-conditional.html#syntax-conditional-match "Match Statements") based alternative. 

  * can be used as an expression inside other expressions. 




### [`if()`](functions-if.html "if\(\)") Examples

Click + next to an example below to get the full details.

#### Add a Field Based on Values of Another Field - Example 1

****

##### Query

logscale
    
    
    | statusClass :=
    if(regex("^1", field=statuscode), then="informational", else=
    if(regex("^2", field=statuscode), then="successful", else=
    if(regex("^3", field=statuscode), then="redirection", else=
    if(regex("^4", field=statuscode), then="client error", else=
    if(regex("^5", field=statuscode), then="server error", else=
    "unknown")))))

##### Introduction

Nested [`if()`](functions-if.html "if\(\)") functions can be used within a larger expression for adding a field whose value is calculated based on another field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | statusClass :=
         if(regex("^1", field=statuscode), then="informational", else=
         if(regex("^2", field=statuscode), then="successful", else=
         if(regex("^3", field=statuscode), then="redirection", else=
         if(regex("^4", field=statuscode), then="client error", else=
         if(regex("^5", field=statuscode), then="server error", else=
         "unknown")))))

Add a statusClass field where the following conditions are set: 

     * If the value of field statuscode begins with `1`, then statusClass is labeled as `informational`, otherwise: 

     * If the value of field statuscode begins with `2`, then statusClass is labeled as `successful`, otherwise: 

     * If the value of field statuscode begins with `3`, then statusClass is labeled as `redirection`, otherwise: 

     * If the value of field statuscode begins with `4`, then statusClass is labeled as `client error`, otherwise: 

     * If the value of field statuscode begins with `5`, then statusClass is labeled as `server error`, otherwise it is labeled as `unknown`. 

  3. Event Result set.




##### Summary and Results

Nested [`if()`](functions-if.html "if\(\)") functions for tagging a field according to different statuscode values. 

#### Add a Field Based on Values of Another Field - Example 2

****

##### Query

logscale
    
    
    | success := if(status >= 500, then=0, else=if(status == 404, then=0, else=1))

##### Introduction

Another example of nested [`if()`](functions-if.html "if\(\)") functions: this is used to add a field success whose value is calculated based on field status. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | success := if(status >= 500, then=0, else=if(status == 404, then=0, else=1))

Adds a success field at the following conditions: 

     * Sets the value of field success to `0` if status is greater or equal to `500` or if it's equal to `400`, otherwise: 

     * Sets the value of field success to `1`. 

  3. Event Result set.




##### Summary and Results

Nested [`if()`](functions-if.html "if\(\)") functions for tagging a field according to different status values. 

#### Add a Field Based on Values of Another Field - Example 3

****

##### Query

logscale
    
    
    | success := if(status < 500, then=if(status!=404, then=1, else=0), else=0)

##### Introduction

Another example of nested [`if()`](functions-if.html "if\(\)") functions to add a field success and calculate its value based on field status. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | success := if(status < 500, then=if(status!=404, then=1, else=0), else=0)

Adds a success field at the following conditions: 

     * If the value of field status is less than `500`, set the value of success to `0`, but: 

     * If the value of field status is not equal to `404`, then set the value of success to `1` otherwise to `0`. 

  3. Event Result set.




##### Summary and Results

Nested [`if()`](functions-if.html "if\(\)") functions for tagging a field according to different status values. 

#### Calculate a Percentage of Successful Status Codes Over Time

****

##### Query

logscale
    
    
    | success := if(status >= 500, then=0, else=1)
    | timeChart(series=customer,function=
    [
      {
        [sum(success,as=success),count(as=total)]
    | pct_successful := (success/total)*100
    | drop([success,total])}],span=15m,limit=100)

##### Introduction

Calculate a percentage of successful status codes inside the [`timeChart()`](functions-timechart.html "timeChart\(\)") function field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         | success := if(status >= 500, then=0, else=1)

Adds a success field at the following conditions: 

     * If the value of field status is greater than or equal to `500`, set the value of success to `0`, otherwise to `1`. 

  3. logscale
         
         | timeChart(series=customer,function=
         [
           {
             [sum(success,as=success),count(as=total)]

Creates a new timechart, generating a new series, customer that uses a compound function. In this example, the embedded function is generating an array of values, but the array values are generated by an embedded aggregate. The embedded aggregate (defined using the `{}` syntax), creates a [`sum()`](functions-sum.html "sum\(\)") and [`count()`](functions-count.html "count\(\)") value across the events grouped by the value of success field generated from the filter query. This is counting the `1`1 or `0` generated by the [`if()`](functions-if.html "if\(\)") function; counting all the values and adding up the ones for successful values. These values will be assigned to the success and total fields. Note that at this point we are still within the aggregate, so the two new fields are within the context of the aggregate, with each field being created for a corresponding success value. 

  4. logscale
         
         | pct_successful := (success/total)*100

Calculates the percentage that are successful. We are still within the aggregate, so the output of this process will be an embedded set of events with the total and success values grouped by each original HTTP response code. 

  5. logscale
         
         | drop([success,total])}],span=15m,limit=100)

Still within the embedded aggregate, drop the total and success fields from the array generated by the aggregate. These fields were temporary to calculate the percentage of successful results, but are not needed in the array for generating the result set. Then, set a span for the buckets for the events of 15 minutes and limit to 100 results overall. 

  6. Event Result set.




##### Summary and Results

This query shows how an embedded aggregate can be used to generate a sequence of values that can be formatted (in this case to calculate percentages) and generate a new event series for the aggregate values. 

#### Categorize Errors in Log Levels

**Categorize errors in log levels using the[`in()`](functions-in.html "in\(\)") function in combination with [`if()`](functions-if.html "if\(\)") **

##### Query

logscale
    
    
    critical_status := if((in(status, values=["500", "404"])), then="Critical", else="Non-Critical")

##### Introduction

In this more advanced example, the [`if()`](functions-if.html "if\(\)") function is used to categorize errors based on a time condition and it compares the status of a log level and decides on the log's criticality. The field critical_status is going to be evaluated based on the [`if()`](functions-if.html "if\(\)") function. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         critical_status := if((in(status, values=["500", "404"])), then="Critical", else="Non-Critical")

Searches for events where the field status contains the values `500` or `400` and assigns the value `Critical` to a field named critical_status for the returned results. If the values are not equal to `500` or `400`, then the returned events will have the value `Non-Critical` assigned to the field critical_status. 

  3. Event Result set.




##### Summary and Results

The query is used to categorize errors in log levels according to their criticality. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| critical_status  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| Critical  
10.0.0.1| INFO| 200| user1| Non-Critical  
172.16.0.5| WARN| 422| user2| Non-Critical  
192.168.1.15| ERROR| 500| admin| Critical  
10.0.0.12| DEBUG| 302| user1| NonCritical  
  
#### Convert Timestamps Based on Accuracy

****

##### Query

logscale
    
    
    errortime := if((@ingesttimestamp > @timestamp), then=@timestamp, else=@ingesttimestamp) / 1000

##### Introduction

When parsing and processing data, the time of the data can be critical, and not all events include an explicit @timestamp field, but the ingest time stamp, when the event was parsed by LogScale, can be a suitable proxy. The lack of timestamp, or a significant difference between the timestamps may result in displaying an empty value (or creating an event stream that cannot be summarized in a graph). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         errortime := if((@ingesttimestamp > @timestamp), then=@timestamp, else=@ingesttimestamp) / 1000

The event field errortime is set to the latest time value, either timestamp or @ingesttimestamp. 

  3. Event Result set.




##### Summary and Results

Selecting time by the accuracy allows for incoming data to be of different time accuracy but still return consistent results. 

#### Determine a Score Based on Field Value

****

##### Query

logscale
    
    
    percentile(filesize, percentiles=[40,80],as=score)
    | symbol := if(filesize > score_80, then=":+1:", else=if(filesize > score_40, then="so-so", else=":-1:"))

##### Introduction

When summarizing and displaying data, it may be necessary to derive a score or validity based on a test value. This can be achieved using [`if()`](functions-if.html "if\(\)") by creating the score value if the underlying field is over a threshold value. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         percentile(filesize, percentiles=[40,80],as=score)

Calculates the [`percentile()`](functions-percentile.html "percentile\(\)") for the filesize field and determines what filesize that is above 40% of the overall event set, and 80% of the overall event set. 

  3. logscale
         
         | symbol := if(filesize > score_80, then=":+1:", else=if(filesize > score_40, then="so-so", else=":-1:"))

Compares whether the filesize is greater than 80% of the events, setting symbol to `:+1:`. Because [`if()`](functions-if.html "if\(\)") functions can be embedded, the [_`else`_](functions-if.html#query-functions-if-else) parameter is another [`if()`](functions-if.html "if\(\)") statement that sets symbol to `so-so` if the size is greater than 40%, or `:+1:` otherwise. 

  4. Event Result set.




##### Summary and Results

Using [`if()`](functions-if.html "if\(\)") is the best way to make conditional choices about values. The function has the benefit of being able to be embedded into other statements, unlike `case`. 

#### Set a Field Value Based on Tag Value

****

##### Query

logscale
    
    
    keyprocess := if(#eventType == "Spawn", then=ChildID, else=ProcessID)

##### Introduction

When processing event data, there are occasions when a value needs to be determined from another field in the event. In this example, the field keyprocess is populated based on the #eventType tag. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         keyprocess := if(#eventType == "Spawn", then=ChildID, else=ProcessID)

Using the [`if()`](functions-if.html "if\(\)"), set the value of keyprocess to the value of the ChildID if #eventType is `Spawn`; otherwise, set keyprocess to ProcessID. 

  3. Event Result set.




##### Summary and Results

Using [`if()`](functions-if.html "if\(\)") provides a simplified way of processing and parsing data when the test value can be easily identified. 

In this example, the process ID has been identified based on whether it is the original or a spawn (child) process. 

#### Use Multiple if() Functions

****

##### Query

logscale
    
    
    score := if(x != "N/A", then=x, else=0) +  if(y != "N/A", then=y, else=0)

##### Introduction

Multiple [`if()`](functions-if.html "if\(\)") functions can be used in a computation (eval/assign). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         score := if(x != "N/A", then=x, else=0) +  if(y != "N/A", then=y, else=0)

This computation checks if fields x or y is not a number, then `0` will be used instead. 

  3. Event Result set.




##### Summary and Results

Setting the value based on an incoming value enables determination of a score triggered by a value.
