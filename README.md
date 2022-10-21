# Things to Consider before Publishing Workbook

1) whenever we publish the twb/twbx file we need to add the below details in project-data json file

 * name          = workbookname

 * file_path     = workbookname (with .twb/.twbx extension for eg sales.twbx) 

 * tags          = if no tags are there than keep it blank ""

 * hidden views  = if the anyworksheet we have to hide then mention the Worksheet name in "sheetname" 

 * show_tabs     =dashboards or worksheet need to show as tabs then mark as true and for no tabs mark it as false

2) If publishing single workbook then add those details in json file or if want to publish multiple workbooks then each workbook details needs to be mention in json   just like below

* Single Workbook json eg:-
  
  {
  "workbooks": [
    {
      "name": "WorkbookName",
      "file_path": "WorkbookName.twbx",
      "project_path": "Technology",
      "tags": [
        "Forecasting",
        "Crop"
      ],
      "hidden_views": [
        "State","Price Forecast"
      ],
      "show_tabs": true,
      "description": "Price Forecast"
    }
  ]
}

* Multiple workbook json for eg(2 workbook publishing):-

  {
  "workbooks": [
         {
      "name": "workbook1",
      "file_path": "workbook1.twbx",
      "project_path": "Technology",
      "tags": [
        "Forecasting",
        "Crop"
      ],
      "hidden_views": [
        "State","Price Forecast"
      ],
      "show_tabs": true,
      "description": "Price Forecast"
    },
    {
      "name": "workbook2",
      "file_path": "workbook2.twbx",
      "project_path": "Default",
      "tags": [
        "",
        ""
      ],
      "hidden_views": [
        "",""
      ],
      "show_tabs": true,
      "description": "Price Forecast"
    }
  ]
}

3) If Any of the Workbook detail in Json file is incorrect then that workbook will not publish

4) If only want to delete workbook from branch then keep fields of json file empty and along with empty json commit for deleting the workbook

5) If we are adding and deleting workbook in single commit then only added file details need to mention in json and no need to add balnk details in json for deleting file 


