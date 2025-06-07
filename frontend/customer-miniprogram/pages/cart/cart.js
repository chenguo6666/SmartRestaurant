const cartManager = require('../../utils/cart')

Page({
  data: {
    cartItems: [],           // 购物车商品列表
    totalCount: 0,          // 商品总数量
    totalAmount: 0,         // 总金额
    isEmpty: true,          // 是否为空
    loading: true           // 加载状态
  },

  onLoad() {
    this.loadCartData()
  },

  onShow() {
    // 每次显示页面时刷新购物车数据
    this.loadCartData()
  },

  // 加载购物车数据
  loadCartData() {
    try {
      const cartItems = cartManager.getCartItems()
      const totalCount = cartManager.getTotalCount()
      const totalAmount = cartManager.getTotalAmount()
      
      this.setData({
        cartItems,
        totalCount,
        totalAmount: totalAmount.toFixed(2),
        isEmpty: cartItems.length === 0,
        loading: false
      })
      
      console.log('购物车数据:', { cartItems, totalCount, totalAmount })
      
    } catch (error) {
      console.error('加载购物车数据失败:', error)
      this.setData({ loading: false })
      
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
    }
  },

  // 减少商品数量
  onDecreaseQuantity(e) {
    const { dishId } = e.currentTarget.dataset
    const currentQuantity = cartManager.getItemQuantity(dishId)
    
    if (currentQuantity > 1) {
      cartManager.updateQuantity(dishId, currentQuantity - 1)
      this.loadCartData()
      
      // 振动反馈
      wx.vibrateShort({
        type: 'light'
      })
    }
  },

  // 增加商品数量
  onIncreaseQuantity(e) {
    const { dishId } = e.currentTarget.dataset
    const currentQuantity = cartManager.getItemQuantity(dishId)
    
    cartManager.updateQuantity(dishId, currentQuantity + 1)
    this.loadCartData()
    
    // 振动反馈
    wx.vibrateShort({
      type: 'light'
    })
  },

  // 删除商品
  onDeleteItem(e) {
    const { dishId, dishName } = e.currentTarget.dataset
    
    wx.showModal({
      title: '确认删除',
      content: `确定要删除「${dishName}」吗？`,
      confirmText: '删除',
      confirmColor: '#ff5722',
      success: (res) => {
        if (res.confirm) {
          cartManager.removeItem(dishId)
          this.loadCartData()
          
          wx.showToast({
            title: '已删除',
            icon: 'success',
            duration: 1000
          })
        }
      }
    })
  },

  // 清空购物车
  onClearCart() {
    if (this.data.isEmpty) {
      return
    }
    
    wx.showModal({
      title: '确认清空',
      content: '确定要清空购物车吗？',
      confirmText: '清空',
      confirmColor: '#ff5722',
      success: (res) => {
        if (res.confirm) {
          cartManager.clearCart()
          this.loadCartData()
          
          wx.showToast({
            title: '已清空',
            icon: 'success',
            duration: 1000
          })
        }
      }
    })
  },

  // 去结算
  onCheckout() {
    if (this.data.isEmpty) {
      wx.showToast({
        title: '购物车为空',
        icon: 'none'
      })
      return
    }
    
    const { cartItems, totalAmount, totalCount } = this.data
    
    // 传递购物车数据到结算页面
    const orderData = {
      items: cartItems,
      totalAmount: parseFloat(totalAmount),
      totalCount: totalCount
    }
    
    wx.navigateTo({
      url: `/pages/checkout/checkout?orderData=${encodeURIComponent(JSON.stringify(orderData))}`
    })
  },

  // 去购物
  onGoShopping() {
    wx.switchTab({
      url: '/pages/menu/menu'
    })
  },

  // 商品详情
  onItemTap(e) {
    const { dishId } = e.currentTarget.dataset
    wx.navigateTo({
      url: `/pages/dish-detail/dish-detail?id=${dishId}`
    })
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadCartData()
    wx.stopPullDownRefresh()
  },

  // 分享功能
  onShareAppMessage() {
    return {
      title: '智能餐厅 - 美食等你来',
      path: '/pages/menu/menu',
      imageUrl: '/images/share-bg.png'
    }
  },

  // 分享到朋友圈
  onShareTimeline() {
    return {
      title: '智能餐厅 - 美食等你来',
      imageUrl: '/images/share-bg.png'
    }
  }
}) 