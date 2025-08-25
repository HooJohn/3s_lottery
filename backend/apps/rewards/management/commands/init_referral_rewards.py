"""
初始化推荐奖励配置
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from apps.rewards.models import ReferralReward


class Command(BaseCommand):
    help = '初始化推荐奖励配置'

    def handle(self, *args, **options):
        """
        创建7级推荐奖励配置
        一级3%、二级2%、三级1%、四级0.7%、五级0.5%、六级0.3%、七级0.1%
        """
        
        # 推荐奖励配置数据
        referral_rewards = [
            {
                'level': 1,
                'reward_rate': Decimal('0.03'),  # 3%
                'name': '一级推荐',
                'description': '直接推荐用户，获得其有效流水的3%奖励'
            },
            {
                'level': 2,
                'reward_rate': Decimal('0.02'),  # 2%
                'name': '二级推荐',
                'description': '二级推荐用户，获得其有效流水的2%奖励'
            },
            {
                'level': 3,
                'reward_rate': Decimal('0.01'),  # 1%
                'name': '三级推荐',
                'description': '三级推荐用户，获得其有效流水的1%奖励'
            },
            {
                'level': 4,
                'reward_rate': Decimal('0.007'),  # 0.7%
                'name': '四级推荐',
                'description': '四级推荐用户，获得其有效流水的0.7%奖励'
            },
            {
                'level': 5,
                'reward_rate': Decimal('0.005'),  # 0.5%
                'name': '五级推荐',
                'description': '五级推荐用户，获得其有效流水的0.5%奖励'
            },
            {
                'level': 6,
                'reward_rate': Decimal('0.003'),  # 0.3%
                'name': '六级推荐',
                'description': '六级推荐用户，获得其有效流水的0.3%奖励'
            },
            {
                'level': 7,
                'reward_rate': Decimal('0.001'),  # 0.1%
                'name': '七级推荐',
                'description': '七级推荐用户，获得其有效流水的0.1%奖励'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for reward_data in referral_rewards:
            reward, created = ReferralReward.objects.update_or_create(
                level=reward_data['level'],
                defaults={
                    'reward_rate': reward_data['reward_rate'],
                    'name': reward_data['name'],
                    'description': reward_data['description'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建推荐奖励配置: L{reward.level} - {reward.name} ({reward.get_reward_percentage()}%)')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新推荐奖励配置: L{reward.level} - {reward.name} ({reward.get_reward_percentage()}%)')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n推荐奖励配置初始化完成！'
                f'\n创建: {created_count}个配置'
                f'\n更新: {updated_count}个配置'
                f'\n总奖励率: {sum([float(r["reward_rate"]) for r in referral_rewards]) * 100:.1f}%'
            )
        )
        
        # 显示配置摘要
        self.stdout.write('\n=== 推荐奖励配置摘要 ===')
        for reward in ReferralReward.objects.all().order_by('level'):
            self.stdout.write(f'L{reward.level}: {reward.name} - {reward.get_reward_percentage()}% - {reward.description}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n总推荐奖励率: {sum([float(r.reward_rate) for r in ReferralReward.objects.all()]) * 100:.1f}%'
                f'\n配合VIP返水系统，总奖励率最高可达8.4% (0.8%返水 + 7.6%推荐)'
            )
        )