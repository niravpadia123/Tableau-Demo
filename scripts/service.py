"""
Neccessory Module imports
"""
import logging
from publish import publish_wb, publish_ds
from helpers import sign_in, get_group_id, get_user_id, get_ds_id, dl_ds, ds_refresh
from permissions import query_permission, add_permission, delete_permission


def temp_func(data, username, password):
    """
    Funcrion Description
    """
    try:
        if data['project_path']:
            server, auth_token, version = sign_in(
                username, password, data['server_url'], data['site_name'], data['is_site_default'])

            # Step: Form a new workbook item and publish.
            wb_id = publish_wb(server, data)

            if len(data['permissions']) > 0:
                for permission_data in data['permissions']:
                    if permission_data['permission_template']:
                        is_group = None

                        # Step: Get the User or Group ID of permission assigned
                        if permission_data['permission_group_name'] and \
                                not permission_data['permission_user_name']:
                            permission_user_or_group_id = get_group_id(
                                server, permission_data['permission_group_name'])[0]
                            is_group = True
                        elif not permission_data['permission_group_name'] and \
                                permission_data['permission_user_name']:
                            permission_user_or_group_id = get_user_id(
                                server, permission_data['permission_user_name'])[0]
                            is_group = False
                        else:
                            logging.info(
                                "permission_group_name and permission_user_name are both null, Please provide anyone of that.")

                        # get permissions of specific workbook
                        user_permissions = query_permission(
                            data, wb_id, permission_user_or_group_id,
                            version, auth_token, is_group)

                        for permission_name, permission_mode in \
                                permission_data['permission_template'].items():
                            if user_permissions is None:
                                add_permission(
                                    data, wb_id, permission_user_or_group_id, version,
                                    auth_token, permission_name, permission_mode, is_group)
                                print(
                                    f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
                            else:
                                for permission in user_permissions:
                                    if permission.get('name') == permission_name and \
                                            permission.get('mode') != permission_mode:
                                        existing_mode = permission.get(
                                            'mode')

                                        delete_permission(
                                            data, auth_token, wb_id,
                                            permission_user_or_group_id, permission_name,
                                            existing_mode, version, is_group)
                                        print(
                                            f"\tPermission {permission_name} : {existing_mode} is deleted Successfully in {wb_id}\n")

                                        add_permission(
                                            data, wb_id, permission_user_or_group_id,
                                            version, auth_token, permission_name,
                                            permission_mode, is_group)
                                        print(
                                            f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
                    else:
                        logging.info(
                            "Something went wrong, Error occured.\n User Name or List of Permissions in template are null")
            else:
                logging.info(
                    "Something went wrong, Error occured.\n Permissions in template are null")

            # Step: Sign Out to the Tableau Server
            server.auth.sign_out()

        if data['datasource'] and data['datasource']['ds_name'] \
                and data['datasource']['get_ds_project_name'] \
                and data['datasource']['publish_ds_project_name']:

            # Step: Sign In to the Tableau Server
            server, auth_token, version = sign_in(
                username, password, data['datasource']['get_ds_server_url'], '', True)

            # Get datasource id from the name and project name
            ds_id = get_ds_id(
                server, data['datasource']['ds_name'], data['datasource']['get_ds_project_name'])[0]

            # Download datasource
            dl_ds_file_path = dl_ds(server, ds_id)

            # Step: Sign Out to the Tableau Server
            server.auth.sign_out()

            # Step: Sign In to the Tableau Server
            server, auth_token, version = sign_in(
                username, password, data['datasource']['publish_ds_server_url'], '', True)

            # Publish Datasource
            publish_ds(server, data, dl_ds_file_path)

            if data['datasource']['is_ds_refresh']:
                # Refresh Datasource
                ds_refresh(server, data['datasource']['ds_name'],
                        data['datasource']['publish_ds_project_name'])

            # Step: Sign Out to the Tableau Server
            server.auth.sign_out()

    except Exception as tableu_exception:
        logging.error(
            "Something went wrong, Exception Fired.\n %s", tableu_exception)
        exit(1)
