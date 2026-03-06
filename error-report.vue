<template>
  <view class="container">
    <view class="error-icon">
      <uni-icons type="info-filled" size="60" color="#fff"></uni-icons>
    </view>

    <text class="error-title">连接失败</text>

    <view class="user-hint">
      <text class="hint-title">请确保：</text>
      <text class="hint-item">• 设备在手机附近</text>
      <text class="hint-item">• 设备已开启</text>
      <text class="hint-item">• 尝试重新靠近</text>
    </view>

    <view class="divider"></view>

    <view class="dev-info">
      <text class="dev-title">设备信息</text>
      <text class="dev-item">DeviceID: {{ deviceId || '--' }}</text>
      <text class="dev-item">Error: {{ errorMessage }}</text>
    </view>

    <button class="retry-btn" @tap="handleRetry">重 试</button>
  </view>
</template>

<script>
import Preferences from '@/src/preferences';

export default {
  data() {
    return {
      deviceId: '',
      errorCode: '',
      accentColor: Preferences.getAccentColor(),
    }
  },
  computed: {
    errorMessage() {
      const errorMap = {
        'E0001': '设备未找到',
        'E0002': '连接失败',
        'E0003': '连接超时'
      }
      return errorMap[this.errorCode] || this.errorCode || '未知错误'
    }
  },
  onLoad(options) {
    this.deviceId = options.deviceId || ''
    this.errorCode = options.error || 'E0002'
  },
  onShow() {
    this.accentColor = Preferences.getAccentColor();
  },
  methods: {
    handleRetry() {
      uni.navigateBack()
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  padding-top: var(--status-bar-height);
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-left: 40rpx;
  padding-right: 40rpx;
  padding-bottom: 100rpx;
  box-sizing: border-box;
}

.error-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background-color: v-bind(accentColor);
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-title {
  margin-top: 40rpx;
  font-size: 40rpx;
  font-weight: 500;
  color: #333;
}

.user-hint {
  margin-top: 60rpx;
  width: 100%;
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
}

.hint-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #333;
}

.hint-item {
  display: block;
  margin-top: 16rpx;
  font-size: 28rpx;
  color: #666;
}

.divider {
  width: 100%;
  height: 1rpx;
  background-color: #e0e0e0;
  margin: 40rpx 0;
}

.dev-info {
  width: 100%;
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
}

.dev-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #999;
}

.dev-item {
  display: block;
  margin-top: 12rpx;
  font-size: 24rpx;
  color: #999;
  font-family: monospace;
}

.retry-btn {
  margin-top: 60rpx;
  width: 60%;
  background-color: v-bind(accentColor);
  color: #fff;
  border-radius: 16rpx;
  font-size: 32rpx;
}

.retry-btn:active {
  opacity: 0.8;
}
</style>