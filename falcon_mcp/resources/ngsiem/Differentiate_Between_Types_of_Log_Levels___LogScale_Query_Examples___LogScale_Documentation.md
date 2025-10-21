# Differentiate Between Types of Log Levels | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-match-wildcard.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Differentiate Between Types of Log Levels

Differentiate between types of log levels using the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function with the match expression 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    loglevel match {     /.*ERROR.*/ => severity := "High";     in(values=["DEBUG", "INFO"]) => severity := "Low"; => severity := "Medium" }

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. It is possible to combine the [`in()`](https://library.humio.com/data-analysis/functions-in.html) with a match expression to differentiate between the different types of log levels. 

In this more advanced example, we match against the loglevel using the match filter statement. Notice that the semi-colon is used to end the different logical expressions. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         loglevel match {     /.*ERROR.*/ => severity := "High";     in(values=["DEBUG", "INFO"]) => severity := "Low"; => severity := "Medium" }

Matches all log levels which have the value/word `ERROR` inside their dataset and creates a new field named severity with the assigned value `High` for the returned results/matches. 

Then it matches events with the values `DEBUG` or `INFO` and assigns the value `Low` to the returned results in the severity field. If the severity field does not exist, it will create it, if the severity field does exist, it will overwrite the value of the field. For anything else, it sets the value in the severity field to `Medium`. 

In this example, a loglevel like `WARN` will therefore be set to `Medium`. 

Notice the use of double-quotes around the values to right of the assignment operator, if not used, it will be interpreted as a field and not a string. 

  3. Event Result set.




### Summary and Results

The query is used to differentiate between types of log levels. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| severity  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| High  
10.0.0.1| INFO| 200| user1| Low  
172.16.0.5| WARN| 422| user2| Medium  
192.168.1.15| ERROR| 500| admin| High  
10.0.0.12| DEBUG| 302| user1| Low
