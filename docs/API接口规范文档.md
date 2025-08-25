# 非洲在线彩票博彩产品 API接口规范文档

## 文档概述

### 版本信息
- **API版本**: v1.0
- **文档版本**: 1.0.0
- **最后更新**: 2025-07-30
- **基础URL**: `https://api.lottery-africa.com/api/v1`

### 产品定位
- **目标市场**: 尼日利亚、喀麦隆等非洲英语区国家
- **产品类型**: 合规在线彩票和博彩综合平台
- **支持平台**: PC端 + 移动端(响应式设计)
- **核心货币**: 尼日利亚奈拉(NGN)，（暂时不支持虚拟货币）
- **核心特色**: 11选5彩票（核心） + "666"刮刮乐 + 大乐透 + 欧洲在线体育彩票 + 统一返水系统

### 技术架构
- **后端框架**: Python Django 4.2+ / Django REST Framework
- **异步处理**: Django Channels + Celery + Redis
- **数据库**: PostgreSQL (主库) + Redis (缓存/会话/队列)
- **认证方式**: Django Auth + JWT + 双因子认证
- **响应格式**: JSON
- **支持规模**: 10万+ 并发用户

## 统一响应格式

### 成功响应
```json
{
  "success": true,
  "code": 200,
  "message": "操作成功",
  "data": {
    // 具体数据内容
  },
  "timestamp": 1640995200000
}
```

### 错误响应
```json
{
  "success": false,
  "code": 4001,
  "message": "余额不足",
  "data": null,
  "timestamp": 1640995200000
}
```

### HTTP状态码规范
- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器内部错误

## 错误码规范

### 通用错误码 (1000-1999)
- `1001` - 参数错误
- `1002` - 未授权访问
- `1003` - 禁止访问
- `1004` - 资源不存在

### 用户相关错误码 (2000-2999)
- `2001` - 用户不存在
- `2002` - 用户名或密码错误
- `2003` - 账户已被锁定
- `2004` - 手机号已存在
- `2005` - 邮箱已存在

### 财务相关错误码 (3000-3999)
- `3001` - 余额不足
- `3002` - 金额无效
- `3003` - 支付失败
- `3004` - 超出提款限额
- `3005` - 银行账户未验证

### 游戏相关错误码 (4000-4999)
- `4001` - 游戏不可用
- `4002` - 投注金额超限
- `4003` - 投注已截止
- `4004` - 号码选择无效
- `4005` - 卡片已刮开

### 奖励相关错误码 (5000-5999)
- `5001` - 奖励已领取
- `5002` - VIP等级不足

## 1. 用户认证模块

### 1.1 用户注册
**接口地址**: `POST /auth/register`

**请求参数**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "phone": "+2348012345678",
  "password": "password123",
  "country": "NG",
  "referral_code": "ABC12345"
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 201,
  "message": "注册成功",
  "data": {
    "user": {
      "id": "uuid-string",
      "username": "testuser",
      "phone": "+2348012345678",
      "referral_code": "XYZ98765"
    },
    "tokens": {
      "access": "jwt-access-token",
      "refresh": "jwt-refresh-token"
    }
  }
}
```

### 1.2 用户登录
**接口地址**: `POST /auth/login`

**请求参数**:
```json
{
  "identifier": "testuser", // 用户名/邮箱/手机号
  "password": "password123",
  "captcha": "1234"
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "message": "登录成功",
  "data": {
    "user": {
      "id": "uuid-string",
      "username": "testuser",
      "phone": "+2348012345678",
      "vip_level": 1
    },
    "tokens": {
      "access": "jwt-access-token",
      "refresh": "jwt-refresh-token"
    }
  }
}
```

### 1.3 刷新Token
**接口地址**: `POST /auth/refresh`

**请求参数**:
```json
{
  "refresh": "jwt-refresh-token"
}
```

### 1.4 用户登出
**接口地址**: `POST /auth/logout`

**请求头**: `Authorization: Bearer {access_token}`

## 2. 用户管理模块

### 2.1 获取用户资料
**接口地址**: `GET /users/profile`

**请求头**: `Authorization: Bearer {access_token}`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "id": "uuid-string",
    "username": "testuser",
    "email": "test@example.com",
    "phone": "+2348012345678",
    "full_name": "Test User",
    "country": "NG",
    "vip_level": 1,
    "total_turnover": "50000.00",
    "referral_code": "XYZ98765",
    "kyc_status": "APPROVED"
  }
}
```

