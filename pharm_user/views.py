from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from firebase import firebase

from django.views.decorators.csrf import csrf_exempt

import requests
import json

import datetime

firebase = firebase.FirebaseApplication('https://pharmacy-test1.firebaseio.com/', None)


# firebase = firebase.FirebaseApplication("https://pharmacy-test1.firebaseio.com")


def index(request):
    return HttpResponse("Hello, world. Home Index of Pharm Registation")


@csrf_exempt
def reg(request):
    error = {
        'error': 'Reg Pharm'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        now = datetime.datetime.now()
        update_date = now.strftime("%Y-%m-%d %H:%M:%S")

        # check if user NIC is exist or not
        check_validity = firebase.get('/login_pharm/', '')
        if check_validity != None:
            for p in check_validity:
                if body['pharmacist_nic'] == check_validity[p]['nic']:
                    error_2 = {'error': 'NIC is already exist'}
                    return JsonResponse(error_2)
                if body['phone']==check_validity[p]['phone']:
                    error_2={'error':'Phone no is already exist'}
                    return JsonResponse(error_2)


        data_reg = {'id': '',
                    'selected': False,
                    'name': body['name'],
                    'owner': body['owner'],
                    'phone': body['phone'],
                    'pharmacist_nic': body['pharmacist_nic'],
                    'pharmacist_name': body['pharmacist_name'],
                    'pharmacist_regno': body['pharmacist_regno'],

                    'p_new_orders': ['False'],
                    'p_current_orders': ['False'],

                    'address': body['address'],
                    'lat': body['lat'],
                    'lng': body['lng'],
                    # 'password': body['password'],
                    'is_hospital': body['is_hospital'],
                    'delivery_cost': body['delivery_cost'],
                    'delivery_time': body['delivery_time'],
                    'date': update_date
                    }

        login_table = {'id': '',
                       'type': "1",
                       'nic': body['pharmacist_nic'],
                       'phone': body['phone'],
                       'password': body['password']
                       }

        result = firebase.post('/pharm_user/', data_reg)
        result_login = firebase.post('/login_pharm/', login_table)
        firebase.put('/login_pharm/' + result_login["name"], 'id', result["name"])

        firebase.put('/pharm_user/' + result["name"], 'id', result["name"])
        succsess = firebase.get('/pharm_user/' + result["name"], '')
        response_reg = JsonResponse(succsess)
        return response_reg
    else:
        return JsonResponse(error)


@csrf_exempt
def vieworder(request):  # client requested (not accepted)
    error = {
        'error': 'View Order'
    }

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        data_order = firebase.get('/orders', '')
        view_order = []

        username = body['user_id']
        # query = body['query']

        # mydetails = firebase.get('/pharm_user/' + username, )
        # mydetails = firebase.get('/pharm_user/' + username, '')

        for z in data_order:
            if username in data_order[z]['pharm_ids']:
                if '0' in data_order[z]['selected_pharm']:
                    temp = data_order[z]
                    view_order.append(temp)

        output_order = {
            'orders_list': view_order
            # 'mydetails': mydetails
        }
        # response_vieworder = json.dumps(output_order)
        response_vieworder = JsonResponse(output_order)
        return response_vieworder
    else:
        return JsonResponse(error)


@csrf_exempt
def getorder(request):
    error = {
        'error': 'Get Order'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        username = body['user_id']
        orderid = body['orderid']

        # succsess = firebase.get('/orders/' + orderid, '')
        # if succsess_1:

        now = datetime.datetime.now()
        update_date = now.strftime("%Y-%m-%d %H:%M:%S")

        firebase.put('/orders/' + orderid, 'selected_pharm', username)
        firebase.put('/orders/' + orderid, 'update', update_date)
        #
        succsess = firebase.get('/orders/' + orderid, '')
        response_reg = JsonResponse(succsess)
        return response_reg
    else:
        return JsonResponse(error)


@csrf_exempt
def viewgetorders(request):
    error = {
        'error': 'View Order'
    }

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        data_order = firebase.get('/orders', '')
        view_order = []

        username = body['user_id']
        # query = body['query']

        for z in data_order:
            if username in data_order[z]['selected_pharm']:
                if 'Active' in data_order[z]['status']:
                    temp = data_order[z]
                    view_order.append(temp)

        output_order = {
            'active_orders_list': view_order
        }
        response_vieworder = JsonResponse(output_order)
        return response_vieworder

    else:
        return JsonResponse(error)


@csrf_exempt
def updateactiveorder(request):
    error = {
        'error': 'updateactiveorder'
    }

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # user_id = body['user_id']
        orderid = body['orderid']
        field = body['field']
        value_update = body['value_update']

        now = datetime.datetime.now()
        update_date = now.strftime("%Y-%m-%d %H:%M:%S")

        # succsess = firebase.get('/orders/' + orderid, '')
        firebase.put('/orders/' + orderid, field, value_update)
        firebase.put('/orders/' + orderid, 'update', update_date)

        if field == 'pharm_note':
            firebase.put('/orders/' + orderid, 'status', 'Order Processing')

        succsess_final = firebase.get('/orders/' + orderid, '')
        response_reg = JsonResponse(succsess_final)
        return response_reg

    else:
        return JsonResponse(error)


@csrf_exempt
def viewpneworder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # user_nic = body['user_nic']
        user_id = body['pharm_id']
        user_data = firebase.get('/pharm_user/' + user_id, '')
        p_new_order = list(user_data['p_new_orders'])

        out = []
        for i in p_new_order:
            if i != None:
                out.append(firebase.get('/orders/' + i, ''))

        final = {
            'p_new_orders': out
        }
        response_out = JsonResponse(final)

        return response_out
    else:
        return JsonResponse(error)


@csrf_exempt
def viewpcurrentorder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # user_nic = body['user_nic']
        user_id = body['pharm_id']
        user_data = firebase.get('/pharm_user/' + user_id, '')
        p_new_order = list(user_data['p_current_orders'])

        out = []
        for i in p_new_order:
            if (i != None) and (i != "False"):
                out.append(firebase.get('/orders/' + i, ''))

        final = {
            'p_current_orders': out
        }
        response_out = JsonResponse(final)

        return response_out
    else:
        return JsonResponse(error)


@csrf_exempt
def updatepharmarr(request):
    error = {
        'error': 'update pharm array'
    }

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        pharm_id = body['pharm_id']
        orderid = body['orderid']
        value_update = body['pharm_ids_arr']

        now = datetime.datetime.now()
        update_date = now.strftime("%Y-%m-%d %H:%M:%S")

        succsess = firebase.get('/orders/' + orderid, '')
        if succsess['is_order_cancel'] == '1':
            error_1 = {'status': 'Order is cancelled by user','order_id':orderid}
            return JsonResponse(error_1)
        else:
            firebase.put('/orders/' + orderid, 'pharm_ids', value_update)
            firebase.put('/orders/' + orderid, 'update', update_date)

            #
            # Delete order id from p_new_orders when pharmacy update order
            user_data_1 = firebase.get('/pharm_user/' + pharm_id, '')
            temp_arr = list(user_data_1['p_new_orders'])
            pos = temp_arr.index(orderid)
            firebase.delete('/pharm_user/' + pharm_id + '/p_new_orders', pos)
            #
            #
            # Update "accepted_pharm_count" value
            succsess_final = firebase.get('/orders/' + orderid, '')

            accepted_pharm_count = 0
            for i in succsess_final['pharm_ids']:
                price = i['drugPrice']
                if price != '':
                    accepted_pharm_count += 1

            firebase.put('/orders/' + orderid, 'accepted_pharm_count', accepted_pharm_count)

            response_reg = JsonResponse(succsess_final)
            return response_reg
    else:
        return JsonResponse(error)


@csrf_exempt
def viewanyorder(request):
    error = {
        'error': 'View Order'
    }

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        orderid = body['order_id']
        data_order = firebase.get('/orders/' + orderid, '')

        response_vieworder = JsonResponse(data_order)
        return response_vieworder
    else:
        return JsonResponse(error)
