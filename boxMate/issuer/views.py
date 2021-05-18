import zipfile
from zipfile import ZipFile, BadZipfile

from django.db import IntegrityError
from issuer.models import *
from issuer.api.serializers import IssuerSerializer
from taxManagement.models import *
from django.db.models import Count
from django.utils import timezone
from django.shortcuts import render, redirect, HttpResponseRedirect
from codes.models import CountryCode
from django.shortcuts import get_object_or_404
from django.db.models import Q
from issuer.forms import *
from datetime import date
from codes.models import TaxSubtypes, CountryCode
import json
from django.http import JsonResponse
from array import *
from custom_user.models import User
from django.contrib import messages
from .decorators import is_issuer
from django.utils.translation import ugettext_lazy as _
from .resources import ReceiverResource
from django.http import HttpResponse
from tablib import Dataset
import pandas as pd
from taxManagement.views import write_to_tmp_storage
from taxManagement.tmp_storage import TempFolderStorage
from taxManagement.db_connection import OracleConnection
import cx_Oracle

TMP_STORAGE_CLASS = getattr(settings, 'IMPORT_EXPORT_TMP_STORAGE_CLASS',
                            TempFolderStorage)

"""
def get_issuer_data(user):
    issuer_data = MainTable.objects.filter(~Q(issuer_registration_num=None) & Q(user=user)).values(
        'issuer_type',
        'issuer_registration_num',
        'issuer_name',
        'issuer_building_num',
        'issuer_room',
        'issuer_floor',
        'issuer_street',
        'issuer_land_mark',
        'issuer_additional_information',
        'issuer_governate',
        'issuer_region_city',
        'issuer_postal_code',
        'issuer_country',
        'issuer_branch_id').annotate(Count('issuer_registration_num'))
    print(issuer_data)
    for data in issuer_data:
        issuer_code = data['issuer_registration_num']
        address = data['issuer_branch_id']
        print("**************", address)
        try:
            issuer_id = Issuer.objects.get(reg_num=issuer_code)
            try:
                address_id = Address.objects.get(issuer=issuer_id, branch_id=address)
            except Address.DoesNotExist as e:
                country_code = data['issuer_country']
                code_obj = CountryCode.objects.get(pk=country_code)
                address_obj = Address(
                    issuer=issuer_id,
                    branch_id=data['issuer_branch_id'],
                    country=code_obj,
                    governate=data['issuer_governate'],
                    regionCity=data['issuer_region_city'],
                    street=data['issuer_street'],
                    buildingNumber=data['issuer_building_num'],
                    postalCode=data['issuer_postal_code'],
                    floor=data['issuer_floor'],
                    room=data['issuer_room'],
                    landmark=data['issuer_land_mark'],
                    additionalInformation=data['issuer_additional_information']
                )
                address_obj.save()
        except Issuer.DoesNotExist as e:
        issuer_obj = Issuer(
                type=issuer.type,
                reg_num=issuer.reg_num,
                name=issuer.name
            )
        issuer_obj.save()
        issuer_id = issuer_obj
        country_code =
        code_obj = CountryCode.objects.get(pk=country_code)
        address = data['issuer_branch_id']
        address_obj = Address(
            issuer=issuer_id,
            branch_id=data['issuer_branch_id'],
            country=code_obj,
            governate=data['issuer_governate'],
            regionCity=data['issuer_region_city'],
            street=data['issuer_street'],
            buildingNumber=data['issuer_building_num'],
            postalCode=data['issuer_postal_code'],
            floor=data['issuer_floor'],
            room=data['issuer_room'],
            landmark=data['issuer_land_mark'],
            additionalInformation=data['issuer_additional_information']
        )
        address_obj.save()
"""


