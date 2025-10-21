# Format a String to Upper Case and Lower Case | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-upper-lower-concat-string.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format a String to Upper Case and Lower Case

Format a string to upper case and lower case using the [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) and [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) functions with [`concat()`](https://library.humio.com/data-analysis/functions-concat.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    lower(@error_msg[0], as=msg1)
     
    | upper(@error_msg[1], as=msg2)
     
    | concat([msg1, msg2], as=test)

### Introduction

The [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) function is used to format a string in lower case, and the [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) function is used to format a string in upper case. 

The [`lower()`](https://library.humio.com/data-analysis/functions-lower.html)/[`upper()`](https://library.humio.com/data-analysis/functions-upper.html) functions return a duplicate of an original string with all characters in lower case/upper case. 

In this example, [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) and [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) functions are used with [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) to concatenate two fields containing error messages, where one field's result is all lower case letters and the other field's results are all upper case letters. 

If no [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) parameter is set, the fields outputted to is by default named _upper and _lower, respectively. 

In this query, the [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) parameter is used for the [`lower()`](https://library.humio.com/data-analysis/functions-lower.html) and [`upper()`](https://library.humio.com/data-analysis/functions-upper.html) functions to label their results. These fields (msg1 and msg2) are then used with the [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) function, returning the concatenated string into a field named test. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         lower(@error_msg[0], as=msg1)

Formats the first element (index 0) of the @error_msg array to lower case and returns the results in a field named msg1. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | upper(@error_msg[1], as=msg2)

Formats the second element (index 1) of the  @error_msg array to upper case and returns the results in a field named msg2. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2>Augment Data] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | concat([msg1, msg2], as=test)

Concatenates (combines) the values in field msg1 and field msg2, and returns the concatenated string in a new field named test. 

If using the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function on the test field, like this: 

`| top(test)`

then the top 10 values for the field test is displayed with a count of their occurrences in a field named _count. 

  5. Event Result set.




### Summary and Results

The query is used to either convert strings to lower case or upper case and return the new concatenated strings/results in a new field. In this example, concatenating error messages. 

The specific labeling of msg1 and msg2 is particularly useful when you have more than one field that use the same query function. 

By converting fields to consistent cases, it helps standardize data for easier analysis and comparison. The concatenation allows you to combine multiple fields into a single field, which can be useful for creating unique identifiers or grouping related information.
