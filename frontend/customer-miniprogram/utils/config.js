// 环境配置文件
// 根据不同环境设置不同的API地址

// 获取当前环境
const envVersion = __wxConfig.envVersion || 'develop'

// 环境配置
const envConfig = {
  // 开发环境
  develop: {
    baseURL: 'http://127.0.0.1:8000/api',
    isDev: true
  },
  // 体验版
  trial: {
    baseURL: 'https://your-test-domain.com/api',
    isDev: false
  },
  // 正式版
  release: {
    baseURL: 'https://your-production-domain.com/api', 
    isDev: false
  }
}

// 当前环境配置
const currentEnv = envConfig[envVersion] || envConfig.develop

// API配置
const config = {
  baseURL: currentEnv.baseURL,
  timeout: 10000,
  isDev: currentEnv.isDev,
  header: {
    'Content-Type': 'application/json'
  },
  // 开发环境提示信息
  devTips: {
    domainError: '检测到域名限制错误，请在微信开发者工具中：\n1. 点击"详情" > "本地设置"\n2. 勾选"不校验合法域名"选项',
    networkError: '网络请求失败，请确保Django服务正在运行：\npython manage.py runserver'
  }
}

// 开发环境辅助方法
const devUtils = {
  // 显示开发提示
  showDevTip(type) {
    if (config.isDev && config.devTips[type]) {
      wx.showModal({
        title: '开发环境提示',
        content: config.devTips[type],
        showCancel: false,
        confirmText: '知道了'
      })
    }
  },

  // 检查服务状态
  async checkServer() {
    if (!config.isDev) return true
    
    try {
      const res = await new Promise((resolve, reject) => {
        wx.request({
          url: config.baseURL.replace('/api', '/'),
          method: 'GET',
          timeout: 5000,
          success: resolve,
          fail: reject
        })
      })
      return true
    } catch (error) {
      this.showDevTip('networkError')
      return false
    }
  }
}

module.exports = {
  config,
  devUtils,
  envVersion,
  isDev: config.isDev
} 