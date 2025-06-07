// app.js
App({
  onLaunch() {
    // 检查登录状态
    this.checkLoginStatus()
    
    // 获取系统信息
    this.getSystemInfo()
  },

  // 检查登录状态
  checkLoginStatus() {
    const token = wx.getStorageSync('token')
    if (token) {
      // 验证token有效性
      this.validateToken(token)
    }
  },

  // 验证token
  validateToken(token) {
    // TODO: 调用后端API验证token
    console.log('验证用户token:', token)
  },

  // 获取系统信息
  getSystemInfo() {
    wx.getSystemInfo({
      success: (res) => {
        this.globalData.systemInfo = res
        this.globalData.statusBarHeight = res.statusBarHeight
        this.globalData.navBarHeight = res.statusBarHeight + 44
      }
    })
  },

  // 微信登录
  wxLogin() {
    return new Promise((resolve, reject) => {
      wx.login({
        success: res => {
          if (res.code) {
            // TODO: 发送code到后台换取token
            console.log('微信登录code:', res.code)
            resolve(res.code)
          } else {
            reject('微信登录失败')
          }
        },
        fail: reject
      })
    })
  },

  // 全局数据
  globalData: {
    userInfo: null,
    token: null,
    systemInfo: null,
    statusBarHeight: 0,
    navBarHeight: 0,
    baseUrl: 'http://127.0.0.1:8000/api', // 后端API地址
    cartItems: [] // 购物车商品
  }
})
