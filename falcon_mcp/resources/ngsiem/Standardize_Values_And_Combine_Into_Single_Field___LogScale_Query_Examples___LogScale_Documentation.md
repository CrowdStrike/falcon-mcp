# Standardize Values And Combine Into Single Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-upper-lower-standardize.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Standardize Values And Combine Into Single Field

Standardize values using the [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) and [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) functions and combine into single field with [`concat()`](https://library.humio.com/data-analysis/functions-concat.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    lower(#severity, as=severity)
     
    | upper(#category, as=category)
     
    | concat([severity, category], as=test)
     
    | top(test)

### Introduction

The [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) function is used to format a string in lower case, and the [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) function is used to format a string in upper case. 

The [`lower()`](https://library.humio.com/data-analysis/functions-lower.html)/[`upper()`](https://library.humio.com/data-analysis/functions-upper.html) functions return a duplicate of an original string with all characters in lower case/upper case. 

Standardizing the format of fields is useful for consistent analysis. In this example, [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) and [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) functions are used with [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) to concatenate the fields #category and severity, where one field's result is all lower case letters and the other field's results are all upper case letters. 

If no [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) parameter is set, the fields outputted to is by default named _upper and _lower, respectively. 

In this query, the [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) parameter is used for the [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) and [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) functions to label their results. These output fields (category and severity) are then used with the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function, returning the concatenated string into a field named test. Finally, it uses the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function, to show which combinations of `severity` and `category` are most common in the data. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         lower(#severity, as=severity)

Converts the values in the #severity field to lower case and returns the results in a field named severity. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | upper(#category, as=category)

Converts the values in the #category field to upper case and returns the results in a field named category. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | concat([severity, category], as=test)

Concatenates (combines) the values in field category and field severity, and returns the concatenated string in a new field named test. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] 4{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | top(test)

Finds the most common values of the field test — the top of an ordered list of results - along with their count. The result of the count of their occurrences is displayed in a field named _count. 

  6. Event Result set.




### Summary and Results

The query is used to standardize the format of the values in the fields #category and severity and concatenate the values into a single field, showing which combinations of `severity` and `category` are most common in the data. 

The specific labeling of category and severity is particularly useful when you have more than one field that use the same query function. 

By converting fields to consistent cases, it helps standardize data for easier analysis and comparison. The concatenation allows you to combine multiple fields into a single field, which can be useful for creating unique identifiers or grouping related information. It provides a quick overview of the distribution of events across different `severity-category` combinations. 

Sample output from the incoming example data (showing the first 10 rows only): 

test| _count  
---|---  
infoALERT| 90005  
infoFILTERALERT| 36640  
errorALERT| 17256  
warningGRAPHQL| 14240  
warningALERT| 13617  
warningSCHEDULEDSEARCH| 11483  
infoSCHEDULEDSEARCH| 5917  
warningFILTERALERT| 1646  
errorFILTERALERT| 1487  
infoACTION| 3  
  
Notice how the value of #severity is in lower case letters, and the value of #category is in upper case letters.
