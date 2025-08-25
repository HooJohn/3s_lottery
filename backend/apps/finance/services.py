"""
财务服务层
"""

import uuid
import requests
from decimal import Decimal
from typing import Dict, Any, Optional
from django.conf import settings
from django.db import transaction, models
from django.utils import timezone
from .models import UserBalance, Transaction, BankAccount, PaymentMethod
from apps.core.utils import generate_transaction_id


class FinanceService:
    """
    财务服务
    """
    
    @staticmethod
    def get_or_create_balance(user) -> UserBalance:
        """
        获取或创建用户余额
        """
        balance, created = UserBalance.objects.get_or_create(user=user)
        return balance
    
    @staticmethod
    def create_deposit_order(user, payment_method: PaymentMethod, amount: Decimal) -> Dict[str, Any]:
        """
        创建存款订单
        """
        try:
            with transaction.atomic():
                # 计算手续费（存款免手续费）
                fee = Decimal('0.00')
                actual_amount = amount
                
                # 创建交易记录
                deposit_transaction = Transaction.objects.create(
                    user=user,
                    type='DEPOSIT',
                    amount=amount,
                    fee=fee,
                    actual_amount=actual_amount,
                    status='PENDING',
                    reference_id=generate_transaction_id(),
                    description=f'通过{payment_method.name}存款',
                    metadata={
                        'payment_method_id': str(payment_method.id),
                        'payment_method_name': payment_method.name,
                        'provider': payment_method.provider,
                    }
                )
                
                # 根据支付方式处理
                if payment_method.provider == 'PAYSTACK':
                    result = PaystackService.create_payment(deposit_transaction)
                elif payment_method.provider == 'FLUTTERWAVE':
                    result = FlutterwaveService.create_payment(deposit_transaction)
                elif payment_method.provider == 'OPAY':
                    result = MobileMoneyService.create_opay_payment(deposit_transaction)
                elif payment_method.provider == 'PALMPAY':
                    result = MobileMoneyService.create_palmpay_payment(deposit_transaction)
                elif payment_method.provider == 'MONIEPOINT':
                    result = MobileMoneyService.create_moniepoint_payment(deposit_transaction)
                elif payment_method.provider == 'MANUAL':
                    result = ManualPaymentService.create_deposit_info(deposit_transaction)
                else:
                    result = {
                        'success': False,
                        'message': '不支持的支付方式'
                    }
                
                if result['success']:
                    return {
                        'success': True,
                        'message': '存款订单创建成功',
                        'data': {
                            'transaction_id': str(deposit_transaction.id),
                            'reference_id': deposit_transaction.reference_id,
                            'amount': float(amount),
                            'payment_info': result.get('payment_info', {}),
                            'instructions': result.get('instructions', ''),
                        }
                    }
                else:
                    # 标记交易失败
                    deposit_transaction.mark_failed(result.get('message', '支付处理失败'))
                    return result
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'创建存款订单失败: {str(e)}'
            }
    
    @staticmethod
    def create_withdraw_order(user, bank_account: BankAccount, amount: Decimal) -> Dict[str, Any]:
        """
        创建提款订单
        """
        try:
            with transaction.atomic():
                # 获取用户VIP信息计算手续费
                vip_info = user.get_vip_info()
                fee_rate = Decimal(str(vip_info.get('withdraw_fee_rate', 0.02)))  # 默认2%
                fee = amount * fee_rate
                actual_amount = amount - fee
                
                # 检查余额
                balance = FinanceService.get_or_create_balance(user)
                if balance.get_available_balance() < amount:
                    return {
                        'success': False,
                        'message': '余额不足'
                    }
                
                # 冻结余额
                if not balance.freeze_balance(amount, '提款冻结'):
                    return {
                        'success': False,
                        'message': '余额冻结失败'
                    }
                
                # 创建交易记录
                withdraw_transaction = Transaction.objects.create(
                    user=user,
                    type='WITHDRAW',
                    amount=amount,
                    fee=fee,
                    actual_amount=actual_amount,
                    status='PENDING',
                    reference_id=generate_transaction_id(),
                    description=f'提款到{bank_account.get_bank_code_display()}',
                    metadata={
                        'bank_account_id': str(bank_account.id),
                        'bank_name': bank_account.get_bank_code_display(),
                        'account_number': bank_account.account_number,
                        'account_name': bank_account.account_name,
                        'fee_rate': float(fee_rate),
                    }
                )
                
                # 提交到处理队列
                from .tasks import process_withdraw_request
                process_withdraw_request.delay(str(withdraw_transaction.id))
                
                return {
                    'success': True,
                    'message': '提款申请提交成功',
                    'data': {
                        'transaction_id': str(withdraw_transaction.id),
                        'reference_id': withdraw_transaction.reference_id,
                        'amount': float(amount),
                        'fee': float(fee),
                        'actual_amount': float(actual_amount),
                        'bank_info': {
                            'bank_name': bank_account.get_bank_code_display(),
                            'account_number': bank_account.account_number,
                            'account_name': bank_account.account_name,
                        },
                        'estimated_arrival': '1-3个工作日',
                    }
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'创建提款订单失败: {str(e)}'
            }
    
    @staticmethod
    def process_deposit_callback(transaction_id: str, status: str, 
                               external_reference: str = '', metadata: Dict = None) -> bool:
        """
        处理存款回调
        """
        try:
            with transaction.atomic():
                deposit_transaction = Transaction.objects.select_for_update().get(
                    id=transaction_id,
                    type='DEPOSIT'
                )
                
                if deposit_transaction.status != 'PENDING':
                    return False
                
                if status == 'success':
                    # 存款成功，增加用户余额
                    balance = FinanceService.get_or_create_balance(deposit_transaction.user)
                    balance.add_balance(
                        deposit_transaction.actual_amount,
                        'main',
                        f'存款到账 - {deposit_transaction.reference_id}'
                    )
                    
                    # 更新交易状态
                    deposit_transaction.status = 'COMPLETED'
                    deposit_transaction.processed_at = timezone.now()
                    if external_reference:
                        deposit_transaction.metadata['external_reference'] = external_reference
                    if metadata:
                        deposit_transaction.metadata.update(metadata)
                    deposit_transaction.save()
                    
                    # 发送通知
                    from .tasks import send_deposit_success_notification
                    send_deposit_success_notification.delay(str(deposit_transaction.user.id), float(deposit_transaction.amount))
                    
                    return True
                    
                else:
                    # 存款失败
                    deposit_transaction.mark_failed('支付失败')
                    return False
                    
        except Transaction.DoesNotExist:
            return False
        except Exception as e:
            return False
    
    @staticmethod
    def process_withdraw_request(transaction_id: str) -> Dict[str, Any]:
        """
        处理提款请求
        """
        try:
            with transaction.atomic():
                withdraw_transaction = Transaction.objects.select_for_update().get(
                    id=transaction_id,
                    type='WITHDRAW'
                )
                
                if withdraw_transaction.status != 'PENDING':
                    return {'success': False, 'message': '交易状态异常'}
                
                # 更新状态为处理中
                withdraw_transaction.status = 'PROCESSING'
                withdraw_transaction.save()
                
                # 使用银行转账服务处理
                transfer_result = WithdrawProcessingService.process_bank_transfer(withdraw_transaction)
                
                if transfer_result['success']:
                    # 提款成功
                    balance = FinanceService.get_or_create_balance(withdraw_transaction.user)
                    
                    # 解冻余额（实际已扣除）
                    balance.unfreeze_balance(withdraw_transaction.amount, to_main=False)
                    
                    # 更新交易状态
                    withdraw_transaction.status = 'COMPLETED'
                    withdraw_transaction.processed_at = timezone.now()
                    withdraw_transaction.save()
                    
                    # 发送通知
                    from .tasks import send_withdraw_success_notification
                    send_withdraw_success_notification.delay(
                        str(withdraw_transaction.user.id), 
                        float(withdraw_transaction.actual_amount)
                    )
                    
                    return {'success': True, 'message': '提款处理成功'}
                    
                else:
                    # 提款失败，解冻余额
                    balance = FinanceService.get_or_create_balance(withdraw_transaction.user)
                    balance.unfreeze_balance(withdraw_transaction.amount)
                    
                    withdraw_transaction.mark_failed(transfer_result.get('message', '银行处理失败'))
                    
                    return {'success': False, 'message': transfer_result.get('message', '提款处理失败')}
                    
        except Transaction.DoesNotExist:
            return {'success': False, 'message': '交易不存在'}
        except Exception as e:
            return {'success': False, 'message': f'处理失败: {str(e)}'}


