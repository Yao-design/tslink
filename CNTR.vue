<template>
  <view class="container">
    <!-- 设备页面顶部栏 -->
    <DeviceHeader
      ref="deviceHeader"
      :mac="mac"
      @message="onMessage"
      @ready="onReady"
    />

    <!-- 主内容区 -->
    <view class="main-content">
      <!-- 计数值（中心焦点） -->
      <view class="counter-area">
        <text class="counter-value">{{ displayCount }}</text>
      </view>
    </view>

    <!-- 设备信息（在按钮上方） -->
    <view class="footer">
      <text class="device-info">{{ formatMac(mac) }} · {{ spec?.version || 'v1.0.0' }}</text>
    </view>

    <!-- 重置按钮（固定底部） -->
    <view class="action-area" @tap.stop>
      <view
        :class="['reset-btn', { disabled: !canInteract }]"
        @tap="handleReset"
      >
        <text class="reset-btn-text">重 置</text>
      </view>
    </view>

    <!-- 全局调试组件 -->
    <GlobalDebug :accentColor="accentColor" />
  </view>
</template>

<script>
import { specs } from '@/src/tslink_spec';
import Preferences from '@/src/preferences';
import DeviceHeader from '@/src/components/device-header.vue';
import GlobalDebug from '@/src/components/global-debug.vue';
import { formatMac } from '@/src/ble';

export default {
  components: {
    DeviceHeader,
    GlobalDebug,
  },
  data() {
    return {
      deviceType: 'CNTR',
      mac: '',
      count: 0,
      connection: null,
      // 偏好设置
      preferences: Preferences.getAll(),
      accentColor: Preferences.getAccentColor(),
    }
  },

  computed: {
    spec() {
      return specs[this.deviceType] || null;
    },

    displayCount() {
      return this.count.toLocaleString()
    },

    // 是否可以与设备交互
    canInteract() {
      const state = this.connection?.reactiveState;
      return this.connection?.enabled && state?.physicalState === 'connected';
    },
  },

  onLoad(options) {
    if (options.deviceType) {
      this.deviceType = options.deviceType
    }
    if (options.mac) {
      this.mac = options.mac
    }
  },

  onShow() {
    this.preferences = Preferences.getAll();
    this.accentColor = Preferences.getAccentColor();
  },

  methods: {
    formatMac,  // 暴露公共函数给模板使用

    onReady({ connection }) {
      this.connection = connection;
    },

    onMessage({ data }) {
      data.forEach((item) => {
        if (item.name === 'count') {
          this.count = item.value
        }
      })
    },

    handleReset() {
      if (!this.canInteract) {
        return
      }

      this.connection.send({ reset: true })
      uni.showToast({
        title: '已重置',
        icon: 'success'
      })
    },
  }
}
</script>

<style>
.container {
  height: 100vh;
  padding-top: var(--status-bar-height);
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

/* 主内容区（占据剩余空间，计数值居中） */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 30rpx 40rpx;
  min-height: 0;
}

/* 计数值区域 */
.counter-area {
  display: flex;
  justify-content: center;
  align-items: center;
}

.counter-value {
  font-size: 120rpx;
  font-weight: 700;
  color: v-bind(accentColor);
  line-height: 1;
}

/* 设备信息（按钮上方） */
.footer {
  padding: 16rpx 30rpx;
  display: flex;
  justify-content: flex-end;
  flex-shrink: 0;
}

.device-info {
  font-size: 24rpx;
  color: #999;
}

/* 重置按钮区域（固定底部） */
.action-area {
  padding: 20rpx 40rpx 40rpx;
  flex-shrink: 0;
}

.reset-btn {
  width: 100%;
  height: 100rpx;
  background-color: v-bind(accentColor);
  border-radius: 16rpx;
  display: flex;
  justify-content: center;
  align-items: center;
}

.reset-btn.disabled {
  background-color: #e0e0e0;
}

.reset-btn:active:not(.disabled) {
  opacity: 0.85;
  transform: scale(0.98);
}

.reset-btn-text {
  font-size: 36rpx;
  font-weight: 500;
  color: #fff;
}

.reset-btn.disabled .reset-btn-text {
  color: #999;
}
</style>