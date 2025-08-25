"""
初始化支付方式数据
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.finance.models import PaymentMethod


class Command(BaseCommand):
    help = '初始化支付方式配置数据'
    
    def handle(self, *args, **options):
        self.stdout.write('开始初始化支付方式数据...')
        
        # 支付方式配置数据
        payment_methods_data = [
            {
                'name': 'Paystack支付',
                'method_type': 'PAYMENT_GATEWAY',
                'provider': 'PAYSTACK',
                'min_amount': Decimal('100.00'),
                'max_amount': Decimal('1000000.00'),
                'daily_limit': Decimal('5000000.00'),
                'fee_type': 'PERCENTAGE',
                'fee_value': Decimal('0.00'),  # 存款免手续费
                'is_active': True,
                'is_deposit_enabled': True,
                'is_withdraw_enabled': False,
                'config': {
                    'description': '支持银行卡、USSD、银行转账等多种支付方式',
                    'supported_banks': ['所有尼日利亚银行'],
                    'processing_time': '即时到账'
                }
            },
            {
                'name': 'Flutterwave支付',
                'method_type': 'PAYMENT_GATEWAY',
                'provider': 'FLUTTERWAVE',
                'min_amount': Decimal('100.00'),
                'max_amount': Decimal('1000000.00'),
                'daily_limit': Decimal('5000000.00'),
                'fee_type': 'PERCENTAGE',
                'fee_value': Decimal('0.00'),  # 存款免手续费
                'is_active': True,
                'is_deposit_enabled': True,
                'is_withdraw_enabled': False,
                'config': {
                    'description': '支持银行卡、移动货币、银行转账等',
                    'supported_networks': ['MTN', 'Airtel', 'Glo', '9mobile'],
                    'processing_time': '即时到账'
                }
            },
            {
                'name': 'OPay钱包',
                'method_type': 'MOBILE_MONEY',
                'provider': 'OPAY',
                'min_amount': Decimal('50.00'),
                'max_amount': Decimal('500000.00'),
                'daily_limit': Decimal('2000000.00'),
                'fee_type': 'PERCENTAGE',
                'fee_value': Decimal('0.00'),  # 存款免手续费
                'is_active': True,
                'is_deposit_enabled': True,
                'is_withdraw_enabled': True,
                'config': {
                    'description': 'OPay移动钱包快速支付',
                    'features': ['即时到账', '24/7可用', '安全可靠'],
                    'processing_time': '即时到账'
                }
            },
            {
                'name': 'PalmPay钱包',
                'method_type': 'MOBILE_MONEY',
                'provider': 'PALMPAY',
                'min_amount': Decimal('50.00'),
                'max_amount': Decimal('500000.00'),
                'daily_limit': Decimal('2000000.00'),
                'fee_type': 'PERCENTAGE',
                'fee_value': Decimal('0.00'),  # 存款免手续费
                'is_active': True,
                'is_deposit_enabled': True,
                'is_withdraw_enabled': True,
                'config': {
                    'description': 'PalmPay移动钱包便捷支付',
                    'features': ['快速转账', '低手续费', '安全保障'],
                    'processing_time': '即时到账'
                }
            },
            {
                'name': 'Moniepoint支付',
                'method_type': 'MOBILE_MONEY',
                'provider': 'MONIEPOINT',
                'min_amount': Decimal('100.00'),
                'max_amount': Decimal('1000000.00'),
                'daily_limit': Decimal('3000000.00'),
                'fee_type': 'PERCENTAGE',
                'fee_value': Decimal('0.00'),  # 存款免手续费
                'is_active': True,
                'is_deposit_enabled': True,
                'is_withdraw_enabled': True,
                'config': {
                    'description': 'Moniepoint代理网络支付',
                    'features': ['覆盖全国', '代理网点多', '可靠稳定'],
                    'processing_time': '即时到账'
                }
            },
            {
                'name': '银行转账',
                'method_type': 'BANK_TRANSFER',
                'provider': 'MANUAL',
                'min_amount': Decimal('500.00'),
                'max_amount': Decimal('10000000.00'),
                'daily_limit': Decimal('50000000.00'),
                'fee_type': 'PERCENTAGE',
                'fee_value': Decimal('0.00'),  # 存款免手续费
                'is_active': True,
                'is_deposit_enabled': True,
                'is_withdraw_enabled': False,
                'config': {
                    'description': '直接银行转账，适合大额存款',
                    'features': ['无手续费', '大额支持', '安全可靠'],
                    'processing_time': '1-3个工作日',
                    'instructions': '请在转账备注中填写您的交易参考号'
                }
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for method_data in payment_methods_data:
            payment_method, created = PaymentMethod.objects.get_or_create(
                name=method_data['name'],
                provider=method_data['provider'],
                defaults=method_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建支付方式: {payment_method.name}')
                )
            else:
                # 更新现有记录
                for key, value in method_data.items():
                    if key not in ['name', 'provider']:
                        setattr(payment_method, key, value)
                payment_method.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新支付方式: {payment_method.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'支付方式初始化完成！创建: {created_count}, 更新: {updated_count}'
            )
        )