import os
import json
import argparse
import tableauserverclient as TSC


def signin(site_name, is_site_default, server_url):
    tableau_auth = TSC.TableauAuth(
            args.username, args.password, None if is_site_default else site_name)
    server = TSC.Server(server_url, use_server_version=True)
    server.auth.sign_in(tableau_auth)
    return server


def getProject(server, project_path, file_path):
    all_projects, pagination_item = server.projects.get()
    project = next(
        (project for project in all_projects if project.name == project_path), None)
    
    if project.id is not None:
        return project.id
    else:
        raiseError(
            f"The project for {file_path} workbook could not be found.", file_path)


def publishWB(server, file_path, name, project_id, show_tabs, hidden_views, tags, project_path, site_name):
    wb_path = os.path.dirname(os.path.realpath(__file__)).rsplit(
        '/', 1)[0] + "/workbooks/" + file_path

    new_workbook = TSC.WorkbookItem(
        name=name, project_id=project_id, show_tabs=show_tabs)
    new_workbook = server.workbooks.publish(
        new_workbook, wb_path, 'Overwrite', hidden_views=hidden_views)

    print(
        f"\nSuccessfully published {file_path} Workbook in {project_path} project in {site_name} site.")

    # Update Workbook and set tags
    if len(tags) > 0:
        new_workbook.tags = set(tags)
        new_workbook = server.workbooks.update(
            new_workbook)
        print(
            f"\nUpdate Workbook Successfully and set Tags.")


def raiseError(e, file_path):
    print(f"{file_path} workbook is not published.")
    raise LookupError(e)
    exit(1)


def main(args):
    project_data_json = json.loads(args.project_data)
    
    try:

        for data in project_data_json:
            # Step 1: Sign in to Tableau server.
            server = signin(data['site_name'], data['is_site_default'], data['server_url'])

            if data['project_path'] is None:
                raiseError(
                    f"The project project_path field is Null in JSON Template.", file_path)
            else:
                # Step 2: Get all the projects on server, then look for the required one.
                project_id = getProject(
                    server, data['project_path'], data['file_path'])

                # Step 3: Form a new workbook item and publish.
                publishWB(server, data['file_path'], data['name'], project_id,
                          data['show_tabs'], data['hidden_views'], data['tags'], data['project_path'], data['site_name'])

                # Step 4: Sign Out to the Tableau Server
                server.auth.sign_out()

    except Exception as e:
        print("Workbook not published.\n", e)
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(allow_abbrev=False)

    parser.add_argument('--username', action='store',
                        type=str, required=True)
    parser.add_argument('--password', action='store',
                        type=str, required=True)
    parser.add_argument('--project_data', action='store',
                        type=str, required=True)

    args = parser.parse_args()
    main(args)