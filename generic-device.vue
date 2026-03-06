<template>
  <view class="container">
    <!-- 设备页面顶部栏 -->
    <DeviceHeader
      ref="deviceHeader"
      :mac="mac"
      @message="onMessage"
      @ready="onReady"
    />

    <view class="content">
      <!-- 设备描述 -->
      <view v-if="preferences.showDescription && spec && spec.description" class="description-section">
        <text class="description-text">{{ spec.description }}</text>
      </view>

      <!-- 数据展示区域 -->
      <view v-if="uplinkFields.length > 0" class="section">
        <text class="section-title">数据</text>
        <view class="data-cards">
          <view
            v-for="field in uplinkFields"
            :key="field.name"
            class="data-card"
          >
            <text class="data-label">{{ field.label }}</text>
            <view class="data-value-wrapper">
              <text class="data-value">{{ formatValue(field, true) }}</text>
              <text class="data-unit" v-if="field.unit">{{ field.unit }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 控制区域 -->
      <view v-if="downlinkFields.length > 0" class="section">
        <text class="section-title">控制</text>
        <view class="control-section">
          <view
            v-for="field in downlinkFields"
            :key="field.name"
            class="control-row"
          >
            <text class="control-label">{{ field.label }}</text>
            <switch
              v-if="field.format === 'bool'"
              :checked="controlValues[field.name]"
              @change="handleSwitchChange(field.name, $event)"
              :color="accentColor"
            />
            <view v-else class="control-input-group">
              <view class="control-input-wrapper">
                <input
                  type="number"
                  v-model="controlValues[field.name]"
                  :placeholder="field.unit || ''"
                  class="control-input"
                />
                <text class="input-unit" v-if="field.unit">{{ field.unit }}</text>
              </view>
            </view>
          </view>
          <button class="send-btn" @tap="sendDownlink" :disabled="!canInteract">
            <text class="btn-text">发送命令</text>
          </button>
        </view>
      </view>

      <view v-if="uplinkFields.length === 0 && downlinkFields.length === 0" class="no-data">
        <view class="no-data-icon">
        <uni-icons type="refresh" size="80" color="#ccc"></uni-icons>
      </view>
        <text class="no-data-text">等待设备数据...</text>
      </view>

      <!-- 设备信息 -->
      <view class="device-info-section">
        <view class="device-info-header" @tap="toggleDeviceInfo">
          <text class="device-info-title">设备信息</text>
          <uni-icons :type="showDeviceInfo ? 'down' : 'right'" size="24" color="#999"></uni-icons>
        </view>
        <view v-if="showDeviceInfo" class="device-info-content">
          <view v-if="preferences.showDeviceType" class="info-row">
            <text class="info-label">设备类型</text>
            <text class="info-value">{{ deviceType }}</text>
          </view>
          <view v-if="preferences.showMAC" class="info-row">
            <text class="info-label">MAC 地址</text>
            <text class="info-value">{{ formatMac(mac) }}</text>
          </view>
          <view v-if="preferences.showVersion && spec && spec.version" class="info-row">
            <text class="info-label">版本</text>
            <text class="info-value">{{ spec.version }}</text>
          </view>
        </view>
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
      deviceType: '',
      mac: '',
      connection: null,
      uplinkData: {},
      controlValues: {},
      preferences: Preferences.getAll(),
      showDeviceInfo: false,
      accentColor: Preferences.getAccentColor(),
    };
  },

  computed: {
    spec() {
      return specs[this.deviceType] || null;
    },

    deviceTitle() {
      if (!this.spec) return '设备详情';
      return this.spec.fullName || this.spec.deviceType;
    },

    // 是否可以与设备交互
    canInteract() {
      const state = this.connection?.reactiveState;
      return this.connection?.enabled && state?.physicalState === 'connected';
    },

    uplinkFields() {
      if (!this.spec?.uplink) return [];
      return this.spec.uplink.map(field => ({
        ...field,
        label: this.formatLabel(field.name),
        value: this.uplinkData[field.name]
      }));
    },

    downlinkFields() {
      if (!this.spec?.downlink) return [];
      return this.spec.downlink.map(field => ({
        ...field,
        label: this.formatLabel(field.name)
      }));
    }
  },

  onLoad(options) {
    this.deviceType = options.deviceType || '';
    this.mac = options.mac || '';

    if (!this.spec) {
      uni.showToast({ title: '未知设备类型', icon: 'none' });
      return;
    }

    // 动态设置导航栏标题为 fullName
    if (this.spec.fullName) {
      uni.setNavigationBarTitle({
        title: this.spec.fullName
      });
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
      this.uplinkData = {};
      data.forEach((item) => {
        this.uplinkData[item.name] = item.value;
      });
    },

    formatLabel(name) {
      return name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    },

    formatValue(field, valueOnly = false) {
      const value = field.value;
      if (value === undefined || value === null) return '--';
      if (typeof value === 'boolean') return value ? '开' : '关';
      if (valueOnly) return String(value);
      return field.unit ? `${value} ${field.unit}` : String(value);
    },

    handleSwitchChange(name, event) {
      this.controlValues[name] = event.detail.value;
    },

    sendDownlink() {
      if (!this.canInteract) {
        uni.showToast({ title: '设备未连接', icon: 'none' });
        return;
      }

      if (this.connection && this.connection.connected) {
        this.connection.send(this.controlValues);
        uni.showToast({ title: '命令已发送', icon: 'success' });
      }
    },

    toggleDeviceInfo() {
      this.showDeviceInfo = !this.showDeviceInfo;
    },
  }
};
</script>

