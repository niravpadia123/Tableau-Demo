"""
Neccessory Module imports
"""
import xml.etree.ElementTree as ET
import tableauserverclient as TSC
xmlns = {'t': 'http://tableau.com/api'}


class ApiCallError(Exception):
    """
    Class Description
    """
    pass


def _encode_for_display(text):
    return text.encode('ascii', errors="backslashreplace").decode('utf-8')


def _check_status(server_response, success_code):
    if server_response.status_code != success_code:
        parsed_response = ET.fromstring(server_response.text)
        error_element = parsed_response.find('t:error', namespaces=xmlns)
        summary_element = parsed_response.find(
            './/t:summary', namespaces=xmlns)
        detail_element = parsed_response.find('.//t:detail', namespaces=xmlns)
        code = error_element.get(
            'code', 'unknown') if error_element is not None else 'unknown code'
        summary = summary_element.text if summary_element is not None else 'unknown summary'
        detail = detail_element.text if detail_element is not None else 'unknown detail'
        error_message = f'{code}: {summary} - {detail}'
        raise ApiCallError(error_message)
    return


def sign_in(data, username, password):
    """
    Funcrion Description
    """
    tableau_auth = TSC.TableauAuth(
        username, password, None if data['is_site_default'] else data['site_name'])
    server = TSC.Server(data['server_url'], use_server_version=True)
    server.auth.sign_in(tableau_auth)
    server_response = vars(server)
    auth_token = server_response.get('_auth_token')
    version = server_response.get('version')
    return server, auth_token, version


def get_project(server, data):
    """
    Funcrion Description
    """
    all_projects, pagination_item = server.projects.get()
    project = next(
        (project for project in all_projects if project.name == data['project_path']), None)
    if project.id is not None:
        return project.id
    else:
        raise LookupError(
            f"The project for {data['file_path']} workbook could not be found.")


def get_group_id(server, permission_group_name):
    """
    Function Description
    """
    all_groups, pagination_item = server.groups.get()
    group_id_list = [
        group.id for group in all_groups if group.name == permission_group_name]
    return group_id_list


def get_user_id(server, permission_user_name):
    """
    Funcrion Description
    """
    all_users, pagination_item = server.users.get()
    user_id_list = [
        user.id for user in all_users if user.name == permission_user_name]
    return user_id_list
