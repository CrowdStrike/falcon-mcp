# Find Least Common Values of a Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-sort-least-common-values.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Least Common Values of a Field

Find the least common values of a field using the [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) function with [`count()`](https://library.humio.com/data-analysis/functions-count.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    groupby([type,kind], limit=max, function=count())
    | sort(_count, order=asc)

### Introduction

The [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) function is used to sort events based on a given field — or fields. 

The [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) function can be used to sort values in a field bottom up. This is the opposite of the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function, that can be used to find the most common values of a field in a set of events. 

In this example, the [`sort()`](https://library.humio.com/data-analysis/functions-sort.html) function is used to find the least common values of a field. Types of parsers used (type field) are grouped with their LogScale logging types (kind field) to find the least common values when searching for events of, for example, kinds `metrics`. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupby([type,kind], limit=max, function=count())

Groups the event set by the fields type and kind. For each unique combination of type and kind, it then counts the number of events, and returns the results in a field named _count. 

The parameter [_`limit`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-limit) is set to `max` to return all counts, as the purpose of this example is to find the least common values of a field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | sort(_count, order=asc)

Sorts the returned results in ascending order from the least common combinations to the most common combinations of type and kind. 

  4. Event Result set.




### Summary and Results

The query is used to find the least common values of a field in a set of events, in this example, identifying the least and most common type/kind combinations in an event set. Identifying rare combinations of type and kind could indicate unusual events or potential security issues. This type of query is useful in various scenarios, particularly for data analysis and understanding patterns in event sets.
