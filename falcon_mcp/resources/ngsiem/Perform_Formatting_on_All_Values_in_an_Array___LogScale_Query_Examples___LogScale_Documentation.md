# Perform Formatting on All Values in an Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-eval-format.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform Formatting on All Values in an Array

Perform formatting on all values in a flat array using the [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

### Introduction

The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function is used to apply a specific function to each value inside an array. The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function processes every item in the list (array) one by one, performs some kind of calculation or operation, and either overwrites the original array or saves the result in a new array. 

In this example, the [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function is used to convert all values (for example `[Thermostat, Smart Light]`) in an array devices[] from lowercase to uppercase and show the results in a new array. 

Example incoming data might look like this: 

Raw Events

{\"devices\":[\"Thermostat\",\"Smart Plug\"],\"room\":\"Kitchen\"}"  
---  
{\"devices\":[\"Smart Light\",\"Thermostat\",\"Smart Plug\"],\"room\":\"Living Room\"}"  
{\"devices\":[\"Smart Light\",\"Smart Plug\"],\"room\":\"Bedroom\"}"  
{\"devices\":[\"Thermostat\",\"Smart Camera\"],\"room\":\"Hallway\"}"  
{\"devices\":[\"Smart Light\",\"Smart Lock\"],\"room\":\"Front Door\"}"  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:eval("devices[]",  asArray="upperDevices[]", var=d, function={upperDevices :=upper("d")})

Formats all values in the array devices[] to uppercase and returns the results in a new array named upperDevices[]. The values in the original array stay the same: `[Thermostat, Smart Plug, Smart Light]` and the new array contains the returned results: `[THERMOSTAT, SMART PLUG, SMART LIGHT]`

  3. Event Result set.




### Summary and Results

The query is used to turn values in an array into uppercase. The [`array:eval()`](https://library.humio.com/data-analysis/functions-array-eval.html) function can also be used for squaring a list of numbers in an array. 

Sample output from the incoming example data: 

devices[]| upperDevices[]  
---|---  
Thermostat| THERMOSTAT  
Smart Plug| SMART PLUG  
Smart Light| SMART LIGHT
