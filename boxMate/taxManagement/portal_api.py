"""
in this file all the interaction with e-invoice portal APIs are done
by: amira
date: 13/4/2021
"""
import time
import requests
from rest_framework import status
from taxManagement.models import Submission


def get_token():
    url = "https://id.preprod.eta.gov.eg/connect/token"
    client_id = "547413a4-79ee-4715-8530-a7ddbe392848"
    client_secret = "913e5e19-6119-45a1-910f-f060f15e666c"
    scope = "InvoicingAPI"

    data = {"grant_type": "client_credentials", "client_id": client_id,
            "client_secret": client_secret, "scope": scope}
    response = requests.post(url, verify=False,
                             data=data)
    global auth_token
    auth_token = response.json()["access_token"]


def get_submission_response(submission_id):
    """
    This function is used to check and save the overall status of the submission ,
    doc number,doc_uuid,doc_count and time received.

    :param submission_id: the subm_id of the invoice to save its submission data
    :return: response object from the gov api
    """
    get_token()
    url = f'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documentSubmissions/{submission_id}?PageSize=1'
    response = requests.get(url, verify=False,
                            headers={'Authorization': 'Bearer ' + auth_token, }
                            )
    # if token is expired
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        response = requests.get(url, verify=False,
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
                                )

    # in case of network error
    # TODO handle connection issues with the gov api
    if response.status_code != status.HTTP_200_OK:
        time.sleep(20)  # wait some time and try again
        response = requests.get(url, verify=False,
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
                                )
    response_code = response
    response_json = response_code.json()

    submission = Submission.objects.get(subm_id=submission_id)

    # document uuid
    submission.subm_uuid = response_json['documentSummary'][0]['uuid']
    submission.document_count = response_json['documentCount']
    submission.date_time_received = response_json['dateTimeReceived']
    submission.over_all_status = response_json['overallStatus']
    submission.save()

    return response


def send_data_by_version(data):
    """
    send data to portal according to document version id
    :param data: data required
    :return: response
    by: amira
    date: 8/4/2021
    """
    get_token()
    url = 'https://api.preprod.invoicing.eta.gov.eg/api/v1/documentsubmissions'
    response = requests.post(url, verify=False,
                             headers={'Content-Type': 'application/json',
                                      'Authorization': 'Bearer ' + auth_token},
                             data=data)

    if response.status_code == status.HTTP_401_UNAUTHORIZED:

        response = requests.post(url, verify=False,
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': 'Bearer ' + auth_token},
                                 data=data)
    return response


def send_cancellation_request(doc_uuid, data):
    """
    send cancellation data to portal
    :param doc_uuid: needed in the url
    :param data: needed for the request data
    :return:
    by: amira
    date: 12/4/2021
    """
    get_token()
    url = f'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/state/{doc_uuid}/state'
    response = requests.put(url, verify=False,
                            headers={'Content-Type': 'application/json',
                                     'Authorization': 'Bearer ' + auth_token},
                            data=data)
    return response


def get_document_details(submission_uuid):
    """
    get document details from portal api
    :param submission_uuid: used in the url
    :return: response
    by: amira
    date: 13/4/2021
    """
    get_token()
    url = f'https://api.preprod.invoicing.eta.gov.eg/api/v1/documents/{submission_uuid}/details'
    response = requests.get(url, verify=False,
                            headers={
                                'Authorization': 'Bearer ' + auth_token, }
                            )
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        response = requests.get(url, verify=False,
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
                                )
    return response


def get_document_printout(doc_uuid):
    """
    send get request to portal to get pdf
    :param doc_uuid:
    :return:
    by: amira
    date: 13/4/2021
    """
    get_token()
    url = f'https://api.preprod.invoicing.eta.gov.eg/api/v1.0/documents/{doc_uuid}/pdf'
    response = requests.get(url, verify=False,
                            headers={
                                'Authorization': 'Bearer ' + auth_token, }
                            )
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        get_token()
        response = requests.get(url, verify=False,
                                headers={
                                    'Authorization': 'Bearer ' + auth_token, }
                                )
    return response