<style lang="scss">
@import "@/src/styles/mixins.scss";

.container {
  @include page-container;
}

.content {
  padding: $page-padding;
}

.description-section {
  @include card;
  margin-bottom: $section-gap;
}

.description-text {
  font-size: 28rpx;
  color: $uni-text-color-secondary;
  line-height: 1.6;
}

/* 区域分隔 */
.section {
  margin-bottom: $section-gap;
}

.section-title {
  @include section-title;
}

/* 数据卡片 */
.data-cards {
  display: flex;
  flex-wrap: wrap;
  gap: $card-gap;
}

.data-card {
  @include card-lg;
  min-width: 280rpx;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.data-card .data-label {
  font-size: 28rpx;
  color: $uni-text-color-secondary;
  margin-bottom: $uni-spacing-col-lg;
}

.data-value-wrapper {
  display: flex;
  align-items: baseline;
  gap: $uni-spacing-row-sm;
}

.data-card .data-value {
  font-size: 72rpx;  // 从 56rpx 增大，更突出
  font-weight: 600;
  color: v-bind(accentColor);
  line-height: 1;
}

.data-card .data-unit {
  font-size: 28rpx;
  color: $uni-text-color-grey;
}

/* 控制区域 */
.control-section {
  @include card;
  padding: 20rpx $card-padding;
}

.control-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx 0;
  border-bottom: 1rpx solid $uni-border-color-light;
}

.control-row:last-of-type {
  border-bottom: none;
}

.control-label {
  font-size: 30rpx;
  color: $uni-text-color;
}

/* 输入框组 */
.control-input-group {
  display: flex;
  align-items: center;
  gap: $uni-spacing-row-base;
}

.control-input-wrapper {
  display: flex;
  align-items: center;
  background-color: $uni-bg-color-grey;
  border-radius: $uni-border-radius-sm;
  padding: 4rpx 4rpx 4rpx 20rpx;
}

.control-input {
  width: 100rpx;
  padding: 12rpx 0;
  font-size: 30rpx;
  text-align: right;
  background: transparent;
  border: none;
}

.input-unit {
  font-size: 26rpx;
  color: $uni-text-color-grey;
  padding: 0 16rpx;
}

/* 发送按钮 */
.send-btn {
  margin-top: $section-gap;
  background-color: v-bind(accentColor);
  color: $uni-text-color-inverse;
  border-radius: $uni-border-radius-base;
  padding: 28rpx 0;
  font-size: 30rpx;
  border: none;
}

.send-btn[disabled] {
  background-color: #ccc;
}

.send-btn:active {
  opacity: 0.8;
}

.btn-text {
  font-weight: 500;
}

/* 无数据状态 */
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
}

.no-data-icon {
  margin-bottom: $uni-spacing-col-lg;
}

.no-data-text {
  font-size: 28rpx;
  color: $uni-text-color-grey;
}

/* 设备信息 */
.device-info-section {
  margin-top: $section-gap;
  background-color: $uni-bg-color;
  border-radius: $uni-border-radius-lg;
  overflow: hidden;
  box-shadow: $shadow-md;
}

.device-info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28rpx $card-padding;
  background-color: $uni-bg-color-grey;
}

.device-info-title {
  font-size: 28rpx;
  font-weight: 500;
  color: $uni-text-color-secondary;
}

.device-info-content {
  padding: 20rpx $card-padding;
}

.info-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $uni-border-color-light;
}

.info-row:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 28rpx;
  color: $uni-text-color-grey;
}

.info-value {
  font-size: 28rpx;
  color: $uni-text-color;
  font-weight: 500;
}
</style>
