# 开始项目

## 1 环境准备

### 1.1 创建虚拟环境

```shell
cd ~/PyProjects
mkdir djangoProject && cd djangoProject

poetry new .
# Python版本
grep '^python = ' pyproject.toml
# 创建
poetry env use 3.9
poetry shell
# 安装依赖 >=3.2.0, <3.3.0
poetry add Django@~3.2 mysqlclient gunicorn djangorestframework django-filter celery django-celery-beat
```

## 2 git配置

```shell
git config --global core.autocrlf input
git init
cat > .gitignore <<EOF
.DS_Store

.idea
.env
.vscode

__pycache__
*.pyc
*.pyo

logs/
tmp/
venv/
EOF
```

## 3 Django

<https://docs.djangoproject.com/zh-hans/3.2/>

### 3.1 创建项目

```shell
django-admin startproject demo
# 目录改名
mv demo src
```

### 3.2 修改配置

settings.py

```python
# 按需配置
# INSTALLED_APPS
# MIDDLEWARE
# 然后注释掉 urls.py 的`path('admin/', admin.site.urls)`

# 修改数据库 使用MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'demo',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': '123456',
        'CONN_MAX_AGE': 10,
        'OPTIONS': {'charset': 'utf8mb4'}
    },
}

# 修改语言和地区
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = True

```

### 3.3 启动项目

```shell
cd src
python manage.py runserver :8000
# 然后浏览器访问 http://127.0.0.1:8000/ 就可以看到小火箭了
```

### 3.4 创建一个应用，编写第一个接口

```shell
# 创建app
python manage.py startapp app1
```

#### views.py

```python
from django.http.response import JsonResponse


def hello(request):
    return JsonResponse({"hello": "world"})
```

#### url.py

```python
# app1.urls.py
from django.urls import path

from app1 import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),
]
```

```python
# demo.urls.py
from django.urls import path, include


urlpatterns = [
    path('app1/', include('app1.urls')),
]
```

#### settings.py 注册应用

```python
INSTALLED_APPS = [
    ...,
    'app1',
]
```

访问浏览器 <http://127.0.0.1:8000/app1/hello/>

### 3.5 ORM

### 模型管理

编写模型 models.py

```python
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.name
```

迁移

```shell
# 生成迁移文件(DDL)
python manage.py makemigrations
# 执行迁移
python manage.py migrate
```

### Queryset

```python
# python manage.py shell

from app1.models import User

# 增
user = User(
    name='aaa',
    email='aaa@email.com',
    password='1'
)
user.save()
# 批量新增
User.objects.bulk_create(
    [
        User(name='a', email='a@email.com', password='1'),
        User(name='b', email='b@email.com', password='1'),
        User(name='c', email='c@email.com', password='1')
    ]
)

# 查一个 get取不到数据会抛异常 请使用common.util.get_obj_or_none
a = User.objects.get(name='aaa')
print(a.password)
# 查多个
objs = User.objects.filter(password='1')
list(objs)

# 更
user.password = '2'
user.save()
a.password = '3'
a.save()

# 删
a.delete()
```

> querysets: <https://docs.djangoproject.com/zh-hans/3.2/ref/models/querysets/>

## 4 django-rest-framework

<https://www.django-rest-framework.org/>

### settings.py

```python
INSTALLED_APPS = [
    #  ...,
    'rest_framework',
]
```

### views.py 新增视图

```python
from rest_framework import serializers, viewsets
from django.http.response import JsonResponse

from app1.models import User


def hello(request):
    return JsonResponse({"hello": "world"})


class UserSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    email = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)


# class MyUserSerializer(serializers.ModelSerializer):
class MyUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        # fields = ['name', 'password', 'email']
        fields = '__all__'


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer
```

### urls.py

```python
from django.urls import path
from rest_framework.routers import DefaultRouter

from app1 import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),
]

router = DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns += router.urls
```

## 5 作业

### 1 熟悉common.drf包

<http://gitlab.onemt.co/django/common.git>

### 2 新增一个配置管理接口

#### 返回格式

- 返回的固定格式

```json
{"result": true, "message": "success", "data": {}}

```

- 查询列表的返回格式

```json
{"result": true, "message": "success", "data": {"page": 1, "page_size": 1000, "count": 0, "items": []}}

```

#### 模型要求

```text
# 字段
key, value, status, create_time, update_time

# 字段类型
key: str
value: JSON
status: int
create_time: datetime
update_time: datetime

# 其他
create_time: 数据入库自动添加时间
update_time: 数据更新时，时间自动更新
```

#### 接口要求

1、ModelViewSet类型接口

```text
# 删除 伪删除
status = -1

# list查询 按分页返回 默认不展示已删除状态数据
支持key的完整匹配查询
query参数：page, page_size, serach, ordering
    page: 返回指定页码数据
    page_size: 每页数据量，没有传，默认100条
    serach: 支持按key模糊查询
    ordering: 支持按key排序
```

2、新增一个ViewSet类型接口，实现下面需求

GET /config/:key/

response:

```json
{
    "result": true,
    "message": "success",
    "data": {
        "value": "xxx"
    }
}
```
