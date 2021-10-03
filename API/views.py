from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from .serializers import ProfileSerializer, ListSerializer, UserSerializer, CartSerializer, SaveSerializer, NewSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Product, Cart, Favourite, New_Arrival
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
#mpesa api imports
from django.http import HttpResponse, JsonResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from . mpesa_credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.views.decorators.csrf import csrf_exempt
from .models import MpesaPayment

# Create your views here.
@api_view(['POST',])
@permission_classes((permissions.AllowAny,))
def register(request):
    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            user = serializer.save()
            data['response'] = "success"
            data['email'] = user.email
            #data['phone'] = user.phone
            request.session['default_phone']=254743793901
            data['username'] = user.username
            data['session_data']=request.session['default_phone']
            print(str(request.session['default_phone']))
        else:
            data = serializer.errors
        return Response(data)

@permission_classes((permissions.AllowAny,))
class TokenView(APIView):
    def post(self, request,):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        serializer = UserSerializer(user)
        if user:
            token = Token.objects.get_or_create(user=user)
            return Response({"token" : user.auth_token.key,"user":serializer.data})
        else:
            return Response({"error" : "Wrong credentials"}, status = status.HTTP_400_BAD_REQUEST)

class CurView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self, request,):
        for user in User.objects.all():
            if request.user.is_authenticated:
                serializer = UserSerializer(request.user)
                return Response({"user":serializer.data})
            else:
                return Response({"error":"not authenticated"})

class productList(generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = ListSerializer

    def get_queryset(self):
        return Product.objects.all()

class userList(generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.all()

@api_view(['GET',])
@permission_classes((permissions.AllowAny,))
def add(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.user.is_authenticated:
        mycart, _ = Cart.objects.get_or_create(user=request.user)
        mycart.product.add(product)
        cart_total=(mycart.product.product_price) * (mycart.objects.filter(product=product).count())
        request.session['cart_total']=cart_total
        print(str(request.session['cart_total']))
        return Response({'item added'})
    else:
        return Response({'error'})


@api_view(['GET',])
@permission_classes((permissions.AllowAny,))
def remove(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.user.is_authenticated:
        mycart, _ = Cart.objects.get_or_create(user=request.user)
        mycart.product.remove(product)
        return Response({'item removed'})
        cart_total=(mycart.product.product_price) * (mycart.objects.filter(product=product).count())
        request.session['cart_total']=cart_total
        print(str(request.session['cart_total']))
    else:
        return Response({'error'})

class CartView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self,request):
        cart = Cart.objects.get(user=request.user)
        serializer = CartSerializer(cart)
        return Response({"cart" : serializer.data})

@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def favourite(request,pk):
    product = get_object_or_404(Product, id=pk)
    if request.user.is_authenticated:
        saved, _ = Favourite.objects.get_or_create(user=request.user)
        saved.product.add(product)
        return Response({'product saved as favourite'})
    else:
        return Response({'error'})
    
class SaveView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        favourite = Favourite.objects.get(user=request.user)
        serializer = SaveSerializer(favourite)
        return Response({"favourite" : serializer.data})

class NewList(generics.ListAPIView):
    lookup_field = 'pk'
    serializer_class = NewSerializer

    def get_queryset(self):
        return New_Arrival.objects.all()

#mpesa integration 
#get mpesa access token
@api_view(['GET',])
@permission_classes((permissions.AllowAny,))
def getAccessToken(request):
    consumer_key = 'qfuKAkuetUmGkN0gxPE7RJgwO6jllbl9'
    consumer_secret = '2IxdUQLKuu74aK95'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    mpesa_access_token = json.loads(r.text)
    validated_mpesa_access_token = mpesa_access_token['access_token']
    return Response(validated_mpesa_access_token)


@api_view(['POST',])
@permission_classes((permissions.AllowAny,))    
def lipa_na_mpesa_online(request):
    if request.method=='POST':
       data={}
       #cart_total=request.session['cart_total']
       phone=request.session['default_phone']
       access_token = MpesaAccessToken.validated_mpesa_access_token
       api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
       headers = {"Authorization": "Bearer %s" % access_token}
       request = {
        "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
        "Password": LipanaMpesaPpassword.decode_password,
        "Timestamp": LipanaMpesaPpassword.lipa_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": 1,
        "PartyA": phone,  # replace with your phone number to get stk push
        "PartyB": LipanaMpesaPpassword.Business_short_code,
        "PhoneNumber": phone,  # replace with your phone number to get stk push
        "CallBackURL": "https://sandbox.safaricom.co.ke/mpesa/",
        "AccountReference": "Betty's Collection",
        "TransactionDesc": "Mpesa stk push"
       }
       response = requests.post(api_url, json=request, headers=headers)
       data['response']=response
       data['message']='Request sent successfully!'
       return Response(data) 

@api_view(['GET',])
@csrf_exempt
@permission_classes((permissions.AllowAny,))  
def register_urls(request):
    access_token = MpesaAccessToken.validated_mpesa_access_token
    api_url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    options = {"ShortCode": LipanaMpesaPpassword.Test_c2b_shortcode,
               "ResponseType": "Completed",
               "ConfirmationURL": "http://192.168.43.30:8000/api/c2b/confirmation",#replace ip address with your domain
               "ValidationURL": "http://192.168.43.30:8000/api/c2b/validation"}
    response = requests.post(api_url, json=options, headers=headers)
    return Response(response)

@api_view(['GET',])
@csrf_exempt
@permission_classes((permissions.AllowAny,))  
def call_back(request):
    pass


@api_view(['GET',])
@csrf_exempt
@permission_classes((permissions.AllowAny,))  
def validation(request):
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return Response(dict(context))


@api_view(['POST',])
@csrf_exempt
@permission_classes((permissions.AllowAny,))  
def confirmation(request):
    mpesa_body =request.body.decode('utf-8')
    mpesa_payment = json.loads(mpesa_body)
    payment = MpesaPayment(
        first_name=mpesa_payment['FirstName'],
        last_name=mpesa_payment['LastName'],
        middle_name=mpesa_payment['MiddleName'],
        description=mpesa_payment['TransID'],
        phone_number=mpesa_payment['MSISDN'],
        amount=mpesa_payment['TransAmount'],
        reference=mpesa_payment['BillRefNumber'],
        organization_balance=mpesa_payment['OrgAccountBalance'],
        type=mpesa_payment['TransactionType'],
    )
    payment.save()
    context = {
        "ResultCode": 0,
        "ResultDesc": "Accepted"
    }
    return Response(dict(context))       