def get_receiver_data(user):
    print('*************', user)
    user_id = User.objects.get(id=user.id)
    issuer = user_id.issuer
    receiver_data = MainTable.objects.filter(~Q(receiver_registration_num=None) & Q(user=user)).values(
        'receiver_type',
        'receiver_registration_num',
        'receiver_name',
        'receiver_building_num',
        'receiver_room',
        'receiver_floor',
        'receiver_street',
        'receiver_land_mark',
        'receiver_additional_information',
        'receiver_governate',
        'receiver_region_city',
        'receiver_postal_code',
        'receiver_country').annotate(Count('receiver_registration_num'))
    print('receiver: ', receiver_data)
    for data in receiver_data:
        receiver_code = data['receiver_registration_num']
        building_num = data['receiver_building_num']
        floor = data['receiver_floor']
        room = data['receiver_room']
        try:
            receiver_id = Receiver.objects.get(reg_num=receiver_code)
            address = Address.objects.filter(receiver=receiver_id, buildingNumber=building_num, floor=floor, room=room)
            if len(address) == 0:
                country_code = data['receiver_country']
                code_obj = CountryCode.objects.get(pk=country_code)
                address_obj = Address(
                    receiver=receiver_id,
                    country=code_obj,
                    governate=data['receiver_governate'],
                    regionCity=data['receiver_region_city'],
                    street=data['receiver_street'],
                    buildingNumber=data['receiver_building_num'],
                    postalCode=data['receiver_postal_code'],
                    floor=data['receiver_floor'],
                    room=data['receiver_room'],
                    landmark=data['receiver_land_mark'],
                    additionalInformation=data['receiver_additional_information']
                )
                address_obj.save()
        except Receiver.DoesNotExist as e:
            receiver_obj = Receiver(
                type=data['receiver_type'],
                reg_num=data['receiver_registration_num'],
                name=data['receiver_name'],
                issuer=issuer
            )
            receiver_obj.save()
            print('after save ', receiver_obj)
            receiver_id = receiver_obj
            country_code = data['receiver_country']
            code_obj = CountryCode.objects.get(pk=country_code)
            address_obj = Address(
                receiver=receiver_id,
                country=code_obj,
                governate=data['receiver_governate'],
                regionCity=data['receiver_region_city'],
                street=data['receiver_street'],
                buildingNumber=data['receiver_building_num'],
                postalCode=data['receiver_postal_code'],
                floor=data['receiver_floor'],
                room=data['receiver_room'],
                landmark=data['receiver_land_mark'],
                additionalInformation=data['receiver_additional_information']
            )
            address_obj.save()


@is_issuer
def list_uploaded_invoice(request):
    return render(request, 'upload-invoice.html')


@is_issuer
def view_issuer(request, issuer_id):
    issuer = Issuer.objects.get(id=issuer_id)
    address = Address.objects.filter(issuer=issuer_id)
    # country = CountryCode.objects.get(code=address.country.code)
    codes = IssuerTax.objects.filter(issuer=issuer_id)
    return render(request, 'view-issuer.html', {
        'issuer': issuer,
        'addresses': address,
        'codes': codes,
    })


@is_issuer
def create_issuer_tax_view(request, issuer_id):
    sub_taxs = TaxSubtypes.objects.all()
    issuer_id = issuer_id

    return render(request, 'create-issuer-tax.html', {
        'issuer_id': issuer_id,
        'sub_taxs': sub_taxs, })


@is_issuer
def create_issuer_tax(request):
    issuer = request.GET.get('issuer')
    codes = request.GET.getlist("codes_arr[]")
    try:
        issuer_id = Issuer.objects.get(id=issuer)
        for code in codes:
            subtax = TaxSubtypes.objects.get(code=code)
            issuer_tax_obj = IssuerTax(
                issuer=issuer_id,
                issuer_sub_tax=subtax,
                start_date=date.today(),
                is_enabled=True,
                created_by=request.user
            )
            issuer_tax_obj.save()
        message = ' taxes added to your company'

    except Issuer.DoesNotExist as e:
        message = 'not added to your company '

    data = {
        'message': message}
    return JsonResponse(data)


