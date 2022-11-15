"""
Neccessory Module imports
"""
import os
from helpers import get_project
import tableauserverclient as TSC


def publish_wb(server, data):
    """
    Funcrion Description
    """

    if data['is_workbook_new']:
        publish_type = "CreateNew"
    else:
        publish_type = "Overwrite"

    project_id = get_project(server, data)
    wb_path = os.path.dirname(os.path.realpath(__file__)).rsplit(
        '/', 1)[0] + "/workbooks/" + data['file_path']

    new_workbook = TSC.WorkbookItem(
        name=data['name'], project_id=project_id, show_tabs=data['show_tabs'])
    new_workbook = server.workbooks.publish(
        new_workbook, wb_path, publish_type, hidden_views=data['hidden_views'] if len(data['hidden_views']) > 0 else None)

    print(
        f"\nSuccessfully published {data['file_path']} Workbook in {data['project_path']} project in {data['site_name']} site.")

    # Update Workbook and set tags
    if len(data['tags']) > 0:
        new_workbook.tags = set(data['tags'])
        new_workbook = server.workbooks.update(
            new_workbook)
        print("\nUpdate Workbook Successfully and set Tags.")

    return new_workbook._id
