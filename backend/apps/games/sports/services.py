"""
体育博彩第三方平台集成服务
"""

import uuid
import requests
from typing import Dict, List, Any, Optional
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
import logging

from apps.finance.models import Transaction, UserBalance
from .models import (
    SportsProvider, UserSportsWallet, SportsWalletTransaction,
    SportsBetRecord, SportsStatistics, SportsProviderConfig
)

logger = logging.getLogger(__name__)


class SportsProviderService:
    """
    体育博彩平台服务
    """
    
    @staticmethod
    def get_active_providers() -> List[Dict[str, Any]]:
        """
        获取活跃的体育平台列表
        """
        try:
            providers = SportsProvider.objects.filter(
                is_active=True
            ).order_by('sort_order', 'name')
            
            result = []
            for provider in providers:
                result.append({
                    'id': str(provider.id),
                    'name': provider.name,
                    'code': provider.code,
                    'logo': provider.logo.url if provider.logo else None,
                    'banner': provider.banner.url if provider.banner else None,
                    'description': provider.description,
                    'features': provider.features,
                    'supported_sports': provider.supported_sports,
                    'status': provider.get_status_display(),
                    'is_maintenance': provider.is_maintenance,
                    'tags': provider.get_tags(),
                    'min_bet_amount': float(provider.min_bet_amount),
                    'max_bet_amount': float(provider.max_bet_amount),
                    'integration_type': provider.integration_type,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取体育平台列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_provider_by_code(code: str) -> Optional[SportsProvider]:
        """
        根据代码获取平台
        """
        try:
            return SportsProvider.objects.get(code=code, is_active=True)
        except SportsProvider.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_wallet(user, provider_code: str) -> Dict[str, Any]:
        """
        获取用户在指定平台的钱包信息
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            # 获取或创建用户钱包
            wallet, created = UserSportsWallet.objects.get_or_create(
                user=user,
                provider=provider,
                defaults={
                    'platform_user_id': f"{user.id}_{provider.code}",
                    'platform_username': user.username or user.phone,
                    'balance': Decimal('0.00'),
                    'is_active': True
                }
            )
            
            # 如果是新创建的钱包，可能需要在第三方平台创建账户
            if created:
                create_result = SportsProviderService._create_platform_account(user, provider, wallet)
                if not create_result['success']:
                    wallet.delete()
                    return create_result
            
            return {
                'success': True,
                'data': {
                    'wallet_id': str(wallet.id),
                    'provider_name': provider.name,
                    'balance': float(wallet.balance),
                    'platform_user_id': wallet.platform_user_id,
                    'last_sync_at': wallet.last_sync_at.isoformat() if wallet.last_sync_at else None,
                    'is_active': wallet.is_active
                }
            }
            
        except Exception as e:
            logger.error(f"获取用户钱包失败: {str(e)}")
            return {'success': False, 'message': f'获取钱包失败: {str(e)}'}
    
    @staticmethod
    def _create_platform_account(user, provider: SportsProvider, wallet: UserSportsWallet) -> Dict[str, Any]:
        """
        在第三方平台创建用户账户
        """
        try:
            # 这里应该调用第三方平台的API创建账户
            # 由于是示例，我们模拟创建成功
            
            # 模拟API调用
            api_data = {
                'username': wallet.platform_username,
                'user_id': wallet.platform_user_id,
                'phone': user.phone,
                'email': user.email or f"{user.phone}@example.com",
            }
            
            # 实际应该调用第三方API
            # response = requests.post(f"{provider.api_endpoint}/create_user", json=api_data)
            
            # 模拟成功响应
            logger.info(f"为用户 {user.phone} 在平台 {provider.name} 创建账户成功")
            
            return {'success': True, 'message': '账户创建成功'}
            
        except Exception as e:
            logger.error(f"创建平台账户失败: {str(e)}")
            return {'success': False, 'message': f'创建账户失败: {str(e)}'}
    
    @staticmethod
    def transfer_to_platform(user, provider_code: str, amount: Decimal) -> Dict[str, Any]:
        """
        转账到体育平台
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            if provider.is_maintenance:
                return {'success': False, 'message': '平台维护中，暂时无法转账'}
            
            # 获取用户钱包
            wallet_result = SportsProviderService.get_user_wallet(user, provider_code)
            if not wallet_result['success']:
                return wallet_result
            
            wallet = UserSportsWallet.objects.get(id=wallet_result['data']['wallet_id'])
            
            # 检查转账金额限制
            config = getattr(provider, 'config', None)
            if config:
                if amount < config.min_transfer_amount:
                    return {
                        'success': False,
                        'message': f'转账金额不能少于 ₦{config.min_transfer_amount}'
                    }
                if amount > config.max_transfer_amount:
                    return {
                        'success': False,
                        'message': f'转账金额不能超过 ₦{config.max_transfer_amount}'
                    }
            
            # 检查用户主钱包余额
            try:
                main_balance = user.balance
                if main_balance.get_available_balance() < amount:
                    return {
                        'success': False,
                        'message': f'主钱包余额不足，需要 ₦{amount}，当前可用余额 ₦{main_balance.get_available_balance()}'
                    }
            except UserBalance.DoesNotExist:
                return {'success': False, 'message': '用户余额信息不存在'}
            
            with transaction.atomic():
                # 从主钱包扣除
                main_balance.deduct_balance(amount, 'available', f'转账到{provider.name}')
                
                # 创建主钱包交易记录
                main_transaction = Transaction.objects.create(
                    user=user,
                    type='TRANSFER_OUT',
                    amount=amount,
                    fee=Decimal('0.00'),
                    actual_amount=amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'转账到{provider.name}',
                    metadata={
                        'provider_code': provider.code,
                        'provider_name': provider.name,
                        'wallet_id': str(wallet.id),
                    }
                )
                
                # 更新体育钱包余额
                balance_before = wallet.balance
                wallet.balance += amount
                wallet.last_sync_at = timezone.now()
                wallet.save()
                
                # 创建体育钱包交易记录
                sports_transaction = SportsWalletTransaction.objects.create(
                    user=user,
                    provider=provider,
                    wallet=wallet,
                    transaction_type='TRANSFER_IN',
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    status='COMPLETED',
                    description=f'从主钱包转入',
                    metadata={
                        'main_transaction_id': str(main_transaction.id),
                    }
                )
                
                # 调用第三方平台API（如果需要）
                if provider.wallet_mode == 'TRANSFER':
                    api_result = SportsProviderService._call_platform_transfer_api(
                        provider, wallet, amount, 'IN'
                    )
                    if not api_result['success']:
                        # API调用失败，记录但不回滚（可以后续重试）
                        sports_transaction.remark = f"API调用失败: {api_result['message']}"
                        sports_transaction.save()
                
                return {
                    'success': True,
                    'message': '转账成功',
                    'data': {
                        'transaction_id': str(sports_transaction.id),
                        'amount': float(amount),
                        'wallet_balance': float(wallet.balance),
                        'main_balance': float(main_balance.get_available_balance()),
                    }
                }
                
        except Exception as e:
            logger.error(f"转账到体育平台失败: {str(e)}")
            return {'success': False, 'message': f'转账失败: {str(e)}'}
    
    @staticmethod
    def transfer_from_platform(user, provider_code: str, amount: Decimal = None) -> Dict[str, Any]:
        """
        从体育平台转出（回收余额）
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            # 获取用户钱包
            try:
                wallet = UserSportsWallet.objects.get(user=user, provider=provider)
            except UserSportsWallet.DoesNotExist:
                return {'success': False, 'message': '钱包不存在'}
            
            # 如果没有指定金额，则转出全部余额
            if amount is None:
                amount = wallet.balance
            
            if amount <= 0:
                return {'success': False, 'message': '转出金额必须大于0'}
            
            if amount > wallet.balance:
                return {'success': False, 'message': '钱包余额不足'}
            
            with transaction.atomic():
                # 更新体育钱包余额
                balance_before = wallet.balance
                wallet.balance -= amount
                wallet.last_sync_at = timezone.now()
                wallet.save()
                
                # 添加到主钱包
                main_balance = user.balance
                main_balance.add_balance(amount, 'available', f'从{provider.name}转入')
                
                # 创建主钱包交易记录
                main_transaction = Transaction.objects.create(
                    user=user,
                    type='TRANSFER_IN',
                    amount=amount,
                    fee=Decimal('0.00'),
                    actual_amount=amount,
                    status='COMPLETED',
                    reference_id=str(uuid.uuid4()),
                    description=f'从{provider.name}转入',
                    metadata={
                        'provider_code': provider.code,
                        'provider_name': provider.name,
                        'wallet_id': str(wallet.id),
                    }
                )
                
                # 创建体育钱包交易记录
                sports_transaction = SportsWalletTransaction.objects.create(
                    user=user,
                    provider=provider,
                    wallet=wallet,
                    transaction_type='TRANSFER_OUT',
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=wallet.balance,
                    status='COMPLETED',
                    description=f'转出到主钱包',
                    metadata={
                        'main_transaction_id': str(main_transaction.id),
                    }
                )
                
                # 调用第三方平台API（如果需要）
                if provider.wallet_mode == 'TRANSFER':
                    api_result = SportsProviderService._call_platform_transfer_api(
                        provider, wallet, amount, 'OUT'
                    )
                    if not api_result['success']:
                        sports_transaction.remark = f"API调用失败: {api_result['message']}"
                        sports_transaction.save()
                
                return {
                    'success': True,
                    'message': '转出成功',
                    'data': {
                        'transaction_id': str(sports_transaction.id),
                        'amount': float(amount),
                        'wallet_balance': float(wallet.balance),
                        'main_balance': float(main_balance.get_available_balance()),
                    }
                }
                
        except Exception as e:
            logger.error(f"从体育平台转出失败: {str(e)}")
            return {'success': False, 'message': f'转出失败: {str(e)}'}
    
    @staticmethod
    def _call_platform_transfer_api(provider: SportsProvider, wallet: UserSportsWallet, 
                                  amount: Decimal, direction: str) -> Dict[str, Any]:
        """
        调用第三方平台转账API
        """
        try:
            # 这里应该根据不同平台调用相应的API
            # 由于是示例，我们模拟API调用
            
            api_data = {
                'user_id': wallet.platform_user_id,
                'amount': float(amount),
                'direction': direction,  # IN/OUT
                'transaction_id': str(uuid.uuid4()),
            }
            
            # 模拟API调用
            # response = requests.post(f"{provider.api_endpoint}/transfer", json=api_data)
            
            # 模拟成功响应
            logger.info(f"平台 {provider.name} 转账API调用成功: {direction} ₦{amount}")
            
            return {'success': True, 'message': 'API调用成功'}
            
        except Exception as e:
            logger.error(f"调用平台转账API失败: {str(e)}")
            return {'success': False, 'message': f'API调用失败: {str(e)}'}
    
    @staticmethod
    def get_launch_url(user, provider_code: str) -> Dict[str, Any]:
        """
        获取平台启动URL
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            if not provider.is_active:
                return {'success': False, 'message': '平台已停用'}
            
            if provider.is_maintenance:
                return {'success': False, 'message': '平台维护中'}
            
            # 确保用户有钱包
            wallet_result = SportsProviderService.get_user_wallet(user, provider_code)
            if not wallet_result['success']:
                return wallet_result
            
            wallet_data = wallet_result['data']
            
            # 生成启动URL
            if provider.integration_type == 'REDIRECT':
                # 跳转模式：生成带参数的URL
                launch_url = f"{provider.launch_url}?user_id={wallet_data['platform_user_id']}&token={SportsProviderService._generate_access_token(user, provider)}"
            elif provider.integration_type == 'IFRAME':
                # iframe模式：生成嵌入URL
                launch_url = f"{provider.launch_url}?embed=1&user_id={wallet_data['platform_user_id']}&token={SportsProviderService._generate_access_token(user, provider)}"
            else:
                # API模式：返回基础URL
                launch_url = provider.launch_url
            
            return {
                'success': True,
                'data': {
                    'launch_url': launch_url,
                    'integration_type': provider.integration_type,
                    'provider_name': provider.name,
                    'wallet_balance': wallet_data['balance'],
                }
            }
            
        except Exception as e:
            logger.error(f"获取启动URL失败: {str(e)}")
            return {'success': False, 'message': f'获取启动URL失败: {str(e)}'}
    
    @staticmethod
    def _generate_access_token(user, provider: SportsProvider) -> str:
        """
        生成访问令牌
        """
        import hashlib
        import time
        
        # 生成简单的访问令牌（实际应该使用JWT或其他安全方式）
        timestamp = str(int(time.time()))
        data = f"{user.id}_{provider.code}_{timestamp}_{provider.api_secret}"
        token = hashlib.md5(data.encode()).hexdigest()
        
        # 缓存令牌（1小时有效）
        cache_key = f"sports_token_{user.id}_{provider.code}"
        cache.set(cache_key, token, 3600)
        
        return token
    
    @staticmethod
    def get_user_wallets(user) -> List[Dict[str, Any]]:
        """
        获取用户所有体育钱包
        """
        try:
            wallets = UserSportsWallet.objects.filter(
                user=user, is_active=True
            ).select_related('provider').order_by('provider__sort_order')
            
            result = []
            for wallet in wallets:
                result.append({
                    'wallet_id': str(wallet.id),
                    'provider_code': wallet.provider.code,
                    'provider_name': wallet.provider.name,
                    'provider_logo': wallet.provider.logo.url if wallet.provider.logo else None,
                    'balance': float(wallet.balance),
                    'is_maintenance': wallet.provider.is_maintenance,
                    'last_sync_at': wallet.last_sync_at.isoformat() if wallet.last_sync_at else None,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户钱包列表失败: {str(e)}")
            return []
    
    @staticmethod
    def get_wallet_transactions(user, provider_code: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取钱包交易记录
        """
        try:
            queryset = SportsWalletTransaction.objects.filter(user=user)
            
            if provider_code:
                provider = SportsProviderService.get_provider_by_code(provider_code)
                if provider:
                    queryset = queryset.filter(provider=provider)
            
            transactions = queryset.select_related('provider').order_by('-created_at')[:limit]
            
            result = []
            for trans in transactions:
                result.append({
                    'transaction_id': str(trans.id),
                    'provider_name': trans.provider.name,
                    'transaction_type': trans.transaction_type,
                    'transaction_type_display': trans.get_transaction_type_display(),
                    'amount': float(trans.amount),
                    'balance_before': float(trans.balance_before),
                    'balance_after': float(trans.balance_after),
                    'status': trans.status,
                    'status_display': trans.get_status_display(),
                    'description': trans.description,
                    'created_at': trans.created_at.isoformat(),
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取钱包交易记录失败: {str(e)}")
            return []
    
    @staticmethod
    def auto_transfer_on_enter(user, provider_code: str, amount: Decimal = None) -> Dict[str, Any]:
        """
        进入平台时自动转账
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            config = getattr(provider, 'config', None)
            if not config or not config.auto_transfer:
                return {'success': True, 'message': '未启用自动转账'}
            
            # 如果没有指定金额，使用默认转账金额
            if amount is None:
                amount = config.min_transfer_amount * 5  # 默认转入最小金额的5倍
            
            # 检查用户主钱包余额
            try:
                main_balance = user.balance
                if main_balance.get_available_balance() < amount:
                    # 余额不足时转入所有可用余额
                    amount = main_balance.get_available_balance()
                    if amount < config.min_transfer_amount:
                        return {
                            'success': False,
                            'message': f'余额不足，至少需要 ₦{config.min_transfer_amount}'
                        }
            except UserBalance.DoesNotExist:
                return {'success': False, 'message': '用户余额信息不存在'}
            
            # 执行转账
            result = SportsProviderService.transfer_to_platform(user, provider_code, amount)
            
            if result['success']:
                logger.info(f"用户 {user.phone} 进入平台 {provider.name} 自动转账成功: ₦{amount}")
            
            return result
            
        except Exception as e:
            logger.error(f"自动转账失败: {str(e)}")
            return {'success': False, 'message': f'自动转账失败: {str(e)}'}
    
    @staticmethod
    def auto_transfer_on_exit(user, provider_code: str) -> Dict[str, Any]:
        """
        退出平台时自动回收余额
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            config = getattr(provider, 'config', None)
            if not config or not config.auto_transfer:
                return {'success': True, 'message': '未启用自动转账'}
            
            # 获取钱包余额
            try:
                wallet = UserSportsWallet.objects.get(user=user, provider=provider)
                if wallet.balance <= 0:
                    return {'success': True, 'message': '钱包余额为0，无需回收'}
            except UserSportsWallet.DoesNotExist:
                return {'success': True, 'message': '钱包不存在'}
            
            # 执行回收
            result = SportsProviderService.transfer_from_platform(user, provider_code)
            
            if result['success']:
                logger.info(f"用户 {user.phone} 退出平台 {provider.name} 自动回收成功: ₦{result['data']['amount']}")
            
            return result
            
        except Exception as e:
            logger.error(f"自动回收失败: {str(e)}")
            return {'success': False, 'message': f'自动回收失败: {str(e)}'}
    
    @staticmethod
    def batch_recover_all_wallets(user) -> Dict[str, Any]:
        """
        一键回收所有平台余额
        """
        try:
            wallets = UserSportsWallet.objects.filter(
                user=user, 
                is_active=True,
                balance__gt=0
            ).select_related('provider')
            
            if not wallets.exists():
                return {'success': True, 'message': '没有需要回收的余额'}
            
            results = []
            total_recovered = Decimal('0.00')
            success_count = 0
            
            for wallet in wallets:
                result = SportsProviderService.transfer_from_platform(
                    user, wallet.provider.code
                )
                
                if result['success']:
                    success_count += 1
                    total_recovered += Decimal(str(result['data']['amount']))
                
                results.append({
                    'provider_name': wallet.provider.name,
                    'provider_code': wallet.provider.code,
                    'amount': result['data']['amount'] if result['success'] else 0,
                    'success': result['success'],
                    'message': result['message']
                })
            
            return {
                'success': True,
                'message': f'批量回收完成，成功{success_count}/{len(wallets)}个平台',
                'data': {
                    'total_recovered': float(total_recovered),
                    'success_count': success_count,
                    'total_count': len(wallets),
                    'results': results
                }
            }
            
        except Exception as e:
            logger.error(f"批量回收失败: {str(e)}")
            return {'success': False, 'message': f'批量回收失败: {str(e)}'}
    
    @staticmethod
    def sync_bet_records_from_platform(provider_code: str, start_date=None, end_date=None) -> Dict[str, Any]:
        """
        从第三方平台同步投注记录
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            # 设置默认时间范围（最近7天）
            if not start_date:
                start_date = timezone.now() - timezone.timedelta(days=7)
            if not end_date:
                end_date = timezone.now()
            
            # 调用第三方平台API获取投注记录
            api_result = SportsProviderService._call_platform_bet_records_api(
                provider, start_date, end_date
            )
            
            if not api_result['success']:
                return api_result
            
            bet_records = api_result['data']
            synced_count = 0
            
            for record_data in bet_records:
                try:
                    # 检查记录是否已存在
                    existing_record = SportsBetRecord.objects.filter(
                        platform_bet_id=record_data['bet_id']
                    ).first()
                    
                    if existing_record:
                        # 更新现有记录
                        existing_record.status = record_data['status']
                        existing_record.actual_win = Decimal(str(record_data.get('actual_win', 0)))
                        existing_record.settle_time = record_data.get('settle_time')
                        existing_record.save()
                    else:
                        # 创建新记录
                        user = User.objects.get(id=record_data['user_id'])
                        
                        SportsBetRecord.objects.create(
                            user=user,
                            provider=provider,
                            platform_bet_id=record_data['bet_id'],
                            platform_user_id=record_data['platform_user_id'],
                            sport_type=record_data['sport_type'],
                            league=record_data.get('league', ''),
                            match_info=record_data.get('match_info', {}),
                            bet_type=record_data['bet_type'],
                            bet_details=record_data.get('bet_details', {}),
                            bet_amount=Decimal(str(record_data['bet_amount'])),
                            potential_win=Decimal(str(record_data.get('potential_win', 0))),
                            actual_win=Decimal(str(record_data.get('actual_win', 0))),
                            odds=Decimal(str(record_data.get('odds', 1.0))),
                            status=record_data['status'],
                            bet_time=record_data['bet_time'],
                            settle_time=record_data.get('settle_time'),
                            match_time=record_data.get('match_time'),
                        )
                    
                    synced_count += 1
                    
                except Exception as e:
                    logger.error(f"同步投注记录失败: {record_data.get('bet_id')} - {str(e)}")
                    continue
            
            return {
                'success': True,
                'message': f'同步完成，处理{synced_count}条记录',
                'data': {
                    'synced_count': synced_count,
                    'total_count': len(bet_records)
                }
            }
            
        except Exception as e:
            logger.error(f"同步投注记录失败: {str(e)}")
            return {'success': False, 'message': f'同步失败: {str(e)}'}
    
    @staticmethod
    def _call_platform_bet_records_api(provider: SportsProvider, start_date, end_date) -> Dict[str, Any]:
        """
        调用第三方平台投注记录API
        """
        try:
            # 这里应该根据不同平台调用相应的API
            # 由于是示例，我们模拟API调用和数据
            
            # 模拟投注记录数据
            mock_records = [
                {
                    'bet_id': f'BET_{provider.code}_001',
                    'user_id': '12345',
                    'platform_user_id': f'12345_{provider.code}',
                    'sport_type': '足球',
                    'league': '英超',
                    'match_info': {
                        'home_team': '曼联',
                        'away_team': '利物浦',
                        'match_date': '2025-01-21'
                    },
                    'bet_type': '胜负',
                    'bet_details': {
                        'selection': '主胜',
                        'odds': 2.5
                    },
                    'bet_amount': 100.00,
                    'potential_win': 250.00,
                    'actual_win': 0.00,
                    'odds': 2.5,
                    'status': 'LOST',
                    'bet_time': timezone.now() - timezone.timedelta(hours=2),
                    'settle_time': timezone.now() - timezone.timedelta(hours=1),
                    'match_time': timezone.now() - timezone.timedelta(hours=2),
                }
            ]
            
            logger.info(f"平台 {provider.name} 投注记录API调用成功，获取{len(mock_records)}条记录")
            
            return {
                'success': True,
                'data': mock_records
            }
            
        except Exception as e:
            logger.error(f"调用平台投注记录API失败: {str(e)}")
            return {'success': False, 'message': f'API调用失败: {str(e)}'}
    
    @staticmethod
    def get_aggregated_bet_records(user, provider_code: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取聚合的投注记录（包含所有平台）
        """
        try:
            queryset = SportsBetRecord.objects.filter(user=user)
            
            if provider_code:
                provider = SportsProviderService.get_provider_by_code(provider_code)
                if provider:
                    queryset = queryset.filter(provider=provider)
            
            records = queryset.select_related('provider').order_by('-bet_time')[:limit]
            
            result = []
            for record in records:
                result.append({
                    'bet_id': str(record.id),
                    'platform_bet_id': record.platform_bet_id,
                    'provider_name': record.provider.name,
                    'provider_code': record.provider.code,
                    'sport_type': record.sport_type,
                    'league': record.league,
                    'match_info': record.match_info,
                    'bet_type': record.bet_type,
                    'bet_details': record.bet_details,
                    'bet_amount': float(record.bet_amount),
                    'potential_win': float(record.potential_win),
                    'actual_win': float(record.actual_win),
                    'odds': float(record.odds),
                    'status': record.status,
                    'status_display': record.get_status_display(),
                    'profit_loss': float(record.get_profit_loss()),
                    'bet_time': record.bet_time.isoformat(),
                    'settle_time': record.settle_time.isoformat() if record.settle_time else None,
                    'match_time': record.match_time.isoformat() if record.match_time else None,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取聚合投注记录失败: {str(e)}")
            return []
    
    @staticmethod
    def get_user_sports_statistics(user) -> Dict[str, Any]:
        """
        获取用户体育博彩统计
        """
        try:
            # 投注统计
            bet_stats = SportsBetRecord.objects.filter(user=user).aggregate(
                total_bets=models.Count('id'),
                total_bet_amount=models.Sum('bet_amount'),
                total_win_amount=models.Sum('actual_win'),
                won_bets=models.Count('id', filter=models.Q(status='WON')),
            )
            
            # 钱包统计
            wallet_stats = SportsWalletTransaction.objects.filter(user=user).aggregate(
                total_transfer_in=models.Sum('amount', filter=models.Q(transaction_type='TRANSFER_IN')),
                total_transfer_out=models.Sum('amount', filter=models.Q(transaction_type='TRANSFER_OUT')),
            )
            
            # 计算统计数据
            total_bets = bet_stats['total_bets'] or 0
            total_bet_amount = bet_stats['total_bet_amount'] or Decimal('0.00')
            total_win_amount = bet_stats['total_win_amount'] or Decimal('0.00')
            won_bets = bet_stats['won_bets'] or 0
            
            win_rate = (won_bets / total_bets * 100) if total_bets > 0 else 0
            profit_loss = total_win_amount - total_bet_amount
            roi = (profit_loss / total_bet_amount * 100) if total_bet_amount > 0 else 0
            
            return {
                'betting_stats': {
                    'total_bets': total_bets,
                    'total_bet_amount': float(total_bet_amount),
                    'total_win_amount': float(total_win_amount),
                    'won_bets': won_bets,
                    'win_rate': round(win_rate, 2),
                    'profit_loss': float(profit_loss),
                    'roi': round(roi, 2),
                },
                'wallet_stats': {
                    'total_transfer_in': float(wallet_stats['total_transfer_in'] or 0),
                    'total_transfer_out': float(wallet_stats['total_transfer_out'] or 0),
                },
                'current_wallets': SportsProviderService.get_user_wallets(user)
            }
            
        except Exception as e:
            logger.error(f"获取用户体育统计失败: {str(e)}")
            return {
                'betting_stats': {
                    'total_bets': 0,
                    'total_bet_amount': 0,
                    'total_win_amount': 0,
                    'won_bets': 0,
                    'win_rate': 0,
                    'profit_loss': 0,
                    'roi': 0,
                },
                'wallet_stats': {
                    'total_transfer_in': 0,
                    'total_transfer_out': 0,
                },
                'current_wallets': []
            }
    
    @staticmethod
    def check_single_wallet_mode(provider_code: str) -> Dict[str, Any]:
        """
        检查是否支持单钱包模式
        """
        try:
            provider = SportsProviderService.get_provider_by_code(provider_code)
            if not provider:
                return {'success': False, 'message': '平台不存在'}
            
            return {
                'success': True,
                'data': {
                    'provider_name': provider.name,
                    'wallet_mode': provider.wallet_mode,
                    'supports_single_wallet': provider.wallet_mode == 'SINGLE',
                    'integration_type': provider.integration_type,
                }
            }
            
        except Exception as e:
            logger.error(f"检查单钱包模式失败: {str(e)}")
            return {'success': False, 'message': f'检查失败: {str(e)}'}