############################################## Issuer Section ###########################################
def create_issuer(request):
    issuer_form = IssuerForm(update=False)
    activity_code_form = ActivityCodeInlineForm()
    address_form = AddressForm()
    if request.method == 'POST':
        issuer_form = IssuerForm(request.POST, update=False)
        activity_code_form = ActivityCodeInlineForm(request.POST)
        address_form = AddressForm(request.POST)
        if issuer_form.is_valid():
            issuer_obj = issuer_form.save(commit=False)
            issuer_obj.created_at = date.today()
            issuer_obj.created_by = request.user
            issuer_obj.save()

            # address_obj = address_form.save(commit=False)
            # address_obj.issuer = issuer_obj
            # address_obj.created_at = date.today()
            # address_obj.created_by = request.user
            # address_obj.save()

            user = User.objects.get(id=request.user.id)
            user.issuer = issuer_obj
            user.save()

            activity_code_form = ActivityCodeInlineForm(request.POST, instance=issuer_obj)
            if activity_code_form.is_valid():
                activity_code_obj = activity_code_form.save(commit=False)
                for obj in activity_code_obj:
                    obj.save()
                return redirect('issuer:create-issuer-address')
                # return redirect('issuer:create-tax',
                #                 issuer_id=issuer_obj.id)
            else:
                print(activity_code_form.errors)

        else:
            print(issuer_form.errors)
            print(address_form.errors)
            return render(request, 'create-issuer.html', {
                'issuer_form': issuer_form,
                'address_form': address_form, })

    else:
        return render(request, 'create-issuer.html', {
            'activity_code_form': activity_code_form,
            'issuer_form': issuer_form,
            'address_form': address_form, })


def update_issuer(request, issuer_id):
    issuer_instance = Issuer.objects.get(id=issuer_id)
    issuer_form = IssuerForm(instance=issuer_instance, update=True)
    activity_code_form = ActivityCodeInlineForm(instance=issuer_instance)
    if request.method == 'POST':
        issuer_form = IssuerForm(request.POST, instance=issuer_instance, update=True)
        # issuer_obj = issuer_form.save(commit=False)
        if issuer_form.is_valid():
            issuer_obj = issuer_form.save(commit=False)
            issuer_obj.last_updated_by = request.user
            issuer_obj.last_updated_at = date.today()
            issuer_obj.save()
            activity_code_form = ActivityCodeInlineForm(request.POST, instance=issuer_obj)

            if activity_code_form.is_valid():
                activity_code_obj = activity_code_form.save(commit=False)
                for obj in activity_code_obj:
                    obj.save()
                return redirect('issuer:list-issuer')
            else:
                print('In activity')
                print(activity_code_form.errors)
        else:
            print('In issuer')
            print(issuer_form.errors)


    return render(request, 'create-issuer.html', {
        'activity_code_form': activity_code_form,
        'issuer_form': issuer_form,
        'update': True, })


def create_issuer_address(request):
    address_formset = AddressInlineForm(Address.objects.none())
    if request.method == 'POST':
        address_formset = AddressInlineForm(request.POST)
        if address_formset.is_valid():
            for address in address_formset:
                address_obj = address.save(commit=False)
                address_obj.issuer = request.user.issuer
                address_obj.created_by = request.user
                address_obj.created_at = datetime.now()
                address_obj.save()
            return redirect('issuer:create-tax', request.user.issuer.id)
    context = {
        'address_formset': address_formset
    }
    return render(request, 'create_issuer_address.html', context)


def list_issuer_address(request):
    addresses = Address.objects.filter(issuer=request.user.issuer)
    context = {
        'addresses': addresses
    }
    return render(request, 'list-issuer-addresses.html', context)


def update_issuer_address(request, id):
    address = Address.objects.get(id=id)
    address_form = AddressForm(instance=address)
    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=address)
        if address_form.is_valid():
            address_obj = address_form.save(commit=False)
            address_obj.issuer = request.user.issuer
            address_obj.last_updated_by = request.user
            address_obj.last_updated_at = datetime.now()
            address_obj.save()
            return redirect('issuer:list-issuer-address')
    context = {
        'address_form': address_form
    }
    return render(request, 'update-issuer-address.html', context)


def delete_issuer_address(request, id):
    address = Address.objects.get(id=id)
    address.delete()
    return redirect('issuer:list-issuer-address')


