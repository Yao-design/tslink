export interface SpecField {
  id: string;
  name: string;
  format: string;
  description?: string;
  unit?: string;
}

export interface Spec {
  deviceType: string;
  fullName?: string;
  description?: string;
  version: string;
  uplink: SpecField[];
  downlink: SpecField[];
}

export const specs: Record<string, Spec> = {
  "CNTR": {
    deviceType: "CNTR",
    fullName: "Counter",
    description: "计数器示例设备，演示 TSLink 基本功能",
    version: "1.0.0",
    uplink: [
      { id: "0x01", name: "count", format: "u32", description: "当前计数值", unit: "count" },
    ],
    downlink: [
      { id: "0x01", name: "reset", format: "void", description: "重置计数器" },
    ],
  },
  "HR": {
    deviceType: "HR",
    fullName: "HeartRate",
    description: "心率监测设备，支持实时心率、电量上报",
    version: "1.0.0",
    uplink: [
      { id: "0x01", name: "heartRate", format: "u16", description: "当前心率值", unit: "bpm" },
      { id: "0x02", name: "battery", format: "u8", description: "电池电量百分比", unit: "%" },
    ],
    downlink: [
      { id: "0x01", name: "led", format: "bool", description: "LED 开关控制" },
    ],
  },
  "LED": {
    deviceType: "LED",
    fullName: "LED",
    description: "LED 控制器，支持电源开关控制",
    version: "1.0.0",
    uplink: [
      { id: "0x01", name: "state", format: "bool", description: "当前 LED 状态（true=开启，false=关闭）" },
      { id: "0x02", name: "battery", format: "u8", description: "电池电量百分比", unit: "%" },
    ],
    downlink: [
      { id: "0x01", name: "power", format: "bool", description: "电源开关（true=开启，false=关闭）" },
    ],
  },
  "TEMP": {
    deviceType: "TEMP",
    fullName: "Temperature",
    description: "温湿度传感器，支持温度、湿度数据采集和上报间隔配置",
    version: "1.0.0",
    uplink: [
      { id: "0x01", name: "temperature", format: "i16", description: "温度值（精度 0.1°C，需除以 10）", unit: "celsius" },
      { id: "0x02", name: "humidity", format: "u8", description: "湿度百分比", unit: "%" },
    ],
    downlink: [
      { id: "0x01", name: "reportInterval", format: "u16", description: "上报间隔（秒）", unit: "seconds" },
    ],
  },
  "TP": {
    deviceType: "TP",
    fullName: "TirePressure",
    description: "胎压监测设备，支持胎压、温度、电量上报",
    version: "1.0.0",
    uplink: [
      { id: "0x01", name: "pressure", format: "u16", description: "胎压值（精度 0.1kPa，需除以 10）", unit: "kpa" },
      { id: "0x02", name: "temperature", format: "i16", description: "轮胎温度（精度 0.1°C，需除以 10）", unit: "celsius" },
      { id: "0x03", name: "battery", format: "u8", description: "电池电量百分比", unit: "%" },
    ],
    downlink: [
    ],
  },
};