### 2.2 更新用户资料
**接口地址**: `PUT /users/profile`

**请求参数**:
```json
{
  "full_name": "Updated Name",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "address": "Lagos, Nigeria"
}
```

## 3. 财务管理模块

### 3.1 获取账户余额
**接口地址**: `GET /finance/balance`

**请求头**: `Authorization: Bearer {access_token}`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "main_balance": "1500.00",
    "bonus_balance": "200.00",
    "frozen_balance": "0.00",
    "total_balance": "1700.00",
    "currency": "NGN"
  }
}
```

### 3.2 创建存款请求
**接口地址**: `POST /finance/deposit`

**请求参数**:
```json
{
  "method": "bank_transfer", // bank_transfer, mobile_money, payment_gateway
  "amount": "1000.00",
  "currency": "NGN",
  "payment_details": {
    "bank_name": "GTBank",
    "account_number": "0123456789"
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 201,
  "message": "存款请求已创建",
  "data": {
    "transaction_id": "uuid-string",
    "status": "PENDING",
    "payment_instructions": {
      "recipient_bank": "GTBank",
      "recipient_account": "0987654321",
      "recipient_name": "Lottery Platform Ltd",
      "reference": "DEP123456789",
      "amount": "1000.00",
      "note": "请在转账备注中填写参考号码"
    }
  }
}
```

### 3.3 创建提款请求
**接口地址**: `POST /finance/withdraw`

**请求参数**:
```json
{
  "method": "bank", // bank, mobile_money
  "amount": "500.00",
  "currency": "NGN",
  "destination": {
    "bank_account_id": "uuid-string"
  },
  "withdrawal_password": "password123",
  "verification_code": "123456"
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 201,
  "message": "提款请求已提交",
  "data": {
    "transaction_id": "uuid-string",
    "status": "PENDING",
    "processing_time": "1-3个工作日",
    "fee": "10.00",
    "net_amount": "490.00"
  }
}
```

### 3.4 获取交易记录
**接口地址**: `GET /finance/transactions`

**查询参数**:
- `type`: 交易类型 (DEPOSIT, WITHDRAWAL, BET, WIN, REBATE)
- `status`: 状态 (PENDING, COMPLETED, FAILED)
- `start_date`: 开始日期 (YYYY-MM-DD)
- `end_date`: 结束日期 (YYYY-MM-DD)
- `page`: 页码 (默认1)
- `limit`: 每页数量 (默认20)

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "transactions": [
      {
        "id": "uuid-string",
        "type": "DEPOSIT",
        "amount": "1000.00",
        "currency": "NGN",
        "status": "COMPLETED",
        "method": "bank_transfer",
        "reference": "DEP123456789",
        "description": "银行转账存款",
        "created_at": "2025-01-19T10:00:00Z",
        "completed_at": "2025-01-19T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "pages": 3
    }
  }
}
```

### 3.5 银行账户管理
**接口地址**: `GET /finance/bank-accounts` (获取列表)
**接口地址**: `POST /finance/bank-accounts` (添加账户)

**添加银行账户请求参数**:
```json
{
  "bank_name": "GTBank",
  "account_name": "Test User",
  "account_number": "0123456789"
}
```

## 4. 11选5彩票模块 (核心功能)

### 4.1 获取当前期次
**接口地址**: `GET /games/11choose5/current-draw`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "draw_id": "uuid-string",
    "draw_number": "20250119-001",
    "draw_time": "2025-01-19T14:00:00Z",
    "close_time": "2025-01-19T13:55:00Z",
    "status": "OPEN",
    "remaining_time": 3300 // 剩余秒数
  }
}
```

### 4.2 投注11选5（核心功能）
**接口地址**: `POST /games/11choose5/place-bet`

**请求参数**:
```json
{
  "draw_id": "uuid-string",
  "bets": [
    {
      "type": "FIXED_POSITION", // 定位胆玩法
      "position": 1, // 定位胆位置 (1-5)
      "numbers": [1, 5, 8],
      "amount": "10.00",
      "multiplier": 2
    },
    {
      "type": "ANY_SELECT", // 任选玩法
      "select_count": 3, // 任选三中三
      "numbers": [2, 6, 9],
      "amount": "20.00",
      "multiplier": 1
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 201,
  "message": "投注成功",
  "data": {
    "bet_records": [
      "uuid-string-1",
      "uuid-string-2"
    ],
    "total_amount": "60.00",
    "draw_number": "20250119-001"
  }
}
```

### 4.3 获取投注历史
**接口地址**: `GET /games/11choose5/bet-history`

**查询参数**:
- `draw_number`: 期号
- `status`: 状态 (PENDING, WIN, LOSE)
- `start_date`: 开始日期
- `end_date`: 结束日期
- `page`: 页码
- `limit`: 每页数量

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "bets": [
      {
        "id": "uuid-string",
        "draw_number": "20250119-001",
        "bet_type": "FIXED_POSITION",
        "position": 1,
        "numbers": [1, 5, 8],
        "amount": "20.00",
        "multiplier": 2,
        "potential_win": "400.00",
        "actual_win": "0.00",
        "status": "LOSE",
        "created_at": "2025-01-19T13:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### 4.4 获取11选5走势分析（核心功能）
**接口地址**: `GET /games/11choose5/trend-analysis`

**查询参数**:
- `periods`: 期数 (30, 50, 100)
- `type`: 分析类型 (position, hot_cold)

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "periods": 50,
    "draws": [
      {
        "draw_number": "20250119-001",
        "winning_numbers": [3, 7, 11, 15, 22],
        "positions": {
          "1": {"number": 3, "miss_count": 0},
          "2": {"number": 7, "miss_count": 2},
          "3": {"number": 11, "miss_count": 1},
          "4": {"number": 15, "miss_count": 5},
          "5": {"number": 22, "miss_count": 3}
        }
      }
    ],
    "hot_numbers": [3, 7, 11],
    "cold_numbers": [1, 9, 20]
  }
}
```

## 5. 大乐透彩票模块

### 5.1 获取当前期次
**接口地址**: `GET /games/super-lotto/current-draw`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "draw_id": "uuid-string",
    "draw_number": "25008",
    "draw_time": "2025-01-22T21:30:00Z",
    "close_time": "2025-01-22T20:00:00Z",
    "jackpot": "50000000.00",
    "sales_amount": "25000000.00",
    "status": "OPEN"
  }
}
```

### 5.2 投注大乐透
**接口地址**: `POST /games/super-lotto/place-bet`

**请求参数**:
```json
{
  "draw_id": "uuid-string",
  "bets": [
    {
      "bet_type": "SINGLE", // SINGLE, MULTIPLE, COMPOUND
      "front_numbers": [5, 12, 18, 25, 33], // 前区5个号码
      "back_numbers": [3, 8], // 后区2个号码
      "amount": "2.00",
      "multiplier": 5
    }
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 201,
  "message": "投注成功",
  "data": {
    "bet_records": ["uuid-string"],
    "total_amount": "10.00",
    "draw_number": "25008"
  }
}
```

### 5.3 获取开奖结果
**接口地址**: `GET /games/super-lotto/results`

**查询参数**:
- `draw_number`: 期号
- `limit`: 获取最近几期 (默认10)

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "results": [
      {
        "draw_number": "25007",
        "draw_time": "2025-01-19T21:30:00Z",
        "front_numbers": [7, 14, 21, 28, 35],
        "back_numbers": [5, 11],
        "jackpot": "45000000.00",
        "prize_breakdown": [
          {
            "level": 1,
            "name": "一等奖",
            "winners": 2,
            "prize_per_winner": "22500000.00"
          },
          {
            "level": 2,
            "name": "二等奖",
            "winners": 15,
            "prize_per_winner": "180000.00"
          }
        ]
      }
    ]
  }
}
```

## 6. 刮刮乐模块

### 6.1 购买刮刮乐
**接口地址**: `POST /games/scratch/purchase`

**请求参数**:
```json
{
  "card_type": "666",
  "quantity": 5,
  "auto_scratch": true
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 201,
  "message": "购买成功",
  "data": {
    "cards": [
      {
        "id": "uuid-string",
        "is_scratched": true,
        "winnings": "50.00"
      }
    ],
    "total_cost": "500.00",
    "total_winnings": "150.00"
  }
}
```

### 6.2 刮开卡片
**接口地址**: `POST /games/scratch/reveal`

**请求参数**:
```json
{
  "card_id": "uuid-string",
  "area_ids": ["area-1", "area-2"] // 可选，不传则全部刮开
}
```

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "message": "刮奖完成",
  "data": {
    "card": {
      "id": "uuid-string",
      "areas": [
        {
          "id": "area-1",
          "symbol": "666",
          "base_amount": "100.00",
          "multiplier": 3,
          "win_amount": "300.00"
        }
      ],
      "total_winnings": "300.00",
      "is_scratched": true
    }
  }
}
```

## 7. 统一返水奖励系统（整合个人返水和推荐奖励）

### 7.1 获取VIP状态和奖励概览（基于充值+流水）
**接口地址**: `GET /rewards/vip-status`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "current_level": 2,
    "total_deposit": "25000.00",
    "next_level_deposit": "50000.00",
    "deposit_progress": 50,
    "current_turnover": "75000.00",
    "next_level_turnover": "100000.00",
    "turnover_progress": 75,
    "rebate_rate": "0.0045",
    "referral_depth": 3,
    "referral_rates": [0.03, 0.02, 0.01], // 7级递减比例：一级3%，二级2%，三级1%
    "withdrawal_fee_rate": "0.01",
    "daily_withdraw_limit": "200000.00",
    "daily_withdraw_times": 8,
    "total_rebate_earned": "1250.00",
    "referral_code": "XYZ98765",
    "direct_referrals": 8,
    "total_team_size": 25,
    "total_referral_earned": "850.00",
    "upgrade_requirement": {
      "needs_deposit": true,
      "needs_turnover": false,
      "missing_deposit": "25000.00",
      "missing_turnover": "0.00"
    },
    "privileges": [
      "日提款次数: 8次",
      "每日提款额度: ₦200,000",
      "提现手续费: 1%",
      "推荐层级: 3级",
      "专属客服",
      "周返水",
      "月礼金"
    ]
  }
}
```

