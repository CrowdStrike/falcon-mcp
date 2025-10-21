# Look up URL IOCs | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-ioclookup-url.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Look up URL IOCs

Look up URL Indicators of Compromise (IOCs) in the URL field using the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    ioc:lookup("url", type="url", confidenceThreshold="low")

### Introduction

The [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function searches for IOCs (Indicators of Compromise) of IP addresses, URLs and domains in a local copy of CrowdStrike's curated database of IOCs and adds security information to the events. If any of the selected fields match an IOC, the field ioc (by default, controlled via the [_`include`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter) will be added to each event. 

In this example, the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function is used to search for IOCs for URLs in the url field where the URL is marked with a confidence threshold of low and annotate events with the associated security information. As default, without explicitly setting different arguments, the [_`confidenceThreshold`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold) parameter is set to `high`. 

By default, a full set of fields is returned, and because an entry could match one or more IOCs, the information is returned as an array for each of these fields. The returned fields can be limited by using the [_`include`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter. The returned results can be limited by using the [_`strict`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ioc:lookup("url", type="url", confidenceThreshold="low")

Specifies which field to check for IOCs, in this case URL, and searches IOCs of all verified confidence levels, for example, `low`, `medium`, and `high`. The [_`type`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-type) of the IOC to detect is `url`. 

Note that the` ioc:lookup()` function returns all the IOCs, as the URL is marked with a confidence threshold of low (`[_`confidenceThreshold`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold)=low`). Lowering confidence thresholds increases matches but may include false positives. 

  3. Event Result set.




### Summary and Results

The query is used to search for URL Indicators of Compromise (IOCs) in the url field and annotate the returned events with the associated security information. In this example, all events are passed through. 

If setting the [_`strict`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter to true, it only output events where at least one of the selected fields matches an IOC. Then the query should look like this: `ioc:lookup("url", type="url", confidenceThreshold="low", strict=true)` to limit the output. Looking up URL IOCs for the field url and only keep the events containing an IOC is useful for finding IOCs in queries used for alerts or scheduled searches. 

### Note

If you use the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function in a query and it does not produce any IOC results, it can be hard to tell whether there were no results or if there is an error in the query. The IOC database is updated constantly.
