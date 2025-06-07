const { dishesAPI } = require('../../utils/api')
const cartManager = require('../../utils/cart')

Page({
  data: {
    searchKeyword: '',           // 搜索关键词
    categories: [],              // 分类列表
    dishes: [],                 // 菜品列表
    filteredDishes: [],         // 筛选后的菜品
    selectedCategoryId: null,    // 选中的分类ID
    cartItems: [],              // 购物车商品
    cartVisible: false,         // 购物车是否显示
    loading: false,             // 加载状态
    hasMore: true,              // 是否还有更多数据
    currentPage: 1,             // 当前页码
    searchTimer: null           // 搜索防抖定时器
  },

  onLoad() {
    this.initData()
  },

  onShow() {
    // 页面显示时更新购物车状态
    this.updateCartDisplay()
  },

  // 初始化数据
  async initData() {
    wx.showLoading({ title: '加载中...' })
    
    try {
      // 并行加载分类和菜品数据
      const [categories, dishesData] = await Promise.all([
        this.loadCategories(),
        this.loadDishes()
      ])
      
      console.log('数据加载完成', { categories, dishesData })
      
    } catch (error) {
      console.error('初始化数据失败:', error)
      wx.showToast({
        title: '加载失败，请重试',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 加载分类数据
  async loadCategories() {
    try {
      const categories = await dishesAPI.getCategories()
      this.setData({ categories })
      return categories
    } catch (error) {
      console.error('加载分类失败:', error)
      throw error
    }
  },

  // 加载菜品数据
  async loadDishes(isLoadMore = false) {
    if (this.data.loading) return
    
    this.setData({ loading: true })
    
    try {
      const params = {
        page: isLoadMore ? this.data.currentPage + 1 : 1
      }
      
      // 只有当分类ID不为空时才添加分类参数
      if (this.data.selectedCategoryId) {
        params.category = this.data.selectedCategoryId
      }
      
      // 只有当搜索关键词不为空时才添加搜索参数
      if (this.data.searchKeyword && this.data.searchKeyword.trim()) {
        params.search = this.data.searchKeyword.trim()
      }
      
      const response = await dishesAPI.getDishes(params)
      const newDishes = response.results || []
      
      const dishes = isLoadMore 
        ? [...this.data.dishes, ...newDishes]
        : newDishes
      
      this.setData({
        dishes,
        filteredDishes: dishes,
        currentPage: response.pagination?.current_page || 1,
        hasMore: response.pagination?.has_next || false,
        loading: false
      })
      
      return response
      
    } catch (error) {
      console.error('加载菜品失败:', error)
      this.setData({ loading: false })
      throw error
    }
  },

  // 搜索输入事件
  onSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ searchKeyword: keyword })
    
    // 防抖搜索
    if (this.data.searchTimer) {
      clearTimeout(this.data.searchTimer)
    }
    
    this.data.searchTimer = setTimeout(() => {
      this.performSearch()
    }, 500)
  },

  // 执行搜索
  async performSearch() {
    console.log('执行搜索:', this.data.searchKeyword)
    
    if (!this.data.searchKeyword.trim()) {
      // 空搜索，重新加载所有菜品
      this.setData({ 
        selectedCategoryId: null,
        currentPage: 1 
      })
      await this.loadDishes()
      return
    }
    
    try {
      wx.showLoading({ title: '搜索中...' })
      const results = await dishesAPI.searchDishes(this.data.searchKeyword)
      
      this.setData({
        dishes: results,
        filteredDishes: results,
        selectedCategoryId: null,
        currentPage: 1,
        hasMore: false
      })
      
      if (results.length === 0) {
        wx.showToast({
          title: '未找到相关菜品',
          icon: 'none'
        })
      }
      
    } catch (error) {
      console.error('搜索失败:', error)
      wx.showToast({
        title: '搜索失败',
        icon: 'error'
      })
    } finally {
      wx.hideLoading()
    }
  },

  // 分类选择
  async onCategorySelect(e) {
    const categoryId = e.currentTarget.dataset.id
    
    this.setData({
      selectedCategoryId: categoryId === this.data.selectedCategoryId ? null : categoryId,
      searchKeyword: '',  // 清空搜索
      currentPage: 1
    })
    
    await this.loadDishes()
  },

  // 加载更多
  async onLoadMore() {
    if (!this.data.hasMore || this.data.loading) {
      return
    }
    
    console.log('加载更多菜品')
    await this.loadDishes(true)
  },

  // 添加到购物车
  onAddToCart(e) {
    const dish = e.currentTarget.dataset.dish
    
    if (!dish) {
      console.error('菜品数据错误')
      return
    }
    
    // 检查库存
    if (dish.stock_quantity === 0) {
      wx.showToast({
        title: '商品已售完',
        icon: 'none'
      })
      return
    }
    
    // 添加到购物车
    cartManager.addItem({
      id: dish.id,
      name: dish.name,
      price: parseFloat(dish.price),
      image: dish.image_url || '/images/default-dish.png',
      stock: dish.stock_quantity
    })
    
    // 显示成功提示
    wx.showToast({
      title: '已添加到购物车',
      icon: 'success',
      duration: 1000
    })
    
    // 更新购物车显示
    this.updateCartDisplay()
  },

  // 减少购物车商品
  onReduceCart(e) {
    const dishId = e.currentTarget.dataset.id
    cartManager.reduceItem(dishId)
    this.updateCartDisplay()
  },

  // 增加购物车商品
  onIncreaseCart(e) {
    const dishId = e.currentTarget.dataset.id
    const dish = this.data.dishes.find(d => d.id === dishId)
    
    if (dish && dish.stock_quantity > 0) {
      cartManager.addItem({
        id: dish.id,
        name: dish.name,
        price: parseFloat(dish.price),
        image: dish.image_url || '/images/default-dish.png',
        stock: dish.stock_quantity
      })
      this.updateCartDisplay()
    }
  },

  // 更新购物车显示
  updateCartDisplay() {
    const cartItems = cartManager.getItems()
    this.setData({ cartItems })
  },

  // 获取商品在购物车中的数量
  getCartItemCount(dishId) {
    return cartManager.getItemQuantity(dishId)
  },

  // 显示/隐藏购物车
  toggleCart() {
    this.setData({
      cartVisible: !this.data.cartVisible
    })
  },

  // 跳转到菜品详情
  onDishTap(e) {
    const dishId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/dish-detail/dish-detail?id=${dishId}`
    })
  },

  // 跳转到购物车页面
  goToCart() {
    wx.switchTab({
      url: '/pages/cart/cart'
    })
  },

  // 页面下拉刷新
  async onPullDownRefresh() {
    try {
      this.setData({
        currentPage: 1,
        searchKeyword: '',
        selectedCategoryId: null
      })
      
      await this.initData()
      
    } catch (error) {
      console.error('刷新失败:', error)
    } finally {
      wx.stopPullDownRefresh()
    }
  },

  // 页面触底加载更多
  onReachBottom() {
    this.onLoadMore()
  },

  // 页面分享
  onShareAppMessage() {
    return {
      title: '美味菜单，快来看看~',
      path: '/pages/menu/menu'
    }
  }
}) 