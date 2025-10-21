# Look up IP address IOCs | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-ioclookup-ip-addresses.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Look up IP address IOCs

Look up IP address Indicators of Compromise (IOCs) in the IP field using the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    ioc:lookup(field=ip, type=ip_address)

### Introduction

The ioc:lookup() function searches for IOCs (Indicators of Compromise) of IP addresses, URLs and domains in a local copy of CrowdStrike's curated database of IOCs and adds security information to the events. If any of the selected fields match an IOC, the field ioc (by default, controlled via the [_`include`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter) will be added to each event. 

In this example, the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function is used to search for IOCs for IP addresses in the ip field where the IP address is marked with a confidence threshold of high and annotate events with the associated security information. As default, without explicitly setting different arguments, the [_`confidenceThreshold`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-confidencethreshold) parameter is set to `high`. 

By default, a full set of fields is returned, and because an entry could match one or more IOCs, the information is returned as an array for each of these fields. The returned fields can be limited by using the [_`include`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter. The returned results can be limited by using the [_`strict`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         ioc:lookup(field=ip, type=ip_address)

Specifies which field to check for IOCs, in this case IP addresses. The [_`type`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-type) of the IOC to detect is `ip_address`. 

Note that the` ioc:lookup()` function only returns the IOC, if the IP address is marked with a confidence threshold of high. Therefore, it may not return anything at all. Lowering confidence thresholds increases matches but may include false positives. 

To explicitly lower the threshold for returned queries, use the following:` ioc:lookup(field=ip, type=ip_address, confidenceThreshold="low")`. This searches for thresholds of low or higher (for example: `low`, `medium` and `high`). 

To explicitly specify fields that should be returned to provide more detail, such as, for example, malicious_confidence and label, use the [_`include`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-include) parameter: `ioc:lookup(field=ip, type=ip_address, include=["malicious_confidence", "labels"])`. This will limit the returned fields. 

  3. Event Result set.




### Summary and Results

The query is used to search for IP address Indicators of Compromise (IOCs) in the ip field and annotate the returned events with the associated security information. In this example, all events are passed through. 

If setting the [_`strict`_](https://library.humio.com/data-analysis/functions-ioc-lookup.html#query-functions-ioc-lookup-strict) parameter to true, it only output events where at least one of the selected fields matches an IOC. Then the query should look like this: `ioc:lookup(field=ip, type=ip_address, strict=true)` to limit the output. 

### Note

If you use the [`ioc:lookup()`](https://library.humio.com/data-analysis/functions-ioc-lookup.html) function in a query and it does not produce any IOC results, it can be hard to tell whether there were no results or if there is an error in the query. The IOC database is updated constantly.
