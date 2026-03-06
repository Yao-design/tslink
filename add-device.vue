<template>
  <view class="container">
    <!-- 扫描控制区域 -->
    <view class="scan-section">
      <view class="scan-animation" @tap="toggleScan">
        <view :class="['scan-circle', isScanning ? 'scanning' : '']">
          <uni-icons 
            class="scan-icon"
            :class="{ 'is-scanning': isScanning }"
            :type="isScanning ? 'close' : 'search'" 
            size="64" 
            color="#666"
          ></uni-icons>
        </view>
        <text class="scan-text">{{ isScanning ? '点击停止扫描' : '点击开始扫描' }}</text>
      </view>
    </view>

    <!-- 附近的设备列表 -->
    <scroll-view class="device-list" scroll-y>
      <view class="list-header">
        <text class="list-title">附近的设备</text>
        <text v-if="isScanning" class="scanning-badge">扫描中</text>
      </view>

      <view
        v-for="device in nearbyDevices"
        :key="device.deviceId"
        class="device-item"
        @tap="addDevice(device)"
      >
        <!-- 第一行：图标 + 名称 + 添加按钮 -->
        <view class="device-header-row">
          <view class="device-icon">
            <uni-icons :type="getDeviceIcon(device.deviceType)" size="40" color="#666"></uni-icons>
          </view>
          <view class="device-title">
            <text class="device-name">{{ getFullName(device) }}</text>
          </view>
          <view class="device-action">
            <text :class="['add-text', isKnownDevice(device.mac) ? 'added' : '']">
              {{ isKnownDevice(device.mac) ? '已添加' : '添加' }}
            </text>
          </view>
        </view>
        
        <!-- 第二行：描述（独立一行） -->
        <text v-if="getDescription(device)" class="device-description">
          {{ getDescription(device) }}
        </text>
        
        <!-- 第三行：技术信息横向排列 -->
        <view class="device-meta-row">
          <!-- 信号强度 -->
          <view class="meta-item">
            <uni-icons type="wifi" size="16" color="#999"></uni-icons>
            <view class="signal-bars">
              <view :class="['bar', 'weak', device.signalLevel >= 1 ? 'active' : '']"></view>
              <view :class="['bar', device.signalLevel >= 2 ? 'medium active' : '']"></view>
              <view :class="['bar', device.signalLevel >= 3 ? 'medium active' : '']"></view>
              <view :class="['bar', device.signalLevel >= 4 ? 'strong active' : '']"></view>
            </view>
            <text v-if="device.rssi" :class="['meta-text', 'signal-text', device.signalLevel <= 1 ? 'weak-text' : '', device.signalLevel >= 4 ? 'strong-text' : '']">{{ device.rssi }}dBm</text>
          </view>
          
          <!-- MAC 地址（完整显示） -->
          <view class="meta-item mac-address">
            <uni-icons type="link" size="16" color="#999"></uni-icons>
            <text class="meta-text">{{ device.mac }}</text>
          </view>
        </view>
      </view>

      <!-- 空状态 -->
      <view v-if="nearbyDevices.length === 0 && !isScanning" class="empty-state">
        <text class="empty-text">未发现附近的设备</text>
        <text class="empty-hint">点击上方扫描按钮查找设备</text>
      </view>

      <!-- 扫描中 -->
      <view v-if="isScanning && nearbyDevices.length === 0" class="scanning-state">
        <view class="scanning-spinner"></view>
        <text class="scanning-text">正在扫描附近设备...</text>
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
      nearbyDevices: [],
      knownDevices: [],
      isScanning: false,
      accentColor: Preferences.getAccentColor(),
      _deviceUpdateHandler: null,  // 设备更新回调函数引用
    };
  },

  onLoad() {
    this.loadKnownDevices();
    this.setupNearbyDevicesListener();
  },

  onShow() {
    this.accentColor = Preferences.getAccentColor();
  },

  onUnload() {
    this.stopScan();
    this.cleanupNearbyDevicesListener();
  },

  methods: {
    loadKnownDevices() {
      this.knownDevices = BLE.getKnownDevices();
    },

    setupNearbyDevicesListener() {
      // 监听设备列表变化（新设备添加）
      BLE.onNearbyDevicesChange((devices) => {
        this.nearbyDevices = devices;
      });

      // 监听单个设备更新（RSSI 变化等），实现精确更新
      this._deviceUpdateHandler = (updatedDevice) => {
        const index = this.nearbyDevices.findIndex(d => d.deviceId === updatedDevice.deviceId);
        if (index !== -1) {
          // 使用 Vue.set 或替换对象以确保响应式更新
          this.$set(this.nearbyDevices, index, { ...this.nearbyDevices[index], ...updatedDevice });
        }
      };
      BLE.onDeviceUpdate(this._deviceUpdateHandler);
    },

    cleanupNearbyDevicesListener() {
      BLE.offNearbyDevicesChange();
      if (this._deviceUpdateHandler) {
        BLE.offDeviceUpdate(this._deviceUpdateHandler);
        this._deviceUpdateHandler = null;
      }
    },

    toggleScan() {
      if (this.isScanning) {
        this.stopScan();
      } else {
        this.startScan();
      }
    },

    startScan() {
      this.isScanning = true;
      this.nearbyDevices = [];
      BLE.startScan();
    },

    stopScan() {
      this.isScanning = false;
      BLE.stopScan();
    },

    addDevice(device) {
      if (BLE.addDevice(device.mac, {
        name: device.name,
        deviceType: device.deviceType,
        deviceId: device.deviceId,
      })) {
        uni.showToast({
          title: '添加成功',
          icon: 'success',
        });
        this.loadKnownDevices();
      } else {
        uni.showToast({
          title: '添加失败',
          icon: 'none',
        });
      }
    },

    isKnownDevice(mac) {
      return this.knownDevices.some(d => d.mac === mac);
    },

    navigateBack() {
      uni.navigateBack();
    },

    getDeviceIcon(deviceType) {
      // 设备类型图标映射（使用 uni-icons 类型名）
      const iconMap = {
        'HR': 'heart-filled',      // 心率设备
        'CNTR': 'calendar',        // 计数器
        'LED': 'lightbulb',        // LED 控制器
        'TMP': 'thermometer',      // 温度传感器
        'TP': 'cart-filled',       // 胎压监测（使用购物车图标作为车的替代）
      };
      return iconMap[deviceType] || 'phone-filled';
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
  },
};
</script>

