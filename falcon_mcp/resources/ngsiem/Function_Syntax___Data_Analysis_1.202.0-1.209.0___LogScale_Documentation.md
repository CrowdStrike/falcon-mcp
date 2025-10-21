# Function Syntax | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-function.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Function Syntax

LogScale query functions process event data by producing, reducing, or modifying values within query pipelines, with support for both built-in functions and user-created functions through saved queries. The documentation covers function syntax including composite function calls, user functions with arguments, link functions for creating clickable results, and repeating queries that execute at regular intervals for dashboards and alerts. 

LogScale query functions take a set of events, parameters, or configurations. From this, they produce, reduce, or modify values within that set, or in the events themselves within a query pipeline. LogScale has many built-in query functions. They are listed and described in the [_Query Functions_](functions.html "Query Functions") section. 

### Composite Function Calls

Whenever a function accepts a function as an argument, there are some special rules. For all variations of [`groupBy()`](functions-groupby.html "groupBy\(\)"), [`bucket()`](functions-bucket.html "bucket\(\)") and [`timeChart()`](functions-timechart.html "timeChart\(\)"), that take a function= argument, you can also use a composite function. Composite functions take the form `{ f1(..) | f2(..) }` which works like the composition of `f1` and `f2`. For example, you can do: 

logscale Syntax
    
    
    groupBy(type, function={ avgFoo := avg(foo)
    | outFoo := round(avgFoo) })

You can also use filters inside such composite function calls, but not saved queries. 

Incidentally, queries can contain [Comments](syntax-comments.html "Comments"). This is useful for long multi-line queries and especially with saved queries, since later, you may not remember the purpose of each step. Below is an example of a comment embedded in a query: 

logscale
    
    
    #type=accesslog // choose the type
    | top(url)  // count urls and choose the most frequently used

### User Functions (Saved Searches)

In addition to built-in functions, you can create your own functions by saving a query that you use often. This can be used either as a saved query or saved search within other queries. Then it can be used as a top-level element of another query, similar to a [Function Call](https://library.humio.com/lql-grammar/syntax-grammar-guide-subset.html#syntax-grammar-guide-subset-function-call). 

To use a saved query this way you invoke it using the syntax `$"SAVED_QUERY_NAME"()` or, if the name does not contain whitespace or special characters you can use `$nameOfSavedQuery()` without quotes. A typical use for this is to define a filter or extraction ruleset that you can use as a prefix of another query. 

Below is an example of how you might name and use a custom function: 

logscale Syntax
    
    
    $"My Saved Query"()
    | $filterOutFalsePositive()
    | ...

Starting from LogScale version 1.140, you can pass multi-valued arguments to a saved query. For example: 

logscale
    
    
    $mySavedQuery(mvArgument=["value1", "value2", "value3"])

It can be used to pass multiple values to functions, for example: 

logscale
    
    
    in(values=?mvArgument,field=argument)

To save a query within the UI, see [Save queries](https://library.humio.com/data-analysis-1.189/writing-queries-manage-save.html). 

#### Using Arguments with User Functions

You can add arguments to your user functions by using the `?argname` in your saved query; you then call the saved query and supply the argument name and matching value. For example, given the following query: 

logscale
    
    
    host = ?host

Now save the query as `findhost`, you can execute the query using: 

logscale
    
    
    $findhost(host="gendarme")

Multiple arguments can be added during the process. For example, when processing [**syslog**](https://en.wikipedia.org/wiki/Syslog) data you can parse the content, create new fields, and then query that in the output: 

logscale
    
    
    regex(regex="Service exited due to (?<signal>\S+)")
    | signal = ?signal
    | regex(regex="sent by (?<process>\S+)[\d+]")
    | process = ?process

Now we have two arguments which we can save to as a query `killedprocess` and then query for killed processes: 

logscale
    
    
    $killedprocess(signal="SIGKILL", process="mds")

To call with only one argument, you can set a default value for the argument using `?{argument=default}`, for example: 

logscale
    
    
    ?{signal="*" }
    | ?{process="*"}
    | regex(regex="Service exited due to (?<signal>\S+)")
    | signal = ?signal
    | regex(regex="sent by (?<process>\S+)\[\d+\]")
    | process = ?process

Now you call the query with either argument: 

logscale
    
    
    $killedprocess(process="mds")

Starting from LogScale version 1.140, you can pass multi-valued arguments to a saved query. For example: 

logscale Syntax
    
    
    $mySavedQuery(mvArgument=["value1", "value2", "value3"])

It can be used to pass multiple values to functions, for example: 

logscale
    
    
    in(values=?mvArgument)

#### Using Functions as Arguments to Other Functions

Saved queries can be used in subqueries, passed to query functions that allow function arguments. However, saved queries used in such context must still meet the same requirements of the function they are in. 

For example, saved queries can be used in functions such as [`stats()`](functions-stats.html "stats\(\)") or [`groupBy()`](functions-groupby.html "groupBy\(\)"), like this: 

logscale Syntax
    
    
    groupBy("myField", function=[count(), {id=42
    | $"My Saved Query"() }])

### Link Functions

When showing search results in a table it is possible to create a link that is clickable. If the value of a field looks like a link, the UI will make it clickable. Links can be constructed using the search language. The [`format()`](functions-format.html "format\(\)") function can be handy for this. 

logscale
    
    
    $extractRepo()
    | top(repo)
    | format("https://example.com/%s", field=repo, as=link)

For further clarity, you can use Markdown formatting to give the link a title: 

logscale
    
    
    $extractRepo()
    | top(repo)
    | format("[Link](https://example.com/%s)", field=repo, as=link)

### Repeating Queries

Some functions have limitations around their use in live queries, such as [`join()`](functions-join.html "join\(\)") — see [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)") and [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)"). 

A repeating query is a static query that is executed at regular intervals and can be used in the same places as live queries, such as in dashboards or alerts. 

You can turn a live query into a repeating by adding the [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)") function to the query. For example, this query will be repeated every 10 minutes and can be used in dashboards and alerts: 

logscale
    
    
    selfJoin(field=email_id, where=[{from=peter},{to=anders}])
    | beta:repeating(10m)

Using [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)") in a static query is allowed, but has no effect. 

#### Enabling Repeating Queries

Repeating queries are in beta. In order to use repeating queries, you must enable them by making the following GraphQL mutation as root from the API explorer found at `$$YOUR_LOGSCALE_URL/docs/api-explorer`: 

graphql
    
    
    mutation {
      enableFeature(feature: RepeatingQueries)
    }

If this feature is disabled later, then any alert, dashboard, or saved query using [`beta:repeating()`](functions-beta-repeating.html "beta:repeating\(\)") in the query will not function.
