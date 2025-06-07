const { ordersAPI, couponsAPI } = require('../../utils/api')
const cartManager = require('../../utils/cart')

Page({
  data: {
    orderItems: [],           // 订单商品列表
    totalAmount: 0,          // 商品总额
    discountAmount: 0,       // 优惠金额
    finalAmount: 0,          // 最终金额
    tableNumber: '',         // 桌号
    customerNotes: '',       // 备注
    selectedCoupon: null,    // 选中的优惠券
    availableCoupons: [],    // 可用优惠券列表
    showCouponModal: false,  // 优惠券弹窗显示状态
    tempSelectedCoupon: null, // 临时选中的优惠券
    loading: true,           // 加载状态
    submitting: false        // 提交状态
  },

  onLoad(options) {
    // 获取购物车传递的订单数据
    if (options.orderData) {
      try {
        const orderData = JSON.parse(decodeURIComponent(options.orderData))
        this.initOrderData(orderData)
      } catch (error) {
        console.error('解析订单数据失败:', error)
        this.showErrorAndBack('订单数据有误')
      }
    } else {
      this.showErrorAndBack('订单数据缺失')
    }
  },

  // 初始化订单数据
  initOrderData(orderData) {
    const { items, totalAmount, totalCount } = orderData
    
    this.setData({
      orderItems: items,
      totalAmount: totalAmount.toFixed(2),
      finalAmount: totalAmount.toFixed(2),
      loading: false
    })

    // 加载可用优惠券
    this.loadAvailableCoupons()
  },

  // 加载可用优惠券
  async loadAvailableCoupons() {
    try {
      const coupons = await couponsAPI.getAvailableCoupons(this.data.totalAmount)
      this.setData({
        availableCoupons: coupons || []
      })
    } catch (error) {
      console.error('加载优惠券失败:', error)
      // 不阻断用户流程，只记录错误
    }
  },

  // 桌号输入
  onTableNumberInput(e) {
    this.setData({
      tableNumber: e.detail.value
    })
  },

  // 备注输入
  onNotesInput(e) {
    this.setData({
      customerNotes: e.detail.value
    })
  },

  // 打开优惠券选择
  onSelectCoupon() {
    this.setData({
      showCouponModal: true,
      tempSelectedCoupon: this.data.selectedCoupon
    })
  },

  // 关闭优惠券弹窗
  onCloseCouponModal() {
    this.setData({
      showCouponModal: false,
      tempSelectedCoupon: null
    })
  },

  // 选择优惠券
  onCouponSelect(e) {
    const coupon = e.currentTarget.dataset.coupon
    this.setData({
      tempSelectedCoupon: coupon
    })
  },

  // 确认选择优惠券
  onConfirmCoupon() {
    const { tempSelectedCoupon } = this.data
    
    this.setData({
      selectedCoupon: tempSelectedCoupon,
      showCouponModal: false,
      tempSelectedCoupon: null
    })

    // 重新计算金额
    this.calculateFinalAmount()
  },

  // 计算最终金额
  calculateFinalAmount() {
    const { totalAmount, selectedCoupon } = this.data
    let discountAmount = 0
    
    if (selectedCoupon) {
      // 检查优惠券使用条件
      if (parseFloat(totalAmount) >= selectedCoupon.min_order_amount) {
        if (selectedCoupon.discount_type === 'fixed') {
          discountAmount = selectedCoupon.discount_amount
        } else if (selectedCoupon.discount_type === 'percentage') {
          discountAmount = parseFloat(totalAmount) * selectedCoupon.discount_percentage / 100
          // 限制最大折扣金额
          if (selectedCoupon.max_discount_amount > 0) {
            discountAmount = Math.min(discountAmount, selectedCoupon.max_discount_amount)
          }
        }
      }
    }

    const finalAmount = parseFloat(totalAmount) - discountAmount
    
    this.setData({
      discountAmount: discountAmount.toFixed(2),
      finalAmount: Math.max(0, finalAmount).toFixed(2)
    })
  },

  // 提交订单
  async onSubmitOrder() {
    if (this.data.submitting) return

    // 验证订单数据
    if (!this.validateOrderData()) return

    this.setData({ submitting: true })

    try {
      // 构建订单数据
      const orderData = this.buildOrderData()
      
      wx.showLoading({ title: '创建订单中...' })
      
      // 调用API创建订单
      const result = await ordersAPI.createOrder(orderData)
      
      wx.hideLoading()

      if (result.success) {
        // 清空购物车
        cartManager.clearCart()
        
        // 显示成功提示
        wx.showToast({
          title: '订单创建成功',
          icon: 'success',
          duration: 2000
        })

        // 跳转到订单详情或支付页面
        setTimeout(() => {
          wx.redirectTo({
            url: `/pages/order-detail/order-detail?id=${result.data.id}`
          })
        }, 2000)

      } else {
        this.showError(result.message || '订单创建失败')
      }

    } catch (error) {
      wx.hideLoading()
      console.error('创建订单失败:', error)
      this.showError('网络异常，请重试')
    } finally {
      this.setData({ submitting: false })
    }
  },

  // 验证订单数据
  validateOrderData() {
    const { orderItems, finalAmount } = this.data

    if (!orderItems || orderItems.length === 0) {
      this.showError('订单商品不能为空')
      return false
    }

    if (parseFloat(finalAmount) <= 0) {
      this.showError('订单金额有误')
      return false
    }

    return true
  },

  // 构建订单数据
  buildOrderData() {
    const { orderItems, tableNumber, customerNotes, selectedCoupon } = this.data

    const cartItems = orderItems.map(item => ({
      dish_id: item.dish_id,
      quantity: item.quantity,
      special_requests: '' // 可以后续扩展单个商品的特殊要求
    }))

    const orderData = {
      cart_items: cartItems,
      customer_notes: customerNotes,
    }

    // 添加桌号（如果有）
    if (tableNumber.trim()) {
      orderData.table_number = tableNumber.trim()
    }

    // 添加优惠券（如果有）
    if (selectedCoupon) {
      orderData.coupon_code = selectedCoupon.code
    }

    return orderData
  },

  // 显示错误信息
  showError(message) {
    wx.showToast({
      title: message,
      icon: 'none',
      duration: 2000
    })
  },

  // 显示错误并返回
  showErrorAndBack(message) {
    wx.showModal({
      title: '提示',
      content: message,
      showCancel: false,
      confirmText: '返回购物车',
      success: () => {
        wx.switchTab({
          url: '/pages/cart/cart'
        })
      }
    })
  },

  // 阻止事件冒泡
  stopPropagation() {
    // 空函数，阻止事件冒泡
  },

  // 返回购物车
  onBack() {
    wx.navigateBack()
  },

  // 页面分享
  onShareAppMessage() {
    return {
      title: '智能餐厅 - 美食订单',
      path: '/pages/menu/menu',
      imageUrl: '/images/share-bg.png'
    }
  }
}) 