@is_issuer
def issuer_oracle_DB_create(request):
    issuer_oracle_DB_form = IssuerOracleDBForm()
    issuer = Issuer.objects.get(id=request.user.issuer.id)
    if request.method == 'POST':
        issuer_oracle_DB_form = IssuerOracleDBForm(request.POST)
        if issuer_oracle_DB_form.is_valid():
            form_data = issuer_oracle_DB_form.cleaned_data
            if form_data['is_active']:
                connection_class = OracleConnection(
                    form_data['ip_address'],
                    form_data['port_number'],
                    form_data['service_number'],
                    form_data['username'],
                    form_data['password'])
                connection = connection_class.init_db_connection()
                if not isinstance(connection, cx_Oracle.Connection):
                    return render(request, "list-issuer-oracle-db.html", get_db_list_context(request, True, connection))

            db_obj = issuer_oracle_DB_form.save(commit=False)
            db_obj.issuer = issuer
            db_obj.save()
            return redirect('issuer:list-issuer-db-connection')
    context = {
        "db_form": issuer_oracle_DB_form,
    }
    return render(request, "create-issuer-oracle-db.html", context)


@is_issuer
def issuer_oracle_DB_list(request):
    if request.method == 'POST':
        select_statement = request.POST.get('query')
        data = run_db_query(request, select_statement)
        for invoice in data:
            temp_invoice = InvoiceImport(issuer=request.user.issuer)
            for column in invoice:
                setattr(temp_invoice, column.lower(), invoice[column])
            temp_invoice.save()
            print(temp_invoice)
        if not isinstance(data, list):
            return render(request, "list-issuer-oracle-db.html", get_db_list_context(request, True, data))
    return render(request, "list-issuer-oracle-db.html", get_db_list_context(request, False, None))

@is_issuer
def issuer_oracle_DB_import(request):
    issuer = Issuer.objects.get(id=request.user.issuer.id)
    import_data = InvoiceImport.objects.filter(issuer=issuer)
    columns = InvoiceImport._meta.get_fields()

    for invoice in import_data:
        new_invoice = InvoiceHeader(issuer=request.user.issuer, receiver=Receiver.objects.first(), taxpayer_activity_code=IssuerActivityCode.objects.first())
        print('EEEEEEEEEEEEE')
        for col in columns:
            if col.name != 'id':
                setattr(new_invoice, col.name, getattr(invoice, col.name))
        new_invoice.save()
    return redirect('issuer:list-issuer-db-cancel')

@is_issuer
def issuer_oracle_DB_cancel(request):
    issuer = Issuer.objects.get(id=request.user.issuer.id)
    import_data = InvoiceImport.objects.filter(issuer=issuer)
    for invoice in import_data:
        invoice.delete()
    return redirect('issuer:list-issuer-db-connection')

@is_issuer
def issuer_oracle_DB_update(request, id):
    oracle_DB_connection = IssuerOracleDB.objects.get(id=id)
    issuer_oracle_DB_form = IssuerOracleDBForm(instance=oracle_DB_connection)
    if request.method == 'POST':
        issuer_oracle_DB_form = IssuerOracleDBForm(request.POST, instance=oracle_DB_connection)
        if issuer_oracle_DB_form.is_valid():
            form_data = issuer_oracle_DB_form.cleaned_data
            if form_data['is_active']:
                connection_class = OracleConnection(
                    form_data['ip_address'],
                    form_data['port_number'],
                    form_data['service_number'],
                    form_data['username'],
                    form_data['password'])
                connection = connection_class.init_db_connection()
                if not isinstance(connection, cx_Oracle.Connection):
                    return render(request, "list-issuer-oracle-db.html", get_db_list_context(request, True, connection))

            db_obj = issuer_oracle_DB_form.save()
            return redirect('issuer:list-issuer-db-connection')
    context = {
        "db_form": issuer_oracle_DB_form,
    }
    return render(request, "create-issuer-oracle-db.html", context)


@is_issuer
def list_issuer(request):
    '''
        created_at: 10/03/2021
        author: Ahd Hozayen
        purpose: list all the current issuer/s for the "logged in user"
    '''
    issuers_list = Issuer.objects.filter(id=request.user.issuer.id)
    context = {
        "page_title": "Issuer List",
        'issuers_list': issuers_list,
    }
    return render(request, 'list-issuer.html', context)


###############################################################################################

