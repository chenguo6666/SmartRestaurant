# 🍽️ 智能餐厅系统 (SmartRestaurant)

[![Version](https://img.shields.io/badge/version-v1.0.0-brightgreen.svg)](https://github.com/chenguo6666/SmartRestaurant)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://djangoproject.com/)
[![WeChat MiniProgram](https://img.shields.io/badge/WeChat-MiniProgram-blue.svg)](https://developers.weixin.qq.com/miniprogram/dev/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> 🚀 **一套完整的餐厅数字化解决方案**  
> 基于Django 5.2 + 微信小程序构建的现代化智能餐厅管理系统

## 📋 项目概述

智能餐厅系统是一个功能完善的餐厅数字化平台，包含：
- 🔧 **Django后端**: RESTful API、数据库管理、业务逻辑
- 📱 **微信小程序**: 用户点餐、购物车、订单管理
- 💳 **支付集成**: 微信支付接口预留
- 🎫 **优惠券系统**: 完整的营销工具

## ✨ 主要功能

### 🛍️ 顾客端功能
- [x] 餐厅首页展示
- [x] 菜品分类浏览
- [x] 菜品搜索筛选
- [x] 购物车管理
- [x] 订单结算
- [x] 优惠券使用
- [ ] 微信登录
- [ ] 订单查询
- [ ] 评价反馈

### 🔧 后端管理
- [x] 用户管理系统
- [x] 菜品分类管理
- [x] 菜品信息管理
- [x] 订单处理系统
- [x] 优惠券管理
- [x] 库存管理
- [ ] 数据统计分析
- [ ] 管理员后台

## 🛠️ 技术栈

| 类型 | 技术选型 |
|------|----------|
| **后端框架** | Django 5.2 + Django REST Framework |
| **数据库** | MySQL 8.0+ |
| **缓存** | Redis |
| **前端** | 微信小程序原生开发 |
| **认证** | JWT + 微信小程序登录 |
| **支付** | 微信支付 |
| **部署** | Docker / 云服务器 |

## 🚀 快速开始

### 环境要求
- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- 微信开发者工具

### 1. 克隆项目
```bash
git clone https://github.com/chenguo6666/SmartRestaurant.git
cd SmartRestaurant
```

### 2. 后端设置
```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库等信息

# 数据库迁移
python manage.py migrate

# 创建测试数据
python create_initial_data.py

# 启动服务
python manage.py runserver 127.0.0.1:8000
```

### 3. 前端设置
```bash
# 1. 打开微信开发者工具
# 2. 导入项目: frontend/customer-miniprogram
# 3. 配置: 详情 > 本地设置 > 不校验合法域名
# 4. 编译运行
```

## 📁 项目结构

```
SmartRestaurant/
├── apps/                           # Django应用模块
│   ├── users/                     # 用户管理
│   ├── dishes/                    # 菜品管理  
│   ├── orders/                    # 订单管理
│   ├── payments/                  # 支付管理
│   ├── coupons/                   # 优惠券管理
│   ├── reviews/                   # 评价管理
│   ├── restaurant/                # 餐厅信息
│   └── common/                    # 公共组件
├── frontend/                      # 前端代码
│   ├── customer-miniprogram/      # 顾客小程序
│   └── admin-miniprogram/         # 管理小程序(待开发)
├── smart_restaurant/              # Django配置
│   └── settings/                  # 多环境配置
├── database/                      # 数据库脚本
├── docs/                         # 开发文档
├── static/                       # 静态文件
├── media/                        # 媒体文件
└── requirements.txt              # Python依赖
```

## 🔄 API接口

### 核心接口
| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/categories/` | GET | 获取菜品分类 |
| `/api/dishes/` | GET | 获取菜品列表 |
| `/api/dishes/{id}/` | GET | 获取菜品详情 |
| `/api/orders/` | POST | 创建订单 |
| `/api/coupons/available/` | GET | 获取可用优惠券 |

### API文档
- **Swagger文档**: `http://127.0.0.1:8000/api/docs/`
- **ReDoc文档**: `http://127.0.0.1:8000/api/redoc/`

## 🗄️ 数据库设计

### 核心数据表
- `users_user` - 用户信息
- `dishes_category` - 菜品分类
- `dishes_dish` - 菜品信息
- `orders_order` - 订单信息
- `orders_orderitem` - 订单项
- `coupons_coupon` - 优惠券
- `payments_payment` - 支付记录

详细设计请查看: [数据库设计文档](docs/数据库设计文档.md)

## 📱 小程序页面

### 页面结构
```
pages/
├── index/          # 首页
├── menu/           # 菜单页
├── dish-detail/    # 菜品详情
├── cart/           # 购物车
└── checkout/       # 订单结算
```

### 功能特性
- 🎨 现代化UI设计
- 📱 响应式布局
- 🔍 实时搜索
- 🛒 购物车管理
- 💰 价格计算
- 🎫 优惠券选择

## 🔧 配置说明

### 环境配置
```bash
# .env 配置示例
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=smart_restaurant
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306
```

### 微信小程序配置
1. 申请微信小程序账号
2. 配置服务器域名
3. 设置支付商户号
4. 配置API接口地址

## 🧪 测试

### 运行测试
```bash
# 后端API测试
python test_dishes_api.py

# 前端集成测试
node test_frontend_integration.js
```

### 测试数据
- ✅ 6个菜品分类
- ✅ 15个测试菜品
- ✅ 5个优惠券
- ✅ 4个测试用户

## 📊 性能优化

- 🔄 **数据库优化**: 索引优化、查询优化
- 🗃️ **缓存策略**: Redis缓存热点数据
- 📱 **前端优化**: 图片压缩、懒加载
- 🚀 **API优化**: 分页查询、响应压缩

## 🔒 安全特性

- 🔐 JWT身份认证
- 🛡️ CSRF防护
- 🔒 SQL注入防护
- 📝 敏感数据加密
- 🚫 XSS攻击防护

## 📖 开发文档

- [后端开发指南](docs/backend/)
- [前端开发指南](docs/frontend/)
- [部署文档](docs/deployment/)
- [API文档](docs/api/)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 更新日志

### v1.0.0 (2025-01-07)
- ✨ 完成核心功能开发
- 🎨 UI界面设计完成
- 🔧 API接口开发完成
- 📱 微信小程序基础功能
- 🗄️ 数据库设计完成

详细更新日志请查看: [VERSION_HISTORY.md](VERSION_HISTORY.md)

## 📧 联系方式

- **项目地址**: [https://github.com/chenguo6666/SmartRestaurant](https://github.com/chenguo6666/SmartRestaurant)
- **问题反馈**: [Issues](https://github.com/chenguo6666/SmartRestaurant/issues)
- **功能建议**: [Discussions](https://github.com/chenguo6666/SmartRestaurant/discussions)

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

⭐ **如果这个项目对您有帮助，请给它一个星标！**

<div align="center">

**[🏠 首页](https://github.com/chenguo6666/SmartRestaurant)** | 
**[📖 文档](docs/)** | 
**[🚀 演示](https://your-demo-url.com)** | 
**[💬 讨论](https://github.com/chenguo6666/SmartRestaurant/discussions)**

</div> 