<template>
  <view class="container">
    <!-- 顶部操作栏 -->
    <view class="header">
      <view class="logo">
        <image src="/static/ts_logo.png" mode="heightFix" class="logo-image" />
        <text class="logo-text">TSLink</text>
      </view>
      <view class="add-btn" @tap="navigateToAddDevice">
        <uni-icons type="plus" size="32" color="#666"></uni-icons>
      </view>
    </view>

    <!-- 已保存的设备列表 -->
    <scroll-view class="device-list" scroll-y>
      <view
        v-for="device in knownDevices"
        :key="device.mac"
        class="device-item"
        @tap="onDeviceClick(device)"
        @longpress="onDeviceLongPress(device)"
      >
        <view class="device-icon">
          <uni-icons :type="getDeviceIcon(device.deviceType)" size="40" color="#666"></uni-icons>
        </view>
        <view class="device-info">
          <text class="device-name">{{ getFullName(device) }}</text>
          <text class="device-description">
            {{ getDescription(device) }}
          </text>
          <view class="device-technical">
            <text class="tech-item">MAC: {{ device.mac }}</text>
            <text v-if="device.rssi" class="tech-item">信号: {{ device.rssi }}dBm</text>
          </view>
        </view>
        <view class="device-arrow">
          <text class="arrow-text">›</text>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="knownDevices.length === 0" class="empty-state">
        <uni-icons type="phone" size="80" color="#ddd"></uni-icons>
        <text class="empty-text">暂无设备</text>
        <text class="empty-hint">点击右上角 + 添加第一个设备</text>
      </view>
    </scroll-view>

    <!-- 全局调试组件 -->
    <GlobalDebug :accentColor="accentColor" />
  </view>
</template>

<script>
import { BLE } from '@/src/ble';
import { router } from '@/src/router';
import { specs } from '@/src/tslink_spec';
import Preferences from '@/src/preferences';
import GlobalDebug from '@/src/components/global-debug.vue';

export default {
  components: {
    GlobalDebug,
  },

  data() {
    return {
      knownDevices: [],
      accentColor: Preferences.getAccentColor(),
    };
  },

  onLoad() {
    this.loadKnownDevices();
    this.setupDeviceChangeListener();
  },

  onShow() {
    this.accentColor = Preferences.getAccentColor();
  },

  onUnload() {
    this.cleanupDeviceChangeListener();
  },

  methods: {
    loadKnownDevices() {
      this.knownDevices = BLE.getKnownDevices();
    },

    setupDeviceChangeListener() {
      BLE.onKnownDevicesChange(this.loadKnownDevices);
    },

    cleanupDeviceChangeListener() {
      BLE.offKnownDevicesChange(this.loadKnownDevices);
    },

    navigateToAddDevice() {
      router.navigateToAddDevice();
    },

    onDeviceClick(device) {
      router.navigateToDevice(device);
    },

    onDeviceLongPress(device) {
      uni.showModal({
        title: '设备操作',
        content: `请选择对 "${this.getFullName(device)}" 的操作`,
        confirmText: '删除',
        confirmColor: '#ff4d4f',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            this.deleteDevice(device);
          }
        }
      });
    },

    deleteDevice(device) {
      const success = BLE.removeDevice(device.mac);
      if (success) {
        uni.showToast({
          title: '已删除',
          icon: 'success',
        });
      } else {
        uni.showToast({
          title: '删除失败',
          icon: 'error',
        });
      }
    },

    getSpec(deviceType) {
      return specs[deviceType] || null;
    },

    getFullName(device) {
      const spec = this.getSpec(device.deviceType);
      return spec ? spec.fullName : device.name;
    },

    getDescription(device) {
      const spec = this.getSpec(device.deviceType);
      return spec ? spec.description : '';
    },

    getDeviceIcon(deviceType) {
      // 设备类型图标映射（使用 uni-icons 类型名）
      const iconMap = {
        'HR': 'heart-filled',      // 心率设备
        'CNTR': 'calendar',        // 计数器
        'LED': 'lightbulb',        // LED 控制器
        'TMP': 'thermometer',      // 温度传感器
        'TP': 'shop',              // 胎压监测
      };
      return iconMap[deviceType] || 'phone-filled';
    },
  },
};
</script>

<style lang="scss">
@import "@/src/styles/mixins.scss";

.container {
  @include page-container;
}

.header {
  padding: $uni-spacing-col-lg $page-padding;
  background-color: $uni-bg-color;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: $shadow-sm;
}

.logo {
  display: flex;
  align-items: center;
}

.logo-image {
  height: 48rpx;
  margin-right: $uni-spacing-row-base;
}

.logo-text {
  font-size: 36rpx;
  font-weight: 600;
  color: $uni-text-color;
}

.add-btn {
  width: 64rpx;
  height: 64rpx;
  background-color: $uni-bg-color-grey;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.add-btn:active {
  background-color: $uni-border-color;
  transform: scale(0.95);
}

.device-list {
  padding: $page-padding;
  width: 100%;
  box-sizing: border-box;
}

.device-item {
  @include list-item;
}

.device-icon {
  @include device-icon-container;
}

.device-info {
  flex: 1;
}

.device-name {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
  display: block;
}

.device-description {
  display: block;
  margin-top: $uni-spacing-col-sm;
  font-size: 26rpx;
  color: $uni-text-color-secondary;
  line-height: 1.4;
}

.device-technical {
  display: flex;
  flex-wrap: wrap;
  gap: $uni-spacing-row-base;
  margin-top: 12rpx;
}

.tech-item {
  font-size: 22rpx;
  color: $uni-text-color-grey;
  background: $uni-bg-color-grey;
  padding: 6rpx 12rpx;
  border-radius: $uni-border-radius-sm;
}

.device-arrow {
  margin-left: $uni-spacing-row-lg;
}

.arrow-text {
  font-size: 40rpx;
  color: $uni-text-color-grey;
  font-weight: 300;
}

.empty-state {
  @include empty-state;
}

.empty-state uni-icons {
  margin-bottom: $uni-spacing-col-lg;
}

.empty-text {
  @include empty-text;
}

.empty-hint {
  @include empty-hint;
}
</style>