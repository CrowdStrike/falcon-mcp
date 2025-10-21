# Calculate Shannon Entropy Value For String | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-shannonentropy-calculation.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Shannon Entropy Value For String

Calculate the Shannon Entropy value for string in a field using the [`shannonEntropy()`](https://library.humio.com/data-analysis/functions-shannonentropy.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    entropy := shannonEntropy(dns_name)

### Introduction

The [`shannonEntropy()`](https://library.humio.com/data-analysis/functions-shannonentropy.html) function can be used to calculate a shannon entropy value of a string. Entropy measurement provides aspects about data patterns and randomness. 

In this example, the [`shannonEntropy()`](https://library.humio.com/data-analysis/functions-shannonentropy.html) function is used to calculate the shannon entropy value for the string `example.com` in the field dns_name. The shannon entropy value is used to measure randomness/unpredictability in data. 

Example incoming data might look like this: 

dns_name  
---  
example.com  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         entropy := shannonEntropy(dns_name)

Calculates the shannon entropy value of the field dns_name, and returns the result in a field named entropy. 

  3. Event Result set.




### Summary and Results

The query is used to calculate the shannon entropy value for the string in a field. In this example, the returned value for `example.com` is `3.095795`. Shannon entropy values typically range from `0` to `~8`. The lower the value is, the more predictable strings. The higher the value is, the more random strings. 

The shannon entropy calculation is primarily used in security analysis and threat detection scenarios to identify, for example, randomly generated malware filenames or expected distribution of characters in a domain name. 

Sample output from the incoming example data: 

entropy  
---  
3.095795  
  
The value `3.095795` is considered medium level and is typical for normal domain names. 

Note that the shannon value alone is not conclusive, context also matters. Use the value for further filtering or combine it with other aggregate functions.
