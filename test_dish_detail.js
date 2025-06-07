// 菜品详情页面测试脚本
const https = require('http')
const baseURL = 'http://127.0.0.1:8000/api'

// 模拟小程序API调用
function mockRequest(url) {
  return new Promise((resolve, reject) => {
    const fullUrl = new URL(baseURL + url)
    const options = {
      hostname: fullUrl.hostname,
      port: fullUrl.port,
      path: fullUrl.pathname + fullUrl.search,
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    }

    const req = https.request(options, (res) => {
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
    req.end()
  })
}

// 测试函数
async function testDishDetail() {
  console.log('🧪 测试菜品详情页面功能\n')
  
  try {
    // 1. 先获取菜品列表，找到一个菜品ID
    console.log('📋 1. 获取菜品列表...')
    const dishListRes = await mockRequest('/dishes/')
    
    if (dishListRes.statusCode === 200 && dishListRes.data.code === 200) {
      const dishes = dishListRes.data.data.results || []
      if (dishes.length > 0) {
        const testDish = dishes[0]
        console.log(`   找到测试菜品: ${testDish.name} (ID: ${testDish.id})`)
        
        // 2. 测试菜品详情API
        console.log('\n📖 2. 测试菜品详情API...')
        const detailRes = await mockRequest(`/dishes/${testDish.id}/`)
        
        if (detailRes.statusCode === 200 && detailRes.data.code === 200) {
          const dish = detailRes.data.data
          console.log('✅ 菜品详情加载成功')
          console.log(`   菜品名称: ${dish.name}`)
          console.log(`   菜品分类: ${dish.category_name || '未分类'}`)
          console.log(`   菜品价格: ¥${dish.price}`)
          console.log(`   菜品描述: ${dish.description}`)
          console.log(`   辣度等级: ${dish.spicy_level_display}`)
          console.log(`   推荐状态: ${dish.is_recommended ? '是' : '否'}`)
          console.log(`   库存状态: ${dish.is_in_stock ? '有货' : '缺货'}`)
          console.log(`   销售数量: ${dish.sales_count}`)
          
          if (dish.original_price) {
            console.log(`   原价: ¥${dish.original_price}`)
            console.log(`   折扣: ${dish.discount_rate}%`)
          }
          
          if (dish.tags) {
            console.log(`   标签: ${dish.tags}`)
          }
          
          // 4. 模拟添加到购物车的逻辑测试
          console.log('\n🛒 4. 模拟购物车功能...')
          console.log('   模拟用户操作:')
          console.log(`   - 选择菜品: ${dish.name}`)
          console.log(`   - 单价: ¥${dish.price}`)
          console.log(`   - 数量: 2`)
          console.log(`   - 总价: ¥${(parseFloat(dish.price) * 2).toFixed(2)}`)
          
          if (dish.is_in_stock) {
            console.log('✅ 可以添加到购物车')
          } else {
            console.log('❌ 商品缺货，无法添加到购物车')
          }
          
        } else {
          console.log('❌ 菜品详情加载失败')
          console.log(`   状态码: ${detailRes.statusCode}`)
          console.log(`   错误信息: ${detailRes.data.message}`)
        }
        
        // 3. 测试相关推荐
        console.log('\n⭐ 3. 测试相关推荐...')
        const recommendRes = await mockRequest('/dishes/recommended/')
        
        if (recommendRes.statusCode === 200 && recommendRes.data.code === 200) {
          const recommended = recommendRes.data.data
          const filtered = recommended.filter(item => item.id !== testDish.id).slice(0, 5)
          console.log(`✅ 推荐菜品加载成功，共${filtered.length}个`)
          filtered.forEach((item, index) => {
            console.log(`   ${index + 1}. ${item.name} - ¥${item.price}`)
          })
        } else {
          console.log('❌ 推荐菜品加载失败')
        }
        
        console.log('\n🎉 菜品详情页面功能测试完成！')
        
      } else {
        console.log('❌ 没有找到菜品数据')
      }
    } else {
      console.log('❌ 获取菜品列表失败')
    }
    
  } catch (error) {
    console.error('❌ 测试过程中发生错误:', error.message)
  }
}

// 运行测试
console.log('🚀 启动菜品详情页面测试...\n')
setTimeout(() => {
  testDishDetail().catch(console.error)
}, 1000) 