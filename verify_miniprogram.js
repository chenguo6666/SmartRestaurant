/**
 * 小程序项目完整性验证
 */

const fs = require('fs')
const path = require('path')

console.log('🔍 验证小程序项目完整性...\n')

const frontendPath = './frontend/customer-miniprogram'

// 1. 检查app.json配置
console.log('📱 检查app.json配置...')
try {
  const appJsonPath = path.join(frontendPath, 'app.json')
  const appJson = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'))
  
  console.log('✅ app.json解析成功')
  console.log('📄 配置的页面:')
  
  // 检查每个页面是否存在
  let allPagesExist = true
  appJson.pages.forEach((page, index) => {
    const pageFiles = [
      `${page}.wxml`,
      `${page}.wxss`, 
      `${page}.js`,
      `${page}.json`
    ]
    
    console.log(`\n  ${index + 1}. ${page}`)
    
    pageFiles.forEach(file => {
      const filePath = path.join(frontendPath, file)
      if (fs.existsSync(filePath)) {
        console.log(`    ✅ ${file}`)
      } else {
        console.log(`    ❌ ${file} - 缺失`)
        allPagesExist = false
      }
    })
  })
  
  if (allPagesExist) {
    console.log('\n🎉 所有页面文件完整!')
  } else {
    console.log('\n⚠️ 部分页面文件缺失')
  }
  
} catch (error) {
  console.log('❌ app.json解析失败:', error.message)
}

// 2. 检查tabBar图标
console.log('\n🖼️ 检查tabBar图标...')
try {
  const appJsonPath = path.join(frontendPath, 'app.json')
  const appJson = JSON.parse(fs.readFileSync(appJsonPath, 'utf8'))
  
  if (appJson.tabBar && appJson.tabBar.list) {
    appJson.tabBar.list.forEach((tab, index) => {
      console.log(`\n  TabBar ${index + 1}: ${tab.text}`)
      
      // 检查页面是否存在
      const pageExists = appJson.pages.includes(tab.pagePath)
      console.log(`    页面: ${pageExists ? '✅' : '❌'} ${tab.pagePath}`)
      
      // 检查图标是否存在
      const iconPath = path.join(frontendPath, tab.iconPath)
      const selectedIconPath = path.join(frontendPath, tab.selectedIconPath)
      
      console.log(`    图标: ${fs.existsSync(iconPath) ? '✅' : '❌'} ${tab.iconPath}`)
      console.log(`    激活图标: ${fs.existsSync(selectedIconPath) ? '✅' : '❌'} ${tab.selectedIconPath}`)
    })
  }
} catch (error) {
  console.log('❌ tabBar检查失败:', error.message)
}

// 3. 检查必要的工具文件
console.log('\n🔧 检查工具文件...')
const utilFiles = [
  'utils/api.js',
  'utils/cart.js',
  'utils/util.js'
]

utilFiles.forEach(file => {
  const filePath = path.join(frontendPath, file)
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file}`)
  } else {
    console.log(`❌ ${file} - 缺失`)
  }
})

// 4. 检查项目配置文件
console.log('\n📋 检查项目配置文件...')
const configFiles = [
  'app.js',
  'app.wxss',
  'sitemap.json',
  'project.config.json'
]

configFiles.forEach(file => {
  const filePath = path.join(frontendPath, file)
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file}`)
  } else {
    console.log(`❌ ${file} - 缺失`)
  }
})

console.log('\n🎯 修复建议:')
console.log('1. 确保所有页面的四个文件(.wxml, .wxss, .js, .json)都存在')
console.log('2. 确保tabBar配置中的页面都在pages数组中')
console.log('3. 确保所有图标文件都存在')
console.log('4. 如果缺少页面，可以先从app.json中移除或创建相应文件')

console.log('\n✅ 验证完成!') 