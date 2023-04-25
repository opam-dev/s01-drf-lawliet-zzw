from rest_framework import serializers, viewsets
from django.http.response import JsonResponse

from app1.models import User


# ---- 基于函数的视图 ----


def hello(request):
    return JsonResponse({"hello": "world"})


# ---- 基于类的视图 ----

class UserSerializer(serializers.Serializer):
    """用户序列化器"""
    name = serializers.CharField(max_length=200)
    email = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)


# MyUserSerializer 基于模型的序列化器
# 只需要选择模型和字段，就可以自动完成序列化
# class MyUserSerializer(serializers.ModelSerializer):
class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        # fields = ['name', 'password', 'email']  # 显示指定字段
        fields = '__all__'  # 显示所有字段


# UserViewSet 模型视图集
class UserModelViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
