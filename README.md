# VOCALOID6 Mac 繁體中文漢化工程

**狀態**: 高覆蓋開發版  
**目標平台**: macOS  
**主要語言**: 繁體中文（`zh-TW`）  
**當前定位**: 已完成 `.strings` 真實 key 全覆蓋的 Mac 繁體中文漢化工程

---

## 這個專案目前是什麼

這不是一個已做完完整視覺驗收、可輕率宣稱「所有 UI 100% 驗證」的 VOCALOID6 Mac 漢化包。

目前倉庫提供的是：

- 繁體中文翻譯詞條
- Mac 專用的安裝 / 卸載 / 還原腳本
- 資源提取與字串提取工具
- 一套可繼續擴展的漢化工程骨架

目前**還沒有**驗證完成的正式 `resources/` 漢化產物，也**沒有**完整的端到端安裝驗證結論。

但和之前不同的是：

- 已在本機真實安裝的 `VOCALOID6 Editor.app` 上跑通資源提取
- 已成功提取 `30` 個 `.strings` 文件
- 已成功整理出 `1078` 條可翻譯字符串
- 已成功整理出 `8494` 條 `.nib` UI 候選文本
- 已把 `zh-TW` 詞條完整接到真實 app key，當前共有 `700` 條翻譯
- 已完成 `613` 個真實提取 `.strings` key 的覆蓋，`unmatched_count = 0`
- 已能生成 `28` 個 `zh-TW.lproj/*.strings` 文件作為安裝輸出
- 已在副本 app 上完成多次安全安裝驗證

---

## 當前真實完成度

如果只看 `.strings` 字層與安裝鏈路，現在已接近 **完成版**；如果把 `.nib` 視覺核對與逐頁 UI 驗收也算進去，整體仍然是 **高覆蓋開發版**。

已完成：

- `zh-TW` 翻譯詞條文件
- 真實 key bootstrap 腳本
- Mac 安裝器 / 卸載器 Python 骨架
- 資源提取工具
- 字串提取工具
- 備份 / 還原流程設計
- 真實 app 資源提取驗證
- 多文件 `.strings` bundle 生成
- 安全副本安裝驗證

未完成：

- 逐頁 UI 視覺驗收報告
- 不同 VOCALOID6 Mac 版本兼容性驗證
- `.nib` 候選文本的最終落地

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

### 3. 建立真實翻譯模板

```bash
python3 scripts/extract_strings.py "/Applications/VOCALOID6 Editor.app" -o ./output
```

這一步目前已在本機驗證可用，會生成：

- `output/extracted_strings.json`
- `output/translation_template.csv`
- `output/nib_ui_candidates.json`
- `output/extraction_report.md`

### 4. 把真實 key 接回 `zh-TW`

```bash
python3 scripts/bootstrap_real_keys.py
```

這一步會根據：

- `output/extracted_strings.json`
- `data/glossaries/source-text-zh-TW.json`

把可匹配的真實 app key 回填到：

- `data/translations/zh-TW.json`

### 5. 安裝繁體中文語言包

```bash
./install.sh
```

實際上這一步目前會：

- 偵測 VOCALOID6 Mac 安裝路徑
- 備份 `Contents/Resources`
- 建立 `zh-TW.lproj`
- 安裝由真實 key 生成的多份 `.strings` 文件
- 如無法生成多文件，才回退為單一 `Localizable.strings`

它**不代表所有 UI 都已完成漢化**，但已不再只是“空骨架安裝”。

### 6. 卸載 / 還原

```bash
./uninstall.sh
```

### 7. 安全測試安裝到副本 app

如果你不想直接動正式安裝，可以先複製一份 app 再測：

```bash
ditto "/Applications/VOCALOID6 Editor.app" "./tmp/VOCALOID6 Editor Test.app"
python3 scripts/installer.py --app-path "./tmp/VOCALOID6 Editor Test.app" -y --install
```

這條路徑目前已經驗證可用。

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
- 目前真正的下一道難關，已經從「能不能提取」變成「怎樣高品質補完 zh-TW」

---

## 已知限制

- 目前只有少量翻譯詞條，覆蓋仍不足
- 尚未確認所有版本的 VOCALOID6 Mac 都使用相同資源結構
- 沒有可直接分發的原版資源替換結果
- [docs/TEST_REPORT.md](./docs/TEST_REPORT.md) 現在只代表「工具鏈驗證狀態」，不是完整產品測試結論

---

## 下一步建議

1. 篩選 `nib_ui_candidates.json`，建立更準確的 UI 對照
2. 對副本 app 做逐頁截圖核對
3. 補齊 `.nib` 層仍未映射的文字
4. 再決定是否發布正式版

---

## 版權與使用

- 這個倉庫只應包含你自己撰寫的腳本、詞條與說明
- 不應直接分發 Yamaha 的原版資源文件
- 請支持正版 VOCALOID6
