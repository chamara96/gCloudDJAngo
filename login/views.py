# from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from firebase import firebase
import json

from django.views.decorators.csrf import csrf_exempt

firebase = firebase.FirebaseApplication("https://pharmacy-test1.firebaseio.com")


@csrf_exempt
def index(request):
    error = {
        'error': 'Login'
    }

    if request.method == 'POST':
        data_login = firebase.get('/login_user', '')
        # data_login_phar=firebase.get('/pharm_user','')

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['username']
        password = body['password']

        for i in data_login:
            if username == data_login[i]["phone"]:
                if password == data_login[i]['password']:
                    if data_login[i]['type'] == "0":
                        user_details = firebase.get('/client_user/' + data_login[i]['id'], '')
                        output = {
                            'msg': 'success',
                            'type': 'client',
                            'data': user_details
                        }
                        break
                    elif data_login[i]['type'] == "1":
                        user_details = firebase.get('/pharm_user/' + data_login[i]['id'], '')
                        output = {
                            'msg': 'success',
                            'type': 'pharmacy',
                            'data': user_details
                        }
                        break
                else:
                    output = {'error': 'Password incorrect'}
                    break
            else:
                output = {"error": "This mobile number hasn't registered yet"}

        response_login = JsonResponse(output)
        return response_login
    else:
        return JsonResponse(error)


@csrf_exempt
def client(request):
    error = {'error': 'Login'}

    if request.method == 'POST':
        data_login = firebase.get('/login_client', '')
        # data_login_phar=firebase.get('/pharm_user','')

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['username']
        password = body['password']

        for i in data_login:
            if username == data_login[i]["phone"]:
                if password == data_login[i]['password']:
                    user_details = firebase.get('/client_user/' + data_login[i]['id'], '')
                    output = {
                        'msg': 'success',
                        'type': 'client',
                        'data': user_details
                    }
                    break
                else:
                    output = {'error': 'Password incorrect'}
                    break
            else:
                output = {"error": "This mobile number hasn't registered yet"}

        response_login = JsonResponse(output)
        return response_login
    else:
        return JsonResponse(error)


@csrf_exempt
def pharm(request):
    error = {
        'error': 'Login'
    }

    if request.method == 'POST':
        data_login = firebase.get('/login_pharm', '')
        # data_login_phar=firebase.get('/pharm_user','')

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        username = body['username']
        password = body['password']

        for i in data_login:
            if username == data_login[i]["phone"]:
                if password == data_login[i]['password']:
                    user_details = firebase.get('/pharm_user/' + data_login[i]['id'], '')
                    output = {
                            'msg': 'success',
                            'type': 'pharmacy',
                            'data': user_details
                        }
                    break
                else:
                    output = {'error': 'Password incorrect'}
                    break
            else:
                output = {"error": "This mobile number hasn't registered yet"}

        response_login = JsonResponse(output)
        return response_login
    else:
        return JsonResponse(error)


@csrf_exempt
def admin(request):
    error = {'login': 'error'}

    if request.method == 'POST':

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)
        
        username = body['username']
        password = body['password']
        
        if username=='admin':
            if password=='admin':
                admin={'login':'done'}
                return JsonResponse(admin)
            else:
                admin={'login':'password incorrect'}
                return JsonResponse(admin)
        else:
            admin={'login':'username incorrect'}
            return JsonResponse(admin)
    else:
        return JsonResponse(error)