### 7.2 获取奖励记录
**接口地址**: `GET /rewards/records`

**查询参数**:
- `period`: 周期 (daily, weekly, monthly)
- `type`: 类型 (REBATE, REFERRAL, ALL)
- `start_date`: 开始日期
- `end_date`: 结束日期

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "current_period": {
      "period_date": "2025-01-19",
      "personal_rebate_amount": "45.50",
      "referral_bonus_amount": "28.30",
      "total_reward_amount": "73.80",
      "status": "PENDING"
    },
    "recent_rewards": [
      {
        "period_date": "2025-01-18",
        "personal_turnover": "5000.00",
        "personal_rebate_rate": "0.0045",
        "personal_rebate_amount": "22.50",
        "referral_turnover": "3000.00",
        "referral_bonus_amount": "15.00",
        "total_reward_amount": "37.50",
        "status": "PAID",
        "paid_at": "2025-01-19T09:00:00Z"
      }
    ]
  }
}
```

### 7.3 获取推荐团队（基于VIP等级的一对一映射）
**接口地址**: `GET /rewards/referral-team`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "referral_code": "XYZ98765",
    "share_url": "https://lottery-africa.com/register?ref=XYZ98765",
    "vip_level": 2,
    "referral_depth": 3,
    "referral_rates": [0.03, 0.02, 0.01], // 7级递减比例：一级3%，二级2%，三级1%
    "team_summary": {
      "total_team_size": 25,
      "active_levels": 3,
      "total_contribution": "35000.00",
      "total_earned": "700.00"
    },
    "team_levels": [
      {
        "level": 1,
        "description": "一级推荐（VIP2可获得）",
        "count": 8,
        "total_contribution": "15000.00",
        "commission_rate": "0.02",
        "earned": "300.00"
      },
      {
        "level": 2,
        "description": "二级推荐（VIP2可获得）",
        "count": 12,
        "total_contribution": "12000.00",
        "commission_rate": "0.02",
        "earned": "240.00"
      },
      {
        "level": 3,
        "description": "三级推荐（VIP2可获得）",
        "count": 5,
        "total_contribution": "8000.00",
        "commission_rate": "0.02",
        "earned": "160.00"
      }
    ],
    "upgrade_benefit": {
      "next_vip_level": 3,
      "additional_depth": 1,
      "potential_earnings": "预计增加收益: 基于4级推荐"
    }
  }
}
```