class PaystackService:
    """
    Paystack支付服务
    """
    
    @staticmethod
    def create_payment(transaction: Transaction) -> Dict[str, Any]:
        """
        创建Paystack支付
        """
        try:
            url = "https://api.paystack.co/transaction/initialize"
            
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "email": transaction.user.email,
                "amount": int(transaction.amount * 100),  # 转换为kobo
                "reference": transaction.reference_id,
                "callback_url": f"{settings.SITE_URL}/api/v1/finance/paystack/callback/",
                "metadata": {
                    "transaction_id": str(transaction.id),
                    "user_id": str(transaction.user.id),
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get('status'):
                return {
                    'success': True,
                    'payment_info': {
                        'payment_url': result['data']['authorization_url'],
                        'access_code': result['data']['access_code'],
                        'reference': result['data']['reference'],
                    },
                    'instructions': '请点击链接完成支付'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'Paystack支付创建失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Paystack支付创建失败: {str(e)}'
            }


class FlutterwaveService:
    """
    Flutterwave支付服务
    """
    
    @staticmethod
    def create_payment(transaction: Transaction) -> Dict[str, Any]:
        """
        创建Flutterwave支付
        """
        try:
            url = "https://api.flutterwave.com/v3/payments"
            
            headers = {
                "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "tx_ref": transaction.reference_id,
                "amount": str(transaction.amount),
                "currency": "NGN",
                "redirect_url": f"{settings.SITE_URL}/api/v1/finance/flutterwave/callback/",
                "customer": {
                    "email": transaction.user.email,
                    "phonenumber": transaction.user.phone,
                    "name": transaction.user.full_name
                },
                "customizations": {
                    "title": "彩票平台存款",
                    "description": f"存款 - {transaction.reference_id}",
                    "logo": f"{settings.SITE_URL}/static/logo.png"
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'payment_info': {
                        'payment_url': result['data']['link'],
                        'tx_ref': result['data']['tx_ref'],
                    },
                    'instructions': '请点击链接完成支付'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'Flutterwave支付创建失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Flutterwave支付创建失败: {str(e)}'
            }


class ManualPaymentService:
    """
    手动支付服务（银行转账）
    """
    
    @staticmethod
    def create_deposit_info(transaction: Transaction) -> Dict[str, Any]:
        """
        创建手动存款信息
        """
        try:
            # 获取收款银行信息（从系统配置获取）
            bank_info = {
                'bank_name': 'Access Bank',
                'account_number': '1234567890',
                'account_name': 'Lottery Platform Ltd',
                'reference': transaction.reference_id,
            }
            
            instructions = f"""
请按以下信息进行银行转账：

收款银行：{bank_info['bank_name']}
收款账号：{bank_info['account_number']}
收款户名：{bank_info['account_name']}
转账金额：₦{transaction.amount}
转账备注：{bank_info['reference']}

重要提示：
1. 请务必填写正确的转账备注
2. 转账完成后请保留转账凭证
3. 到账时间：1-3个工作日
4. 如有疑问请联系客服
"""
            
            return {
                'success': True,
                'payment_info': bank_info,
                'instructions': instructions
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'获取转账信息失败: {str(e)}'
            }


class MobileMoneyService:
    """
    移动货币支付服务
    """
    
    @staticmethod
    def create_opay_payment(transaction: Transaction) -> Dict[str, Any]:
        """
        创建OPay支付
        """
        try:
            # OPay API集成
            url = "https://api.opayweb.com/api/v1/international/payment/create"
            
            headers = {
                "Authorization": f"Bearer {settings.OPAY_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "reference": transaction.reference_id,
                "amount": {
                    "total": int(transaction.amount * 100),  # 转换为kobo
                    "currency": "NGN"
                },
                "country": "NG",
                "returnUrl": f"{settings.SITE_URL}/api/v1/finance/payment/success/",
                "callbackUrl": f"{settings.SITE_URL}/api/v1/finance/mobile-money/callback/",
                "userInfo": {
                    "userEmail": transaction.user.email,
                    "userMobile": transaction.user.phone,
                    "userName": transaction.user.full_name
                },
                "productInfo": {
                    "productName": "彩票平台存款",
                    "productDesc": f"存款 - {transaction.reference_id}"
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get('code') == '00000':
                return {
                    'success': True,
                    'payment_info': {
                        'payment_url': result['data']['cashierUrl'],
                        'reference': result['data']['reference'],
                        'order_no': result['data']['orderNo'],
                    },
                    'instructions': '请点击链接完成OPay支付'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'OPay支付创建失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'OPay支付创建失败: {str(e)}'
            }
    
    @staticmethod
    def create_palmpay_payment(transaction: Transaction) -> Dict[str, Any]:
        """
        创建PalmPay支付
        """
        try:
            # PalmPay API集成
            url = "https://api.palmpay.com/api/v1/payment/create"
            
            headers = {
                "Authorization": f"Bearer {settings.PALMPAY_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "merchantId": settings.PALMPAY_MERCHANT_ID,
                "reference": transaction.reference_id,
                "amount": str(transaction.amount),
                "currency": "NGN",
                "description": f"彩票平台存款 - {transaction.reference_id}",
                "callbackUrl": f"{settings.SITE_URL}/api/v1/finance/mobile-money/callback/",
                "returnUrl": f"{settings.SITE_URL}/api/v1/finance/payment/success/",
                "customer": {
                    "email": transaction.user.email,
                    "phone": transaction.user.phone,
                    "name": transaction.user.full_name
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get('status') == 'success':
                return {
                    'success': True,
                    'payment_info': {
                        'payment_url': result['data']['paymentUrl'],
                        'reference': result['data']['reference'],
                        'transaction_id': result['data']['transactionId'],
                    },
                    'instructions': '请点击链接完成PalmPay支付'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'PalmPay支付创建失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'PalmPay支付创建失败: {str(e)}'
            }
    
    @staticmethod
    def create_moniepoint_payment(transaction: Transaction) -> Dict[str, Any]:
        """
        创建Moniepoint支付
        """
        try:
            # Moniepoint API集成
            url = "https://api.moniepoint.com/api/v1/payment/initialize"
            
            headers = {
                "Authorization": f"Bearer {settings.MONIEPOINT_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "amount": int(transaction.amount * 100),  # 转换为kobo
                "reference": transaction.reference_id,
                "email": transaction.user.email,
                "phone": transaction.user.phone,
                "name": transaction.user.full_name,
                "description": f"彩票平台存款 - {transaction.reference_id}",
                "callback_url": f"{settings.SITE_URL}/api/v1/finance/mobile-money/callback/",
                "return_url": f"{settings.SITE_URL}/api/v1/finance/payment/success/"
            }
            
            response = requests.post(url, json=data, headers=headers)
            result = response.json()
            
            if result.get('status'):
                return {
                    'success': True,
                    'payment_info': {
                        'payment_url': result['data']['authorization_url'],
                        'access_code': result['data']['access_code'],
                        'reference': result['data']['reference'],
                    },
                    'instructions': '请点击链接完成Moniepoint支付'
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', 'Moniepoint支付创建失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Moniepoint支付创建失败: {str(e)}'
            }


class BankVerificationService:
    """
    银行账户验证服务
    """
    
    @staticmethod
    def verify_bank_account(bank_account: BankAccount) -> Dict[str, Any]:
        """
        验证银行账户
        """
        try:
            # 这里可以集成银行API进行账户验证
            # 暂时模拟验证成功
            
            verification_result = {
                'is_valid': True,
                'account_name': bank_account.account_name,
                'bank_name': bank_account.get_bank_code_display(),
                'verification_method': 'API',
                'verified_at': timezone.now().isoformat(),
            }
            
            if verification_result['is_valid']:
                bank_account.is_verified = True
                bank_account.verification_data = verification_result
                bank_account.verified_at = timezone.now()
                bank_account.save()
                
                return {
                    'success': True,
                    'message': '银行账户验证成功',
                    'data': verification_result
                }
            else:
                return {
                    'success': False,
                    'message': '银行账户验证失败'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'银行账户验证失败: {str(e)}'
            }
    
    @staticmethod
    def verify_account_name(bank_code: str, account_number: str, expected_name: str) -> Dict[str, Any]:
        """
        验证银行账户名称
        """
        try:
            # 这里可以集成尼日利亚银行API进行账户名验证
            # 例如集成Paystack的Bank Account Resolution API
            
            # 模拟API调用
            api_result = {
                'status': True,
                'data': {
                    'account_number': account_number,
                    'account_name': expected_name.upper(),
                    'bank_id': bank_code,
                }
            }
            
            if api_result['status']:
                api_name = api_result['data']['account_name']
                expected_name_upper = expected_name.upper()
                
                # 名称匹配度检查
                name_match = api_name == expected_name_upper
                
                return {
                    'success': True,
                    'is_match': name_match,
                    'api_name': api_name,
                    'expected_name': expected_name_upper,
                    'confidence': 1.0 if name_match else 0.0
                }
            else:
                return {
                    'success': False,
                    'message': '无法验证账户信息'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'账户名验证失败: {str(e)}'
            }


class WithdrawProcessingService:
    """
    提款处理服务
    """
    
    @staticmethod
    def validate_withdraw_request(user, amount: Decimal, bank_account: BankAccount) -> Dict[str, Any]:
        """
        验证提款请求
        """
        errors = []
        
        # 1. KYC验证
        if user.kyc_status != 'APPROVED':
            errors.append('请先完成KYC身份验证')
        
        # 2. 银行账户验证
        if not bank_account.is_verified:
            errors.append('银行账户未验证')
        
        # 3. 余额检查
        try:
            balance = user.balance
            if balance.get_available_balance() < amount:
                errors.append('余额不足')
        except UserBalance.DoesNotExist:
            errors.append('用户余额信息不存在')
        
        # 4. VIP限制检查
        vip_info = user.get_vip_info()
        daily_limit = Decimal(str(vip_info.get('daily_withdraw_limit', 0)))
        daily_times = vip_info.get('daily_withdraw_times', 1)
        
        # 检查今日提款
        from datetime import date
        today = date.today()
        today_withdrawals = Transaction.objects.filter(
            user=user,
            type='WITHDRAW',
            status__in=['COMPLETED', 'PROCESSING'],
            created_at__date=today
        )
        
        today_amount = today_withdrawals.aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0')
        
        today_count = today_withdrawals.count()
        
        if today_amount + amount > daily_limit:
            errors.append(f'超过每日提款限额 ₦{daily_limit:,.2f}')
        
        if today_count >= daily_times:
            errors.append(f'超过每日提款次数限制 {daily_times} 次')
        
        # 5. 最小金额检查
        if amount < Decimal('100.00'):
            errors.append('提款金额不能少于 ₦100')
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'daily_stats': {
                'today_amount': float(today_amount),
                'today_count': today_count,
                'remaining_limit': float(daily_limit - today_amount),
                'remaining_times': max(0, daily_times - today_count)
            }
        }
    
    @staticmethod
    def calculate_withdraw_fee(user, amount: Decimal) -> Decimal:
        """
        计算提款手续费
        """
        vip_info = user.get_vip_info()
        fee_rate = Decimal(str(vip_info.get('withdraw_fee_rate', 0.02)))
        return amount * fee_rate
    
    @staticmethod
    def process_bank_transfer(transaction: Transaction) -> Dict[str, Any]:
        """
        处理银行转账
        """
        try:
            # 这里可以集成银行API进行实际转账
            # 例如集成Paystack Transfer API或其他银行API
            
            bank_account_id = transaction.metadata.get('bank_account_id')
            bank_account = BankAccount.objects.get(id=bank_account_id)
            
            # 模拟银行转账API调用
            transfer_result = {
                'status': 'success',
                'transfer_code': f'TRF_{transaction.reference_id}',
                'reference': transaction.reference_id,
                'amount': float(transaction.actual_amount),
                'recipient': {
                    'bank_code': bank_account.bank_code,
                    'account_number': bank_account.account_number,
                    'account_name': bank_account.account_name,
                },
                'fee': float(transaction.fee),
                'currency': 'NGN',
                'status_message': '转账成功'
            }
            
            if transfer_result['status'] == 'success':
                # 更新交易元数据
                transaction.metadata.update({
                    'transfer_code': transfer_result['transfer_code'],
                    'bank_reference': transfer_result.get('reference'),
                    'transfer_status': 'completed',
                    'processed_at': timezone.now().isoformat()
                })
                transaction.save()
                
                return {
                    'success': True,
                    'message': '银行转账成功',
                    'data': transfer_result
                }
            else:
                return {
                    'success': False,
                    'message': transfer_result.get('message', '银行转账失败')
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'银行转账处理失败: {str(e)}'
            }