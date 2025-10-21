# Find Top N Value of Series - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-timechart-topnvalue-multi-functions.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Top N Value of Series - Example 2

Find top N value of series using the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function with [`max()`](https://library.humio.com/data-analysis/functions-max.html) and [`selectLast()`](https://library.humio.com/data-analysis/functions-selectlast.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    timeChart(series=key, function=[max(value), {foo := value % 41 | selectLast(foo)}], limit=2)

### Introduction

In this example, the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used with multiple functions and modulus operation to find the top 2 values of the [key](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-fdr-ingest.html) series and display the results in a [Table](https://library.humio.com/data-analysis/widgets-table.html). 

The _`limit`_ parameter of [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) prioritizes the top N series. The top N value being the series with the highest numerical value attributed to it by the subquery across all fields. The selection is based on the numerical values produced by the subquery/function. When multiple functions are used, it considers all values produced for the corresponding key or keys selected by the [_`series`_](https://library.humio.com/data-analysis/functions-timechart.html#query-functions-timechart-series) parameter. In this example values are calculated for the foo value and _max maximum value of the field. The selection process is not based on the series values from the [key](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-fdr-ingest.html) field. 

Example incoming data might look like this: 

key| value  
---|---  
a| 42  
b| 41  
c| 40  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         timeChart(series=key, function=[max(value), {foo := value % 41 | selectLast(foo)}], limit=2)

Groups data by time using the [key](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-fdr-ingest.html) field as the series identifier, then takes the maximum value and performs a modulus operation (represented by `% 41` in the example) on the value, comparing that to the last value of foo using the [`selectLast()`](https://library.humio.com/data-analysis/functions-selectlast.html) function. With a limit 2, only the top 2 results are displayed. 

The series selection is based on combined numerical output of both the [`max()`](https://library.humio.com/data-analysis/functions-max.html) function and the calculation for foo. 

Note that each value is divided by `41` and the modulus operator returns the remainder and stores it in the field foo. The modulus operation creates a new set of values that, combined with `max(value)`, determines which series have the highest total numerical values. The series selection is based on combined numerical output of both values. 

The modulus calculations in this example are as follows: 

     * `42 % 41 = 1 (42 divided by 41 = 1 remainder 1, foo=1)`

     * `41 % 41 = 0 (41 divided by 41 = 1 remainder 0, foo=0)`

     * `40 % 41 = 40 (40 divided by 41 = 0 remainder 40, foo=40)`

  3. Event Result set.




### Summary and Results

The query is used to find top 2 value of series using multiple functions and display the results in a [Table](https://library.humio.com/data-analysis/widgets-table.html). When multiple functions are used, it considers all values produced for each element in the series. 

The top 2 series are (in this example with multiple functions used) `a` and `c`, as the output of the subquery is: 
    
    
    _max = 42, foo = 1  // for 'a', (total=43)
    _max = 41, foo = 0  // for 'b', (total=41)
    _max = 40, foo = 40 // for 'c', (total=80)

meaning `a` and `c` have the highest combined numerical values and thus are the top series. 

Note how `c` has higher total despite lower [`max()`](https://library.humio.com/data-analysis/functions-max.html). This is because all produced values are considered and the result of the modulus calculation creates a higher remainder and overall total. 

The query can be used, for example, for advanced pattern detection to find series with interesting combinations of metrics, or for anomaly detection to identify unusual patterns using multiple calculations. 

Sample output from the incoming example data: 

_bucket| key| _max| foo  
---|---|---|---  
1747109790000| a| 42| 1  
1747109790000| c| 40| 40  
  
The same input can output a different result if the [`timeChart()`](https://library.humio.com/data-analysis/functions-timechart.html) function is used with a single aggregator function only. For more information, see [Find Top N Value of Series - Example 1](examples-timechart-topnvalue-single-function.html "Find Top N Value of Series - Example 1").
