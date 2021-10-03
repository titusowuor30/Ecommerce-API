from django.db.models import fields
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product, Cart, Favourite, New_Arrival

class ProfileSerializer(serializers.ModelSerializer):
    #phone=serializers.CharField(max_length=15)
    password2 = serializers.CharField(style={'input_type' : 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email','password', 'password2')
        extra_kwargs = {
            'password' : {'write_only' : True}
        }

    def save(self):
        user = User(
            email = self.validated_data['email'],
            #phone = self.validated_data['phone'],
            username = self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password' : 'passwords do not match'})
        user.set_password(password)
        user.save()
        return user

class ListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('product_name','product_category','product_price','thumbnail','id')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email')

class CartSerializer(serializers.ModelSerializer):
    product = ListSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = ('user','product')

class SaveSerializer(serializers.ModelSerializer):
    product = ListSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)
    class Meta:
        model = Favourite
        fields = ('user','product')

class NewSerializer(serializers.ModelSerializer):
    class Meta:
        model = New_Arrival
        fields = ('product_name', 'product_price', 'thumbnail', 'id')