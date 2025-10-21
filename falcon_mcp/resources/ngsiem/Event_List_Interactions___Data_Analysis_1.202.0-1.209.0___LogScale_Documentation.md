# Event List Interactions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-search-interactions.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Mar 28, 2023

## Event List Interactions

##### Security Requirements and Controls

  * [ _`Change interactions`_](https://library.humio.com/falcon-logscale-self-hosted/security-authorization-role-permissions.html#security-search-permissions-changeinteractions) permission




**Event List Interactions** allows to interact actively with the data and explore it in deep detail. These interactions are added as options in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events"), and work as quick workflows triggered directly from the search results. 

For example, every time an event includes an IP address, you can: 

  * Trigger a look up in an external system directly from the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") — a kind of "WHOIS" search based on the IP address found in the event. 

  * Control the context in which the interaction should be displayed, to only show it in events that actually have the field IP address — because this interaction makes sense only if such specific condition is met. 




Event list interactions are available within a certain scope — that is, they apply to some given [_Manage Repositories and Views_](repositories.html "Manage Repositories and Views"). 

These scoped interactions are collected in an overview page from which to create more preset interactions, or where other users in the Organization access to reuse the interactions you have created, see [Figure 108, “Overview of your interactions”](searching-data-search-interactions.html#figure_searching-data-search-interactions-create1 "Figure 108. Overview of your interactions"). 

Not every user can see, configure or edit these interactions, this depends on the permissions set for them in the given repository. 

Once created, these interactions are displayed in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") for every search within a repository. 

For the steps on how to configure Event List interactions, see [Access and Create Event List Interactions](searching-data-search-interactions.html#searching-data-search-interactions-create "Access and Create Event List Interactions"). 

### Access and Create Event List Interactions

To create a new interaction: 

  1. Click the avatar icon  → select Manage interactions: 

![Access Interactions from the Profile Menu](images/search-data/interactions-overview-profile-menu.png)  
---  
  
**Figure 107. Access Interactions from the Profile Menu**

  


The [`Interactions`](searching-data-field-interactions.html "Field Interactions") overview page is displayed, showing all interactions you have previously created: 

![Interactions Overview](images/search-data/interactions-overview.png)  
---  
  
**Figure 108. Overview of your interactions**

  

  2. To see the available interactions created by other users for a specific repository, open the [`Resources`](ui-repo-resources.html "Resources interface") tab within a repository → click Interactions from the left-hand navigation panel: 

![Interactions Overview from the Resources tab](images/search-data/interactions-overview-resources.png)  
---  
  
**Figure 109. Repository Interactions by multiple users**

  


For information on the available interactions metadata in this page, see [Asset type interface elements](ui-repo-resources-types.html "Asset type interface elements"). 

  3. Click \+ New interaction. The Create new interaction dialog box opens, which allows you to configure the new interaction. 

![Create New Interaction](images/search-data/create-new-event-interaction.png)  
---  
  
**Figure 110. Create new interaction**

  

  4. Enter the Name — the name assigned to the interaction, by default **`Interaction #1`** , which you can change for example, **`Lookup IP.`**

  5. Enter the Title template — A template for the text that appears in the interaction menus. Values for fields are entered using a required language syntax, the [_Template Language_](template-language.html "Template Language"). For example, to use the aid field from FDR data, the syntax would be **`{{ fields.aid }}`**. 

If you want to provide a more precise label for the interaction, you can add it here: for example, for an element or row where the field IPAddress is set to **`172.17.0.30`** , the title of the interaction in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") when clicking on that element or row would be Lookup 172.17.0.30, see [Figure 112, “Event List Interaction”](searching-data-search-interactions.html#figure_searching-data-search-interactions-create4 "Figure 112. Event List Interaction"). 

If left empty, Name will be used to label the interaction. 

  6. Specify the Scope — the repository or view where you want the new interaction to be added. 

  7. Specify the Behavior — the destination Type you want your widget to interact with, between: 

     * Dashboard link — lookup for an item in a related dashboard. 

You can open the destination dashboard to a new tab, and either use the time from the current dashboard or the time from the destination dashboard. See [???]() for more information on how to configure this type of interaction. 

     * Custom link — lookup for an item in an external location by linking your widget to the destination URL. See [???]() for more information on how to configure this type of interaction. 

     * Search link — allows navigation to the Search page by running a query detected from the dashboard. See [???]() for more information on how to configure this type of interaction. 

  8. Set the Parameter bindings (only visible if Search link is selected) — use fields from within events and bind them to the [parameters]() in the destination target. The value can be static text and/or variables such as parameters and fields, for example, **`{{ fields.myField }}`** — see [Template Variable Types](template-language-variables.html "Template Variable Types"). 

You can choose whether to bind the parameter to some defined values or keep it unbound (to retain the default behavior of the target destination when the interaction is triggered). To keep it unbound, leave the input field empty. 

Other parameter options are: 

     * **Empty list alias**. 

In case of [???](), you can also specifically bind the parameter to an empty list of values by selecting the **`empty list`** alias in the input field — it is available as an option along with the other input values. This option acts as a parameter binding with no values selected for that parameter, and will serve as an argument to the parameter itself. 

     * **Unused parameters bindings**. 

When creating or editing interactions you may need to change the target query, resulting in some parameter bindings no longer mapping to any parameters in the current query. The interaction panel shows such unused parameter bindings, and gives you the option to remove them via the UI. 

![Unused Parameter Bindings](images/dashboards/unused-bindings.png)  
---  
  
**Figure 111. Unused Parameter Bindings**

  


Use the [_Template Language_](template-language.html "Template Language") to populate values based on the widget you are interacting with. 

  9. Under Conditions, click +Add condition to set when you want the interaction to be shown, given some specified conditions. This allows to show the interaction only when a given field in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") is equal to a specified value, for example #event_simpleName field equal to **`NetworkConnectIP4`** value. 

### Note

Field names and values with spaces (for example, field: Alert Name, value: Network Scans Count) must be put _without_ quotes in the Conditions field. 

With quotes around them (for example, "Alert Name") the condition does not work, and the contextual ⋮ menu disappears. 

  10. Click the ⋮ icon next to each event in the [Event list](searching-data-changing-the-events-display.html "Display Results and Events") to see the interaction in the contextual menu (under [Inspect](searching-data-inspecting-events.html "Inspect Events") and [Show in context](searching-data-show-context.html "Show Events in Context") menu options). See [Show in Context](searching-data-show-context.html "Show Events in Context"). 




In the following example, the interaction looks for a specific IP found in the event. 

![Event List Interaction](images/search-data/event-list-interaction.png)  
---  
  
**Figure 112. Event List Interaction**

  


#### Deleting and Duplicating Event List Interactions

It is possible to delete or duplicate an existing interaction. 

From the `Interactions` overview page, click the ⋮ icon next to a specific interaction and select the relevant option to either delete or dublicate it. 

Clicking Duplicate interaction opens the Create new interaction dialog box where you can make appropriate changes. 

![Interaction Context Menu](images/search-data/event-list-interaction-menu.png)  
---  
  
**Figure 113. Interaction Context Menu**
