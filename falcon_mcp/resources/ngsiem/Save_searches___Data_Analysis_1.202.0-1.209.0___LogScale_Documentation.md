# Save searches | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/writing-queries-manage-save-new.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Write Queries](writing-queries.html)

/ [Query management](writing-queries-manage.html)

Page was created:Jul 22, 2025

### Save searches

##### Security Requirements and Controls

  *  _`Delete saved queries`_ permission

  *  _`Create saved queries`_ permission

  *  _`Update saved queries`_ permission




You can save a query for future use — you save the query, not the resulting data. You can access saved queries, or recall recently run queries anytime later. 

From the [`Search`](searching-data.html "Search Data") interface, the Searches button organizes your queries in three tabs for recent, saved and favorite queries. 

![Screenshot showing the available tabs and functionality for managing saved and recent searches](images/queries/saved-searches.png)  
---  
  
**Figure 131. Saved Searches**

  


  * My recents tab. Lists recently run queries divided by date. You may either: 

    * Click on a recent query in the list to get a preview of the query in read-only mode, from which you can: 

      * click Run to make it running again 

      * save it as is by clicking ⋮ → Save to make it a new saved search (see [Figure 133, “Save a recent search”](writing-queries-manage-save-new.html#figure_ui-repo-search-saved-searches2 "Figure 133. Save a recent search")). 

      * load it to the query editor side panel to make changes before running your query again. 

    * Hover over a recent query to: 

      * make it running again without any preview by clicking Run

      * save it as is by clicking Save

      * edit directly in the query editor side panel before running your query again. 

**Figure 132. Playing with Recent Queries**

  


![Screenshot showing how to save a recent query](images/queries/save-recent-query.png)  
---  
  
**Figure 133. Save a recent search**

  


  * Saved searches tab. Shows all of your saved queries. This list also displays the labels and the package name each query comes from. 

The sorting of the Saved Searches list is organized by Package, Favourite status (user selected), and the name. The status of each saved search (whether it has been favourited) is not shown in the display.

You may either click or hover over a saved query in the list to access several functionalities: 

    * Add as function adds the query as a function (`$"MySavedQuery"()`) to the pipeline at the cursor position in the side panel. For more information about using saved queries as functions, see [User Functions (Saved Searches)](syntax-function.html#syntax-function-user "User Functions \(Saved Searches\)"). 

    * Load to editor loads the query to the query editor side panel without running the query. 

    * Run runs the query. 

    * Edit brings the query back to the [`Search`](searching-data.html "Search Data") page in Editing saved search mode. 

    * Add to favorites Stars/unstars the saved query. Starring the saved query will make it appear in the Favorites tab. 

    * Export as YAML exports the saved query as a file in yaml format. 

    * Duplicate allows for copying a saved query to the same repository or to a different repository/view. 

    * Asset sharing allows for sharing the saved search with another user, see [Grant permissions for saved queries](writing-queries-manage-asset-sharing.html "Grant permissions for saved queries") for more information. 

    * Delete deletes the saved query. 

Hint

Clicking instead of hovering a query allows you to preview the query in read-only mode and copy the query string, before taking any of the above actions. 

**Figure 134. Playing with Saved Queries**

  

  * Favorites tab. Lists the saved searches that have been marked as favorite. The functionalities available for saved searches also apply for favorites searches.
