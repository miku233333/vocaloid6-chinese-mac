# VOCALOID6 Mac 繁體中文漢化工程

**狀態**: 工具鏈公開版  
**目標平台**: macOS  
**主要語言**: 繁體中文（`zh-TW`）  
**當前定位**: 公開倉庫僅保留通用安裝 / 提取 / 套用工具；VOCALOID6 專用翻譯與補丁資料改為本機私有保存

---

## 這個專案目前是什麼

這不是一個已做完完整視覺驗收、可輕率宣稱「所有 UI 100% 驗證」的 VOCALOID6 Mac 漢化包。

目前倉庫提供的是：

- Mac 專用的安裝 / 卸載 / 還原腳本
- 資源提取與字串提取工具
- 本機私有資料的載入規約
- 一套可繼續擴展的漢化工程骨架

目前**還沒有**做完完整視覺層驗收的正式 `resources/` 漢化成品，但已完成基於真實 app 的端到端安裝與啟動驗證。

## 版權與公開策略

這個公開倉庫現在刻意**不再附帶**下列 VOCALOID6 專用內容：

- 從 app 提取或整理出的來源文本
- 產品專用翻譯詞條
- compiled nib 定向補丁映射
- 任何可直接重建 VOCALOID6 本地化內容的派生資料

這些資料應放在你的**本機私有目錄**：

- `~/.vocaloid6-chinese-mac-private/glossaries/`
- `~/.vocaloid6-chinese-mac-private/translations/`

也可以用環境變數覆蓋：

```bash
export VOCALOID6_PRIVATE_DATA_DIR=/your/private/path
```

但和之前不同的是：

- 已在本機真實安裝的 `VOCALOID6 Editor.app` 上跑通資源提取
- 已成功提取 `30` 個 `.strings` 文件
- 已成功整理出 `1078` 條可翻譯字符串
- 已成功整理出 `8494` 條 `.nib` UI 候選文本
- 已把 `.nib` 原始候選清洗成 `283` 條較像真實 UI 的可見文案
- 其中 `134` 條已可自動匹配到繁體中文建議翻譯
- 已在本機私有資料目錄完成 `zh-TW` 詞條與真實 app key 的接回
- 已在本機私有資料目錄完成 `.strings` key 全覆蓋驗證
- 已能生成 `28` 個 `zh-TW.lproj/*.strings` 文件作為安裝輸出
- 已在副本 app 上完成多次安全安裝驗證
- 安裝器現在會對修改後的副本 app 自動做 ad-hoc 重簽名
- 已確認安裝後的副本 app 可直接重新啟動
- 已確認 app 使用者語言偏好可由安裝器寫入 `zh-TW`
- 已確認主啟動畫面來自 `VEHomeWC` compiled nib，且已在副本 app 實測將 `NEW PROJECT / OPEN / RECENT OPEN / NEWS` 轉為繁體中文
- 已加入 Finder 可雙擊的一鍵安裝入口，原 app 不可寫時會自動回退到使用者副本

---

## 當前真實完成度

如果只看本機私有資料配合這套工具鏈的效果，`.strings` 字層、安裝鏈路、以及首頁核心靜態 UI 已接近完成；如果把所有頁面的逐頁視覺驗收與不同版本兼容性也算進去，整體仍然是 **高覆蓋準正式版**。

已完成：

- 真實 key bootstrap 腳本
- Mac 安裝器 / 卸載器 Python 骨架
- 資源提取工具
- 字串提取工具
- 備份 / 還原流程設計
- 真實 app 資源提取驗證
- 多文件 `.strings` bundle 生成
- 安全副本安裝驗證
- `VEHomeWC` compiled nib 首頁靜態文案補丁

未完成：

- 逐頁 UI 視覺驗收報告
- 不同 VOCALOID6 Mac 版本兼容性驗證
- 其餘 compiled nib / 動態內容的最終落地

---

## 倉庫結構

- [data/translations/README.md](./data/translations/README.md)
  說明私有翻譯資料應放在哪裡
- [data/glossaries/README.md](./data/glossaries/README.md)
  說明私有 glossary / patch 資料應放在哪裡
- [scripts/installer.py](./scripts/installer.py)
  Mac 安裝 / 還原 / 卸載入口
- [scripts/one_click_install.py](./scripts/one_click_install.py)
  一鍵安裝策略入口
