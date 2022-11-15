"""
Neccessory Module imports
"""
import argparse
import json
import logging
from publish import publish_wb
from helpers import sign_in, get_group_id, get_user_id
from permissions import query_permission, add_permission, delete_permission

xmlns = {'t': 'http://tableau.com/api'}


def main(arguments):
    """
    Funcrion Description
    """
    project_data_json = json.loads(arguments.project_data)

    try:
        for data in project_data_json:

            # Step: Sign in to Tableau server.
            server, auth_token, version = sign_in(
                data, arguments.username, arguments.password)

            if data['project_path'] is None:
                raise LookupError(
                    "The project_path field is Null in JSON Template.")
            else:
                # Step: Form a new workbook item and publish.
                wb_id = publish_wb(server, data)

                if len(data['permissions']) > 0:
                    for permission_data in data['permissions']:
                        if permission_data['permission_template']:
                            print(
                                "---------------------------------------------------------------------------------------------------------------------------------")

                            is_group = None

                            # Step: Get the User or Group ID of permission assigned
                            if permission_data['permission_group_name'] and not permission_data['permission_user_name']:
                                permission_user_or_group_id = get_group_id(
                                    server, permission_data['permission_group_name'])[0]
                                is_group = True
                            elif not permission_data['permission_group_name'] and permission_data['permission_user_name']:
                                permission_user_or_group_id = get_user_id(
                                    server, permission_data['permission_user_name'])[0]
                                is_group = False
                            else:
                                logging.info(
                                    "permission_group_name and permission_user_name are both null, Please provide anyone of that.")

                            # get permissions of specific workbook
                            user_permissions = query_permission(
                                data, wb_id, permission_user_or_group_id, version, auth_token, is_group)

                            for permission_name, permission_mode in permission_data['permission_template'].items():
                                update_permission_flag = True
                                if user_permissions is None:
                                    add_permission(
                                        data, wb_id, permission_user_or_group_id, version, auth_token, permission_name, permission_mode, is_group)
                                    print(
                                        f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
                                    update_permission_flag = False
                                else:
                                    for permission in user_permissions:
                                        if permission.get('name') == permission_name:
                                            if permission.get('mode') != permission_mode:
                                                existing_mode = permission.get(
                                                    'mode')
                                                delete_permission(
                                                    data, auth_token, wb_id, permission_user_or_group_id, permission_name, existing_mode, version, is_group)
                                                update_permission_flag = True
                                                print(
                                                    f"\tPermission {permission_name} : {existing_mode} is deleted Successfully in {wb_id}\n")
                                            else:
                                                update_permission_flag = False

                                if update_permission_flag:
                                    add_permission(
                                        data, wb_id, permission_user_or_group_id, version, auth_token, permission_name, permission_mode, is_group)
                                    print(
                                        f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
                                else:
                                    print(
                                        f"\tPermission {permission_name} is already set to {permission_mode} on {data['name']}\n")

                        else:
                            logging.info(
                                "Something went wrong, Error occured.\n User Name or List of Permissions in template are null")
                else:
                    logging.info(
                        "Something went wrong, Error occured.\n Permissions in template are null")

            # Step: Sign Out to the Tableau Server
            server.auth.sign_out()

    except Exception as tableu_exception:
        logging.error(
            "Something went wrong, Exception Fired.\n %s", tableu_exception)
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
