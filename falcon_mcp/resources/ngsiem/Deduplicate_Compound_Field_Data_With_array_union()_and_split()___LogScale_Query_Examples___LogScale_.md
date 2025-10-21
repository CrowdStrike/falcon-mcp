# Deduplicate Compound Field Data With array:union() and split()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-dedupe-arrays-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Deduplicate Compound Field Data With [`array:union()`](https://library.humio.com/data-analysis/functions-array-union.html) and [`split()`](https://library.humio.com/data-analysis/functions-split.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2["Expression"] 3{{Aggregate}} 4[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ffbf00;

logscale
    
    
    splitString(field=userAgent,by=" ",as=agents)
    |array:filter(array="agents[]", function={bname=/\//}, var="bname")
    |array:union(array=agents,as=browsers)
    | split(browsers)

### Introduction

Deduplicating fields of information where there are multiple occurrences of a value in a single field, maybe separated by a single character can be achieved in a variety of ways. This solution uses [`array:union()`](https://library.humio.com/data-analysis/functions-array-union.html) and `split` create a unique array and then split the content out to a unique list. 

For example, when examining the [humio](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio.html) and looking for the browsers or user agents that have used your instance, the `UserAgent` data will contain the browser and toolkits used to support them, for example: 

Raw Events

Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36  
---  
  
The actual names are the `Name/Version` pairs showing compatibility with different browser standards. Resolving this into a simplified list requires splitting up the list, simplifying (to remove duplicates), filtering, and then summarizing the final list. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2["Expression"] 3{{Aggregate}} 4[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         splitString(field=userAgent,by=" ",as=agents)

First we split up the userAgent field using a call to [`splitString()`](https://library.humio.com/data-analysis/functions-splitstring.html) and place the output into the array field agents

This will create individual array entries into the agents array for each event: 

agents[0]| agents[1]| agents[2]| agents[3]| agents[4]| agents[5]| agents[6]| agents[7]| agents[8]| agents[9]| agents[10]| agents[11]| agents[12]  
---|---|---|---|---|---|---|---|---|---|---|---|---  
Mozilla/5.0| (Macintosh;| Intel| Mac| OS| X| 10_15_7)| AppleWebKit/537.36| (KHTML,| like| Gecko)| Chrome/116.0.0.0| Safari/537.36  
  
  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2["Expression"] 3{{Aggregate}} 4[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ffbf00; style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |array:filter(array="agents[]", function={bname=/\//}, var="bname")

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2["Expression"] 3{{Aggregate}} 4[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ffbf00; style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         |array:union(array=agents,as=browsers)

Using [`array:union()`](https://library.humio.com/data-analysis/functions-array-union.html) we aggregate the list of user agents across all the events to create a list of unique entries. This will eliminate duplicates where the value of the user agent is the same value. 

The event data now looks like this: 

browsers[0]| browsers[1]| browsers[2]  
---|---|---  
Gecko/20100101| Safari/537.36| AppleWebKit/605.1.15  
  
An array of the individual values. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2["Expression"] 3{{Aggregate}} 4[\Update Field Data\\] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ffbf00; style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | split(browsers)

Using the [`split()`](https://library.humio.com/data-analysis/functions-split.html) will split the array into individual events, turning: 

browsers[0]| browsers[1]| browsers[2]  
---|---|---  
Gecko/20100101| Safari/537.36| AppleWebKit/605.1.15  
  
into: 

_index| row[1]  
---|---  
0| Gecko/20100101  
1| Safari/537.36  
2| AppleWebKit/605.1.15  
  
  6. Event Result set.




### Summary and Results

The resulting output from the query is a list of events with each event containing a matching _index and browser. This can be useful if you want to perform further processing on a list of events rather than an array of values.
