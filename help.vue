<template>
  <view class="container">
    <scroll-view class="content" scroll-y>
      <view class="section">
        <text class="section-title">快速入门</text>
        <view class="help-item">
          <text class="help-title">1. 添加设备</text>
          <text class="help-content">点击首页右上角的"+"按钮，扫描附近的TSLink设备。找到设备后点击"添加"即可将其保存到设备列表。</text>
        </view>
        <view class="help-item">
          <text class="help-title">2. 连接设备</text>
          <text class="help-content">点击设备列表中的设备，进入设备页面。如果开启了"自动连接"，系统会自动尝试连接设备；否则需要手动点击连接按钮。</text>
        </view>
        <view class="help-item">
          <text class="help-title">3. 查看数据</text>
          <text class="help-content">连接成功后，设备页面上方会显示设备上报的数据，下方可以发送控制指令给设备。</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">常见问题</text>
        <view class="help-item">
          <text class="help-title">无法发现设备？</text>
          <text class="help-content">请确保：\n• 设备已开启并处于可发现状态\n• 设备在蓝牙有效范围内（10米内）\n• 手机蓝牙已开启</text>
        </view>
        <view class="help-item">
          <text class="help-title">连接失败？</text>
          <text class="help-content">请尝试：\n• 靠近设备后重试\n• 重启设备\n• 在设置中调整"连接超时"时间</text>
        </view>
        <view class="help-item">
          <text class="help-title">如何切换主题颜色？</text>
          <text class="help-content">进入"设置"页面，在"个性化"部分选择你喜欢的主题颜色。</text>
        </view>
      </view>

      <view class="section">
        <text class="section-title">功能说明</text>
        <view class="help-item">
          <text class="help-title">自动连接模式</text>
          <text class="help-content">开启后，进入设备页面时会自动尝试连接设备。关闭后需要手动点击连接按钮。</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
export default {
  data() {
    return {};
  },
};
</script>

<style scoped>
.container {
  min-height: 100vh;
  padding-top: var(--status-bar-height);
  background: #f5f5f5;
  box-sizing: border-box;
}

.content {
  padding: 20rpx;
  width: 100%;
  box-sizing: border-box;
}

.section {
  background: #fff;
  border-radius: 24rpx;
  margin-bottom: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
  box-sizing: border-box;
  width: 100%;
  overflow: hidden;
}

.section-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #999;
  margin-bottom: 30rpx;
  display: block;
}

.help-item {
  margin-bottom: 30rpx;
}

.help-item:last-child {
  margin-bottom: 0;
}

.help-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.help-content {
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
  display: block;
  white-space: pre-line;
  word-break: break-all;
  word-wrap: break-word;
}
</style>
