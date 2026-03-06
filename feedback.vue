<template>
  <view class="container">
    <scroll-view class="content" scroll-y>
      <view class="section">
        <text class="section-title">反馈问题</text>
        <text class="desc">请详细描述你遇到的问题，我们会尽快处理。</text>
        
        <view class="form-item">
          <text class="label">问题类型</text>
          <picker mode="selector" :range="feedbackTypes" :value="typeIndex" @change="onTypeChange">
            <view class="picker">
              <text>{{ feedbackTypes[typeIndex] }}</text>
              <uni-icons type="down" size="16" color="#999"></uni-icons>
            </view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="label">问题描述</text>
          <textarea 
            class="textarea" 
            v-model="description" 
            placeholder="请详细描述你遇到的问题..."
            maxlength="500"
          />
          <text class="count">{{ description.length }}/500</text>
        </view>
        
        <view class="form-item">
          <text class="label">联系邮箱（选填）</text>
          <input 
            class="input" 
            v-model="email" 
            placeholder="方便我们联系你"
            type="text"
          />
        </view>
        
        <button class="submit-btn" @tap="submitFeedback" :disabled="!canSubmit">
          提交反馈
        </button>
      </view>
      
      <view class="section">
        <text class="section-title">其他联系方式</text>
        <view class="contact-item">
          <text class="contact-label">客服邮箱</text>
          <text class="contact-value">support@techstorm.com</text>
        </view>
        <view class="contact-item">
          <text class="contact-label">官方网站</text>
          <text class="contact-value">www.techstorm.com</text>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import Preferences from '@/src/preferences';

export default {
  data() {
    return {
      feedbackTypes: ['功能建议', 'Bug反馈', '使用问题', '其他'],
      typeIndex: 0,
      description: '',
      email: '',
      accentColor: Preferences.getAccentColor(),
    };
  },
  
  computed: {
    canSubmit() {
      return this.description.length > 0;
    },
  },
  
  onShow() {
    this.accentColor = Preferences.getAccentColor();
  },
  
  methods: {
    onTypeChange(e) {
      this.typeIndex = e.detail.value;
    },

    validateEmail(email) {
      if (!email) return true; // 邮箱是选填的
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    },

    submitFeedback() {
      if (!this.description) {
        uni.showToast({ title: '请填写问题描述', icon: 'none' });
        return;
      }

      // 邮箱格式校验
      if (!this.validateEmail(this.email)) {
        uni.showToast({ title: '邮箱格式不正确', icon: 'none' });
        return;
      }

      // 这里可以实现实际的反馈提交逻辑
      // 例如发送到服务器或发送邮件

      uni.showToast({
        title: '反馈已提交',
        icon: 'success',
        duration: 2000,
        success: () => {
          setTimeout(() => {
            uni.navigateBack();
          }, 2000);
        },
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
  margin-bottom: 20rpx;
  display: block;
}

.desc {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 30rpx;
  display: block;
}

.form-item {
  margin-bottom: 30rpx;
}

.label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
  display: block;
}

.picker {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  font-size: 30rpx;
  color: #333;
}

.arrow {
  font-size: 24rpx;
  color: #999;
}

.input {
  padding: 24rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  font-size: 30rpx;
  color: #333;
}

.textarea {
  padding: 24rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  font-size: 30rpx;
  color: #333;
  height: 240rpx;
  width: 100%;
  box-sizing: border-box;
}

.count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  margin-top: 12rpx;
  display: block;
}

.submit-btn {
  margin-top: 40rpx;
  background-color: v-bind(accentColor);
  color: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  font-size: 32rpx;
  border: none;
}

.submit-btn[disabled] {
  background: #ccc;
}

.contact-item {
  display: flex;
  justify-content: space-between;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.contact-item:last-child {
  border-bottom: none;
}

.contact-label {
  font-size: 30rpx;
  color: #666;
}

.contact-value {
  font-size: 30rpx;
  color: #333;
}
</style>
