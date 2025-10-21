# round() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-round.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`round()`](functions-round.html "round\(\)")

Rounds a numeric input field to the nearest integer, with an optional method to set the rounding type. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-round.html#query-functions-round-as)|  string| optional[a] | `Same name as input field`|  The output name of the field to round.   
[_`field`_](functions-round.html#query-functions-round-field)[b]| string| required |  |  The names of the field to round.   
[_`how`_](functions-round.html#query-functions-round-how)|  string| optional[[a]](functions-round.html#ftn.table-functions-round-optparamfn) | [`round`](functions-round.html#query-functions-round-how-option-round)|  Method used to round the number.   
|  |  | **Values**  
|  |  | [`ceil`](functions-round.html#query-functions-round-how-option-ceil)| Round up to the nearest whole number  
|  |  | [`floor`](functions-round.html#query-functions-round-how-option-floor)| Round down to the nearest whole number  
|  |  | [`round`](functions-round.html#query-functions-round-how-option-round)| Standard rules; for example, <0.5 rounds down, >0.5 rounds up  
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-round.html#query-functions-round-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-round.html#query-functions-round-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     round("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     round(field="value")
> 
> These examples show basic structure only.

### [`round()`](functions-round.html "round\(\)") Examples

Click + next to an example below to get the full details.

#### Basic Rounding

****

##### Query

logscale
    
    
    round(myvalue)

##### Introduction

The [`round()`](functions-round.html "round\(\)") function rounds a number to the nearest integer (whole number) using standard math rules. Numbers greater than 0.5 are rounded up, numbers lower than 0.5 are rounded down. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         round(myvalue)

Rounds the number in myvalue. 

  3. Event Result set.




##### Summary and Results

The query is used to round a floating point number to the nearest integer. Rounding is used to simplify numbers. The benefit to rounding is that it returns numbers that are easier to work with. 

### Note

To format a number, or round to a specific decimal accuracy, use [`format()`](functions-format.html "format\(\)"). See [Rounding to n Decimal Places](https://library.humio.com/examples/examples-functions-round-decimalpoint.html). 

#### Rounding Within a Timechart

**Round down a number in a field and display information in a timechart using the[`round()`](functions-round.html "round\(\)") and [`timeChart()`](functions-timechart.html "timeChart\(\)") functions **

##### Query

logscale
    
    
    timeChart(function={max(value) | round(_max, how=floor)})timechart(function=max(value))

##### Introduction

In this example, the [`round()`](functions-round.html "round\(\)") function is used with a _`floor`_ parameter to round down a field value to an integer (whole number) and display information within a timechart. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         timeChart(function={max(value) | round(_max, how=floor)})timechart(function=max(value))

Creates a time chart using [`max()`](functions-max.html "max\(\)") as the aggregate function for a field named value to find the highest value in each time bucket, and returns the result in a field named _max. 

Rounds the implied field _max from the aggregate [`max()`](functions-max.html "max\(\)") using the `floor` option to round down the value. 

Example of original _max values: `10.8`, `15.3`, `20.7`. 

After floor: `10`, `15`, `20`. 

  3. Event Result set.




##### Summary and Results

The query is used to round down maximum values over time to nearest integer (whole value). This is useful when displaying information in a time chart. Rounding to nearest integer will make it easier to distinguish the differences between values when used on a graph for time-based visualization. The query simplifies the data presentation. 

### Note

To round to a specific decimal accuracy, the [`format()`](functions-format.html "format\(\)") function must be used. 

![Showing Round with timeChart\(\)](images/timechart-round-max.png)  
---  
  
#### Rounding to n Decimal Places

****

##### Query

logscale
    
    
    format("%.2f", field=value)

##### Introduction

To round a number to a specific number of decimal points, use [`format()`](functions-format.html "format\(\)") rather than [`round()`](functions-round.html "round\(\)"). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("%.2f", field=value)

Rounds the field value to two decimal places. 

  3. Event Result set.




##### Summary and Results

When using [`format()`](functions-format.html "format\(\)"), rounding is performed using standard math rules. The [`format()`](functions-format.html "format\(\)") rounds a number to a specific decimal accuracy. 

### Note

To round a number to the nearest integer, use [`round()`](functions-round.html "round\(\)"). See [Basic Rounding](https://library.humio.com/examples/examples-functions-round-basic.html).
