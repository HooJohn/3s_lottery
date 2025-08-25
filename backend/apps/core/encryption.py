# -*- coding: utf-8 -*-
"""
数据加密和安全传输模块
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class DataEncryption:
    """数据加密类"""
    
    def __init__(self):
        self.symmetric_key = self._get_symmetric_key()
        self.fernet = Fernet(self.symmetric_key)
    
    def _get_symmetric_key(self) -> bytes:
        """获取对称加密密钥"""
        # 从设置中获取密钥，如果没有则生成
        key = getattr(settings, 'ENCRYPTION_KEY', None)
        if not key:
            # 基于SECRET_KEY生成固定密钥
            password = settings.SECRET_KEY.encode()
            salt = b'lottery_encryption_salt_2024'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
        else:
            key = key.encode() if isinstance(key, str) else key
        
        return key
    
    def encrypt_string(self, plaintext: str) -> str:
        """加密字符串"""
        try:
            encrypted = self.fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted).decode('ascii')
        except Exception as e:
            logger.error(f"字符串加密失败: {e}")
            raise
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """解密字符串"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode('ascii'))
            decrypted = self.fernet.decrypt(encrypted_bytes)
            return decrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"字符串解密失败: {e}")
            raise
    
    def encrypt_json(self, data: Dict[str, Any]) -> str:
        """加密JSON数据"""
        try:
            json_string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            return self.encrypt_string(json_string)
        except Exception as e:
            logger.error(f"JSON加密失败: {e}")
            raise
    
    def decrypt_json(self, encrypted_text: str) -> Dict[str, Any]:
        """解密JSON数据"""
        try:
            json_string = self.decrypt_string(encrypted_text)
            return json.loads(json_string)
        except Exception as e:
            logger.error(f"JSON解密失败: {e}")
            raise
    
    def encrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """加密敏感字段"""
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                try:
                    encrypted_data[field] = self.encrypt_string(str(encrypted_data[field]))
                except Exception as e:
                    logger.error(f"加密字段 {field} 失败: {e}")
        
        return encrypted_data
    
    def decrypt_sensitive_fields(self, data: Dict[str, Any], sensitive_fields: list) -> Dict[str, Any]:
        """解密敏感字段"""
        decrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt_string(decrypted_data[field])
                except Exception as e:
                    logger.error(f"解密字段 {field} 失败: {e}")
        
        return decrypted_data


class PasswordSecurity:
    """密码安全类"""
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """哈希密码"""
        if not salt:
            salt = secrets.token_hex(32)
        
        # 使用Scrypt算法
        kdf = Scrypt(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=32768,
            block_size=8,
            parallelization=1,
        )
        
        key = kdf.derive(password.encode())
        hashed = base64.b64encode(key).decode()
        
        return hashed, salt
    
    @staticmethod
    def verify_password(password: str, hashed: str, salt: str) -> bool:
        """验证密码"""
        try:
            expected_hash, _ = PasswordSecurity.hash_password(password, salt)
            return hmac.compare_digest(hashed, expected_hash)
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    @staticmethod
    def generate_secure_password(length: int = 12) -> str:
        """生成安全密码"""
        import string
        
        # 确保包含各种字符类型
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*"
        
        # 至少包含一个每种类型的字符
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # 填充剩余长度
        all_chars = lowercase + uppercase + digits + symbols
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # 打乱顺序
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """检查密码强度"""
        import re
        
        score = 0
        feedback = []
        
        # 长度检查
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("密码长度至少8位")
        
        # 字符类型检查
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("需要包含小写字母")
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("需要包含大写字母")
        
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("需要包含数字")
        
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            feedback.append("需要包含特殊字符")
        
        # 常见密码检查
        common_passwords = ['123456', 'password', 'admin', 'qwerty']
        if password.lower() in common_passwords:
            score = 0
            feedback.append("不能使用常见密码")
        
        # 评级
        if score >= 5:
            strength = "强"
        elif score >= 3:
            strength = "中等"
        else:
            strength = "弱"
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback
        }