<style lang="scss">
@import "@/src/styles/mixins.scss";

.container {
  @include page-container;
}

/* 扫描区域 */
.scan-section {
  background-color: $uni-bg-color;
  padding: 60rpx $page-padding;
  display: flex;
  justify-content: center;
  align-items: center;
}

.scan-animation {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scan-circle {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background-color: $uni-bg-color-grey;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.scan-circle.scanning {
  background-color: v-bind(accentColor + '1A');
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 v-bind(accentColor + '66');
  }
  70% {
    box-shadow: 0 0 0 30rpx v-bind(accentColor + '00');
  }
  100% {
    box-shadow: 0 0 0 0 v-bind(accentColor + '00');
  }
}

.scan-text {
  margin-top: $uni-spacing-col-lg;
  font-size: 28rpx;
  color: $uni-text-color-secondary;
}

.scan-icon {
  transition: color 0.3s ease;
}

.scan-icon.is-scanning {
  color: v-bind(accentColor) !important;
}

/* 设备列表 */
.device-list {
  padding: $page-padding;
  width: 100%;
  box-sizing: border-box;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: $card-gap;
  padding: 0 $uni-spacing-row-sm;
}

.list-title {
  font-size: 28rpx;
  color: $uni-text-color-secondary;
}

.scanning-badge {
  font-size: 24rpx;
  color: v-bind(accentColor);
  background-color: v-bind(accentColor + '1A');
  padding: 8rpx 16rpx;
  border-radius: 100rpx;
}

.device-item {
  @include card;
  margin-bottom: $card-gap;
  display: flex;
  flex-direction: column;
  padding: 24rpx;
}

.device-item:active {
  opacity: 0.8;
}

/* 第一行：图标 + 名称 + 添加按钮 */
.device-header-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.device-icon {
  width: 72rpx;
  height: 72rpx;
  background-color: $uni-bg-color-grey;
  border-radius: $uni-border-radius-base;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: $uni-spacing-row-lg;
  flex-shrink: 0;
}

.device-title {
  flex: 1;
  min-width: 0;
}

.device-name {
  font-size: 32rpx;
  font-weight: 500;
  color: $uni-text-color;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 第二行：描述 */
.device-description {
  display: block;
  font-size: 26rpx;
  color: $uni-text-color-secondary;
  line-height: 1.4;
  margin-bottom: 20rpx;
  margin-left: 96rpx; /* 与图标对齐 */
}

/* 第三行：技术信息 */
.device-meta-row {
  display: flex;
  align-items: center;
  gap: 24rpx;
  margin-left: 96rpx; /* 与图标对齐 */
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.meta-text {
  font-size: 22rpx;
  color: $uni-text-color-grey;
}

/* 信号强度 */
.signal-bars {
  display: flex;
  align-items: flex-end;
  gap: 3rpx;
  height: 20rpx;
}

.bar {
  width: 4rpx;
  background-color: $uni-border-color;
  border-radius: 2rpx;
  transition: background-color 0.3s;
}

.bar:nth-child(1) { height: 6rpx; }
.bar:nth-child(2) { height: 10rpx; }
.bar:nth-child(3) { height: 14rpx; }
.bar:nth-child(4) { height: 18rpx; }

.bar.active {
  background-color: $uni-color-success;
}

/* 信号强度颜色分级 */
.bar.weak.active {
  background-color: $uni-color-error;
}

.bar.medium.active {
  background-color: $uni-color-warning;
}

.bar.strong.active {
  background-color: $uni-color-success;
}

/* 信号强度文字颜色 */
.signal-text.weak-text {
  color: $uni-color-error;
}

.signal-text.strong-text {
  color: $uni-color-success;
}

/* 设备类型标签 */
.device-type-tag {
  background-color: $uni-bg-color-grey;
  padding: 4rpx 12rpx;
  border-radius: $uni-border-radius-sm;
}

.device-type-tag .meta-text {
  font-size: 20rpx;
  color: $uni-text-color-secondary;
  font-weight: 500;
}

/* 添加按钮 */
.device-action {
  margin-left: $uni-spacing-row-lg;
  flex-shrink: 0;
}

.add-text {
  font-size: 28rpx;
  color: v-bind(accentColor);
  padding: 12rpx 24rpx;
  background-color: v-bind(accentColor + '1A');
  border-radius: 100rpx;
}

.add-text.added {
  color: $uni-text-color-grey;
  background-color: $uni-bg-color-grey;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.empty-text {
  font-size: 32rpx;
  color: $uni-text-color-secondary;
}

.empty-hint {
  margin-top: $uni-spacing-col-lg;
  font-size: 26rpx;
  color: $uni-text-color-grey;
}

/* 扫描中状态 */
.scanning-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.scanning-spinner {
  width: 60rpx;
  height: 60rpx;
  border: 4rpx solid $uni-bg-color-grey;
  border-top-color: $uni-color-primary;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: $uni-spacing-col-lg;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.scanning-text {
  font-size: 28rpx;
  color: $uni-text-color-secondary;
}
</style>