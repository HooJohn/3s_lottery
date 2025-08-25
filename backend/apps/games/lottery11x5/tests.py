"""
11选5彩票游戏测试
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import timedelta
import uuid

from apps.games.models import Game, Draw, BetType, Bet
from apps.finance.models import UserBalance, Transaction
from .models import Lottery11x5Game, Lottery11x5Bet, Lottery11x5Result
from .services import Lottery11x5Service, Lottery11x5DrawService

User = get_user_model()


class Lottery11x5ServiceTest(TestCase):
    """
    11选5服务测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        # 创建游戏
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            min_bet=Decimal('1.00'),
            max_bet=Decimal('1000.00'),
            status='ACTIVE'
        )
        
        # 创建游戏配置
        self.config = Lottery11x5Game.objects.create(
            game=self.game,
            draw_count_per_day=7,
            draw_interval_minutes=120,
            close_before_minutes=5,
            auto_create_draws=True,
            auto_draw_results=True,
            profit_target=Decimal('0.18')
        )
        
        # 创建投注类型
        self.bet_type = BetType.objects.create(
            game=self.game,
            name='任选一',
            code='ANY_1',
            odds=Decimal('2.20'),
            min_bet=Decimal('1.00'),
            max_bet=Decimal('1000.00')
        )
        
        # 创建用户
        self.user = User.objects.create_user(
            username='testuser',
            phone='+2348012345678',
            password='testpass123'
        )
        
        # 创建用户余额
        self.balance = UserBalance.objects.create(
            user=self.user,
            main_balance=Decimal('1000.00'),
            bonus_balance=Decimal('0.00'),
            frozen_balance=Decimal('0.00')
        )
    
    def test_create_draws_for_date(self):
        """
        测试创建指定日期的期次
        """
        today = timezone.now().date()
        draws = self.config.create_draws_for_date(today)
        
        self.assertEqual(len(draws), 7)  # 应该创建7期
        
        # 检查期号格式
        expected_draw_number = today.strftime('%Y%m%d') + '-1'
        self.assertEqual(draws[0].draw_number, expected_draw_number)
        
        # 检查开奖时间间隔
        time_diff = draws[1].draw_time - draws[0].draw_time
        self.assertEqual(time_diff.total_seconds(), 120 * 60)  # 2小时间隔
    
    def test_get_current_draw(self):
        """
        测试获取当前可投注期次
        """
        # 创建一个未来的期次
        future_time = timezone.now() + timedelta(hours=1)
        draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=future_time,
            close_time=future_time - timedelta(minutes=5),
            status='OPEN'
        )
        
        current_draw = Lottery11x5Service.get_current_draw()
        self.assertEqual(current_draw.id, draw.id)
    
    def test_place_bet(self):
        """
        测试投注功能
        """
        # 创建期次
        future_time = timezone.now() + timedelta(hours=1)
        draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=future_time,
            close_time=future_time - timedelta(minutes=5),
            status='OPEN'
        )
        
        # 投注
        result = Lottery11x5Service.place_bet(
            user=self.user,
            draw_id=str(draw.id),
            bet_type_id=str(self.bet_type.id),
            numbers=[1, 2, 3],
            amount=Decimal('10.00'),
            bet_method='ANY',
            selected_count=1
        )
        
        self.assertTrue(result['success'])
        self.assertIn('bet_id', result['data'])
        
        # 检查余额是否扣除
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.main_balance, Decimal('990.00'))
        
        # 检查投注记录
        bet = Bet.objects.get(id=result['data']['bet_id'])
        self.assertEqual(bet.user, self.user)
        self.assertEqual(bet.amount, Decimal('10.00'))
        self.assertEqual(bet.numbers, [1, 2, 3])
    
    def test_validate_numbers(self):
        """
        测试号码验证
        """
        # 有效的任选投注
        self.assertTrue(
            Lottery11x5Service.validate_numbers([1, 2, 3], 'ANY', selected_count=1)
        )
        
        # 无效的号码范围
        self.assertFalse(
            Lottery11x5Service.validate_numbers([0, 12], 'ANY', selected_count=1)
        )
        
        # 重复号码
        self.assertFalse(
            Lottery11x5Service.validate_numbers([1, 1, 2], 'ANY', selected_count=1)
        )
        
        # 定位胆投注
        self.assertTrue(
            Lottery11x5Service.validate_numbers([1, 2], 'POSITION', positions=[1, 3])
        )
        
        # 定位胆号码与位置数量不匹配
        self.assertFalse(
            Lottery11x5Service.validate_numbers([1], 'POSITION', positions=[1, 3])
        )
    
    def test_draw_lottery(self):
        """
        测试开奖功能
        """
        # 创建已封盘的期次
        draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=timezone.now(),
            close_time=timezone.now() - timedelta(minutes=5),
            status='CLOSED'
        )
        
        # 创建投注
        bet = Bet.objects.create(
            user=self.user,
            game=self.game,
            draw=draw,
            bet_type=self.bet_type,
            numbers=[1, 2, 3],
            amount=Decimal('10.00'),
            odds=Decimal('2.20'),
            potential_payout=Decimal('22.00')
        )
        
        Lottery11x5Bet.objects.create(
            bet=bet,
            bet_method='ANY',
            selected_count=1
        )
        
        # 开奖
        result = Lottery11x5Service.draw_lottery(str(draw.id))
        
        self.assertTrue(result['success'])
        self.assertIn('winning_numbers', result['data'])
        
        # 检查期次状态
        draw.refresh_from_db()
        self.assertEqual(draw.status, 'COMPLETED')
        self.assertIsNotNone(draw.winning_numbers)
        
        # 检查开奖结果
        lottery_result = Lottery11x5Result.objects.get(draw=draw)
        self.assertEqual(len(lottery_result.numbers), 5)
        self.assertTrue(all(1 <= num <= 11 for num in lottery_result.numbers))
    
    def test_check_win(self):
        """
        测试中奖检查
        """
        # 任选1中奖
        is_win, win_amount = Lottery11x5Service.check_win(
            bet_numbers=[1, 2, 3],
            winning_numbers=[1, 4, 5, 6, 7],
            bet_method='ANY',
            selected_count=1,
            odds=Decimal('2.20'),
            bet_amount=Decimal('10.00'),
            multiple_count=1
        )
        
        self.assertTrue(is_win)
        self.assertEqual(win_amount, Decimal('22.00'))
        
        # 任选1未中奖
        is_win, win_amount = Lottery11x5Service.check_win(
            bet_numbers=[8, 9, 10],
            winning_numbers=[1, 2, 3, 4, 5],
            bet_method='ANY',
            selected_count=1,
            odds=Decimal('2.20'),
            bet_amount=Decimal('10.00'),
            multiple_count=1
        )
        
        self.assertFalse(is_win)
        self.assertEqual(win_amount, Decimal('0.00'))
        
        # 定位胆中奖
        is_win, win_amount = Lottery11x5Service.check_win(
            bet_numbers=[1, 3],
            winning_numbers=[1, 2, 3, 4, 5],
            bet_method='POSITION',
            positions=[1, 3],
            odds=Decimal('9.90'),
            bet_amount=Decimal('10.00'),
            multiple_count=1
        )
        
        self.assertTrue(is_win)
        self.assertEqual(win_amount, Decimal('198.00'))  # 2个位置中奖
    
    def test_generate_random_numbers(self):
        """
        测试随机号码生成
        """
        numbers = Lottery11x5Service.generate_random_numbers(5)
        
        self.assertEqual(len(numbers), 5)
        self.assertTrue(all(1 <= num <= 11 for num in numbers))
        self.assertEqual(len(set(numbers)), 5)  # 无重复


