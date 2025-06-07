// 前端API集成测试脚本
// 模拟微信小程序API调用，测试与Django后端的集成

const https = require('http')
const baseURL = 'http://127.0.0.1:8000/api'

// 模拟微信小程序的wx.request
function mockWxRequest(options) {
  return new Promise((resolve, reject) => {
    const url = new URL(options.url)
    const requestOptions = {
      hostname: url.hostname,
      port: url.port,
      path: url.pathname + url.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.header
      }
    }

    const req = https.request(requestOptions, (res) => {
      let data = ''
      res.on('data', chunk => data += chunk)
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data)
          resolve({
            statusCode: res.statusCode,
            data: jsonData
          })
        } catch (error) {
          reject(error)
        }
      })
    })

    req.on('error', reject)
    
    if (options.data && options.method !== 'GET') {
      req.write(JSON.stringify(options.data))
    }
    
    req.end()
  })
}

// 模拟小程序API服务
class MiniProgramAPI {
  constructor() {
    this.baseURL = baseURL
  }

  async request(url, options = {}) {
    try {
      console.log(`🔄 请求: ${this.baseURL + url}`)
      
      const res = await mockWxRequest({
        url: this.baseURL + url,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'Content-Type': 'application/json',
          ...options.header
        }
      })

      console.log(`✅ 响应状态: ${res.statusCode}`)
      
      if (res.statusCode === 200) {
        if (res.data.code === 200) {
          return res.data.data
        } else {
          throw new Error(res.data.message || 'API请求失败')
        }
      } else {
        throw new Error(`HTTP ${res.statusCode}`)
      }
    } catch (error) {
      console.error(`❌ 请求失败: ${url}`, error.message)
      throw error
    }
  }

  // 菜品相关API - 修正路径
  async getCategories() {
    return this.request('/categories/')
  }

  async getDishes(params = {}) {
    const query = Object.keys(params)
      .filter(key => params[key] !== undefined && params[key] !== '')
      .map(key => `${key}=${encodeURIComponent(params[key])}`)
      .join('&')
    
    const url = query ? `/dishes/?${query}` : '/dishes/'
    return this.request(url)
  }

  async searchDishes(keyword) {
    return this.request(`/dishes/search/?q=${encodeURIComponent(keyword)}`)
  }

  async getRecommendedDishes() {
    return this.request('/dishes/recommended/')
  }

  async getHotDishes() {
    return this.request('/dishes/hot/')
  }
}

// 测试用例
async function runTests() {
  console.log('🚀 开始前端API集成测试\n')
  
  const api = new MiniProgramAPI()
  let passedTests = 0
  let totalTests = 0

  const tests = [
    {
      name: '获取菜品分类',
      test: async () => {
        const categories = await api.getCategories()
        console.log(`📂 分类数量: ${categories.length}`)
        console.log(`📂 分类列表: ${categories.map(c => c.name).join(', ')}`)
        return categories.length > 0
      }
    },
    {
      name: '获取菜品列表',
      test: async () => {
        const result = await api.getDishes()
        const dishes = result.results || []
        console.log(`🍽️ 菜品数量: ${dishes.length}`)
        console.log(`🍽️ 分页信息: 第${result.pagination.current_page}页，共${result.pagination.total_pages}页`)
        return dishes.length > 0
      }
    },
    {
      name: '搜索菜品功能',
      test: async () => {
        const results = await api.searchDishes('牛肉')
        console.log(`🔍 搜索"牛肉"结果: ${results.length}个`)
        if (results.length > 0) {
          console.log(`🔍 找到: ${results[0].name}`)
        }
        return true // 搜索无结果也算正常
      }
    },
    {
      name: '获取推荐菜品',
      test: async () => {
        const recommended = await api.getRecommendedDishes()
        console.log(`⭐ 推荐菜品数量: ${recommended.length}`)
        if (recommended.length > 0) {
          console.log(`⭐ 推荐菜品: ${recommended.map(d => d.name).join(', ')}`)
        }
        return recommended.length > 0
      }
    },
    {
      name: '获取热销菜品',
      test: async () => {
        const hotDishes = await api.getHotDishes()
        console.log(`🔥 热销菜品数量: ${hotDishes.length}`)
        return hotDishes.length > 0
      }
    },
    {
      name: '分类筛选功能',
      test: async () => {
        const result = await api.getDishes({ category: 1 })
        const dishes = result.results || []
        console.log(`🏷️ 分类1菜品数量: ${dishes.length}`)
        return true // 可能某些分类没有菜品
      }
    }
  ]

  for (const { name, test } of tests) {
    totalTests++
    console.log(`\n🧪 测试: ${name}`)
    console.log('─'.repeat(50))
    
    try {
      const result = await test()
      if (result) {
        console.log(`✅ ${name}: 通过`)
        passedTests++
      } else {
        console.log(`❌ ${name}: 失败`)
      }
    } catch (error) {
      console.log(`❌ ${name}: 失败 - ${error.message}`)
    }
  }

  console.log('\n' + '='.repeat(60))
  console.log('📊 测试总结')
  console.log('='.repeat(60))
  console.log(`✅ 通过: ${passedTests}/${totalTests}`)
  console.log(`📈 成功率: ${((passedTests / totalTests) * 100).toFixed(1)}%`)
  
  if (passedTests === totalTests) {
    console.log('🎉 所有测试通过！前端API集成成功！')
  } else {
    console.log('⚠️ 部分测试失败，请检查API服务')
  }
}

// 等待服务器启动后运行测试
setTimeout(() => {
  runTests().catch(console.error)
}, 1000)

console.log('⏳ 等待Django服务器响应...') 