# selfJoinFilter() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-selfjoinfilter.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)")

This function is a filter query that runs in two phases: 

  1. Runs a query to determine a set of IDs (specified using the _`field`_ parameter), for which there exists an event with that field ID which satisfy all the _`where`_ clauses. Each _`where`_ clause can be satisfied by distinct events (but they must all have the same ID). 

  2. Runs as a filter function that lets all events that have one of the determined IDs pass through. In the secondary run, the events need only match the ID, not any of the _`where`_ clauses; unless `prefilter=true` is set. 




Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`field`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-field)[a]| array of strings| required |  |  Specifies which field in the event (log line) is the join key identifier.   
[_`prefilter`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-prefilter)|  boolean| optional[b] | [`false`](functions-selfjoinfilter.html#query-functions-selfjoinfilter-prefilter-option-false)|  Defines whether to include events that match the `where` clauses.   
|  |  | **Values**  
|  |  | [`false`](functions-selfjoinfilter.html#query-functions-selfjoinfilter-prefilter-option-false)| Passes all events with matching IDs and includes events that do not match the `where` clauses.  
|  |  | [`true`](functions-selfjoinfilter.html#query-functions-selfjoinfilter-prefilter-option-true)| Only passes events that directly match `where` clauses.  
[_`where`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-where)| [filter]| required |  |  The subquery to execute producing the values to join with.   
[a] The parameter name [_`field`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-field) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-selfjoinfilter.html#query-functions-selfjoinfilter-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     selfJoinFilter(["value"],where="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     selfJoinFilter(field=["value"],where="value")
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
>     !selfJoinFilter()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not selfJoinFilter()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") Function Operation

The basic function of the operation is: 

  * [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") without prefilter selects the events X where some other A, B, and C events exist with the same keys, but X itself does not have to be an A, B or C. 

  * Enabling prefilter means yes, X does have to be an A, B, or C: no other kinds should be included. 




The function uses a compact and fast, but imprecise, summary of the relevant keys being filtered and is therefore useful when narrowing down the set of events and keys in an efficient manner where other aggregate functions may reach their key limit. This can be used most effectively to produce a data set of events that share a common key. 

When using the function, a query should use: 

  * Filter the event set to find the base set of events. 

  * Use [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") to find events with the common keys. 

  * Correlate the content, for example by using [`groupBy()`](functions-groupby.html "groupBy\(\)") to aggregate the contents. 

  * (Optionally) filter the results to exclude any correlated data not required in the output. 




[`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") is probabilistic and the result can contain false positives. 

matches |  false positive rate |  number of false positives   
---|---|---  
1000 |  0.00000% |  0.0   
10000 |  0.00029% |  0.0   
20000 |  0.00224% |  0.4   
25000 |  0.00434% |  1.1   
50000 |  0.03289% |  16.4   
  
If, for example, the _`where`_ clauses (along with any preceding filtering) limits the matching IDs to 25,000 elements, then out of those 1.1 will be false positives on average. 

When passed the additional argument `prefilter=true`, the resulting output will only contain those log lines that match one of the _`where`_ clauses. With `prefilter` set to `false` by default, all log lines with a join key for which there exists events that satisfy the _`where`_ clauses will be passed through. 

Warning

This function does two passes over the data and can therefore not be used in a live query unless in combination with [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)"). 

### Note

If multiple fields are specified in the _`field`_ parameter, they must all exist in an event, for it to be valid for [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)"). 

### [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") Examples

Click + next to an example below to get the full details.

#### Compare and Filter Values in Same Table

**Retrieves all emails with attachments sent from one given person to another given person using the[`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") function matching only the ID **

##### Query

logscale
    
    
    selfJoinFilter(field=email_id, where=[{ from=peter }, {to=paul}])
    | attachment=*

##### Introduction

In this example, emails are logged with one event for each header (each email has its own ID) and the [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") function is used to find all attachments for emails sent from one given person to another given person. Notice, that this query does two passes over the data and, therefore, cannot be used in a live query. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         selfJoinFilter(field=email_id, where=[{ from=peter }, {to=paul}])

Finds all the values in the emails_id field that correspond to mails from `Peter` to `Paul`. 

  3. logscale
         
         | attachment=*

Finds all log messages with one of those values in the emails_ids field that has been passed on from first phase that also have an attachment. 

  4. Event Result set.




##### Summary and Results

The query is used to find all emails with attachments sent from one given person to another person. In general, the [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") function is useful for narrowing down a set of events in a fairly efficient manner, in cases where the total set of events is too voluminous.
