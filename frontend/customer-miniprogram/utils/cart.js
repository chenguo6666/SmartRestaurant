// 购物车管理工具类
const app = getApp()

class CartService {
  constructor() {
    this.storageKey = 'cartItems'
  }

  // 获取购物车商品
  getCartItems() {
    const items = wx.getStorageSync(this.storageKey) || []
    app.globalData.cartItems = items
    return items
  }

  // 添加商品到购物车
  addItem(dish, quantity = 1) {
    const items = this.getCartItems()
    const existingItem = items.find(item => item.dish_id === dish.id)
    
    if (existingItem) {
      existingItem.quantity += quantity
    } else {
      items.push({
        dish_id: dish.id,
        dish_name: dish.name,
        dish_price: dish.price,
        dish_image: dish.image || dish.image_url || '/images/default-dish.png',
        quantity: quantity
      })
    }
    
    this.saveCartItems(items)
    this.showToast(`已添加到购物车`)
    return items
  }

  // 更新商品数量
  updateQuantity(dishId, quantity) {
    const items = this.getCartItems()
    const item = items.find(item => item.dish_id === dishId)
    
    if (item) {
      if (quantity <= 0) {
        this.removeItem(dishId)
      } else {
        item.quantity = quantity
        this.saveCartItems(items)
      }
    }
    
    return items
  }

  // 移除商品
  removeItem(dishId) {
    const items = this.getCartItems()
    const filteredItems = items.filter(item => item.dish_id !== dishId)
    this.saveCartItems(filteredItems)
    return filteredItems
  }

  // 清空购物车
  clearCart() {
    wx.removeStorageSync(this.storageKey)
    app.globalData.cartItems = []
    return []
  }

  // 获取购物车商品总数
  getTotalCount() {
    const items = this.getCartItems()
    return items.reduce((total, item) => total + item.quantity, 0)
  }

  // 获取购物车总金额
  getTotalAmount() {
    const items = this.getCartItems()
    return items.reduce((total, item) => total + (item.dish_price * item.quantity), 0)
  }

  // 检查商品是否在购物车中
  isInCart(dishId) {
    const items = this.getCartItems()
    return items.some(item => item.dish_id === dishId)
  }

  // 获取商品在购物车中的数量
  getItemQuantity(dishId) {
    const items = this.getCartItems()
    const item = items.find(item => item.dish_id === dishId)
    return item ? item.quantity : 0
  }

  // 获取购物车商品（别名方法）
  getItems() {
    return this.getCartItems()
  }

  // 减少商品数量
  reduceItem(dishId) {
    const currentQuantity = this.getItemQuantity(dishId)
    if (currentQuantity > 1) {
      this.updateQuantity(dishId, currentQuantity - 1)
    } else if (currentQuantity === 1) {
      this.removeItem(dishId)
    }
    return this.getCartItems()
  }

  // 保存购物车到本地存储
  saveCartItems(items) {
    wx.setStorageSync(this.storageKey, items)
    app.globalData.cartItems = items
    
    // 更新tabBar购物车徽标
    this.updateTabBarBadge()
  }

  // 更新tabBar徽标
  updateTabBarBadge() {
    const count = this.getTotalCount()
    if (count > 0) {
      wx.setTabBarBadge({
        index: 1, // 购物车tab的索引
        text: count.toString()
      })
    } else {
      wx.removeTabBarBadge({
        index: 1
      })
    }
  }

  // 显示提示信息
  showToast(title, icon = 'success') {
    wx.showToast({
      title,
      icon,
      duration: 1500
    })
  }
}

// 创建购物车服务实例
const cartService = new CartService()

module.exports = cartService 