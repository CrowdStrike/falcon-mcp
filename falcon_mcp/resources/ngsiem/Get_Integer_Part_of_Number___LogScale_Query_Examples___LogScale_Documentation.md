# Get Integer Part of Number | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-regex-capturing-groups-combined-examples.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Get Integer Part of Number

Get the integer part of a number using the [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function and regex capturing groups 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    regex("(?<b>\\d+)\\..*",field=a)

### Introduction

Regex capturing groups are a way to treat multiple characters as a single unit. The capturing groups are created by placing the characters to be grouped inside a set of parentheses. The parentheses capture the text matched by the regex inside them into a numbered group that can be reused with a numbered backreference. This way you can get the integer part of a number. The syntax for creating a new named group is `/(?<b>)/`. 

The [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function works as a filter and can extract new fields using a regular expression. The regular expression can contain one or more named capturing groups. Fields with the names of the groups will be added to the events. 

In this example, regex pattern matching with a named capturing group is used to look at a filename and find something after the backslash, then store it in a new field named b, leaving the original field a unchanged. 

See also alternative method mentioned under the summary. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         regex("(?<b>\\d+)\\..*",field=a)

Looks for a sequence of characters in a capturing group and replaces the character with a digit (number): \\\ backslash (\\) \d+ one or more digits \\\ backslash (\\) . any character .* zero or more characters. If the sequence of characters in an event looks like this `\folder58\` instead of `\folder58\a` , then there is no filename as nothing comes after the `\`. 

  3. Event Result set.




### Summary and Results

The query with regex pattern matching and named capturing group is used to get the integer part of a number, storing the replacement (the matched value) automatically in a new field named b. This is useful when searching for specific filenames. 

The query using the [`regex()`](https://library.humio.com/data-analysis/functions-regex.html) function is primarily used for pattern matching and extraction as regex is generally very concise for simple extraction tasks. 

Alternative

There is another way of achieving the same end result using the [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function in a query like this: `replace("(\\d+)\\..*", with="$1", field=a, as=b)`. This query uses the replace function with numbered references to perform substitution, whereas the first one uses regex pattern matching with a named capture group. 

The query using [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) captures digits before the decimal point in an unnamed group, and explicitly creates a new field b with the result (\\\d+). 

This query using the [`replace()`](https://library.humio.com/data-analysis/functions-replace.html) function is more used for string manipulation and transformation in a replacement operation.
