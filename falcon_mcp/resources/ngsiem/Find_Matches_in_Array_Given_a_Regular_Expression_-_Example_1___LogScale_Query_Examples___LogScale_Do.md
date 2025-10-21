# Find Matches in Array Given a Regular Expression - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-regex-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Matches in Array Given a Regular Expression - Example 1

Use regular expressions to search for and match specific patterns in flat arrays 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    array:regex("incidents[]", regex="^Cozy Bear.*")
    | groupBy(host)

### Introduction

A regular expression is a form of advanced searching that looks for specific patterns, as opposed to certain terms and phrases. You can use a regular expression to find all matches in an array. 

In this example, the regular expression is used to search for patterns where the value `Cozy Bear` appears in a certain position across arrays. 

Example incoming data might look like this: 

host| incidents[0]| incidents[1]| incidents[2]  
---|---|---|---  
v1| Evil Bear| Cozy Bear|   
v15| Fancy Fly| Tiny Cat| Cozy Bears  
v22| Fancy Fly| Tiny Cat| Cold Bears  
v4| Fancy Fly| Tiny Cat| Cozy Bearskins  
v1| Evil Bear| Cozy Bears|   
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:regex("incidents[]", regex="^Cozy Bear.*")

Searches in the incidents array for values that only start with `Cozy Bear`. Find all matches given that regular expression. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Array Manipulation]] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | groupBy(host)

Groups the returned results by host. 

  4. Event Result set.




### Summary and Results

The query using the regex expression are used to quickly search and return results for specific values in arrays. Regular expressions are useful when searching for different strings containing the same patterns; such as social security numbers, URLs, email addresses, and other strings that follow a specific pattern. 

Sample output from the incoming example data: 

host| _count  
---|---  
v1| 2  
v15| 1  
v4| 1