def activate_database(request, id):
    oracle_DB_connection = IssuerOracleDB.objects.get(id=id)
    connection_class = OracleConnection(
        oracle_DB_connection.ip_address,
        oracle_DB_connection.port_number,
        oracle_DB_connection.service_number,
        oracle_DB_connection.username,
        oracle_DB_connection.password)
    connection = connection_class.init_db_connection()
    if not isinstance(connection, cx_Oracle.Connection):
        return render(request, "list-issuer-oracle-db.html", get_db_list_context(request, True, connection))

    oracle_DB_connection.is_active = True
    oracle_DB_connection.save()
    return redirect('issuer:list-issuer-db-connection')

def run_db_query(request, query):
    issuer = Issuer.objects.get(id=request.user.issuer.id)
    db_credintials = IssuerOracleDB.objects.get(issuer=issuer, is_active=True)
    address = db_credintials.ip_address
    port = db_credintials.port_number
    service_nm = db_credintials.service_number
    username = db_credintials.username
    password = db_credintials.password
    connection_class = OracleConnection(
        address, port, service_nm, username, password)
    data = connection_class.get_data_from_db(query)
    return data

@is_issuer
def create_receiver(request):
    '''
        created_at:08/03/2021
        author: Mamadouh
        purpose:create new reciever for this issuer
    '''

    receiver_form = ReceiverForm()
    address_formset = AddressInlineForm(queryset=Address.objects.none())
    if request.method == 'POST':
        receiver_form = ReceiverForm(request.POST)
        address_formset = AddressInlineForm(request.POST)
        if receiver_form.is_valid() and address_formset.is_valid():
            receiver_obj = receiver_form.save(commit=False)
            receiver_obj.issuer = request.user.issuer
            receiver_obj.created_by = request.user
            receiver_obj.created_at = date.today()
            receiver_obj.save()

            for address in address_formset:
                address_obj = address.save(commit=False)
                address_obj.receiver = receiver_obj
                address_obj.created_by = request.user
                address_obj.created_at = datetime.now()
                address_obj.save()
            return redirect('issuer:list-receiver')

        else:
            print(receiver_form.errors)
            print(address_form.errors)
            return render(request, 'create-receiver.html', {
                'receiver_form': receiver_form,
                'address_form': address_formset,
                "page_title": _("Create Receiver"),
            })

    else:
        return render(request, 'create-receiver.html', {
            'receiver_form': receiver_form,
            'address_formset': address_formset,
            "page_title": _("Create Receiver"),
        })


@is_issuer
def list_receiver(request):
    '''
        created_at:08/03/2021
        author: Mamadouh
        purpose:list all recievers for this issuer
    '''
    receivers = Receiver.objects.filter(issuer=request.user.issuer)
    context = {
        'receivers': receivers,
    }
    return render(request, 'list-receiver.html', context)


@is_issuer
def update_receiver(request, pk):
    '''
        created_at:08/03/2021
        author: Mamadouh
        purpose:update reciever
    '''

    receiver = Receiver.objects.get(id=pk)
    address = Address.objects.filter(receiver=receiver)
    receiver_form = ReceiverForm(instance=receiver)
    address_formset = AddressInlineForm(queryset=address)
    # address_form = AddressInlineForm(queryset=address)
    if request.method == 'POST':
        receiver_form = ReceiverForm(request.POST, instance=receiver)
        address_form = AddressForm(request.POST, instance=address)
        if receiver_form.is_valid() and address_form.is_valid():
            receiver_obj = receiver_form.save(commit=False)
            receiver_obj.issuer = request.user.issuer
            receiver_obj.last_updated_by = request.user
            receiver_obj.last_updated_at = date.today()
            receiver_obj.save()

            address_obj = address_form.save(commit=False)
            address_obj.receiver = receiver_obj
            address_obj.last_updated_by = request.user
            address_obj.last_updated_at = date.today()
            address_obj.save()

            return redirect('issuer:list-receiver')

        else:
            return render(request, 'create-receiver.html', {
                'receiver_form': receiver_form,
                'address_form': address_form,
                "page_title": _("Update Receiver"),
            })

    else:
        return render(request, 'create-receiver.html', {
            'receiver_form': receiver_form,
            'address_formset': address_formset,
            "page_title": _("Update Receiver"),
        })


