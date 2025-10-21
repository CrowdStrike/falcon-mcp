# Categorize Events Based on Values in More Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-combined.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Categorize Events Based on Values in More Fields

Categorize events based on values across multiple fields - the example uses a combination of [`in()`](https://library.humio.com/data-analysis/functions-in.html) with `case`, [`match()`](https://library.humio.com/data-analysis/functions-match.html), and [`if()`](https://library.humio.com/data-analysis/functions-if.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    case {     in(srcIP, values=["192.168.1.*"])
    | type := "Internal";     !in(loglevel, values=["DEBUG", "INFO"])
    | type := "Critical";
    | type := "Other" }

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. It is possible to combine the [`in()`](https://library.humio.com/data-analysis/functions-in.html) with a case statement to categorize events. 

In this more advanced example, a case statement is used to categorize events based on the fields srcIP and loglevel, using both [`in()`](https://library.humio.com/data-analysis/functions-in.html) and negated [`in()`](https://library.humio.com/data-analysis/functions-in.html). Notice that the semi-colon is used to end the different logical expressions. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         case {     in(srcIP, values=["192.168.1.*"])
         | type := "Internal";     !in(loglevel, values=["DEBUG", "INFO"])
         | type := "Critical";
         | type := "Other" }

Returns all events with values starting with `192.168.1.*` followed by anything in the scrIP field and then creates a new field named type with the assigned value `Internal` for the returned results. Notice that since the wildcard is used, the double-quotes is required. 

Next, the query searches for events where the field loglevel does not contain the values `DEBUG` or `INFO` and assigns the value `Critical` to the returned results in the type field. For anything else, it sets the value in the type field to `Other`. 

In this example, `INFO` and `DEBUG` will therefore be set to `Other`. The above case statement can also be expressed like this: If the sourceIP equals the value `192.168.1.*` followed by anything, then identify the type field as `Internal`. If it is not equal to the loglevel of debug or info, then identify the type field as `Critical`. If it does not match either of the above, identify the type field as `Other`. 

  3. Event Result set.




### Summary and Results

The query is used to to categorize events and define their type. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| type  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| Internal  
10.0.0.1| INFO| 200| user1| Other  
172.16.0.5| WARN| 422| user2| Critical  
192.168.1.15| ERROR| 500| admin| Internal  
10.0.0.12| DEBUG| 302| user1| Other