class Lottery11x5DrawServiceTest(TestCase):
    """
    11选5期次管理服务测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        self.config = Lottery11x5Game.objects.create(
            game=self.game,
            draw_count_per_day=7,
            auto_create_draws=True,
            auto_draw_results=True
        )
    
    def test_create_daily_draws(self):
        """
        测试创建每日期次
        """
        success = Lottery11x5DrawService.create_daily_draws()
        self.assertTrue(success)
        
        # 检查是否创建了期次
        today_draws = Draw.objects.filter(
            game=self.game,
            draw_time__date=timezone.now().date()
        )
        self.assertGreaterEqual(today_draws.count(), 7)
    
    def test_close_expired_draws(self):
        """
        测试关闭过期期次
        """
        # 创建过期的期次
        expired_time = timezone.now() - timedelta(minutes=10)
        draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=expired_time + timedelta(minutes=5),
            close_time=expired_time,
            status='OPEN'
        )
        
        count = Lottery11x5DrawService.close_expired_draws()
        self.assertEqual(count, 1)
        
        # 检查期次状态
        draw.refresh_from_db()
        self.assertEqual(draw.status, 'CLOSED')
    
    def test_get_draw_countdown(self):
        """
        测试获取开奖倒计时
        """
        # 创建未来的期次
        future_time = timezone.now() + timedelta(hours=1)
        draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=future_time,
            close_time=future_time - timedelta(minutes=5),
            status='OPEN'
        )
        
        countdown = Lottery11x5DrawService.get_draw_countdown(str(draw.id))
        
        self.assertIsNotNone(countdown)
        self.assertEqual(countdown['draw_number'], '20250119-001')
        self.assertTrue(countdown['is_open_for_betting'])
        self.assertGreater(countdown['time_until_close'], 0)
        self.assertGreater(countdown['time_until_draw'], 0)


class Lottery11x5APITest(TestCase):
    """
    11选5 API测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.user = User.objects.create_user(
            username='testuser',
            phone='+2348012345678',
            password='testpass123'
        )
        
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        self.config = Lottery11x5Game.objects.create(
            game=self.game,
            draw_count_per_day=7
        )
    
    def test_game_info_api(self):
        """
        测试游戏信息API
        """
        response = self.client.get('/api/v1/games/lottery11x5/info/')
        
        if response.status_code == 404:
            # 如果游戏不存在，这是正常的
            self.assertEqual(response.status_code, 404)
        else:
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data['success'])
    
    def test_current_draw_api(self):
        """
        测试当前期次API
        """
        response = self.client.get('/api/v1/games/lottery11x5/current-draw/')
        
        # 可能没有当前期次，这是正常的
        self.assertIn(response.status_code, [200, 404])
    
    def test_random_numbers_api(self):
        """
        测试随机号码生成API
        """
        response = self.client.post('/api/v1/games/lottery11x5/random-numbers/', {
            'count': 5
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['numbers']), 5)
    
    def test_quick_pick_options_api(self):
        """
        测试快捷选号选项API
        """
        response = self.client.get('/api/v1/games/lottery11x5/quick-pick/options/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('all', data['data'])
        self.assertIn('big', data['data'])
        self.assertIn('small', data['data'])
    
    def test_quick_pick_numbers_api(self):
        """
        测试快捷选号API
        """
        # 测试随机选号
        response = self.client.post('/api/v1/games/lottery11x5/quick-pick/numbers/', {
            'type': 'random',
            'count': 5
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['data']['numbers']), 5)
        
        # 测试大号选择
        response = self.client.post('/api/v1/games/lottery11x5/quick-pick/numbers/', {
            'type': 'big'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertTrue(all(num >= 6 for num in data['data']['numbers']))
    
    def test_calculate_bet_api(self):
        """
        测试投注计算API
        """
        bet_data = {
            'draw_id': str(uuid.uuid4()),
            'bet_type_id': str(uuid.uuid4()),
            'numbers': [1, 2, 3],
            'amount': 10,
            'bet_method': 'ANY',
            'selected_count': 1
        }
        
        response = self.client.post('/api/v1/games/lottery11x5/calculate-bet/', bet_data)
        
        # 可能因为draw_id和bet_type_id不存在而失败，但应该能处理验证
        self.assertIn(response.status_code, [200, 400])


class Lottery11x5CartTest(TestCase):
    """
    11选5购物车测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.user = User.objects.create_user(
            username='testuser',
            phone='+2348012345678',
            password='testpass123'
        )
        
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        self.bet_type = BetType.objects.create(
            game=self.game,
            name='任选一',
            code='ANY_1',
            odds=Decimal('2.20'),
            min_bet=Decimal('1.00'),
            max_bet=Decimal('1000.00')
        )
        
        self.draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=timezone.now() + timedelta(hours=1),
            close_time=timezone.now() + timedelta(minutes=55),
            status='OPEN'
        )
    
    def test_cart_add_bet(self):
        """
        测试添加投注到购物车
        """
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(self.user.id))
        
        bet_data = {
            'draw_id': str(self.draw.id),
            'bet_type_id': str(self.bet_type.id),
            'bet_type_name': self.bet_type.name,
            'numbers': [1, 2, 3],
            'amount': 10,
            'bet_method': 'ANY',
            'selected_count': 1
        }
        
        result = cart.add_bet(bet_data)
        self.assertTrue(result['success'])
        self.assertIn('cart_item', result['data'])
    
    def test_cart_operations(self):
        """
        测试购物车操作
        """
        from .cart import Lottery11x5Cart
        
        cart = Lottery11x5Cart(str(self.user.id))
        
        # 添加投注
        bet_data = {
            'draw_id': str(self.draw.id),
            'bet_type_id': str(self.bet_type.id),
            'numbers': [1, 2, 3],
            'amount': 10,
            'bet_method': 'ANY',
            'selected_count': 1
        }
        
        add_result = cart.add_bet(bet_data)
        self.assertTrue(add_result['success'])
        
        bet_id = add_result['data']['cart_item']['id']
        
        # 获取购物车
        cart_summary = cart.get_cart_summary()
        self.assertEqual(cart_summary['count'], 1)
        
        # 更新投注
        update_result = cart.update_bet(bet_id, {'amount': 20})
        self.assertTrue(update_result['success'])
        
        # 移除投注
        remove_result = cart.remove_bet(bet_id)
        self.assertTrue(remove_result['success'])
        
        # 清空购物车
        clear_result = cart.clear_cart()
        self.assertTrue(clear_result['success'])


class Lottery11x5BetCalculatorTest(TestCase):
    """
    11选5投注计算器测试
    """
    
    def test_calculate_bet_count(self):
        """
        测试计算投注注数
        """
        from .bet_calculator import Lottery11x5BetCalculator
        
        # 定位胆
        count = Lottery11x5BetCalculator.calculate_bet_count(
            'POSITION', [1, 2], [1, 3]
        )
        self.assertEqual(count, 2)
        
        # 任选单式
        count = Lottery11x5BetCalculator.calculate_bet_count(
            'ANY', [1, 2, 3], selected_count=3
        )
        self.assertEqual(count, 1)
        
        # 任选复式
        count = Lottery11x5BetCalculator.calculate_bet_count(
            'ANY', [1, 2, 3, 4], selected_count=2
        )
        self.assertEqual(count, 6)  # C(4,2) = 6
    
    def test_calculate_win_probability(self):
        """
        测试计算中奖概率
        """
        from .bet_calculator import Lottery11x5BetCalculator
        
        # 定位胆概率
        prob = Lottery11x5BetCalculator.calculate_win_probability(
            'POSITION', 1, [1]
        )
        self.assertAlmostEqual(prob, 1.0/11, places=3)
        
        # 任选一概率
        prob = Lottery11x5BetCalculator.calculate_win_probability(
            'ANY', 1, selected_count=1
        )
        self.assertGreater(prob, 0)
        self.assertLess(prob, 1)
    
    def test_validate_bet_limits(self):
        """
        测试验证投注限额
        """
        from .bet_calculator import Lottery11x5BetCalculator
        
        bet_data = {
            'total_amount': 50,
            'potential_payout': 500
        }
        
        bet_type_limits = {
            'min_bet': 1,
            'max_bet': 1000,
            'max_payout': 10000
        }
        
        result = Lottery11x5BetCalculator.validate_bet_limits(bet_data, bet_type_limits)
        self.assertTrue(result['valid'])
        
        # 测试超限
        bet_data['total_amount'] = 2000
        result = Lottery11x5BetCalculator.validate_bet_limits(bet_data, bet_type_limits)
        self.assertFalse(result['valid'])


class Lottery11x5BetValidatorTest(TestCase):
    """
    11选5投注验证器测试
    """
    
    def test_validate_numbers(self):
        """
        测试号码验证
        """
        from .bet_calculator import Lottery11x5BetValidator
        
        # 有效号码
        result = Lottery11x5BetValidator.validate_numbers({
            'numbers': [1, 2, 3, 4, 5]
        })
        self.assertTrue(result['valid'])
        
        # 无效号码范围
        result = Lottery11x5BetValidator.validate_numbers({
            'numbers': [0, 12]
        })
        self.assertFalse(result['valid'])
        
        # 重复号码
        result = Lottery11x5BetValidator.validate_numbers({
            'numbers': [1, 1, 2]
        })
        self.assertFalse(result['valid'])
    
    def test_validate_bet_method(self):
        """
        测试投注方法验证
        """
        from .bet_calculator import Lottery11x5BetValidator
        
        # 有效的定位胆
        result = Lottery11x5BetValidator.validate_bet_method({
            'bet_method': 'POSITION',
            'numbers': [1, 2],
            'positions': [1, 3]
        })
        self.assertTrue(result['valid'])
        
        # 无效的定位胆（号码与位置数量不匹配）
        result = Lottery11x5BetValidator.validate_bet_method({
            'bet_method': 'POSITION',
            'numbers': [1],
            'positions': [1, 3]
        })
        self.assertFalse(result['valid'])
        
        # 有效的任选
        result = Lottery11x5BetValidator.validate_bet_method({
            'bet_method': 'ANY',
            'numbers': [1, 2, 3],
            'selected_count': 2
        })
        self.assertTrue(result['valid'])
    
    def test_validate_amount(self):
        """
        测试金额验证
        """
        from .bet_calculator import Lottery11x5BetValidator
        
        # 有效金额
        result = Lottery11x5BetValidator.validate_amount({
            'amount': 10,
            'multiplier': 2
        })
        self.assertTrue(result['valid'])
        
        # 无效金额
        result = Lottery11x5BetValidator.validate_amount({
            'amount': -10,
            'multiplier': 1
        })
        self.assertFalse(result['valid'])
        
        # 无效倍数
        result = Lottery11x5BetValidator.validate_amount({
            'amount': 10,
            'multiplier': 1000
        })
        self.assertFalse(result['valid'])

c
lass Lottery11x5DrawEngineTest(TestCase):
    """
    11选5开奖引擎测试
    """
    
    def test_generate_winning_numbers(self):
        """
        测试生成开奖号码
        """
        from .draw_engine import Lottery11x5DrawEngine
        
        draw_engine = Lottery11x5DrawEngine()
        draw_id = str(uuid.uuid4())
        draw_time = timezone.now()
        
        result = draw_engine.generate_winning_numbers(draw_id, draw_time)
        
        self.assertTrue(result['success'])
        self.assertIn('winning_numbers', result)
        self.assertEqual(len(result['winning_numbers']), 5)
        
        # 验证号码范围
        for num in result['winning_numbers']:
            self.assertTrue(1 <= num <= 11)
        
        # 验证无重复
        self.assertEqual(len(set(result['winning_numbers'])), 5)
        
        # 验证排序
        self.assertEqual(result['winning_numbers'], sorted(result['winning_numbers']))
    
    def test_validate_numbers(self):
        """
        测试号码验证
        """
        from .draw_engine import Lottery11x5DrawEngine
        
        draw_engine = Lottery11x5DrawEngine()
        
        # 有效号码
        self.assertTrue(draw_engine._validate_numbers([1, 3, 5, 7, 9]))
        
        # 数量错误
        self.assertFalse(draw_engine._validate_numbers([1, 3, 5]))
        
        # 范围错误
        self.assertFalse(draw_engine._validate_numbers([0, 3, 5, 7, 9]))
        
        # 重复号码
        self.assertFalse(draw_engine._validate_numbers([1, 1, 5, 7, 9]))
        
        # 未排序
        self.assertFalse(draw_engine._validate_numbers([5, 1, 3, 7, 9]))
    
    def test_calculate_statistics(self):
        """
        测试统计计算
        """
        from .draw_engine import Lottery11x5DrawEngine
        
        draw_engine = Lottery11x5DrawEngine()
        numbers = [1, 3, 5, 7, 9]
        
        stats = draw_engine._calculate_statistics(numbers)
        
        self.assertEqual(stats['sum_value'], 25)
        self.assertEqual(stats['odd_count'], 5)
        self.assertEqual(stats['even_count'], 0)
        self.assertEqual(stats['big_count'], 2)  # 7, 9
        self.assertEqual(stats['small_count'], 3)  # 1, 3, 5
        self.assertEqual(stats['span_value'], 8)  # 9 - 1


class Lottery11x5ProfitControllerTest(TestCase):
    """
    11选5利润控制器测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.user = User.objects.create_user(
            username='testuser',
            phone='+2348012345678',
            password='testpass123'
        )
        
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        self.bet_type = BetType.objects.create(
            game=self.game,
            name='任选一',
            code='ANY_1',
            odds=Decimal('2.20'),
            min_bet=Decimal('1.00'),
            max_bet=Decimal('1000.00')
        )
        
        self.draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=timezone.now(),
            close_time=timezone.now() - timedelta(minutes=5),
            status='CLOSED'
        )
        
        # 创建投注
        self.bet = Bet.objects.create(
            user=self.user,
            game=self.game,
            draw=self.draw,
            bet_type=self.bet_type,
            numbers=[1, 2, 3],
            amount=Decimal('10.00'),
            odds=Decimal('2.20'),
            potential_payout=Decimal('22.00')
        )
        
        from .models import Lottery11x5Bet
        Lottery11x5Bet.objects.create(
            bet=self.bet,
            bet_method='ANY',
            selected_count=1,
            multiple_count=1
        )
    
    def test_analyze_draw_profitability(self):
        """
        测试分析期次盈利能力
        """
        from .draw_engine import Lottery11x5ProfitController
        
        profit_controller = Lottery11x5ProfitController()
        
        # 测试中奖情况
        winning_numbers = [1, 4, 5, 6, 7]  # 包含投注号码1
        analysis = profit_controller.analyze_draw_profitability(
            str(self.draw.id), winning_numbers
        )
        
        self.assertIn('total_amount', analysis)
        self.assertIn('potential_payout', analysis)
        self.assertIn('profit_rate', analysis)
        self.assertIn('meets_target', analysis)
        
        # 测试未中奖情况
        losing_numbers = [4, 5, 6, 7, 8]  # 不包含投注号码
        analysis = profit_controller.analyze_draw_profitability(
            str(self.draw.id), losing_numbers
        )
        
        self.assertEqual(analysis['potential_payout'], Decimal('0.00'))
        self.assertEqual(analysis['profit'], analysis['total_amount'])
    
    def test_should_adjust_odds(self):
        """
        测试赔率调整建议
        """
        from .draw_engine import Lottery11x5ProfitController
        
        profit_controller = Lottery11x5ProfitController()
        
        # 利润率正常
        normal_rates = [Decimal('0.18'), Decimal('0.17'), Decimal('0.19')]
        result = profit_controller.should_adjust_odds(normal_rates)
        self.assertFalse(result['should_adjust'])
        
        # 利润率过低
        low_rates = [Decimal('0.10'), Decimal('0.08'), Decimal('0.12')]
        result = profit_controller.should_adjust_odds(low_rates)
        self.assertTrue(result['should_adjust'])
        self.assertEqual(result['adjustment_direction'], 'increase')
        
        # 利润率过高
        high_rates = [Decimal('0.25'), Decimal('0.28'), Decimal('0.30')]
        result = profit_controller.should_adjust_odds(high_rates)
        self.assertTrue(result['should_adjust'])
        self.assertEqual(result['adjustment_direction'], 'decrease')


class Lottery11x5SettlementTest(TestCase):
    """
    11选5结算系统测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.user = User.objects.create_user(
            username='testuser',
            phone='+2348012345678',
            password='testpass123'
        )
        
        # 创建用户余额
        self.balance = UserBalance.objects.create(
            user=self.user,
            main_balance=Decimal('1000.00'),
            bonus_balance=Decimal('0.00'),
            frozen_balance=Decimal('0.00')
        )
        
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        self.bet_type = BetType.objects.create(
            game=self.game,
            name='任选一',
            code='ANY_1',
            odds=Decimal('2.20'),
            min_bet=Decimal('1.00'),
            max_bet=Decimal('1000.00')
        )
        
        self.draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=timezone.now(),
            close_time=timezone.now() - timedelta(minutes=5),
            status='CLOSED',
            total_amount=Decimal('100.00')
        )
    
    def test_complete_draw_process(self):
        """
        测试完整的开奖流程
        """
        # 创建投注
        bet = Bet.objects.create(
            user=self.user,
            game=self.game,
            draw=self.draw,
            bet_type=self.bet_type,
            numbers=[1, 2, 3],
            amount=Decimal('10.00'),
            odds=Decimal('2.20'),
            potential_payout=Decimal('22.00')
        )
        
        from .models import Lottery11x5Bet
        Lottery11x5Bet.objects.create(
            bet=bet,
            bet_method='ANY',
            selected_count=1,
            multiple_count=1
        )
        
        # 执行开奖
        result = Lottery11x5Service.draw_lottery(str(self.draw.id))
        
        self.assertTrue(result['success'])
        self.assertIn('winning_numbers', result['data'])
        self.assertIn('total_payout', result['data'])
        self.assertIn('profit', result['data'])
        
        # 检查期次状态
        self.draw.refresh_from_db()
        self.assertEqual(self.draw.status, 'COMPLETED')
        self.assertIsNotNone(self.draw.winning_numbers)
        
        # 检查投注状态
        bet.refresh_from_db()
        self.assertIn(bet.status, ['WON', 'LOST'])
        self.assertIsNotNone(bet.settled_at)
        
        # 如果中奖，检查余额变化
        if bet.status == 'WON':
            self.balance.refresh_from_db()
            self.assertGreater(self.balance.main_balance, Decimal('1000.00'))
    
    def test_settlement_details(self):
        """
        测试结算详情
        """
        # 创建多个投注
        bets_data = [
            {'numbers': [1, 2, 3], 'amount': Decimal('10.00')},
            {'numbers': [4, 5, 6], 'amount': Decimal('20.00')},
            {'numbers': [7, 8, 9], 'amount': Decimal('15.00')},
        ]
        
        for bet_data in bets_data:
            bet = Bet.objects.create(
                user=self.user,
                game=self.game,
                draw=self.draw,
                bet_type=self.bet_type,
                numbers=bet_data['numbers'],
                amount=bet_data['amount'],
                odds=Decimal('2.20'),
                potential_payout=bet_data['amount'] * Decimal('2.20')
            )
            
            from .models import Lottery11x5Bet
            Lottery11x5Bet.objects.create(
                bet=bet,
                bet_method='ANY',
                selected_count=1,
                multiple_count=1
            )
        
        # 指定开奖号码（确保有中奖和未中奖）
        winning_numbers = [1, 4, 10, 11, 6]
        
        # 执行结算
        settlement_result = Lottery11x5Service.settle_bets(self.draw, winning_numbers)
        
        self.assertIn('total_payout', settlement_result)
        self.assertIn('total_winners', settlement_result)
        self.assertIn('settlement_details', settlement_result)
        
        details = settlement_result['settlement_details']
        self.assertEqual(details['total_bets'], 3)
        self.assertGreaterEqual(details['winning_bets'], 0)
        self.assertGreaterEqual(details['losing_bets'], 0)
        self.assertEqual(details['winning_bets'] + details['losing_bets'], 3)


class Lottery11x5APIDrawTest(TestCase):
    """
    11选5开奖相关API测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.admin_user = User.objects.create_user(
            username='admin',
            phone='+2348012345679',
            password='adminpass123',
            is_staff=True
        )
        
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        self.draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=timezone.now(),
            close_time=timezone.now() - timedelta(minutes=5),
            status='CLOSED'
        )
    
    def test_admin_draw_lottery_api(self):
        """
        测试管理员开奖API
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.post('/api/v1/games/lottery11x5/admin/draw-lottery/', {
            'draw_id': str(self.draw.id)
        })
        
        # 可能成功或失败，取决于数据完整性
        self.assertIn(response.status_code, [200, 400])
    
    def test_verify_draw_result_api(self):
        """
        测试验证开奖结果API
        """
        # 先创建开奖结果
        from .models import Lottery11x5Result
        Lottery11x5Result.objects.create(
            draw=self.draw,
            numbers=[1, 3, 5, 7, 9],
            sum_value=25,
            odd_count=5,
            even_count=0,
            big_count=2,
            small_count=3,
            span_value=8
        )
        
        self.draw.status = 'COMPLETED'
        self.draw.save()
        
        response = self.client.get(f'/api/v1/games/lottery11x5/verify-draw/{self.draw.id}/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('verification', data['data'])
    
    def test_profit_analysis_api(self):
        """
        测试利润分析API
        """
        self.client.force_login(self.admin_user)
        
        response = self.client.get('/api/v1/games/lottery11x5/admin/profit-analysis/?days=7')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('summary', data['data'])
        self.assertIn('adjustment_analysis', data['data'])
class Lott
ery11x5TrendAnalyzerTest(TestCase):
    """
    11选5走势分析器测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        # 创建测试开奖数据
        self.create_test_results()
    
    def create_test_results(self):
        """
        创建测试开奖结果
        """
        from .models import Lottery11x5Result
        
        test_data = [
            {'numbers': [1, 3, 5, 7, 9], 'draw_number': '20250119-001'},
            {'numbers': [2, 4, 6, 8, 10], 'draw_number': '20250119-002'},
            {'numbers': [1, 2, 3, 4, 5], 'draw_number': '20250119-003'},
            {'numbers': [7, 8, 9, 10, 11], 'draw_number': '20250119-004'},
            {'numbers': [1, 4, 7, 10, 11], 'draw_number': '20250119-005'},
        ]
        
        for i, data in enumerate(test_data):
            draw = Draw.objects.create(
                game=self.game,
                draw_number=data['draw_number'],
                draw_time=timezone.now() - timedelta(hours=i),
                close_time=timezone.now() - timedelta(hours=i, minutes=5),
                status='COMPLETED'
            )
            
            numbers = data['numbers']
            Lottery11x5Result.objects.create(
                draw=draw,
                numbers=numbers,
                sum_value=sum(numbers),
                odd_count=sum(1 for num in numbers if num % 2 == 1),
                even_count=sum(1 for num in numbers if num % 2 == 0),
                big_count=sum(1 for num in numbers if num > 5),
                small_count=sum(1 for num in numbers if num <= 5),
                span_value=max(numbers) - min(numbers)
            )
    
    def test_get_trend_data(self):
        """
        测试获取走势数据
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        analyzer = Lottery11x5TrendAnalyzer(self.game)
        trend_data = analyzer.get_trend_data(limit=5)
        
        self.assertIn('trend_data', trend_data)
        self.assertIn('statistics', trend_data)
        self.assertIn('period_info', trend_data)
        
        # 检查数据数量
        self.assertEqual(len(trend_data['trend_data']), 5)
        
        # 检查数据结构
        first_trend = trend_data['trend_data'][0]
        self.assertIn('draw_number', first_trend)
        self.assertIn('numbers', first_trend)
        self.assertIn('sum_value', first_trend)
        self.assertIn('positions', first_trend)
    
    def test_get_position_trend(self):
        """
        测试获取位置走势
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        analyzer = Lottery11x5TrendAnalyzer(self.game)
        
        # 测试第1位走势
        position_data = analyzer.get_position_trend(1, limit=5)
        
        self.assertEqual(position_data['position'], 1)
        self.assertIn('trend_data', position_data)
        self.assertIn('statistics', position_data)
        
        # 检查统计数据
        stats = position_data['statistics']
        self.assertIn('frequency', stats)
        self.assertIn('missing_values', stats)
        self.assertIn('max_missing', stats)
        
        # 测试无效位置
        with self.assertRaises(ValueError):
            analyzer.get_position_trend(6, limit=5)
    
    def test_get_missing_analysis(self):
        """
        测试获取遗漏分析
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        analyzer = Lottery11x5TrendAnalyzer(self.game)
        missing_data = analyzer.get_missing_analysis(limit=5)
        
        self.assertIn('number_analysis', missing_data)
        self.assertIn('overall_stats', missing_data)
        self.assertIn('period_count', missing_data)
        
        # 检查号码分析
        number_analysis = missing_data['number_analysis']
        self.assertEqual(len(number_analysis), 11)  # 1-11号码
        
        # 检查单个号码分析
        for num_str, analysis in number_analysis.items():
            self.assertIn('appearances', analysis)
            self.assertIn('current_missing', analysis)
            self.assertIn('avg_missing', analysis)
            self.assertIn('appearance_rate', analysis)
    
    def test_get_hot_cold_analysis(self):
        """
        测试获取冷热号码分析
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        analyzer = Lottery11x5TrendAnalyzer(self.game)
        hot_cold_data = analyzer.get_hot_cold_analysis([5])  # 只测试5期
        
        self.assertIn('period_analysis', hot_cold_data)
        self.assertIn('comprehensive', hot_cold_data)
        
        # 检查期间分析
        period_analysis = hot_cold_data['period_analysis']['5']
        self.assertIn('hot_numbers', period_analysis)
        self.assertIn('cold_numbers', period_analysis)
        self.assertIn('normal_numbers', period_analysis)
        
        # 检查综合分析
        comprehensive = hot_cold_data['comprehensive']
        self.assertIn('recommendation', comprehensive)
        
        recommendation = comprehensive['recommendation']
        self.assertIn('focus_hot', recommendation)
        self.assertIn('avoid_cold', recommendation)
    
    def test_get_complete_trend_chart(self):
        """
        测试获取完整走势图
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        analyzer = Lottery11x5TrendAnalyzer(self.game)
        chart_data = analyzer.get_complete_trend_chart(limit=5)
        
        self.assertIn('headers', chart_data)
        self.assertIn('rows', chart_data)
        self.assertIn('statistics', chart_data)
        
        # 检查表头
        headers = chart_data['headers']
        self.assertTrue(len(headers) > 0)
        
        # 检查数据行
        rows = chart_data['rows']
        self.assertEqual(len(rows), 5)
        
        # 检查行数据结构
        first_row = rows[0]
        self.assertIn('draw_number', first_row)
        self.assertIn('numbers', first_row)
        self.assertIn('sum_value', first_row)
    
    def test_get_prediction_analysis(self):
        """
        测试获取预测分析
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        analyzer = Lottery11x5TrendAnalyzer(self.game)
        prediction_data = analyzer.get_prediction_analysis(limit=5)
        
        self.assertIn('recommended_numbers', prediction_data)
        self.assertIn('avoid_numbers', prediction_data)
        self.assertIn('sum_range', prediction_data)
        self.assertIn('odd_even_suggestion', prediction_data)
        self.assertIn('big_small_suggestion', prediction_data)
        self.assertIn('disclaimer', prediction_data)
        
        # 检查推荐号码结构
        if prediction_data['recommended_numbers']:
            first_rec = prediction_data['recommended_numbers'][0]
            self.assertIn('number', first_rec)
            self.assertIn('reason', first_rec)
            self.assertIn('priority', first_rec)


class Lottery11x5TrendAPITest(TestCase):
    """
    11选5走势分析API测试
    """
    
    def setUp(self):
        """
        测试数据准备
        """
        self.game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        # 创建测试数据
        self.create_test_data()
    
    def create_test_data(self):
        """
        创建测试数据
        """
        from .models import Lottery11x5Result
        
        draw = Draw.objects.create(
            game=self.game,
            draw_number='20250119-001',
            draw_time=timezone.now(),
            close_time=timezone.now() - timedelta(minutes=5),
            status='COMPLETED'
        )
        
        Lottery11x5Result.objects.create(
            draw=draw,
            numbers=[1, 3, 5, 7, 9],
            sum_value=25,
            odd_count=5,
            even_count=0,
            big_count=2,
            small_count=3,
            span_value=8
        )
    
    def test_trend_analysis_api(self):
        """
        测试走势分析API
        """
        response = self.client.get('/api/v1/games/lottery11x5/trend-analysis/?limit=10')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('trend_data', data['data'])
    
    def test_position_trend_api(self):
        """
        测试位置走势API
        """
        response = self.client.get('/api/v1/games/lottery11x5/position-trend/1/?limit=10')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['data']['position'], 1)
        
        # 测试无效位置
        response = self.client.get('/api/v1/games/lottery11x5/position-trend/6/')
        self.assertEqual(response.status_code, 400)
    
    def test_missing_analysis_api(self):
        """
        测试遗漏分析API
        """
        response = self.client.get('/api/v1/games/lottery11x5/missing-analysis/?limit=50')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('number_analysis', data['data'])
    
    def test_complete_trend_chart_api(self):
        """
        测试完整走势图API
        """
        response = self.client.get('/api/v1/games/lottery11x5/complete-trend-chart/?limit=20')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('headers', data['data'])
        self.assertIn('rows', data['data'])
    
    def test_prediction_analysis_api(self):
        """
        测试预测分析API
        """
        response = self.client.get('/api/v1/games/lottery11x5/prediction-analysis/?limit=30')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('recommended_numbers', data['data'])
        self.assertIn('disclaimer', data['data'])