@is_issuer
def delete_receiver(request, pk):
    '''
        created_at:08/03/2021
        author: Mamadouh
        purpose:delete reciever
    '''
    receiver = Receiver.objects.get(id=pk)
    receiver.delete()
    return redirect('issuer:list-receiver')

def export_receiver_template(request):
    """
    export a template to fill receiver info
    :param request:
    :return:
    By: amira
    Date: 18-03-2021
    """
    receiver_resource = ReceiverResource()
    dataset = receiver_resource.export(queryset=Receiver.objects.none())
    response = HttpResponse(dataset.xlsx, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="receiver_template.xlsx"'
    print(response)
    return response


def is_empty(xl_file, request):
    """
    check if file is empty or not
    :param xl_file: file to be checked
    :return: true file is empty / false
    By: amira
    Date: 21/03/2021
    """
    try:
        xls_file = pd.read_excel(xl_file, engine='openpyxl')
        empty = xls_file.empty  # return false if not empty
    except zipfile.BadZipfile as e:
        print('exception occurred in is_empty() ', e)
        messages.error(request, _('Please, make sure file is saved correctly'))
        empty = True  # always empty on exception
    except OSError as e:
        print('exception occurred in is_empty() ', e)
        messages.error(request, _('Please, make sure file is filled with data'))
        empty = True  # always empty on exception
    return empty


def import_receiver_template(request):
    """
    import data from excel sheet
    :param request:
    :return:
    """
    try:
        receiver_resource = ReceiverResource()
        imported_file = request.FILES['import_file']
        dataset = Dataset()
        excel_data = dataset.load(imported_file.read())
        # check file is empty
        if is_empty(imported_file, request):
            messages.error(request, _('Please, make sure file is filled with data'))
            return redirect('/issuer/list/receiver')

        # test dataset have errors
        result = receiver_resource.import_data(excel_data, dry_run=True, user=request.user)
        # write file in tmp
        tmp_storage = write_to_tmp_storage(imported_file)
        if not result.has_errors() and not result.has_validation_errors():
            tmp_storage = TMP_STORAGE_CLASS(name=tmp_storage.name)
            data = tmp_storage.read('rb')
            dataset = Dataset()
            imported_data = dataset.load(data)

            receiver_resource.import_data(imported_data,
                                          dry_run=False,
                                          raise_errors=True,
                                          file_name=tmp_storage.name,
                                          user=request.user)
            tmp_storage.remove()
            # create receiver and his/her address
            get_receiver_data(request.user)
            messages.success(request, _('Receiver record is inserted successfully'))
            # deletes record from maintable
            success = MainTable.objects.filter(user=request.user).delete()
            if not success:
                messages.error(request, 'Failed to import Excel sheet')
                return redirect('/issuer/list/receiver')
        else:
            messages.error(request, 'Invalid Excel Sheet ' +
                           str(result.base_errors))
            return redirect('/issuer/list/receiver')

    except zipfile.BadZipfile as e:
        print('Exception occurred while uploading a file --> ', e)
        messages.error(request, _('Please, make sure file is saved correctly'))

    return redirect('/issuer/list/receiver')

@is_issuer
def view_receiver(request , pk):
    '''
        created_at:21/03/2021
        author: Mamadouh
        purpose:view reciever details
    '''
    receiver = Receiver.objects.get(id=pk)
    receiver_addresses = Address.objects.filter(receiver=receiver)
    context = {
        'receiver' : receiver,
        'addresses' : receiver_addresses,
    }
    return render(request , 'view-receiver.html' , context)

def get_db_list_context(request, has_errors, conn):
    issuer_oracle_DB_form = IssuerOracleDBForm()
    issuer = Issuer.objects.get(id=request.user.issuer.id)
    oracle_DB_connections = IssuerOracleDB.objects.filter(issuer=issuer)
    import_data = InvoiceImport.objects.filter(issuer=issuer)
    context = {
        'issuer': issuer,
        'connections': oracle_DB_connections,
        'db_form': issuer_oracle_DB_form,
        'import_data': import_data
    }
    if has_errors:
        context['errors'] = conn
    print('__________')
    print(context)
    return context
