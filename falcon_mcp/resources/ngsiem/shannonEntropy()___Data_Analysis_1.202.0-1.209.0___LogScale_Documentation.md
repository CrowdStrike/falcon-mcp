# shannonEntropy() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-shannonentropy.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`shannonEntropy()`](functions-shannonentropy.html "shannonEntropy\(\)")

Calculates a entropy measure from a string of characters. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-shannonentropy.html#query-functions-shannonentropy-as)|  string| optional[a] | `_shannonentropy`|  The output name of the field to set.   
[_`field`_](functions-shannonentropy.html#query-functions-shannonentropy-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-shannonentropy.html#query-functions-shannonentropy-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-shannonentropy.html#query-functions-shannonentropy-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     shannonEntropy("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     shannonEntropy(field="value")
> 
> These examples show basic structure only.

### [`shannonEntropy()`](functions-shannonentropy.html "shannonEntropy\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Shannon Entropy Value For String

**Calculate the Shannon Entropy value for string in a field using the[`shannonEntropy()`](functions-shannonentropy.html "shannonEntropy\(\)") function **

##### Query

logscale
    
    
    entropy := shannonEntropy(dns_name)

##### Introduction

In this example, the [`shannonEntropy()`](functions-shannonentropy.html "shannonEntropy\(\)") function is used to calculate the shannon entropy value for the string `example.com` in the field dns_name. The shannon entropy value is used to measure randomness/unpredictability in data. 

Example incoming data might look like this: 

dns_name  
---  
example.com  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         entropy := shannonEntropy(dns_name)

Calculates the shannon entropy value of the field dns_name, and returns the result in a field named entropy. 

  3. Event Result set.




##### Summary and Results

The query is used to calculate the shannon entropy value for the string in a field. In this example, the returned value for `example.com` is `3.095795`. Shannon entropy values typically range from `0` to `~8`. The lower the value is, the more predictable strings. The higher the value is, the more random strings. 

The shannon entropy calculation is primarily used in security analysis and threat detection scenarios to identify, for example, randomly generated malware filenames or expected distribution of characters in a domain name. 

Sample output from the incoming example data: 

entropy  
---  
3.095795  
  
The value `3.095795` is considered medium level and is typical for normal domain names. 

Note that the shannon value alone is not conclusive, context also matters. Use the value for further filtering or combine it with other aggregate functions.
