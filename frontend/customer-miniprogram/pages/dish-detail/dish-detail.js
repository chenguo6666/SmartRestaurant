const { dishesAPI } = require('../../utils/api')
const cartManager = require('../../utils/cart')

Page({
  data: {
    dishId: null,                    // 菜品ID
    dish: {},                       // 菜品详情
    quantity: 1,                    // 选择数量
    totalPrice: '0.00',             // 总价
    loading: true,                  // 加载状态
    tagsList: [],                   // 解析后的标签列表
    nutritionInfo: [],              // 营养信息（模拟数据）
    relatedDishes: []               // 相关推荐菜品
  },

  onLoad(options) {
    const dishId = options.id
    if (dishId) {
      this.setData({ dishId })
      this.loadDishDetail(dishId)
    } else {
      wx.showToast({
        title: '菜品不存在',
        icon: 'error'
      })
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    }
  },

  onShow() {
    // 页面显示时更新价格显示
    this.updateTotalPrice()
  },

  // 加载菜品详情
  async loadDishDetail(dishId) {
    try {
      wx.showLoading({ title: '加载中...' })
      
      // 并行加载菜品详情和相关推荐
      const [dish, relatedDishes] = await Promise.all([
        dishesAPI.getDishDetail(dishId),
        this.loadRelatedDishes()
      ])
      
      console.log('菜品详情:', dish)
      
      // 处理标签数据
      const tagsList = dish.tags ? dish.tags.split(',').map(tag => tag.trim()) : []
      
      // 模拟营养信息（实际项目中可从后端获取）
      const nutritionInfo = this.generateNutritionInfo(dish)
      
      this.setData({
        dish,
        tagsList,
        nutritionInfo,
        relatedDishes,
        loading: false
      })
      
      // 更新页面标题
      wx.setNavigationBarTitle({
        title: dish.name || '菜品详情'
      })
      
      this.updateTotalPrice()
      
    } catch (error) {
      console.error('加载菜品详情失败:', error)
      this.setData({ loading: false })
      
      wx.showToast({
        title: '加载失败',
        icon: 'error'
      })
      
      setTimeout(() => {
        wx.navigateBack()
      }, 1500)
    } finally {
      wx.hideLoading()
    }
  },

  // 加载相关推荐菜品
  async loadRelatedDishes() {
    try {
      // 获取推荐菜品，过滤掉当前菜品
      const recommended = await dishesAPI.getRecommendedDishes()
      return recommended
        .filter(item => item.id !== parseInt(this.data.dishId))
        .slice(0, 5) // 只显示5个推荐
    } catch (error) {
      console.error('加载推荐菜品失败:', error)
      return []
    }
  },

  // 生成营养信息（模拟数据）
  generateNutritionInfo(dish) {
    // 根据菜品类型生成不同的营养信息
    const baseInfo = [
      { name: '热量', value: `${Math.floor(Math.random() * 200 + 150)} 千卡` },
      { name: '蛋白质', value: `${Math.floor(Math.random() * 15 + 5)} g` },
      { name: '脂肪', value: `${Math.floor(Math.random() * 10 + 2)} g` },
      { name: '碳水化合物', value: `${Math.floor(Math.random() * 30 + 10)} g` }
    ]
    
    // 可根据菜品分类添加特定营养信息
    if (dish.category_name === '汤品') {
      baseInfo.push({ name: '钠', value: `${Math.floor(Math.random() * 500 + 200)} mg` })
    }
    
    return baseInfo
  },

  // 返回上一页
  goBack() {
    wx.navigateBack()
  },

  // 减少数量
  onDecreaseQuantity() {
    if (this.data.quantity > 1) {
      this.setData({
        quantity: this.data.quantity - 1
      })
      this.updateTotalPrice()
    }
  },

  // 增加数量
  onIncreaseQuantity() {
    if (this.data.dish.is_in_stock) {
      // 可以添加库存检查逻辑
      this.setData({
        quantity: this.data.quantity + 1
      })
      this.updateTotalPrice()
    }
  },

  // 更新总价
  updateTotalPrice() {
    const price = parseFloat(this.data.dish.price || 0)
    const totalPrice = (price * this.data.quantity).toFixed(2)
    this.setData({ totalPrice })
  },

  // 添加到购物车
  onAddToCart() {
    const { dish, quantity } = this.data
    
    if (!dish.id) {
      wx.showToast({
        title: '菜品信息错误',
        icon: 'error'
      })
      return
    }
    
    if (!dish.is_in_stock) {
      wx.showToast({
        title: '商品已售完',
        icon: 'none'
      })
      return
    }
    
    try {
      // 添加到购物车
      cartManager.addItem({
        id: dish.id,
        name: dish.name,
        price: parseFloat(dish.price),
        image: dish.image_url || '/images/default-dish.png',
        stock: dish.stock_quantity
      }, quantity)
      
      // 显示成功提示
      wx.showToast({
        title: `已添加${quantity}份到购物车`,
        icon: 'success',
        duration: 1500
      })
      
      // 可选：振动反馈
      wx.vibrateShort()
      
      // 重置数量
      this.setData({ quantity: 1 })
      this.updateTotalPrice()
      
    } catch (error) {
      console.error('添加购物车失败:', error)
      wx.showToast({
        title: '添加失败，请重试',
        icon: 'error'
      })
    }
  },

  // 点击推荐菜品
  onRecommendTap(e) {
    const dishId = e.currentTarget.dataset.id
    wx.redirectTo({
      url: `/pages/dish-detail/dish-detail?id=${dishId}`
    })
  },

  // 页面分享
  onShareAppMessage() {
    const { dish } = this.data
    return {
      title: `${dish.name} - 智能餐厅`,
      path: `/pages/dish-detail/dish-detail?id=${dish.id}`,
      imageUrl: dish.image_url || '/images/default-dish.png'
    }
  },

  // 页面分享到朋友圈
  onShareTimeline() {
    const { dish } = this.data
    return {
      title: `推荐一道美味：${dish.name}`,
      imageUrl: dish.image_url || '/images/default-dish.png'
    }
  },

  // 下拉刷新
  async onPullDownRefresh() {
    try {
      await this.loadDishDetail(this.data.dishId)
    } catch (error) {
      console.error('刷新失败:', error)
    } finally {
      wx.stopPullDownRefresh()
    }
  }
}) 