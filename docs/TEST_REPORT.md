# VOCALOID6 Mac 繁體中文漢化工程 - 驗證狀態

**更新日期**: 2026-04-02  
**適用範圍**: 本倉庫目前可證實的工具鏈 / 文檔 / 詞條狀態  
**不代表**: 已完成正式漢化包的端到端實機測試

---

## 目前能確定的事

### 1. 倉庫內確實存在可用的工程骨架

已確認存在：

- 安裝器：[scripts/installer.py](../scripts/installer.py)
- 資源提取工具：[scripts/extract_resources.py](../scripts/extract_resources.py)
- 字串提取工具：[scripts/extract_strings.py](../scripts/extract_strings.py)
- 替換工具：[scripts/resource_replacer.py](../scripts/resource_replacer.py)
- 繁體中文詞條：[data/translations/zh-TW.json](../data/translations/zh-TW.json)

### 2. 繁體中文詞條目前只有初步覆蓋

目前 `zh-TW.json` 共有 **87** 條翻譯。

這代表：

- 已有基礎 UI 詞條
- 但距離完整 GUI 漢化仍有很大距離

### 3. Shell 入口已可作為 Python 安裝器封裝

- [install.sh](../install.sh)
- [uninstall.sh](../uninstall.sh)

現在這兩個入口的定位是：

- Mac 使用者的簡單入口
- 真正邏輯仍以 `scripts/installer.py` 為主

---

## 目前還不能宣稱的事

以下內容目前**不能**被視為已驗證通過：

- 「已通過所有核心功能測試」
- 「可以安全使用」
- 「安裝後 GUI 覆蓋率達 85% / 91%」
- 「已在真實 VOCALOID6 v6.4.2 上完成完整驗證」

原因很簡單：

- 倉庫內沒有正式漢化產物
- 沒有可信的實機測試證據隨倉庫保存
- 文檔先前把工程骨架寫得像成品

---

## 目前建議的驗證方式

如果要把這個項目往前推，建議按這個順序驗證：

1. 在真實 VOCALOID6 Mac 安裝上執行資源提取
2. 檢查 `Contents/Resources` 裡實際有哪些 `.strings` / `.plist` / 其他可本地化文件
3. 用 `zh-TW` 詞條生成 `Localizable.strings`
4. 實際安裝到測試環境
5. 對照安裝前後 UI 截圖，做一份真正的測試報告

---

## 當前結論

**現在最準確的定性是：**

這是一個 **Mac 繁體中文漢化工程骨架**，不是已驗證完成的正式漢化包。

可以繼續開發。  
但如果對外公開，必須誠實描述為：

- 開發中
- 工具鏈可用
- 實機驗證不足
