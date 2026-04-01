# VOCALOID6 Mac 繁體中文漢化工程

**狀態**: 開發中  
**目標平台**: macOS  
**主要語言**: 繁體中文（`zh-TW`）  
**當前定位**: 工具鏈 + 翻譯詞條 + 安裝/還原腳本骨架

---

## 這個專案目前是什麼

這不是一個已完成、可直接發布的 VOCALOID6 Mac 漢化包。

目前倉庫提供的是：

- 繁體中文翻譯詞條
- Mac 專用的安裝 / 卸載 / 還原腳本
- 資源提取與字串提取工具
- 一套可繼續擴展的漢化工程骨架

目前**還沒有**驗證完成的正式 `resources/` 漢化產物，也**沒有**可信的端到端實機測試結論。

---

## 當前真實完成度

以「可持續開發的 Mac 繁體中文漢化工程」來看，現在大約是 **40% - 45%**。

已完成：

- `zh-TW` 翻譯詞條文件
- Mac 安裝器 / 卸載器 Python 骨架
- 資源提取工具
- 字串提取工具
- 備份 / 還原流程設計

未完成：

- 真正可發布的漢化資源包
- 可信的實機安裝驗證
- 不同 VOCALOID6 Mac 版本兼容性驗證
- 完整 UI 覆蓋

---

## 倉庫結構

- [data/translations/zh-TW.json](./data/translations/zh-TW.json)
  繁體中文翻譯詞條
- [scripts/installer.py](./scripts/installer.py)
  Mac 安裝 / 還原 / 卸載入口
- [scripts/extract_resources.py](./scripts/extract_resources.py)
  資源提取工具
- [scripts/extract_strings.py](./scripts/extract_strings.py)
  字串提取工具
- [scripts/resource_replacer.py](./scripts/resource_replacer.py)
  本地化包生成 / 替換工具
- [USER_GUIDE.md](./USER_GUIDE.md)
  使用說明
- [COMPLETION_REPORT.md](./COMPLETION_REPORT.md)
  完成度說明
- [docs/TEST_REPORT.md](./docs/TEST_REPORT.md)
  目前可證實的驗證狀態

---

## 安裝前注意

- 僅適用於 **macOS 上的 VOCALOID6**
- 請先備份原始應用
- 請使用正版軟件
- 目前屬於開發中工程，**不要把它當成已驗證完成的正式漢化包**

---

## 快速使用

### 1. 檢查語法

```bash
python3 -m py_compile scripts/installer.py scripts/extract_resources.py scripts/extract_strings.py scripts/resource_replacer.py
bash -n install.sh uninstall.sh
```

### 2. 提取資源

```bash
python3 scripts/extract_resources.py
```

### 3. 安裝繁體中文語言包骨架

```bash
./install.sh
```

實際上這一步目前會：

- 偵測 VOCALOID6 Mac 安裝路徑
- 備份 `Contents/Resources`
- 建立 `zh-TW.lproj`
- 生成 `Localizable.strings`

它**不代表所有 UI 都已完成漢化**。

### 4. 卸載 / 還原

```bash
./uninstall.sh
```

---

## 支援的安裝路徑

目前腳本會優先嘗試這些 macOS 路徑：

- `/Applications/VOCALOID6.app`
- `~/Applications/VOCALOID6.app`
- `/Applications/VOCALOID 6.app`
- `~/Applications/VOCALOID 6.app`
- `/Applications/VOCALOID6 Editor.app`
- `~/Applications/VOCALOID6 Editor.app`

---

## 語言策略

本倉庫目前以 **繁體中文 (`zh-TW`)** 為主。

- `zh-TW` 是主要維護目標
- `zh-CN` 目前只保留為參考翻譯文件，不作主要交付承諾

---

## 已知限制

- 目前只有少量翻譯詞條，覆蓋仍不足
- 尚未確認所有版本的 VOCALOID6 Mac 都使用相同資源結構
- 沒有可直接分發的原版資源替換結果
- [docs/TEST_REPORT.md](./docs/TEST_REPORT.md) 現在只代表「工具鏈驗證狀態」，不是完整產品測試結論

---

## 下一步建議

1. 在本機實際提取 VOCALOID6 資源
2. 建立真實 `translation_template` 與資源映射
3. 用 `zh-TW` 優先補齊高頻 UI
4. 做一次真正的安裝前後對比驗證

---

## 版權與使用

- 這個倉庫只應包含你自己撰寫的腳本、詞條與說明
- 不應直接分發 Yamaha 的原版資源文件
- 請支持正版 VOCALOID6
