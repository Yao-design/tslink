<template>
  <view class="container">
    <scroll-view class="content" scroll-y>
      <!-- 个性化 -->
      <view class="section">
        <text class="section-title">个性化</text>
        
        <!-- 个性色 -->
        <view class="setting-item">
          <view class="setting-info">
            <text class="setting-name">主题颜色</text>
            <text class="setting-desc">选择你喜欢的界面颜色</text>
          </view>
          <view class="color-preview" :style="{ backgroundColor: currentAccentColor }"></view>
        </view>
        <view class="color-grid">
          <view
            v-for="color in accentColors"
            :key="color.value"
            class="color-item"
            @tap="selectAccentColor(color)"
          >
            <view
              :class="['color-circle', currentAccentColor === color.value ? 'active' : '']"
              :style="{ backgroundColor: color.value, color: color.value }"
            >
              <text v-if="currentAccentColor === color.value" class="color-check">✓</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 设备连接 -->
      <view class="section">
        <text class="section-title">设备连接</text>
        
        <view class="setting-item">
          <view class="setting-info">
            <text class="setting-name">自动连接</text>
            <text class="setting-desc">进入设备页面时自动连接设备</text>
          </view>
          <switch
            :checked="preferences.autoConnectMode === 'auto'"
            @change="toggleAutoConnect"
            :color="currentAccentColor"
          />
        </view>
      </view>

      <!-- 数据管理 -->
      <view class="section">
        <text class="section-title">数据管理</text>
        
        <view class="action-item" @tap="exportDeviceData">
          <view class="action-info">
            <text class="action-name">导出设备配置</text>
            <text class="action-desc">将所有设备配置导出为JSON文件</text>
          </view>
          <uni-icons type="right" size="20" color="#ccc"></uni-icons>
        </view>
        
        <view class="action-item" @tap="clearAllData">
          <view class="action-info">
            <text class="action-name">清除所有数据</text>
            <text class="action-desc">删除所有已保存设备和日志</text>
          </view>
          <uni-icons type="right" size="20" color="#ccc"></uni-icons>
        </view>
      </view>

      <!-- 开发者选项 -->
      <view class="section">
        <text class="section-title">开发者选项</text>

        <view class="setting-item">
          <view class="setting-info">
            <text class="setting-name">调试面板</text>
            <text class="setting-desc">点击悬浮按钮打开调试面板</text>
          </view>
          <switch
            :checked="preferences.debugPanelEnabled"
            @change="toggleDebugPanel"
            :color="currentAccentColor"
          />
        </view>

        <view class="setting-item">
          <view class="setting-info">
            <text class="setting-name">显示非 TSLink 设备</text>
            <text class="setting-desc">在调试面板中记录扫描到的非 TSLink 设备</text>
          </view>
          <switch
            :checked="preferences.showNonTSLink"
            @change="toggleShowNonTSLink"
            :color="currentAccentColor"
          />
        </view>

      </view>

      <!-- 关于与帮助 -->
      <view class="section">
        <text class="section-title">关于与帮助</text>
        
        <view class="action-item" @tap="goToHelp">
          <view class="action-info">
            <text class="action-name">使用帮助</text>
            <text class="action-desc">查看TSLink使用指南</text>
          </view>
          <uni-icons type="right" size="20" color="#ccc"></uni-icons>
        </view>
        
        <view class="action-item" @tap="goToFeedback">
          <view class="action-info">
            <text class="action-name">反馈问题</text>
            <text class="action-desc">向我们反馈使用中遇到的问题</text>
          </view>
          <uni-icons type="right" size="20" color="#ccc"></uni-icons>
        </view>

        <!-- 关于信息 -->
        <view class="about-item">
          <image src="/static/ts_logo.png" mode="heightFix" class="about-logo" />
          <text class="app-name">TSLink</text>
          <text class="app-version">版本 {{ appVersion }}</text>
          <text class="app-company">TechStorm</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import Preferences from '@/src/preferences';
import { BLE } from '@/src/ble';
import debugEvents from '@/src/debug-events';

