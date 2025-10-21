# sum() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-sum.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`sum()`](functions-sum.html "sum\(\)")

Calculates the sum for a field over a set of events. Result is returned in a field named _sum. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-sum.html#query-functions-sum-as)|  string| optional[a] | `_sum`|  Name of output field.   
[_`field`_](functions-sum.html#query-functions-sum-field)[b]| string| required |  |  Field to extract a number from and sum over.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-sum.html#query-functions-sum-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-sum.html#query-functions-sum-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     sum("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     sum(field="value")
> 
> These examples show basic structure only.

### [`sum()`](functions-sum.html "sum\(\)") Syntax Examples

How many bytes did our webserver send per minute 

logscale
    
    
    bucket(function=sum(bytes_sent))

### [`sum()`](functions-sum.html "sum\(\)") Examples

Click + next to an example below to get the full details.

#### Bucket Events Into Groups

**Bucket events into 24 groups using the[`count()`](functions-count.html "count\(\)") function and [`bucket()`](functions-bucket.html "bucket\(\)") function **

##### Query

logscale
    
    
    bucket(buckets=24, function=sum("count"))
    | parseTimestamp(field=_bucket,format=millis)

##### Introduction

In this example, the [`bucket()`](functions-bucket.html "bucket\(\)") function is used to request 24 buckets over a period of one day in the [humio-metrics](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-metrics.html) repository. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         bucket(buckets=24, function=sum("count"))

Buckets the events into 24 groups spanning over a period of one day, using the [`sum()`](functions-sum.html "sum\(\)") function on the count field. 

  3. logscale
         
         | parseTimestamp(field=_bucket,format=millis)

Extracts the timestamp from the generated bucket and converts the timestamp to a date time value. In this example, the bucket outputs the timestamp as an epoch value in the _bucket field. This results in an additional bucket containing all the data after the requested timespan for the requested number of buckets. 

  4. Event Result set.




##### Summary and Results

The query is used to optimizing data storage and query performance by making et easier to manage and locate data subsets when performing analytics tasks. Note that the resulting outputs shows 25 buckets; the original requested 24 buckets and in addition the bucket for the extracted timestamp. 

Sample output from the incoming example data: 

_bucket| _sum| @timestamp  
---|---|---  
1681290000000| 1322658945428| 1681290000000  
1681293600000| 1879891517753| 1681293600000  
1681297200000| 1967566541025| 1681297200000  
1681300800000| 2058848152111| 1681300800000  
1681304400000| 2163576682259| 1681304400000  
1681308000000| 2255771347658| 1681308000000  
1681311600000| 2342791941872| 1681311600000  
1681315200000| 2429639369980| 1681315200000  
1681318800000| 2516589869179| 1681318800000  
1681322400000| 2603409167993| 1681322400000  
1681326000000| 2690189000694| 1681326000000  
1681329600000| 2776920777654| 1681329600000  
1681333200000| 2873523432202| 1681333200000  
1681336800000| 2969865160869| 1681336800000  
1681340400000| 3057623890645| 1681340400000  
1681344000000| 3144632647026| 1681344000000  
1681347600000| 3231759376472| 1681347600000  
1681351200000| 3318929777092| 1681351200000  
1681354800000| 3406027872076| 1681354800000  
1681358400000| 3493085788508| 1681358400000  
1681362000000| 3580128551694| 1681362000000  
1681365600000| 3667150316470| 1681365600000  
1681369200000| 3754207997997| 1681369200000  
1681372800000| 3841234050532| 1681372800000  
1681376400000| 1040019734927| 1681376400000  
  
#### Calculate Total Network Bandwidth Per Host

**Analyze network traffic patterns using the[`groupBy()`](functions-groupby.html "groupBy\(\)") function with [`sum()`](functions-sum.html "sum\(\)") **

##### Query

logscale
    
    
    event_simpleName="NetworkConnectStats"
    groupBy([ComputerName], function=[
            sum(field="BytesReceived", as=InboundTraffic),
            sum(field="BytesSent", as=OutboundTraffic)
            ])
    TotalTraffic := InboundTraffic + OutboundTraffic
    sort(field="TotalTraffic", order="desc")

##### Introduction

In this example, the [`groupBy()`](functions-groupby.html "groupBy\(\)") is used with nested [`sum()`](functions-sum.html "sum\(\)") functions to calculate total inbound and outbound network traffic per host, followed by calculating the total bandwidth consumption. 

Example incoming data might look like this: 

@timestamp| event_simpleName| ComputerName| BytesReceived| BytesSent  
---|---|---|---|---  
1686837825000| NetworkConnectStats| DESKTOP-A1| 15000000| 8500000  
1686837825000| NetworkConnectStats| DESKTOP-A1| 8900000| 4200000  
1686837825000| NetworkConnectStats| LAPTOP-B2| 25000000| 12000000  
1686837826000| NetworkConnectStats| SERVER-C3| 95000000| 45000000  
1686837826000| NetworkConnectStats| DESKTOP-A1| 12000000| 6800000  
1686837826000| NetworkConnectStats| LAPTOP-B2| 18000000| 9500000  
1686837827000| NetworkConnectStats| SERVER-C3| 85000000| 42000000  
1686837827000| NetworkConnectStats| DESKTOP-D4| 5000000| 2800000  
1686837827000| NetworkConnectStats| LAPTOP-B2| 22000000| 11000000  
1686837828000| NetworkConnectStats| SERVER-C3| 105000000| 52000000  
1686837828000| NetworkConnectStats| DESKTOP-D4| 6500000| 3200000  
1686837828000| NetworkConnectStats| DESKTOP-A1| 9800000| 5100000  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         event_simpleName="NetworkConnectStats"

Filters events to include only those where event_simpleName equals `NetworkConnectStats`. 

  3. logscale
         
         groupBy([ComputerName], function=[
                 sum(field="BytesReceived", as=InboundTraffic),
                 sum(field="BytesSent", as=OutboundTraffic)
                 ])

Groups the data by the ComputerName field and calculates two aggregate values: the sum of BytesReceived stored in a field named InboundTraffic, and the sum of BytesSent stored in a field named OutboundTraffic. 

  4. logscale
         
         TotalTraffic := InboundTraffic + OutboundTraffic

Creates a new field named TotalTraffic containing the values from the InboundTraffic and OutboundTraffic fields. 

  5. logscale
         
         sort(field="TotalTraffic", order="desc")

Sorts the results based on the TotalTraffic field in descending order ([_`order`_](functions-sort.html#query-functions-sort-order)=`desc`), showing hosts with highest bandwidth consumption first. 

  6. Event Result set.




##### Summary and Results

The query is used to analyze network bandwidth consumption patterns across different hosts in the network. 

This query is useful, for example, to identify hosts consuming excessive bandwidth, monitor network usage patterns, or detect potential network-intensive applications or anomalies. 

Sample output from the incoming example data: 

ComputerName| InboundTraffic| OutboundTraffic| TotalTraffic  
---|---|---|---  
SERVER-C3| 285000000| 139000000| 424000000  
LAPTOP-B2| 65000000| 32500000| 97500000  
DESKTOP-A1| 45700000| 24600000| 70300000  
DESKTOP-D4| 11500000| 6000000| 17500000  
  
Note that the traffic values are in bytes and that each row represents the aggregated traffic for a unique host 

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
