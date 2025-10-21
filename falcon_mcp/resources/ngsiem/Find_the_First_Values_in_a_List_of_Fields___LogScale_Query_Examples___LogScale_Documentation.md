# Find the First Values in a List of Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-coalesce-first-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find the First Values in a List of Fields

Find the first values of a list of fields to normalize data using the [`coalesce()`](https://library.humio.com/data-analysis/functions-coalesce.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    coalesce([host, server, host[0].name, "example.com"])

### Introduction

The [`coalesce()`](https://library.humio.com/data-analysis/functions-coalesce.html) function accepts a list of fields and returns the first value that is not null or empty. Using [`coalesce()`](https://library.humio.com/data-analysis/functions-coalesce.html) returns the first matching value across the selection of supplied fields. 

In this example, [`coalesce()`](https://library.humio.com/data-analysis/functions-coalesce.html) is used to normalize data from different sources — the fields have the same meaning but different names in the input data. 

Example incoming data might look like this: 

host=''  
---  
server='crowdstrike.com'  
host[0].name='crowdstrike.com'  
machine='clienta'  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         coalesce([host, server, host[0].name, "example.com"])

Finds the values of the first three fields host, server, host[0].name and the value of a string `"example.com"` and returns the results in a new field named __coalesce. Notice that the query uses a string literal as the last expression, which serves as a default value, because its value is not null. The first three expressions, on the other hand, are field names. 

In this example, the field names are simple and do not contain unsupported characters. 

If the field names contain unsupported characters, for example a space or an operator like '-', then the field cannot be quoted in LogScale, as it would be interpreted as string literals. In these situations, the [`getField()`](https://library.humio.com/data-analysis/functions-getfield.html) must be used together with the [`coalesce()`](https://library.humio.com/data-analysis/functions-coalesce.html) function, like in the following example: `coalesce([getField("host-name"), getField("server name"), "example.com"])`

  3. Event Result set.




### Summary and Results

The query is used to normalize data from different sources by finding the first value of a list of fields that are defined. The [`coalesce()`](https://library.humio.com/data-analysis/functions-coalesce.html) function is useful if, for example, you want to easily pick the first non-null value from the list of prioritized fields and save it as a new field, or if you want to be able to use default (string) value or an expression instead of field name as an argument. 

Sample output from the incoming example data: 

_coalesce| host| server| host[0].name| machine  
---|---|---|---|---  
crowdstrike.com| <no value>| crowdstrike.com|  |
