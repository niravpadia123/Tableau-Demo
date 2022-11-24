"""
Neccessory Module imports
"""
import xml.etree.ElementTree as ET
from helpers import _check_status, _encode_for_display
import requests
xmlns = {'t': 'http://tableau.com/api'}


def query_permission(server_url, version, site_id, wb_id, auth_token, permission_user_or_group_id, is_group):
    """
    Funcrion Description
    """
    url = f"{server_url}api/{version}/sites/{site_id}/workbooks/{wb_id}/permissions"

    server_response = requests.get(
        url, headers={'x-tableau-auth': auth_token}, timeout=5000)
    _check_status(server_response, 200)
    server_response = _encode_for_display(server_response.text)
    parsed_response = ET.fromstring(server_response)
    capabilities = parsed_response.findall(
        './/t:granteeCapabilities', namespaces=xmlns)

    if is_group:
        for capability in capabilities:
            group = capability.find('.//t:group', namespaces=xmlns)
            if group is not None and group.get('id') == permission_user_or_group_id:
                return capability.findall('.//t:capability', namespaces=xmlns)
    else:
        for capability in capabilities:
            user = capability.find('.//t:user', namespaces=xmlns)
            if user is not None and user.get('id') == permission_user_or_group_id:
                return capability.findall('.//t:capability', namespaces=xmlns)


def add_permission(server_url, site_id, wb_id, permission_user_or_group_id, version,
                   auth_token, permission_name, permission_mode, is_group):
    """
    Funcrion Description
    """
    url = f"{server_url}api/{version}/sites/{site_id}/workbooks/{wb_id}/permissions"

    xml_request = ET.Element('tsRequest')
    permissions_element = ET.SubElement(xml_request, 'permissions')
    ET.SubElement(permissions_element, 'workbook', id=wb_id)
    grantee_element = ET.SubElement(permissions_element, 'granteeCapabilities')

    if is_group:
        ET.SubElement(grantee_element, 'group', id=permission_user_or_group_id)
    else:
        ET.SubElement(grantee_element, 'user', id=permission_user_or_group_id)

    capabilities_element = ET.SubElement(grantee_element, 'capabilities')
    ET.SubElement(capabilities_element, 'capability',
                  name=permission_name, mode=permission_mode)
    xml_request = ET.tostring(xml_request)

    server_request = requests.put(
        url, data=xml_request,  headers={'x-tableau-auth': auth_token}, timeout=5000)
    _check_status(server_request, 200)


def delete_permission(server_url, site_id, auth_token, wb_id, permission_user_or_group_id,
                      permission_name, existing_permission_mode, version, is_group):
    """
    Funcrion Description
    """
    if is_group:
        group_or_user = "groups"
    else:
        group_or_user = "users"

    url = f"{server_url}api/{version}/sites/{site_id}/workbooks/{wb_id}/permissions/{group_or_user}/{permission_user_or_group_id}/{permission_name}/{existing_permission_mode}"

    server_response = requests.delete(
        url, headers={'x-tableau-auth': auth_token},
        timeout=5000)
    _check_status(server_response, 204)