export default {
  data() {
    return {
      preferences: Preferences.getAll(),
      currentAccentColor: Preferences.getAccentColor(),
      appVersion: '1.0.0',
      accentColors: Preferences.ACCENT_COLORS,
    };
  },

  onShow() {
    this.preferences = Preferences.getAll();
    this.currentAccentColor = Preferences.getAccentColor();
  },

  methods: {
    // 选择个性色
    selectAccentColor(color) {
      Preferences.setAccentColor(color.value);
      this.currentAccentColor = color.value;
      uni.showToast({ title: '已更换主题色', icon: 'success' });
    },

    // 切换自动连接模式
    toggleAutoConnect(e) {
      const mode = e.detail.value ? 'auto' : 'manual';
      Preferences.set('autoConnectMode', mode);
      this.preferences.autoConnectMode = mode;
    },

    // 导出设备数据
    exportDeviceData() {
      uni.showModal({
        title: '导出设备配置',
        content: '这将导出所有已保存设备的配置信息',
        confirmText: '导出',
        success: (res) => {
          if (res.confirm) {
            // 获取设备数据并导出
            const devices = BLE.getKnownDevices();
            const data = JSON.stringify(devices, null, 2);
            
            // #ifdef H5
            const blob = new Blob([data], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'tslink_devices.json';
            a.click();
            URL.revokeObjectURL(url);
            // #endif
            
            uni.showToast({ title: '导出成功', icon: 'success' });
          }
        }
      });
    },

    // 清除所有数据
    clearAllData() {
      uni.showModal({
        title: '清除所有数据',
        content: '确定要删除所有已保存设备和日志吗？此操作不可恢复。',
        confirmText: '清除',
        confirmColor: '#F44336',
        success: (res) => {
          if (res.confirm) {
            // 清除设备数据
            const devices = BLE.getKnownDevices();
            devices.forEach(device => {
              BLE.removeDevice(device.mac);
            });
            
            uni.showToast({ title: '已清除', icon: 'success' });
          }
        }
      });
    },

    // 跳转到帮助页面
    goToHelp() {
      uni.navigateTo({ url: '/pages/common/help' });
    },

    // 跳转到反馈页面
    goToFeedback() {
      uni.navigateTo({ url: '/pages/common/feedback' });
    },

    // 切换调试面板
    toggleDebugPanel(e) {
      const enabled = e.detail.value;
      Preferences.setDebugPanelEnabled(enabled);
      this.preferences.debugPanelEnabled = enabled;
      
      // 同步到调试事件管理器
      debugEvents.setEnabled(enabled);
      
      uni.showToast({
        title: enabled ? '调试面板已开启' : '调试面板已关闭',
        icon: 'none'
      });
    },

    // 切换显示非 TSLink 设备
    toggleShowNonTSLink(e) {
      const enabled = e.detail.value;
      Preferences.set('showNonTSLink', enabled);
      this.preferences.showNonTSLink = enabled;
      
      uni.showToast({
        title: enabled ? '已开启非 TSLink 设备显示' : '已关闭非 TSLink 设备显示',
        icon: 'none'
      });
    },
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

/* 设置项 */
.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
}

.setting-info {
  flex: 1;
}

.setting-name {
  font-size: 32rpx;
  color: #333;
  display: block;
}

.setting-desc {
  font-size: 26rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

/* 颜色选择 */
.color-preview {
  width: 48rpx;
  height: 48rpx;
  border-radius: 50%;
  margin-left: 20rpx;
}

.color-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-top: 20rpx;
}

.color-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.color-circle {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
  border: 4rpx solid transparent;
  box-sizing: border-box;
  transition: all 0.2s ease;
}

.color-circle.active {
  border-color: #fff;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.25), 0 0 0 2rpx currentColor;
}

.color-check {
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
}

/* 操作项 */
.action-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.action-item:last-child {
  border-bottom: none;
}

.action-info {
  flex: 1;
}

.action-name {
  font-size: 32rpx;
  color: #333;
  display: block;
}

.action-desc {
  font-size: 26rpx;
  color: #999;
  margin-top: 8rpx;
  display: block;
}

.action-arrow {
  font-size: 40rpx;
  color: #ccc;
  margin-left: 20rpx;
}

/* 关于 */
.about-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 30rpx;
  margin-top: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.about-logo {
  height: 80rpx;
  margin-bottom: 20rpx;
}

.app-name {
  font-size: 40rpx;
  font-weight: 600;
  color: #333;
}

.app-version {
  font-size: 28rpx;
  color: #999;
  margin-top: 12rpx;
}

.app-company {
  font-size: 26rpx;
  color: #999;
  margin-top: 8rpx;
}
</style>
