# selfJoin() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-selfjoin.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)")

This function is used to collate data from events that share a key. Often the [`groupBy()`](functions-groupby.html "groupBy\(\)") function can be used for this, but if there are too many keys (defaulting to 100,000) then the result is imprecise since some random subset of keys is left out of the result once the limit is reached. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`collect`_](functions-selfjoin.html#query-functions-selfjoin-collect)|  array of strings| optional[a] | `(none)`|  Specifies columns to include.   
[_`field`_](functions-selfjoin.html#query-functions-selfjoin-field)[b]| array of strings| required |  |  Specifies which field in the event (log line) that must match the given column value.   
[_`limit`_](functions-selfjoin.html#query-functions-selfjoin-limit)|  number| optional[[a]](functions-selfjoin.html#ftn.table-functions-selfjoin-optparamfn) | `20000`|  Specifies the maximum number of rows in the subquery   
|  | **Minimum**| `1`|   
|  | **Maximum**| [`MAX_STATE_LIMIT`](functions-selfjoin.html#query-functions-selfjoin-limit-max-max_state_limit)|   
|  | **Controlling Variables**  
|  | [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html)|  **Variable default:**`1,000,000 group elements`  
|  | `MAX_STATE_LIMIT`|   
[_`postfilter`_](functions-selfjoin.html#query-functions-selfjoin-postfilter)|  boolean| optional[[a]](functions-selfjoin.html#ftn.table-functions-selfjoin-optparamfn) | `false`|  Re-run the `and` of the `where` clauses after collating results. If all fields needed for satisfying the `where` clauses are provided as values for collect, this will eliminate false positives in the output.   
[_`prefilter`_](functions-selfjoin.html#query-functions-selfjoin-prefilter)|  boolean| optional[[a]](functions-selfjoin.html#ftn.table-functions-selfjoin-optparamfn) | `false`|  Only pass values matching at least one of the _`where`_ clauses into the embedded [`groupBy()`](functions-groupby.html "groupBy\(\)").   
[_`select`_](functions-selfjoin.html#query-functions-selfjoin-select)|  array of strings| optional[[a]](functions-selfjoin.html#ftn.table-functions-selfjoin-optparamfn) | `(none)`|  Specifies columns to include.   
[_`where`_](functions-selfjoin.html#query-functions-selfjoin-where)| [filter]| required |  |  The subquery to execute producing the values to join with.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-selfjoin.html#query-functions-selfjoin-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-selfjoin.html#query-functions-selfjoin-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     selfJoin(["value"],where="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     selfJoin(field=["value"],where="value")
> 
> These examples show basic structure only.

### [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") Function Operation

Say you want to run a query like this: 

logscale
    
    
    groupBy(field=email_id, function=[collect(from), collect(to)])
    | from=peter AND to=anders

If there are many email_ids then the state size is exhausted. Even if you rewrite it like this to: 

logscale
    
    
    from=peter OR to=anders
    | groupBy(field=email_id, function=[collect(from), collect(to)])
    | from=peter AND to=anders

because either there are many emails from Peter or to Anders. 

With [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") you specify a join key (the [_`field`_](functions-selfjoin.html#query-functions-selfjoin-field) argument), and a series of tests (the [_`where`_](functions-selfjoin.html#query-functions-selfjoin-where) clauses); it will then perform the above operation in a two-phase way so that only those log lines with an `email_id` for which there exists both a `from=peter` event and a `to=anders` event are passed into the [`groupBy()`](functions-groupby.html "groupBy\(\)"). This is done in a probabilistic fashion, by using a bloom filter. 

The embedded [`groupBy()`](functions-groupby.html "groupBy\(\)") then uses either [`collect()`](functions-collect.html "collect\(\)") or [`selectLast()`](functions-selectlast.html "selectLast\(\)") on the specified fields depending on the value of one of the [_`select`_](functions-selfjoin.html#query-functions-selfjoin-select) or [_`collect`_](functions-selfjoin.html#query-functions-selfjoin-collect) parameter to the [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") function. 

The above query can be simplied (and be made more efficient) by using the [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") function: 

logscale
    
    
    selfJoin(field=email_id, where=[{from=peter},{to=anders}])

[`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") limits the number of matching join keys to what is configured in [`GroupMaxLimit`](https://library.humio.com/falcon-logscale-self-hosted/configuration-dynamic-config-settingdetails-group_max_limit.html) dynamic configuration. Default is 20,000. These limits apply to the number of join key values that satisfy the collective requirements of the [_`where`_](functions-selfjoin.html#query-functions-selfjoin-where) clauses. In this case, the function would return the number of emails from Peter to Anders. 

### Important

[`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") is probabilistic and the result can contain false positives. 

matches |  false positive rate |  number of false positives   
---|---|---  
1000 |  0.00000% |  0.0   
10000 |  0.00029% |  0.0   
20000 |  0.00224% |  0.4   
25000 |  0.00434% |  1.1   
50000 |  0.03289% |  16.4   
  
If, for example, the [_`where`_](functions-selfjoin.html#query-functions-selfjoin-where) clauses (along with any preceding filtering) limit the matching IDs to 25,000 elements, then 1.1 of those will be false positives on average. 

Warning

The [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") does two passes over the data and can therefore not run truly live. 

### [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") Examples

Click + next to an example below to get the full details.

#### Filter and Collect Values in Same Table

**Retrieves all emails sent from one given person to another given person using the[`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") function **

##### Query

logscale
    
    
    selfJoin(email_id, where=[{from=*peter*}, {to=*anders*}], collect=[from,to])

##### Introduction

In this example, emails are logged with one event for each header (each email has its own ID) and the [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") function is used to find and collect all emails sent from one given person to another given person. Notice, that this query does two passes over the data and, therefore, cannot be used in a live query. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         selfJoin(email_id, where=[{from=*peter*}, {to=*anders*}], collect=[from,to])

Finds and collects all the values in the emails_id field that correspond to mails from `Peter` to `Anders`. 

  3. Event Result set.




##### Summary and Results

The query is used to find and collect all emails sent from one given person to another person. In general, the [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") function is useful for narrowing down a set of events in a fairly efficient manner, in cases where the total set of events is too voluminous.
