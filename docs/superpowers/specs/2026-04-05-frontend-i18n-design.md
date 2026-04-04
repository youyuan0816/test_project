# Frontend 多语言支持设计

## 目标

为前端添加 i18n（国际化）支持，实现中文/英文切换。

## 方案

使用 react-i18next 库实现多语言支持。

## 技术架构

### 1. 安装依赖
```bash
npm install react-i18next i18next
```

### 2. 目录结构
```
frontend/src/locales/
  ├── zh.json    # 中文翻译
  └── en.json    # 英文翻译
```

### 3. i18n 配置
创建 `i18n.ts`：
```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import zh from './locales/zh.json';
import en from './locales/en.json';

i18n.use(initReactI18next).init({
  resources: { zh: { translation: zh }, en: { translation: en } },
  lng: 'zh',
  fallbackLng: 'zh',
});
```

### 4. Header 组件
在 Header 添加语言切换按钮：
```tsx
<Select value={i18n.language} onChange={(lng) => i18n.changeLanguage(lng)}>
  <Option value="zh">中文</Option>
  <Option value="en">EN</Option>
</Select>
```

### 5. 使用方式
在组件中使用 `t('key')`：
```tsx
const { t } = useTranslation();
<span>{t('task.name')}</span>
```

## 翻译文件示例

**zh.json:**
```json
{
  "header": { "title": "UI 测试生成器" },
  "task": { "name": "任务名称", "status": "状态" },
  "action": { "download": "下载", "upload": "上传Excel", "generate": "生成代码", "remove": "删除" }
}
```

**en.json:**
```json
{
  "header": { "title": "UI Test Generator" },
  "task": { "name": "Name", "status": "Status" },
  "action": { "download": "Download", "upload": "Upload Excel", "generate": "Generate Code", "remove": "Remove" }
}
```

## 实现步骤

1. 安装 i18n 依赖
2. 创建 locales 目录和翻译文件
3. 创建 i18n.ts 配置文件
4. 在 main.tsx 引入 i18n 配置
5. 在 Header 添加语言切换按钮
6. 逐步替换组件中的硬编码文本
