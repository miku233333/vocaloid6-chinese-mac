# VOCALOID6 Mac 繁體中文漢化工程 - 驗證狀態

**更新日期**: 2026-04-02  
**適用範圍**: 本倉庫目前可證實的工具鏈 / 文檔 / 詞條狀態  
**不代表**: `.nib` 視覺層與所有版本兼容性都已完全驗證

---

## 目前能確定的事

### 1. 倉庫內確實存在可用的工程骨架

已確認存在：

- 安裝器：[scripts/installer.py](../scripts/installer.py)
- 資源提取工具：[scripts/extract_resources.py](../scripts/extract_resources.py)
- 字串提取工具：[scripts/extract_strings.py](../scripts/extract_strings.py)
- 替換工具：[scripts/resource_replacer.py](../scripts/resource_replacer.py)
- 繁體中文詞條：[data/translations/zh-TW.json](../data/translations/zh-TW.json)

### 2. 真實 app 資源提取已驗證可行

已在本機這個真實安裝路徑上驗證：

- `/Applications/VOCALOID6 Editor.app`

提取結果：

- `30` 個 `.strings` 文件
- `1078` 條字符串
- `8494` 條 `.nib` 候選 UI 文本
- `700` 條 `zh-TW` 翻譯
- `613` 個真實提取 `.strings` key 已全部匹配
- `unmatched_count = 0`
- `28` 個可生成的 `zh-TW.lproj/*.strings` 文件

目前已能穩定生成：

- `extracted_strings.json`
- `translation_template.csv`
- `nib_ui_candidates.json`
- `extraction_report.md`

### 3. 安裝器已在副本 app 上驗證可用

已用這條安全路徑驗證：

- 複製 `/Applications/VOCALOID6 Editor.app`
- 對副本執行 `installer.py --app-path ... -y --install`

驗證結果：

- 成功建立備份
- 成功在副本 `Info.plist` 寫入 `zh-TW`
- 成功安裝 `28` 個 `.strings` 文件
- 成功對修改後的副本 app 執行 ad-hoc 重簽名
- `codesign --verify --deep --strict` 通過
- 已確認副本 app 安裝後可直接重新啟動
- `VEPreferencesVC.strings`、`VEAddTrackVC.strings`、`Localizable.strings` 均確認有繁體中文內容

### 4. 繁體中文 `.strings` 詞條已達完整覆蓋

目前 `zh-TW.json` 共有 **700** 條翻譯。

這代表：

- 真實提取到的 `.strings` key 已全部有對應詞條
- 目前剩下的主要不是 `.strings` 缺詞，而是 `.nib` 候選文本整理與逐頁視覺驗收

### 5. Shell 入口已可作為 Python 安裝器封裝

- [install.sh](../install.sh)
- [uninstall.sh](../uninstall.sh)

現在這兩個入口的定位是：

- Mac 使用者的簡單入口
- 真正邏輯仍以 `scripts/installer.py` 為主
- 安裝器現在已會安裝真實生成的多文件 `.strings` bundle

---

## 目前還不能宣稱的事

以下內容目前**不能**被視為已驗證通過：

- 「已通過所有核心功能測試」
- 「可以安全使用」
- 「安裝後 GUI 覆蓋率達 85% / 91%」
- 「已在真實 VOCALOID6 v6.4.2 上完成完整驗證」
- 「`.nib` / 視覺層也已 100% 驗證」

原因很簡單：

- 倉庫內沒有正式漢化產物
- 尚未有逐頁 UI 截圖與視覺驗收證據隨倉庫保存
- 文檔先前把工程骨架寫得像成品

---

## 目前建議的驗證方式

如果要把這個項目往前推，建議按這個順序驗證：

1. 檢查 `nib_ui_candidates.json`，去噪並建立 UI 映射
2. 重新生成並安裝 `zh-TW.lproj` 多文件 bundle
3. 實際安裝到測試環境
4. 對照安裝前後 UI 截圖，做一份真正的視覺測試報告

---

## 當前結論

**現在最準確的定性是：**

這是一個 **字串層已做滿、安裝鏈路已驗證的 Mac 繁體中文漢化工程**，但還不是已完成全部視覺驗收的正式最終版。

可以繼續開發。  
但如果對外公開，必須誠實描述為：

- 高覆蓋開發版
- `.strings` 層已完整覆蓋
- `.nib` / 視覺驗收仍待完成
