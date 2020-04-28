from django.shortcuts import render
from math import sin, cos, sqrt, atan2, radians
from django.http import HttpResponse, JsonResponse
from firebase import firebase

import requests
import json

from django.views.decorators.csrf import csrf_exempt

import datetime

# now = datetime.datetime.now()
# create_date = now.strftime("%Y-%m-%d %H:%M:%S")

firebase = firebase.FirebaseApplication('https://pharmacy-test1.firebaseio.com/', None)


@csrf_exempt
def index(request):
    if request.method == 'GET':
        now = datetime.datetime.now()
        create_date = now.strftime("%Y-%m-%d %H:%M:%S")
        haii={'date':create_date}
        return JsonResponse(haii)
        # return HttpResponse("Hello, GET Client Registation")
    elif request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        content = body['pharm_ids']

        responseData = {
            'id': 4,
            'name': content,
            'roles': ['Admin', 'User']
        }
        # response_reg = JsonResponse(mydata)
        # return HttpResponse("Hello, POST Client Registation")
        # return render(request, response_reg)
        return JsonResponse(responseData)


@csrf_exempt
def clientsetorder(request):
    error = {
        'error': 'something went wrong'
    }

    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # pharm_list = pharmlist.split(",")
        # selected_pharm = "none"
        # status = "none"

        pharm_ids = body['pharm_ids']

        # GAMMA
        # final = []
        # for i in pharm_ids:
        #     data_body = {i: {"seen": "0", "price": "Not Set", "note": "Not Set"}}
        #     final.append(data_body)
        #     GAMMA

        now = datetime.datetime.now()

        data_order = {
            'order_id': '',
            'client_nic': body['client_nic'],
            'pharm_ids': pharm_ids,

            'image_url': body['image_url'],
            'selected_pharm': '',
            'accepted_pharm_count': '',
            'selected_pharm_contact': '',
            'selected_pharm_name': '',
            'is_order_cancel': '',
            'total_price': '',

            'patient_nic': body['patient_nic'],
            'patient_note': body['patient_note'],
            'pharm_note': 'Not yet',
            'checked_by': '',
            'create_date': now.strftime("%Y-%m-%d %H:%M:%S"),
            'update': '',
            'status': 'Not seen yet'
        }

        result = firebase.post('/orders/', data_order)
        firebase.put('/orders/' + result["name"], 'order_id', result["name"])
        #
        #   update pharm user's p_new_order field

        pharm_datas = firebase.get('/orders/' + result["name"] + '/pharm_ids/', '')
        for i in pharm_datas:
            res = i['id']
            # res = str(list(i.keys())[4])
            old_1 = firebase.get('/pharm_user/' + res + '/p_new_orders', '')
            arr_new_1 = list(old_1)
            arr_new_1.append(result["name"])
            firebase.put('/pharm_user/' + res, '/p_new_orders', arr_new_1)
        #
        #
        # firebase.put('/client_user/' + body['client_id'], 'order_id', result["name"])
        req_order_list = firebase.get('/client_user/' + body['client_id'], '')
        new_order_id = result["name"]
        arr = list(req_order_list['my_requested_orders'])

        for i in arr:
            if i == new_order_id:
                found = True
                break
            else:
                found = False

        if not found:
            arr.append(new_order_id)
            firebase.put('/client_user/' + body['client_id'], 'my_requested_orders', arr)

            succsess = firebase.get('/orders/' + result["name"], '')
            response_setorder = JsonResponse(succsess)
            return response_setorder
        else:
            return JsonResponse(error)
    else:
        return JsonResponse(error)

def caldistancelocal(user_lat, user_lng, pharm_lat, pharm_lng):
    R = 6373.0
    lat1 = radians(user_lat)
    lon1 = radians(user_lng)
    lat2 = radians(pharm_lat)
    lon2 = radians(pharm_lng)
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return round(distance, 2)