class SecureToken:
    """安全令牌类"""
    
    @staticmethod
    def generate_token(payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """生成安全令牌"""
        import jwt
        
        # 添加过期时间
        payload['exp'] = datetime.utcnow() + timedelta(seconds=expires_in)
        payload['iat'] = datetime.utcnow()
        payload['jti'] = secrets.token_hex(16)  # JWT ID
        
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        # 缓存令牌用于撤销检查
        cache_key = f"token:{payload['jti']}"
        cache.set(cache_key, True, expires_in)
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证令牌"""
        try:
            import jwt
            
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            
            # 检查令牌是否被撤销
            cache_key = f"token:{payload.get('jti')}"
            if not cache.get(cache_key):
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"无效令牌: {e}")
            return None
    
    @staticmethod
    def revoke_token(token: str) -> bool:
        """撤销令牌"""
        try:
            payload = SecureToken.verify_token(token)
            if payload:
                cache_key = f"token:{payload.get('jti')}"
                cache.delete(cache_key)
                return True
            return False
        except Exception as e:
            logger.error(f"撤销令牌失败: {e}")
            return False
    
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """生成一次性密码"""
        import random
        
        digits = '0123456789'
        return ''.join(random.choice(digits) for _ in range(length))
    
    @staticmethod
    def verify_otp(user_id: int, otp: str, otp_type: str = 'general') -> bool:
        """验证一次性密码"""
        cache_key = f"otp:{otp_type}:{user_id}"
        stored_otp = cache.get(cache_key)
        
        if stored_otp and hmac.compare_digest(stored_otp, otp):
            cache.delete(cache_key)  # 使用后删除
            return True
        
        return False
    
    @staticmethod
    def store_otp(user_id: int, otp: str, otp_type: str = 'general', expires_in: int = 300):
        """存储一次性密码"""
        cache_key = f"otp:{otp_type}:{user_id}"
        cache.set(cache_key, otp, expires_in)


class SecureTransmission:
    """安全传输类"""
    
    @staticmethod
    def generate_rsa_keypair() -> Tuple[bytes, bytes]:
        """生成RSA密钥对"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem
    
    @staticmethod
    def rsa_encrypt(data: str, public_key_pem: bytes) -> str:
        """RSA加密"""
        public_key = serialization.load_pem_public_key(public_key_pem)
        
        encrypted = public_key.encrypt(
            data.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(encrypted).decode()
    
    @staticmethod
    def rsa_decrypt(encrypted_data: str, private_key_pem: bytes) -> str:
        """RSA解密"""
        private_key = serialization.load_pem_private_key(private_key_pem, password=None)
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        decrypted = private_key.decrypt(
            encrypted_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return decrypted.decode()
    
    @staticmethod
    def create_secure_session(user_id: int) -> Dict[str, str]:
        """创建安全会话"""
        session_id = secrets.token_urlsafe(32)
        session_key = secrets.token_bytes(32)
        
        # 存储会话信息
        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            'session_key': base64.b64encode(session_key).decode()
        }
        
        cache_key = f"secure_session:{session_id}"
        cache.set(cache_key, session_data, 3600)  # 1小时有效
        
        return {
            'session_id': session_id,
            'session_key': base64.b64encode(session_key).decode()
        }
    
    @staticmethod
    def verify_secure_session(session_id: str) -> Optional[Dict[str, Any]]:
        """验证安全会话"""
        cache_key = f"secure_session:{session_id}"
        session_data = cache.get(cache_key)
        
        if session_data:
            # 更新会话过期时间
            cache.set(cache_key, session_data, 3600)
            return session_data
        
        return None


class DataIntegrity:
    """数据完整性类"""
    
    @staticmethod
    def calculate_checksum(data: str, algorithm: str = 'sha256') -> str:
        """计算数据校验和"""
        if algorithm == 'md5':
            return hashlib.md5(data.encode()).hexdigest()
        elif algorithm == 'sha1':
            return hashlib.sha1(data.encode()).hexdigest()
        elif algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        else:
            raise ValueError(f"不支持的算法: {algorithm}")
    
    @staticmethod
    def verify_checksum(data: str, expected_checksum: str, algorithm: str = 'sha256') -> bool:
        """验证数据校验和"""
        actual_checksum = DataIntegrity.calculate_checksum(data, algorithm)
        return hmac.compare_digest(actual_checksum, expected_checksum)
    
    @staticmethod
    def sign_data(data: str, secret_key: str) -> str:
        """数据签名"""
        return hmac.new(
            secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
    
    @staticmethod
    def verify_signature(data: str, signature: str, secret_key: str) -> bool:
        """验证数据签名"""
        expected_signature = DataIntegrity.sign_data(data, secret_key)
        return hmac.compare_digest(signature, expected_signature)


# 全局实例
data_encryption = DataEncryption()
password_security = PasswordSecurity()
secure_token = SecureToken()
secure_transmission = SecureTransmission()
data_integrity = DataIntegrity()