- [One-Click Install.command](./One-Click%20Install.command)
  Finder 可雙擊的一鍵安裝腳本
- [scripts/extract_resources.py](./scripts/extract_resources.py)
  資源提取工具
- [scripts/extract_strings.py](./scripts/extract_strings.py)
  字串提取工具
- [scripts/resource_replacer.py](./scripts/resource_replacer.py)
  本地化包生成 / 替換工具
- [scripts/smoke_test_install.py](./scripts/smoke_test_install.py)
  一鍵驗證副本安裝、重簽名、codesign 與啟動
- [scripts/bootstrap_nib_visible_texts.py](./scripts/bootstrap_nib_visible_texts.py)
  清洗 `.nib` 可見文案並自動匹配繁體中文建議翻譯
- [scripts/analyze_compiled_nib.py](./scripts/analyze_compiled_nib.py)
  分析 compiled nib 內嵌字串偏移，供未來定向 patch 參考
- [scripts/patch_compiled_nibs.py](./scripts/patch_compiled_nibs.py)
  對 `VEHomeWC` 這類 compiled nib 做定向字串補丁
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
- 公開倉庫不再直接附帶 VOCALOID6 專用翻譯/補丁資料
- 目前屬於開發中工程，**不要把它當成已驗證完成的正式漢化包**

---

## 快速使用

### 0. 從 GitHub Releases 下載

如果你只是想直接拿來安裝，不想先讀完整倉庫，可以優先去 GitHub 的 `Releases` 頁面下載目前的測試版。

注意：公開 release 只包含工具，不再附帶 VOCALOID6 專用翻譯資料；你仍需要在本機私有目錄放入或生成對應資料後，再執行：

- `One-Click Install.command`

如果你是從原始碼倉庫下載，也可以直接使用倉庫根目錄的同名檔案。

### 1. 檢查語法

```bash
python3 -m py_compile scripts/installer.py scripts/extract_resources.py scripts/extract_strings.py scripts/resource_replacer.py
bash -n install.sh uninstall.sh
```

### 2. 提取資源

```bash
python3 scripts/extract_resources.py
```

### 3. 建立真實翻譯模板

```bash
python3 scripts/extract_strings.py "/Applications/VOCALOID6 Editor.app" -o ./output
```

這一步目前已在本機驗證可用，會生成：

- `output/extracted_strings.json`
- `output/translation_template.csv`
- `output/nib_ui_candidates.json`
- `output/extraction_report.md`

### 4. 準備本機私有翻譯資料

先建立私有目錄：

```bash
mkdir -p ~/.vocaloid6-chinese-mac-private/glossaries
mkdir -p ~/.vocaloid6-chinese-mac-private/translations
```

然後把你自己的 VOCALOID6 專用 glossary / translation 放進去，或由你本機私有流程生成。

### 5. 把真實 key 接回 `zh-TW`

```bash
python3 scripts/bootstrap_real_keys.py
```

這一步會根據：

- `output/extracted_strings.json`
- `~/.vocaloid6-chinese-mac-private/glossaries/source-text-zh-TW.json`

把可匹配的真實 app key 回填到：

- `~/.vocaloid6-chinese-mac-private/translations/zh-TW.json`

### 6. 一鍵安裝繁體中文語言包

在 Finder 直接雙擊：

- [One-Click Install.command](./One-Click%20Install.command)

或命令列執行：

```bash
python3 scripts/one_click_install.py
```

這個入口目前會：

- 優先嘗試直接安裝到現有 `VOCALOID6 Editor.app`
- 若 `/Applications` 下的原始 app 不可寫，則自動安裝到
  `~/Applications/VOCALOID6 Editor zh-TW.app`
- 自動完成備份、安裝、重簽名與啟動

### 7. 傳統安裝繁體中文語言包

```bash
./install.sh
```

實際上這一步目前會：

- 偵測 VOCALOID6 Mac 安裝路徑
- 備份 `Contents/Resources`
- 建立 `zh-TW.lproj`
- 安裝由真實 key 生成的多份 `.strings` 文件
- 對 `VEHomeWC` 首頁 compiled nib 套用靜態文案補丁
- 如無法生成多文件，才回退為單一 `Localizable.strings`

它**不代表所有 UI 都已完成漢化**，但已不再只是“空骨架安裝”。

### 8. 卸載 / 還原

