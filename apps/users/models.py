from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """自定义用户管理器"""
    
    def create_user(self, openid, **extra_fields):
        """创建普通用户"""
        if not openid:
            raise ValueError('必须提供微信openid')
        
        user = self.model(openid=openid, **extra_fields)
        user.set_unusable_password()  # 微信登录不需要密码
        user.save(using=self._db)
        return user
    
    def create_superuser(self, openid, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_admin') is not True:
            raise ValueError('超级用户必须设置is_admin=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置is_superuser=True')
        
        return self.create_user(openid, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """用户模型"""
    
    GENDER_CHOICES = [
        (0, '未知'),
        (1, '男'),
        (2, '女'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='用户ID')
    openid = models.CharField(max_length=100, unique=True, verbose_name='微信openid')
    union_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='微信unionid')
    nickname = models.CharField(max_length=100, default='微信用户', verbose_name='微信昵称')
    avatar_url = models.URLField(max_length=500, blank=True, null=True, verbose_name='微信头像URL')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=0, verbose_name='性别')
    is_active = models.BooleanField(default=True, verbose_name='账号是否激活')
    is_admin = models.BooleanField(default=False, verbose_name='是否为管理员')
    last_login_time = models.DateTimeField(blank=True, null=True, verbose_name='最后登录时间')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='注册时间')
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'openid'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = '用户'
        verbose_name_plural = '用户'
        indexes = [
            models.Index(fields=['openid'], name='idx_users_openid'),
            models.Index(fields=['phone'], name='idx_users_phone'),
            models.Index(fields=['created_time'], name='idx_users_created_time'),
        ]
    
    def __str__(self):
        return f"{self.nickname}({self.openid})"
    
    @property
    def is_staff(self):
        """Django admin需要的属性"""
        return self.is_admin
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_time = timezone.now()
        self.save(update_fields=['last_login_time'])
