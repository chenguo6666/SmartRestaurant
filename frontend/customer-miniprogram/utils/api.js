// 引入配置文件
const { config, devUtils } = require('./config.js')

console.log('API配置加载:', {
  baseURL: config.baseURL,
  isDev: config.isDev
})

// 通用请求方法
function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: config.baseURL + url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        ...config.header,
        ...options.header
      },
      timeout: config.timeout,
      success: (res) => {
        console.log(`API请求成功: ${url}`, res.data)
        
        // 统一处理API响应格式
        if (res.statusCode === 200) {
          if (res.data.code === 200) {
            resolve(res.data.data)
          } else {
            console.error(`API业务错误: ${url}`, res.data.message)
            reject(new Error(res.data.message || 'API请求失败'))
          }
        } else {
          console.error(`API状态错误: ${url}`, res.statusCode)
          reject(new Error(`HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => {
        console.error(`API请求失败: ${url}`, err)
        
        // 开发环境域名错误提示
        if (config.isDev && err.errMsg && err.errMsg.includes('request:fail')) {
          if (err.errMsg.includes('合法域名列表')) {
            devUtils.showDevTip('domainError')
          } else if (err.errMsg.includes('timeout') || err.errMsg.includes('connect')) {
            devUtils.showDevTip('networkError')
          }
        }
        
        reject(err)
      }
    })
  })
}

// 菜品相关API
const dishesAPI = {
  // 获取菜品分类列表 - 修正路径
  getCategories() {
    return request('/categories/')
  },

  // 获取菜品列表
  getDishes(params = {}) {
    const query = Object.keys(params)
      .filter(key => {
        const value = params[key]
        return value !== undefined && value !== null && value !== ''
      })
      .map(key => `${key}=${encodeURIComponent(params[key])}`)
      .join('&')
    
    const url = query ? `/dishes/?${query}` : '/dishes/'
    return request(url)
  },

  // 搜索菜品 - 修正路径
  searchDishes(keyword) {
    return request(`/dishes/search/?q=${encodeURIComponent(keyword)}`)
  },

  // 获取推荐菜品 - 修正路径
  getRecommendedDishes() {
    return request('/dishes/recommended/')
  },

  // 获取热销菜品 - 修正路径
  getHotDishes() {
    return request('/dishes/hot/')
  },

  // 获取菜品详情
  getDishDetail(dishId) {
    return request(`/dishes/${dishId}/`)
  }
}

// 订单API
const ordersAPI = {
  // 创建订单
  async createOrder(orderData) {
    return request('/orders/', {
      method: 'POST',
      data: orderData
    })
  },

  // 获取我的订单列表
  async getMyOrders(params = {}) {
    return request('/orders/my_orders/', {
      method: 'GET',
      data: params
    })
  },

  // 获取订单详情
  async getOrderDetail(orderId) {
    return request(`/orders/${orderId}/`, {
      method: 'GET'
    })
  },

  // 取消订单
  async cancelOrder(orderId, reason = '') {
    return request(`/orders/${orderId}/cancel/`, {
      method: 'POST',
      data: { reason }
    })
  }
}

// 优惠券API
const couponsAPI = {
  // 获取可用优惠券
  async getAvailableCoupons(totalAmount) {
    return request('/coupons/available/', {
      method: 'GET',
      data: { total_amount: totalAmount }
    })
  },

  // 验证优惠券
  async validateCoupon(couponCode, totalAmount) {
    return request('/coupons/validate/', {
      method: 'POST',
      data: { 
        coupon_code: couponCode,
        total_amount: totalAmount 
      }
    })
  }
}

module.exports = {
  request,
  dishesAPI,
  ordersAPI,
  couponsAPI
} 