```bash
./uninstall.sh
```

### 9. 安全測試安裝到副本 app

如果你不想直接動正式安裝，可以先複製一份 app 再測：

```bash
ditto "/Applications/VOCALOID6 Editor.app" "./tmp/VOCALOID6 Editor Test.app"
python3 scripts/installer.py --app-path "./tmp/VOCALOID6 Editor Test.app" -y --install
```

這條路徑目前已經驗證可用。

安裝器現在還會自動對修改過的 `.app` 做 ad-hoc 重簽名，避免因 bundle 被修改而無法啟動。

### 10. 一鍵冒煙測試

```bash
python3 scripts/smoke_test_install.py
```

這條腳本目前會自動完成：

- 複製原始 app 到測試副本
- 安裝 `zh-TW` 語言包
- 驗證 `zh-TW.lproj` 與 `.strings` 文件
- 驗證 `codesign --verify --deep --strict`
- 嘗試啟動測試副本並確認進程存在

### 11. 清洗 `.nib` 可見 UI 文案

```bash
python3 scripts/bootstrap_nib_visible_texts.py
```

這一步目前會生成：

- `output/nib_visible_ui_texts.json`
- `output/nib_visible_ui_translation_template.csv`
- `output/nib_visible_ui_report.md`

目前已驗證結果：

- 原始 `.nib` 候選：`8494`
- 清洗後較像可見 UI 的唯一候選：`283`
- 已可自動匹配繁中建議翻譯：`134`

### 11. 分析 compiled nib 啟動畫面

```bash
python3 scripts/analyze_compiled_nib.py "/Applications/VOCALOID6 Editor.app/Contents/Resources/VEHomeWC.nib" --contains "PROJECT"
```

目前已確認：

- 啟動畫面主窗口來自 `VEHomeWC.nib`
- `NEW PROJECT`、`OPEN`、`NEWS`、`RECENT OPEN` 這些文字直接內嵌在 `keyedobjects-*.nib`
- 安裝器現在會對兩份 `keyedobjects-*.nib` 自動套用首頁靜態文案補丁

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

## 最新已驗證進展

- 已在本機 `/Applications/VOCALOID6 Editor.app` 上完成真實提取
- 已確認 app bundle 內存在可本地化的 `.strings` / `.nib` 資源
- 字串提取工具已不再卡在編碼解碼錯誤
- 已能為 `zh-TW.lproj` 生成 `28` 個本地化 strings 文件
- 已在 `VOCALOID6 Editor Test.app` 副本上成功完成一次安裝
- 已在安裝後直接重新打開 `VOCALOID6 Editor Test.app`
- 已確認 `codesign --verify --deep --strict` 通過
- 已有 `scripts/smoke_test_install.py` 可一鍵重跑整條驗證鏈
- 已有 `scripts/bootstrap_nib_visible_texts.py` 可把 `.nib` 層收斂成可維護清單
- 已有 `scripts/analyze_compiled_nib.py` 可定位 `VEHomeWC` 這類 compiled nib 的內嵌英文
- 已有 `scripts/patch_compiled_nibs.py` 可自動把首頁 `新增專案 / 開啟 / 最近開啟 / 最新消息` 打進副本 app
- 目前真正的下一道難關，已經從「能不能提取」變成「怎樣高品質補完 zh-TW」

---

## 已知限制

- `zh-TW.json` 已有 `700` 條翻譯，但 `.nib` / 視覺層仍未做完
- 右側新聞內容仍保留原始來源語言，這部分屬於內容層而不是 UI shell 漏翻
- 尚未確認所有版本的 VOCALOID6 Mac 都使用相同資源結構
- 沒有可直接分發的原版資源替換結果
- [docs/TEST_REPORT.md](./docs/TEST_REPORT.md) 現在只代表「工具鏈驗證狀態」，不是完整產品測試結論

---

## 下一步建議

1. 以 `output/nib_visible_ui_report.md` 為基礎，補齊剩餘高價值 UI 文案
2. 對副本 app 做逐頁截圖核對
3. 把 `.nib` 層真正能落地的文字再往前推
4. 再決定是否發布正式版

---

## 版權與使用

- 這個倉庫只應包含你自己撰寫的腳本、詞條與說明
- 不應直接分發 Yamaha 的原版資源文件
- 請支持正版 VOCALOID6
