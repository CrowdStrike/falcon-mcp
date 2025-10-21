# setField() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-setfield.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`setField()`](functions-setfield.html "setField\(\)")

Takes two expressions — `target` and `value` — and sets the field named by the result of the `target` expression to the result of the `value` expression. 

Can be used to manipulate fields whose names are not statically known, but computed at runtime. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`target`_](functions-setfield.html#query-functions-setfield-target)|  expression| required | `__setField`|  Evaluates the name of the field to set.   
[_`value`_](functions-setfield.html#query-functions-setfield-value)|  expression| required |  |  An expression whose result becomes the value for the field.   
  
### [`setField()`](functions-setfield.html "setField\(\)") Examples

Click + next to an example below to get the full details.

#### Set Values for Multiple Fields

****

##### Query

logscale
    
    
    item := 4
    | bar := "baz"
    | setField(target=bar, value=item + 10)
    | setField(target="foo", value=item + 20)
    | setField(target="baaz", value=if(item == 4, then="OK", else="not OK"))

##### Introduction

Set the value of more fields as the result of several expressions. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         item := 4

In a `test` event where field item is set to `4`: 

  3. logscale
         
         | bar := "baz"

Points field bar to field "baz": 

  4. logscale
         
         | setField(target=bar, value=item + 10)

Takes field bar as the target, gets the field pointed to by bar (baz) and sets its value as the result of the expression `value of item + 10`. 

  5. logscale
         
         | setField(target="foo", value=item + 20)

Takes field foo as the target, sets its value as the result of the expression "value of item \+ 20": 

  6. logscale
         
         | setField(target="baaz", value=if(item == 4, then="OK", else="not OK"))

Adds an [`if()`](functions-if.html "if\(\)") function whose condition will set the value of the new target field baaz: for example, if item is equal to `4`, then the value of field baaz is `OK`, otherwise `not OK`. 

  7. Event Result set.




##### Summary and Results

We look at different target fields to set their values as the result of a given expression. Functions can be added as part of the expression in the [_`value`_](functions-setfield.html#query-functions-setfield-value) parameter, to determine the value of another target expression. 

baaz| bar| bar| baz| foo| item  
---|---|---|---|---|---  
OK| baz| baz| 14| 24| 4  
  
#### Set the Value of a Field

****

##### Query

logscale
    
    
    item := 4
    | setField(target="foo", value=item + 10)

##### Introduction

Set the value of a target field as the result of an expression. This is equivalent to: 

logscale
    
    
    item := 4
    | foo := item + 10

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         item := 4

In a `test` event the field item is set to `4`. 

  3. logscale
         
         | setField(target="foo", value=item + 10)

Sets the value of the target field foo as the result of the expression `value of item + 10`. 

  4. Event Result set.




##### Summary and Results

foo| item  
---|---  
14| 4