def get_near_locations(username, lat_user, lng_user):
    succsess = firebase.get('/pharm_user/', '')
    u_lat=float(lat_user)
    u_lng=float(lng_user)
    pharm_id = []
    g_map_destination = ""
    not_found_one = True
    for j in succsess:
        p_lat = float(succsess[j]['lat'])
        p_lng = float(succsess[j]['lng'])
        local_distance = caldistancelocal(u_lat, u_lng, p_lat, p_lng)
        if local_distance < 60:
            not_found_one=False
            zz = [j, succsess[j]["name"], False, succsess[j]["phone"]]
            pharm_id.append(zz)
            lat = str(succsess[j]["lat"])
            lng = str(succsess[j]["lng"])
            g_map_destination += "%7C" + lat + "%2C" + lng

    if not_found_one:
        return {'error':'Not Found Pharmacy in your area'}

    final_g_map_dest = g_map_destination[3:]
    # final_g_map_dest = "7.294681%2C80.631272"
    # lat="7.294246"
    # lng="80.626552"
    # print(final_g_map_dest)
    # ------------------------

    g_map_url = "https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins=" + lat_user + "," + lng_user + "&destinations=" + final_g_map_dest + "&key=AIzaSyAdnXu5TE8yzZDBaneprA857VAuYnjsC8k"

    json_distance = requests.get(g_map_url)

    row_distance = json.loads(json_distance.text)

    pharmacy_distance = row_distance["rows"][0]["elements"]
    pharmacy_address_gmap = row_distance["destination_addresses"]
    origin_address = row_distance["origin_addresses"]

    phar_list = []
    for i, k, q in zip(pharmacy_distance, pharm_id, pharmacy_address_gmap):
        # temp = [{'pharm_id': k}, {'distance': i["distance"]["value"]}, {'time': i["duration"]["text"]},{'destination_addresses': q}]
        temp = {"pharm_id": k, "distance_val": i["distance"]["value"],"distance": i["distance"]["text"], "time": i["duration"]["text"],
                "destination_addresses": q}
        phar_list.append(temp)

    # sorted_phar_list = sorted(phar_list, key=lambda x: x[1]['distance'])
    sorted_phar_list = sorted(phar_list, key=lambda x: x['distance_val'])
    # sorted_phar_list=[{'pharm_id': '004', 'distance': '1501', 'time': '5 mins', 'destination_addresses': '60 Sri Dalada Veediya, Kandy, Sri Lanka'}, {'pharm_id': '003', 'distance': '1869', 'time': '7 mins', 'destination_addresses': '41, 1 Sri Pushpadana Mawatha, Kandy, Sri Lanka'}, {'pharm_id': '002', 'distance': '2708', 'time': '10 mins', 'destination_addresses': '41 A9, Kandy 20000, Sri Lanka'}, {'pharm_id': '001', 'distance': '3910', 'time': '10 mins', 'destination_addresses': 'Department Office, A1, Kandy, Sri Lanka'}]
    # print(sorted_phar_list)
    # my_json_string = json.dumps(sorted_phar_list)
    # ///////////////////////
    # data_pharm = {sorted_phar_list
    #               }
    data_pharm = {'data': sorted_phar_list,
                  'username': username,
                  'origin_address': origin_address
                  }

    return data_pharm


