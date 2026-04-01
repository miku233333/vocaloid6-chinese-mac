# VOCALOID6 Mac 繁體中文漢化工程 - 用戶指南

**版本**: 0.x 開發中  
**最後更新**: 2026-04-02

---

## 📋 安裝前須知

### ⚠️ 重要提醒

1. **本倉庫目前是工程骨架，不是已完成正式漢化包**
2. **僅供個人研究與學習使用**
3. **請支持正版軟件**
4. **安裝前務必備份原始文件**
5. **請預期可能需要手動調整**

### 系統要求

**Mac**:
- macOS 10.15 或更高版本
- VOCALOID6 Editor for Mac
- Python 3.8+

本倉庫目前以 **Mac / 繁體中文 (`zh-TW`)** 為主。

---

## 🚀 安裝步驟

### 方法 A: 自動安裝（推薦）

#### Mac
```bash
# 1. 下載漢化包
git clone https://github.com/miku233333/vocaloid6-chinese-mac.git
cd vocaloid6-chinese-mac

# 2. 運行安裝器
chmod +x install.sh
./install.sh

# 3. 重啟 VOCALOID6 Editor
```

### 方法 B: 手動安裝 / 提取翻譯模板

#### 步驟 1: 提取原版資源

```bash
python3 scripts/extract_resources.py
```

**注意**: 這會從 VOCALOID6 安裝目錄提取資源文件到 `extracted_resources/`

#### 步驟 2: 提取真實字串模板

```bash
python3 scripts/extract_strings.py "/Applications/VOCALOID6 Editor.app" -o ./output
```

這一步目前已在本機驗證可用，會產生：

- `output/extracted_strings.json`
- `output/translation_template.csv`
- `output/nib_ui_candidates.json`
- `output/extraction_report.md`

#### 步驟 3: 接回真實 app key

```bash
python3 scripts/bootstrap_real_keys.py
```

這一步會把已知來源文本對應到真實 app key，更新：

- `data/translations/zh-TW.json`

#### 步驟 4: 編輯翻譯文件

目前主要編輯：

- `data/translations/zh-TW.json`
- `output/translation_template.csv`

#### 步驟 5: 生成本地化包

```bash
python3 scripts/resource_replacer.py "/Applications/VOCALOID6 Editor.app" --mode bundle --lang zh-TW --output ./output
```

這一步現在會生成：

- `zh-TW.lproj/Localizable.strings`
- 多個對應實際對話框 / 面板的 `.strings` 文件

#### 步驟 6: 執行安裝

```bash
./install.sh
```

#### 步驟 7: 安全測試到副本 app（推薦）

```bash
ditto "/Applications/VOCALOID6 Editor.app" "./tmp/VOCALOID6 Editor Test.app"
python3 scripts/installer.py --app-path "./tmp/VOCALOID6 Editor Test.app" -y --install
```

這樣可以先看：

- `zh-TW.lproj` 是否正確生成
- `Info.plist` 是否寫入 `zh-TW`
- 安裝器流程是否正常

---

## 🔧 卸載

### Mac
```bash
./uninstall.sh
```

---

## 📊 當前狀態

| 組件 | 狀態 | 說明 |
|------|------|------|
| 安裝器 | 🟡 部分完成 | 已會安裝多文件 `.strings` bundle，且副本安裝已驗證 |
| 翻譯文件 | 🟡 部分完成 | `zh-TW` 目前已有 321 條實際可用翻譯 |
| 資源提取工具 | ✅ 可用 | 已在真實 app 上驗證可提取 1078 條字符串 |
| 實際漢化資源 | 🟡 初步可生成 | 已能生成 28 個 `.strings` 文件 |
| 實機測試 | ❌ 未完成 | 不能宣稱已完成 |

**整體狀態**: 工程骨架可用，正式漢化仍未完成

---

## ❓ 常見問題

### Q1: 安裝後沒有效果？

**A**: 請檢查：
1. VOCALOID6 是否已重啟
2. 語言設置是否選擇了"繁體中文"
3. 目前詞條是否已覆蓋你看到的界面

### Q2: 軟件崩潰或異常？

**A**: 立即卸載漢化包：
```bash
./uninstall.sh
```

### Q3: 如何貢獻翻譯？

**A**: 
1. Fork 本倉庫
2. 編輯 `data/translations/zh-TW.json`
3. 提交 Pull Request

### Q4: 支持簡體中文嗎？

**A**: 目前支持：
- ✅ 繁體中文 (zh-TW)
- 🟡 簡體中文 (zh-CN) - 僅保留參考詞條，不是主要交付

---

## 📝 反饋與支持

**問題反饋**: GitHub Issues

---

## 📄 許可證

請以倉庫當前 License 為準。無論如何，都不應直接分發 Yamaha 的原始資源文件。

---

## 🙏 致謝

感謝所有後續願意幫忙提取資源、補詞條與驗證的使用者。

---

**最後更新**: 2026-04-02  
**狀態**: 開發中 / 繁體中文優先
