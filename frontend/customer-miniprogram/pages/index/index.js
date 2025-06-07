// index.js
Page({
  data: {
    restaurantName: '智能餐厅',
    slogan: '美味触手可及'
  },
  onLoad(options) {
    console.log('首页加载完成');
  },
  onShow() {
    console.log('首页显示');
  },
  // 跳转到菜单页面
  goToMenu() {
    wx.switchTab({
      url: '/pages/menu/menu',
      success: () => {
        console.log('跳转到菜单页面');
      },
      fail: (err) => {
        console.error('跳转菜单页面失败:', err);
        wx.showToast({
          title: '跳转失败',
          icon: 'error',
          duration: 2000
        });
      }
    });
  },
  // 跳转到购物车页面
  goToCart() {
    wx.switchTab({
      url: '/pages/cart/cart',
      success: () => {
        console.log('跳转到购物车页面');
      },
      fail: (err) => {
        console.error('跳转购物车页面失败:', err);
        wx.showToast({
          title: '跳转失败',
          icon: 'error',
          duration: 2000
        });
      }
    });
  },
  // 拨打电话
  makeCall() {
    wx.makePhoneCall({
      phoneNumber: '400-888-6666',
      success: () => {
        console.log('拨打电话成功');
      },
      fail: (err) => {
        console.error('拨打电话失败:', err);
      }
    });
  },
  // 查看地址
  viewLocation() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none',
      duration: 2000
    });
  }
})