@csrf_exempt
def pharmlocations(request):
    error = {
        'error': 'location error'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        username = body['client_nic']
        client_id = body['client_id']
        # lng_user = body['lng_user']

        user_details = firebase.get('/client_user/' + client_id, '')
        # for i in user_details:
        if user_details["nic"] == username:
            lat_user = user_details["lat"]
            lng_user = user_details["lng"]
            data_login = get_near_locations(username, lat_user, lng_user)
        else:
            data_login = {"error": "Wrong NIC"}

        response_login = JsonResponse(data_login)
        return response_login
    else:
        return JsonResponse(error)


@csrf_exempt
def reg(request):
    error = {
        'error': 'registation error'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        now = datetime.datetime.now()
        create_date = now.strftime("%Y-%m-%d %H:%M:%S")

        # check if user NIC is exist or not
        check_validity = firebase.get('/login_client/', '')
        if check_validity != None:
            for p in check_validity:
                if body['nic']==check_validity[p]['nic']:
                    error_2={'error':'NIC is already exist'}
                    return JsonResponse(error_2)
                if body['phone']==check_validity[p]['phone']:
                    error_2={'error':'Phone no is already exist'}
                    return JsonResponse(error_2)


        data_reg = {'id': '',
                    'type': "0",
                    'nic': body['nic'],
                    'name': body['name'],
                    'phone': body['phone'],
                    # 'password': body['password'],
                    'address': body['address'],
                    'lat': body['lat'],
                    'lng': body['lng'],
                    'create_date': create_date,
                    'my_requested_orders': ['False'],
                    'my_confirmed_orders': ['False'],
                    'my_past_orders': ['False']
                    }

        login_table = {'id': '',
                       'type': "0",
                       'nic': body['nic'],
                       'phone': body['phone'],
                       'password': body['password']
                       }

        result = firebase.post('/client_user/', data_reg)
        result_login = firebase.post('/login_client/', login_table)
        firebase.put('/login_client/' + result_login["name"], 'id', result["name"])

        firebase.put('/client_user/' + result["name"], 'id', result["name"])
        succsess = firebase.get('/client_user/' + result["name"], '')
        response_reg = JsonResponse(succsess)
        return response_reg
    else:
        return JsonResponse(error)


# get only status="0"   means current orders
@csrf_exempt
def mycurrentorder(request):
    error = {
        'status': 'My orders'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        my_nic = body['my_nic']

        my_orders_list = firebase.get('/orders/', '')

        myorder_output = []
        for i in my_orders_list:
            if (my_nic in my_orders_list[i]['client_nic']) and ("0" in my_orders_list[i]['status']):
                myorder_output.append(my_orders_list[i])

        output = {'my_current_orders': myorder_output}
        response_reg = JsonResponse(output)
        return response_reg
    else:
        return JsonResponse(error)


# get only status !="0" means history
@csrf_exempt
def myorderhistory(request):
    error = {
        'status': 'My orders History'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        my_nic = body['my_nic']

        my_orders_list = firebase.get('/orders/', '')

        myorder_output = []
        for i in my_orders_list:
            if (my_nic in my_orders_list[i]['client_nic']) and ("0" not in my_orders_list[i]['status']):
                myorder_output.append(my_orders_list[i])

        output = {'my_orders_history': myorder_output}
        response_reg = JsonResponse(output)
        return response_reg
    else:
        return JsonResponse(error)


@csrf_exempt
def hospital(request):
    error = {
        'error': 'Error Hospital Data'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        hos_keyword = body['hos_keyword']
        hos_keyword = hos_keyword.lower()
        hos_list = []

        hos_data = firebase.get('/pharm_user/', '')

        for i in hos_data:
            if ("1" in hos_data[i]['is_hospital']):
                if hos_keyword in hos_data[i]['name'].lower():
                    hos_list.append(hos_data[i])

        output = {'hospital_list': hos_list}
        response_reg = JsonResponse(output)
        return response_reg
    else:
        return JsonResponse(error)


####################################################
@csrf_exempt
def confirmpharm(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        user_nic = body['user_nic']
        user_id = body['user_id']
        orderid = body['orderid']
        # pharmid=body['pharmid']
        selected_pharm_id = body['selected_pharm_id']

        # succsess = firebase.get('/orders/' + orderid, '')
        # if succsess_1:

        now = datetime.datetime.now()
        update_date = now.strftime("%Y-%m-%d %H:%M:%S")

        get_details = firebase.get('/orders/' + orderid, '')

        for i in get_details['pharm_ids']:
            if i['id'] == selected_pharm_id:
                selected_pharm_contact=i['mobile']
                selected_pharm_name=i['name']
                total_price=i['totalPrice']
                break
            else:
                selected_pharm_contact = 'Not Found'
                selected_pharm_name = 'Not Found'
                total_price = 'Not Found'


        if get_details['client_nic'] == user_nic:
            firebase.put('/orders/' + orderid, 'selected_pharm', selected_pharm_id)
            firebase.put('/orders/' + orderid, 'selected_pharm_contact', selected_pharm_contact)
            firebase.put('/orders/' + orderid, 'selected_pharm_name', selected_pharm_name)
            firebase.put('/orders/' + orderid, 'total_price', total_price)
            firebase.put('/orders/' + orderid, 'status', 'Confirmed')
            firebase.put('/orders/' + orderid, 'update', update_date)
            #
            # Delete order id from my_requested_orders when user confirmed final pharmacy he got
            user_data = firebase.get('/client_user/' + user_id, '')
            temp_arr = list(user_data['my_requested_orders'])
            pos = temp_arr.index(orderid)
            firebase.delete('/client_user/' + user_id + '/my_requested_orders', pos)
            #
            # Add orderid to my_confirmed_orders
            temp_arr_2 = list(user_data['my_confirmed_orders'])
            temp_arr_2.append(orderid)
            firebase.put('/client_user/' + user_id, '/my_confirmed_orders', temp_arr_2)
            #
            # Add confirmed order id to pharm_user's p_current_orders
            user_data_3 = firebase.get('/pharm_user/' + selected_pharm_id, '')
            temp_arr_3 = list(user_data_3['p_current_orders'])
            temp_arr_3.append(orderid)
            firebase.put('/pharm_user/' + selected_pharm_id, '/p_current_orders', temp_arr_3)
            #
            #
            # Return confirmed order details
            succsess = firebase.get('/orders/' + orderid, '')
            response_out = JsonResponse(succsess)
            return response_out
        else:
            return JsonResponse(error)
    else:
        return JsonResponse(error)


@csrf_exempt
def myrequestedorder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        user_nic = body['user_nic']
        user_id = body['user_id']
        user_data = firebase.get('/client_user/' + user_id, '')
        orderlist = list(user_data['my_requested_orders'])

        out = []
        for i in orderlist:
            if (i != None) and (i != "False"):
                out.append(firebase.get('/orders/' + i, ''))

        final = {
            'my_requested_orders': out
        }
        response_out = JsonResponse(final)

        return response_out
    else:
        return JsonResponse(error)


@csrf_exempt
def myconfirmedorder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        user_nic = body['user_nic']
        user_id = body['user_id']
        user_data = firebase.get('/client_user/' + user_id, '')
        orderlist = list(user_data['my_confirmed_orders'])

        out = []
        for i in orderlist:
            if (i != None) and (i != "False"):
                out.append(firebase.get('/orders/' + i, ''))

        final = {
            'my_confirmed_orders': out
        }
        response_out = JsonResponse(final)

        return response_out
    else:
        return JsonResponse(error)


@csrf_exempt
def mypastorder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        user_nic = body['user_nic']
        user_id = body['user_id']
        user_data = firebase.get('/client_user/' + user_id, '')
        orderlist = list(user_data['my_past_orders'])

        out = []
        for i in orderlist:
            if (i != None) and (i != "False"):
                out.append(firebase.get('/orders/' + i, ''))

        final = {
            'my_past_orders': out
        }
        response_out = JsonResponse(final)

        return response_out
    else:
        return JsonResponse(error)


@csrf_exempt
def completeorder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        user_nic = body['user_nic']
        user_id = body['user_id']
        orderid = body['orderid']
        pharmid = body['pharmid']

        # Delete order id from my_confirmed_orders when user clicked "Complete Order"
        user_data = firebase.get('/client_user/' + user_id, '')
        temp_arr = list(user_data['my_confirmed_orders'])
        pos = temp_arr.index(orderid)
        firebase.delete('/client_user/' + user_id + '/my_confirmed_orders', pos)
        #
        # Add order id to my past orders as a history of my ordes
        temp_arr_3 = list(user_data['my_past_orders'])
        temp_arr_3.append(orderid)
        firebase.put('/client_user/' + user_id, 'my_past_orders', temp_arr_3)
        #
        #
        # Delete order id from p_current_orders when user click "Complete Order"
        pham_user_data = firebase.get('/pharm_user/' + pharmid, '')
        temp_arr_4 = list(pham_user_data['p_current_orders'])
        pos_4 = temp_arr_4.index(orderid)
        firebase.delete('/pharm_user/' + pharmid + '/p_current_orders', pos_4)
        #
        # Return this completed order details
        succsess = firebase.get('/orders/' + orderid, '')
        response_out = JsonResponse(succsess)
        return response_out
    else:
        return JsonResponse(error)


@csrf_exempt
def cancelorder(request):
    error = {
        'error': 'something went wrong'
    }
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        # user_nic = body['user_nic']
        orderid = body['orderid']
        user_id = body['user_id']

        # Delete order id from my_requested_orders when user clicked "Cancel Order"
        user_data = firebase.get('/client_user/' + user_id, '')
        temp_arr = list(user_data['my_requested_orders'])
        pos = temp_arr.index(orderid)
        firebase.delete('/client_user/' + user_id + '/my_requested_orders', pos)
        #
        # Delete order id from all pharmacy's p_new_orders when user clicked "Cancel Order"
        pharm_datas = firebase.get('/orders/' + orderid + '/pharm_ids/', '')
        for i in pharm_datas:
            res = i['id']
            # res = str(list(i.keys())[4])
            old_1 = firebase.get('/pharm_user/' + res + '/p_new_orders', '')
            arr_new_1 = list(old_1)
            pos_2 = arr_new_1.index(orderid)
            firebase.delete('/pharm_user/' + res + '/p_new_orders', pos_2)
        #

        # Delete order id from order table when user clicked "Cancel Order"
        # firebase.delete('/orders/', orderid)
        firebase.put('/orders/' + orderid, 'is_order_cancel', '1')

        succsess = {'result': 'deleted', 'orderid': orderid}
        response_out = JsonResponse(succsess)
        return response_out
    else:
        return JsonResponse(error)