## 8. 体育博彩模块

### 8.1 获取体育平台列表
**接口地址**: `GET /sports/providers`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "providers": [
      {
        "id": "nuxgame-sports",
        "name": "NuxGame Sports",
        "logo": "https://cdn.example.com/nuxgame-logo.png",
        "description": "欧洲顶级体育博彩平台",
        "is_active": true,
        "is_maintenance": false,
        "features": ["足球", "篮球", "网球", "电竞"],
        "entry_url": "https://sports.lottery-africa.com/nuxgame"
      }
    ],
    "user_balance": {
      "main_wallet": "1500.00",
      "sports_wallets": {
        "nuxgame-sports": "200.00"
      }
    }
  }
}
```

### 8.2 钱包转账
**接口地址**: `POST /sports/wallet-transfer`

**请求参数**:
```json
{
  "from_wallet": "MAIN", // MAIN, SPORTS
  "to_wallet": "SPORTS",
  "amount": "500.00",
  "provider_id": "nuxgame-sports"
}
```

## 9. 系统配置模块

### 9.1 获取系统配置
**接口地址**: `GET /system/config`

**响应示例**:
```json
{
  "success": true,
  "code": 200,
  "data": {
    "app_version": "1.0.0",
    "maintenance_mode": false,
    "supported_currencies": ["NGN"],
    "min_deposit": "100.00",
    "max_deposit": "1000000.00",
    "min_withdrawal": "500.00",
    "max_withdrawal": "500000.00",
    "lottery_draw_times": [
      "09:00", "11:00", "13:00", "15:00", "17:00", "19:00", "21:00"
    ]
  }
}
```

## 10. WebSocket实时通信

### 10.1 连接地址
`wss://api.lottery-africa.com/ws/`

