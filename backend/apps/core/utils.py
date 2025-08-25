"""
核心工具函数
"""

import uuid
import random
import string
import hashlib
from datetime import datetime
from django.utils import timezone


def generate_transaction_id():
    """生成交易ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"TXN{timestamp}{random_str}"


def generate_reference_id():
    """生成参考ID"""
    return str(uuid.uuid4()).replace('-', '').upper()[:16]


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """获取用户代理"""
    return request.META.get('HTTP_USER_AGENT', '')


def generate_secure_token(length=32):
    """生成安全令牌"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def hash_password(password, salt=None):
    """密码哈希"""
    if salt is None:
        salt = generate_secure_token(16)
    
    combined = f"{password}{salt}"
    hashed = hashlib.sha256(combined.encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(password, hashed_password):
    """验证密码"""
    try:
        salt, hash_value = hashed_password.split('$')
        combined = f"{password}{salt}"
        computed_hash = hashlib.sha256(combined.encode()).hexdigest()
        return computed_hash == hash_value
    except:
        return False


def format_currency(amount, currency='NGN'):
    """格式化货币"""
    if currency == 'NGN':
        return f"₦{amount:,.2f}"
    return f"{amount:,.2f} {currency}"


def calculate_percentage(part, total):
    """计算百分比"""
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def generate_otp(length=6):
    """生成OTP验证码"""
    return ''.join(random.choices(string.digits, k=length))


def mask_phone_number(phone):
    """掩码手机号"""
    if len(phone) <= 4:
        return phone
    return phone[:3] + '*' * (len(phone) - 6) + phone[-3:]


def mask_email(email):
    """掩码邮箱"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"


def validate_nigerian_phone(phone):
    """验证尼日利亚手机号"""
    import re
    pattern = r'^\+234[0-9]{10}$'
    return bool(re.match(pattern, phone))


def normalize_phone_number(phone):
    """标准化手机号"""
    # 移除所有非数字字符
    digits_only = ''.join(filter(str.isdigit, phone))
    
    # 处理不同格式
    if digits_only.startswith('234'):
        return f"+{digits_only}"
    elif digits_only.startswith('0') and len(digits_only) == 11:
        return f"+234{digits_only[1:]}"
    elif len(digits_only) == 10:
        return f"+234{digits_only}"
    
    return phone  # 返回原始格式如果无法标准化


def get_time_ago(dt):
    """获取时间差描述"""
    now = timezone.now()
    if dt.tzinfo is None:
        dt = timezone.make_aware(dt)
    
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"


def truncate_string(text, length=50, suffix='...'):
    """截断字符串"""
    if len(text) <= length:
        return text
    return text[:length - len(suffix)] + suffix


def safe_divide(numerator, denominator, default=0):
    """安全除法"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except:
        return default


def generate_lottery_numbers(min_num=1, max_num=11, count=5):
    """生成彩票号码"""
    return sorted(random.sample(range(min_num, max_num + 1), count))


def calculate_lottery_odds(total_numbers, selected_numbers, winning_numbers):
    """计算彩票中奖概率"""
    from math import comb
    
    total_combinations = comb(total_numbers, selected_numbers)
    winning_combinations = comb(winning_numbers, selected_numbers)
    
    if winning_combinations == 0:
        return 0
    
    return 1 / (total_combinations / winning_combinations)


def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def is_business_hours(start_hour=9, end_hour=21):
    """检查是否在营业时间内"""
    current_hour = timezone.now().hour
    return start_hour <= current_hour <= end_hour


def get_next_business_day():
    """获取下一个工作日"""
    from datetime import timedelta
    
    today = timezone.now().date()
    next_day = today + timedelta(days=1)
    
    # 跳过周末（周六=5，周日=6）
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    
    return next_day


def validate_json_structure(data, required_fields):
    """验证JSON结构"""
    if not isinstance(data, dict):
        return False, "数据必须是字典格式"
    
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        return False, f"缺少必需字段: {', '.join(missing_fields)}"
    
    return True, "验证通过"


def clean_html_tags(text):
    """清理HTML标签"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def generate_qr_code_data(data):
    """生成二维码数据"""
    import base64
    import json
    
    json_data = json.dumps(data)
    encoded_data = base64.b64encode(json_data.encode()).decode()
    return encoded_data