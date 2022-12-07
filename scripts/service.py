"""
Neccessory Module imports
"""
import logging
from publish import publish_wb, publish_ds
from helpers import sign_in, get_group_id, get_user_id, get_ds_id, dl_ds, ds_refresh
from permissions import query_permission, add_permission, delete_permission


def service_func(data, username, password, prod_username, prod_password, mpd):
    """
    This function call all internal methods and apis conditionally
    """
    # Datasource Part
    try:
        if data['is_datasource_update']:
            for datasources in data['datasources']:
                # Step: Sign In to the Tableau Server
                if datasources['get_ds_data']['get_ds_server_name'] == "dev":
                    uname, pname, surl = username, password, data['dev_server_url']
                elif datasources['get_ds_data']['get_ds_server_name'] == "prod":
                    uname, pname, surl = prod_username, prod_password, data['prod_server_url']

                server, auth_token, version = sign_in(
                    uname, pname, surl,
                    datasources['get_ds_data']['get_ds_site_name'],
                    datasources['get_ds_data']['is_site_default']
                )

                # Get datasource id from the name and project name
                ds_id = get_ds_id(
                    server, datasources['ds_name'],
                    datasources['get_ds_data']['get_ds_project_name'])[0]

                # Download datasource
                dl_ds_file_path = dl_ds(server, ds_id)

                # Step: Sign Out to the Tableau Server
                server.auth.sign_out()

                # Step: Sign In to the Tableau Server
                if datasources['publish_ds_data']['publish_ds_server_name'] == "dev":
                    uname, pname, surl = username, password, data['dev_server_url']
                elif datasources['publish_ds_data']['publish_ds_server_name'] == "prod":
                    uname, pname, surl = prod_username, prod_password, data['prod_server_url']

                server, auth_token, version = sign_in(
                    uname, pname, surl,
                    datasources['publish_ds_data']['publish_ds_site_name'],
                    datasources['publish_ds_data']['is_site_default']
                )

                # Publish Datasource
                ds_id = publish_ds(
                    server, datasources['publish_ds_data']['publish_ds_project_name'],
                    datasources['ds_name'], dl_ds_file_path,
                    datasources['publish_ds_data']['publish_ds_site_name']
                )

                mpd[data['index_id']]['_is_' + data['publish_wb_data']
                                      ['wb_name'] + '_datasource_updated'] = True

                # Refresh Datasource
                ds_refresh(server, datasources['ds_name'], ds_id)

            # Step: Sign Out to the Tableau Server
            server.auth.sign_out()
    except Exception as tableu_exception:
        mpd[data['index_id']]['_is_' + data['publish_wb_data']
                              ['wb_name'] + '_datasource_updated'] = False
        logging.error(
            "Something went wrong in publish datasource.\n %s", tableu_exception)


    is_sign_in = False
    # Sign in and Publish Workbook Part
    try:
        # Step: Sign In to the Tableau Server
        if data['is_wb_publish'] or data['is_wb_permissions_update']:
            if data['publish_wb_data']['server_name'] == "dev":
                uname, pname, surl = username, password, data['dev_server_url']
            elif data['publish_wb_data']['server_name'] == "prod":
                uname, pname, surl = prod_username, prod_password, data['prod_server_url']

            server, auth_token, version = sign_in(
                uname, pname, surl, data['publish_wb_data'][
                    'site_name'], data['publish_wb_data']['is_site_default']
            )

            is_sign_in = True

        if data['is_wb_publish']:
            wb_id = publish_wb(server, data)
            mpd[data['index_id']]['_is_' + data['publish_wb_data']
                                  ['wb_name'] + '_published'] = True
    except Exception as tableu_exception:
        mpd[data['index_id']]['_is_' + data['publish_wb_data']
                              ['wb_name'] + '_published'] = False
        logging.error(
            "Something went wrong in publishing workbook.\n %s", tableu_exception)

    # Permissions Part
    try:
        if data['is_wb_permissions_update']:
            for permission_data in data['permissions']:
                is_group = None

                mpd[data['index_id']]['_is_' + data['publish_wb_data']
                                      ['wb_name'] + '_permissions_updated'] = True

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

                # get permissions of specific workbook
                user_permissions = query_permission(
                    surl, version, data['publish_wb_data']['site_id'],
                    wb_id, auth_token, permission_user_or_group_id, is_group
                )

                if user_permissions is None:
                    for permission_name, permission_mode in \
                            permission_data['permission_template'].items():
                        add_permission(
                            surl, data['publish_wb_data']['site_id'],
                            wb_id, permission_user_or_group_id, version,
                            auth_token, permission_name, permission_mode, is_group)
                        print(
                            f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
                else:
                    existed_permissions_dict = {}
                    delete_permissions_dict = {}
                    existed_permissions_dict_key_list = []
                    all_permissions_key_list = []

                    for permission in user_permissions:
                        existed_permissions_dict.update(
                            {permission.get('name'): permission.get('mode')})

                    existed_permissions_dict_key_list = list(
                        existed_permissions_dict.keys())
                    all_permissions_key_list = list(
                        permission_data['permission_template'].keys())

                    common_permissioins_list = list(set(
                        existed_permissions_dict_key_list).intersection(set(all_permissions_key_list)))

                    for common_permissioins in common_permissioins_list:
                        delete_permissions_dict.update(
                            {common_permissioins: existed_permissions_dict.get(common_permissioins)})

                    for permission_name, permission_mode in delete_permissions_dict.items():
                        delete_permission(
                            surl, data['publish_wb_data']['site_id'], auth_token, wb_id,
                            permission_user_or_group_id, permission_name,
                            permission_mode, version, is_group)
                        print(
                            f"\tPermission {permission_name} : {permission_mode} is deleted Successfully in {wb_id}\n")

                    for permission_name, permission_mode in \
                            permission_data['permission_template'].items():
                        add_permission(
                            surl, data['publish_wb_data']['site_id'],
                            wb_id, permission_user_or_group_id, version,
                            auth_token, permission_name, permission_mode, is_group)
                        print(
                            f"\tPermission {permission_name} is set to {permission_mode} Successfully in {wb_id}\n")
    except Exception as tableu_exception:
        mpd[data['index_id']]['_is_' + data['publish_wb_data']
                              ['wb_name'] + '_permissions_updated'] = False
        logging.error(
            "Something went wrong in update permission of workbook.\n %s", tableu_exception)

    # Step: Sign Out to the Tableau Server
    if is_sign_in:
        server.auth.sign_out()