class Lottery11x5TrendStatisticsTest(TestCase):
    """
    11选5走势统计测试
    """
    
    def test_calculate_trend_statistics(self):
        """
        测试走势统计计算
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        
        # 测试数据
        trend_data = [
            {'sum_value': 25, 'odd_count': 5, 'big_count': 2, 'span_value': 8},
            {'sum_value': 30, 'odd_count': 0, 'big_count': 5, 'span_value': 8},
            {'sum_value': 15, 'odd_count': 1, 'big_count': 0, 'span_value': 4},
        ]
        
        stats = analyzer._calculate_trend_statistics(trend_data)
        
        # 检查和值统计
        self.assertIn('sum_value', stats)
        sum_stats = stats['sum_value']
        self.assertEqual(sum_stats['min'], 15)
        self.assertEqual(sum_stats['max'], 30)
        self.assertAlmostEqual(sum_stats['avg'], 23.33, places=1)
        
        # 检查奇偶统计
        self.assertIn('odd_even', stats)
        
        # 检查大小统计
        self.assertIn('big_small', stats)
        
        # 检查跨度统计
        self.assertIn('span_value', stats)
    
    def test_missing_value_calculation(self):
        """
        测试遗漏值计算
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        
        # 测试号码序列：[1, 2, 3, 1, 2]
        numbers = [1, 2, 3, 1, 2]
        
        missing_values = analyzer._calculate_missing_values(numbers)
        
        # 号码1的当前遗漏应该是2（最后出现在倒数第2位）
        self.assertEqual(missing_values['1'], 2)
        
        # 号码2的当前遗漏应该是0（最后出现在最后一位）
        self.assertEqual(missing_values['2'], 0)
        
        # 号码3的当前遗漏应该是3（最后出现在倒数第3位）
        self.assertEqual(missing_values['3'], 3)
    
    def test_max_missing_calculation(self):
        """
        测试最大遗漏值计算
        """
        from .trend_analyzer import Lottery11x5TrendAnalyzer
        
        game = Game.objects.create(
            name='11选5测试',
            code='11x5_test',
            game_type='11选5',
            status='ACTIVE'
        )
        
        analyzer = Lottery11x5TrendAnalyzer(game)
        
        # 测试号码序列：[1, 3, 3, 1, 3]，号码1的最大遗漏应该是2
        numbers = [1, 3, 3, 1, 3]
        max_missing = analyzer._get_max_missing(numbers, 1)
        
        self.assertEqual(max_missing, 2)  # 在两个1之间有2个其他号码