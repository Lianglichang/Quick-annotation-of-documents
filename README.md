# PDF 批注工具

基于 PyMuPDF 的 PDF 高亮与批注工具，支持长文本模糊匹配、批注去重、按指令清除批注，并提供可复用的模块化结构。

## 功能

- 根据 `instructions.json` 批量高亮/下划线并写入批注
- comment 前缀类型驱动颜色：`Key` / `Detail` / `Parameter`
- 长文本匹配：去断词、空格修复、分段匹配、必要时模糊匹配
- 重复批注检测：同位置同内容不会重复添加
- 按指令清除批注（仅清除指令对应的批注）

## 目录结构

- `main.py`：批注入口
- `core.py`：批注主流程
- `text_match.py`：文本匹配策略
- `annot_utils.py`：批注去重与现有批注索引
- `instruction_utils.py`：指令读取与 comment 规范化
- `clear_annotations.py`：按指令清除批注
- `instructions.json`：批注指令列表
- `data/`：输入 PDF
- `result/`：输出 PDF（仅在非就地保存时使用）

## 环境与依赖

PowerShell 中执行：

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 使用方式

### 1) 批注（默认就地保存）

```powershell
python main.py
```

程序会输出统计日志：

```
matched=20/20 added=20 duplicates=0
```

含义：
- matched：匹配成功的指令数
- expected：去重后的指令数
- added：新增的批注数
- duplicates：因已存在而跳过的批注数

### 2) 清除批注（按指令）

```powershell
python clear_annotations.py
```

仅删除 `instructions.json` 对应的批注，其它批注保留。

## 指令格式（instructions.json）

```json
{
  "page": 1,
  "text": "tables come in a large variety of shapes and sizes.",
  "action": "highlight",
  "comment": "Key: 强调真实表格分布的复杂性，是问题难的根源",
  "subject": "表格复杂性"
}
```

说明：
- `page` 为 1-based 页码，`null` 表示全页搜索
- `action` 支持 `highlight` / `underline`
- `comment` 前缀影响颜色，大小写不敏感；缺省默认 `Detail:`
- `text` 中带前缀也会被自动剥离后用于搜索

## 匹配策略说明

按优先级逐级降级：
1. 直接精确匹配
2. 去断词/空格修复后再匹配
3. 分段匹配
4. 模糊匹配（基于词序列相似度）

为避免误高亮，分段匹配有最小长度阈值。

## 常见问题

### 1) MuPDF 解析警告

如果 PDF 结构存在问题，MuPDF 可能输出解析警告。当前入口已关闭显示：

```python
pymupdf.TOOLS.mupdf_display_errors(False)
```

如需恢复，设置为 `True`。

### 2) 批注条数不一致

当指令文本与 PDF 实际文本差异较大时可能出现不匹配。建议：
- 缩短 `text`
- 替换为 PDF 中实际文本
- 避免引入新的错别字或缺失词
