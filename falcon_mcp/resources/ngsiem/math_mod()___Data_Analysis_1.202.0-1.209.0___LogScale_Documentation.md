# math:mod() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-mod.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:mod()`](functions-math-mod.html "math:mod\(\)")

Calculates the floor modulus of field value and the divisor, for example, `x mod y` where `y` is the divisor and x is a field. Both the field or divisor are floor rounded before the calculation. Decimal values are supported. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-mod.html#query-functions-math-mod-as)|  string| optional[a] | `_mod`|  The name of the output field.   
[_`divisor`_](functions-math-mod.html#query-functions-math-mod-divisor)|  number| required |  |  The divisor to use, for example, x mod divisor.   
[_`field`_](functions-math-mod.html#query-functions-math-mod-field)[b]| string| required |  |  The name of the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-math-mod.html#query-functions-math-mod-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-math-mod.html#query-functions-math-mod-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     math:mod("value",divisor="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     math:mod(field="value",divisor="value")
> 
> These examples show basic structure only.

### [`math:mod()`](functions-math-mod.html "math:mod\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Floor Modulus of Values

**Calculate the remainder using floor modulus with the[`math:mod()`](functions-math-mod.html "math:mod\(\)") function **

##### Query

logscale
    
    
    x := 7
    | math:mod(x, 3, as=remainder)

##### Introduction

In this example, the [`math:mod()`](functions-math-mod.html "math:mod\(\)") function is used to calculate the remainder when a field value is divided by a specified [_`divisor`_](functions-math-mod.html#query-functions-math-mod-divisor) (`y = 3` in this case). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         x := 7

Assigns the value `7` to a field named x. This field value will be divided by the divisor in the modulus calculation. 

  3. logscale
         
         | math:mod(x, 3, as=remainder)

Calculates the floor modulus of the field value x with divisor (`y`) `3`, and returns the result in a new field named remainder. Both values are floor rounded before the calculation. If the [_`as`_](functions-math-mod.html#query-functions-math-mod-as) parameter is not specified, the result is returned in a field named _mod as default. 

  4. Event Result set.




##### Summary and Results

The query is used to calculate the remainder after division using floor modulus, which handles both positive and negative numbers consistently. 

This query is useful, for example, to determine if numbers are divisible evenly by a specific value, to implement circular buffers, or to distribute items evenly across groups. 

Sample output from the incoming example data: 

remainder  
---  
1  
  
The result shows that when `7` is divided by `3`, the remainder is `1` (as `7 = 2 × 3 + 1`). 

The function can also handle: 

  * Negative numbers (for example, `-7 mod 3 = 2`) 

  * Decimal values (for example, `7.8 mod 3 = 1`, as the value is floor rounded first) 

  * Decimal divisors (which are also floor rounded before calculation)