### 10.2 认证
连接时需要在URL中传递token参数：
`wss://api.lottery-africa.com/ws/?token={access_token}`

### 10.3 消息格式

#### 开奖结果推送
```json
{
  "type": "lottery_result",
  "data": {
    "game_type": "11选5",
    "draw_number": "20250119-001",
    "winning_numbers": [3, 7, 11, 15, 22],
    "draw_time": "2025-01-19T14:00:00Z"
  }
}
```

#### 余额变动通知
```json
{
  "type": "balance_update",
  "data": {
    "main_balance": "1650.00",
    "bonus_balance": "200.00",
    "total_balance": "1850.00",
    "change_amount": "150.00",
    "change_type": "WIN",
    "description": "11选5中奖"
  }
}
```

#### 系统通知
```json
{
  "type": "system_notification",
  "data": {
    "title": "系统维护通知",
    "message": "系统将于今晚23:00-01:00进行维护",
    "level": "INFO", // INFO, WARNING, ERROR
    "timestamp": "2025-01-19T15:00:00Z"
  }
}
```

## 11. 安全规范

### 11.1 请求签名
对于敏感操作（存款、提款、投注），需要在请求头中添加签名：
```
X-Signature: sha256_hash_of_request_body_with_secret
```

### 11.2 频率限制
- 登录接口：每分钟最多5次
- 投注接口：每秒最多2次
- 查询接口：每秒最多10次

### 11.3 IP白名单
生产环境建议配置IP白名单，限制API访问来源。

## 12. 测试环境

### 12.1 测试地址
- **基础URL**: `https://api-test.lottery-africa.com/api/v1`
- **WebSocket**: `wss://api-test.lottery-africa.com/ws/`

### 12.2 测试账户
- **用户名**: `testuser`
- **密码**: `test123456`
- **手机号**: `+2348000000001`

### 12.3 测试数据
测试环境会定期重置数据，请勿用于生产用途。

---

**文档维护**: 本文档将随着API的更新而持续维护，请关注版本变更。
**技术支持**: 如有疑问，请联系技术团队。