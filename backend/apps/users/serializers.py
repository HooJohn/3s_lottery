"""
用户认证序列化器
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from .models import User, UserProfile, KYCDocument


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    referral_code_input = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="推荐码(可选)"
    )
    
    class Meta:
        model = User
        fields = [
            'phone', 'email', 'full_name', 'country',
            'password', 'password_confirm', 'referral_code_input'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True},
        }
    
    def validate_phone(self, value):
        """验证手机号格式"""
        phone_regex = RegexValidator(
            regex=r'^\+234[0-9]{10}$',
            message="手机号格式错误，正确格式: +2348012345678"
        )
        phone_regex(value)
        
        # 检查手机号是否已存在
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("该手机号已被注册")
        
        return value
    
    def validate_email(self, value):
        """验证邮箱"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value
    
    def validate(self, attrs):
        """验证密码确认"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("两次输入的密码不一致")
        
        # 验证推荐码
        referral_code_input = attrs.get('referral_code_input')
        if referral_code_input:
            try:
                referrer = User.objects.get(referral_code=referral_code_input, is_active=True)
                attrs['referred_by'] = referrer
            except User.DoesNotExist:
                raise serializers.ValidationError("推荐码无效")
        
        return attrs
    
    def create(self, validated_data):
        """创建用户"""
        # 移除确认密码和推荐码输入字段
        validated_data.pop('password_confirm')
        validated_data.pop('referral_code_input', None)
        
        # 创建用户
        user = User.objects.create_user(
            username=validated_data['phone'],  # 使用手机号作为用户名
            **validated_data
        )
        
        # 创建用户资料
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    支持用户名/邮箱/手机号任一方式登录
    """
    login = serializers.CharField(help_text="用户名/邮箱/手机号")
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, attrs):
        login = attrs.get('login')
        password = attrs.get('password')
        
        if login and password:
            # 尝试不同的登录方式
            user = None
            
            # 1. 尝试用户名登录
            user = authenticate(username=login, password=password)
            
            # 2. 尝试邮箱登录
            if not user:
                try:
                    user_obj = User.objects.get(email=login, is_active=True)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            # 3. 尝试手机号登录
            if not user:
                try:
                    user_obj = User.objects.get(phone=login, is_active=True)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError("用户名或密码错误")
            
            if not user.is_active:
                raise serializers.ValidationError("账户已被禁用")
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError("请输入用户名和密码")


class UserProfileSerializer(serializers.ModelSerializer):
    """
    用户资料序列化器
    """
    vip_info = serializers.SerializerMethodField()
    referral_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'email', 'full_name', 'country',
            'vip_level', 'total_turnover', 'referral_code',
            'kyc_status', 'two_factor_enabled', 'created_at',
            'vip_info', 'referral_stats'
        ]
        read_only_fields = [
            'id', 'phone', 'vip_level', 'total_turnover',
            'referral_code', 'kyc_status', 'created_at'
        ]
    
    def get_vip_info(self, obj):
        """获取VIP信息"""
        return obj.get_vip_info()
    
    def get_referral_stats(self, obj):
        """获取推荐统计"""
        referrals = obj.referrals.filter(is_active=True)
        return {
            'total_referrals': referrals.count(),
            'active_referrals': referrals.filter(last_login__isnull=False).count(),
            'referral_code': obj.referral_code,
        }


class UserDetailSerializer(serializers.ModelSerializer):
    """
    用户详细信息序列化器
    """
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'phone', 'email', 'full_name', 'country',
            'vip_level', 'total_turnover', 'referral_code',
            'kyc_status', 'two_factor_enabled', 'is_active',
            'last_login', 'created_at', 'profile'
        ]
    
    def get_profile(self, obj):
        """获取用户资料"""
        try:
            profile = obj.profile
            return {
                'avatar': profile.avatar.url if profile.avatar else None,
                'birth_date': profile.birth_date,
                'gender': profile.gender,
                'address': profile.address,
                'city': profile.city,
                'state': profile.state,
                'language': profile.language,
                'timezone': profile.timezone,
                'email_notifications': profile.email_notifications,
                'sms_notifications': profile.sms_notifications,
            }
        except UserProfile.DoesNotExist:
            return None


class KYCDocumentSerializer(serializers.ModelSerializer):
    """
    KYC文档序列化器
    """
    class Meta:
        model = KYCDocument
        fields = [
            'id', 'document_type', 'document_number',
            'front_image', 'back_image', 'selfie_image',
            'status', 'rejection_reason', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'rejection_reason', 'created_at']
    
    def validate(self, attrs):
        """验证KYC文档"""
        user = self.context['request'].user
        
        # 检查是否已有待审核的文档
        if KYCDocument.objects.filter(user=user, status='PENDING').exists():
            raise serializers.ValidationError("您已有待审核的KYC文档，请等待审核结果")
        
        # 检查是否已通过KYC
        if user.kyc_status == 'APPROVED':
            raise serializers.ValidationError("您的KYC已通过审核，无需重复提交")
        
        return attrs
    
    def create(self, validated_data):
        """创建KYC文档"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class PasswordChangeSerializer(serializers.Serializer):
    """
    密码修改序列化器
    """
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码错误")
        return value
    
    def validate(self, attrs):
        """验证新密码确认"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("两次输入的新密码不一致")
        return attrs
    
    def save(self):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ReferralTreeSerializer(serializers.Serializer):
    """
    推荐关系树序列化器
    """
    level = serializers.IntegerField()
    user_id = serializers.CharField()
    phone = serializers.CharField()
    total_turnover = serializers.DecimalField(max_digits=15, decimal_places=2)
    vip_level = serializers.IntegerField()
    created_at = serializers.DateTimeField()