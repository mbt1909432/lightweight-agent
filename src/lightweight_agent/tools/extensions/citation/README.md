# BibTeX Tools 使用说明

## 概述

BibTeX 工具集包含三个独立的工具，用于管理 BibTeX 条目和 LaTeX 引用，封装了 `BibTeXManager` 的功能。

## 工具列表

1. **BibTeXExtractTool** - 从文本文件中提取 BibTeX 条目（自动去重）
2. **BibTeXInsertTool** - 将 BibTeX 条目插入到 LaTeX 文件的引用中（平均分配）
3. **BibTeXSaveTool** - 将提取的 BibTeX 条目保存到文件

## 使用方法

### 1. 在 Agent 中注册工具

```python
from lightweight_agent import ReActAgent, OpenAIClient
from lightweight_agent.tools.extensions import (
    BibTeXExtractTool,
    BibTeXInsertTool,
    BibTeXSaveTool
)

# 创建客户端和 Agent
client = OpenAIClient(api_key="your-api-key")
agent = ReActAgent(
    client=client,
    working_dir="./workspace"
)

# 注册所有 BibTeX 工具
extract_tool = BibTeXExtractTool(agent.session)
insert_tool = BibTeXInsertTool(agent.session)
save_tool = BibTeXSaveTool(agent.session)

agent.register_tool(extract_tool)
agent.register_tool(insert_tool)
agent.register_tool(save_tool)
```

### 2. 使用工具

#### 提取 BibTeX 条目 (bibtex_extract)

```python
# Agent 会自动调用工具
# 工具名: bibtex_extract
# 参数: input_file="references.txt"
```

#### 插入到 LaTeX 文件 (bibtex_insert)

```python
# 工具名: bibtex_insert
# 参数: 
#   - input_file="paper.tex" (必需)
#   - output_file="paper_modified.tex" (可选，不提供则覆盖原文件)
```

#### 保存 BibTeX 条目 (bibtex_save)

```python
# 工具名: bibtex_save
# 参数: output_file="output.bib" (必需)
# 注意：需要先执行 bibtex_extract
```

## 状态管理

三个工具共享同一个会话级别的 `BibTeXManager` 实例。这意味着：
- 每个会话有独立的 BibTeX 条目存储
- 使用 `bibtex_extract` 提取的条目可以在同一会话中被 `bibtex_insert` 和 `bibtex_save` 使用
- 不同会话之间的数据互不干扰

## 工具参数说明

### BibTeXExtractTool (bibtex_extract)

- **input_file** (必需): BibTeX 文本文件路径

### BibTeXInsertTool (bibtex_insert)

- **input_file** (必需): LaTeX 文件路径
- **output_file** (可选): 修改后的 LaTeX 文件路径（不提供则覆盖原文件）

### BibTeXSaveTool (bibtex_save)

- **output_file** (必需): BibTeX 条目保存路径

## 工作流程示例

```python
# 1. 提取 BibTeX 条目
# 使用 bibtex_extract 工具，input_file="references.txt"

# 2. 插入到 LaTeX 文件
# 使用 bibtex_insert 工具，input_file="paper.tex", output_file="paper_with_citations.tex"

# 3. 保存提取的条目（可选）
# 使用 bibtex_save 工具，output_file="extracted_references.bib"
```

## 注意事项

1. **顺序执行**: `bibtex_insert` 和 `bibtex_save` 需要先执行 `bibtex_extract`
2. **路径验证**: 所有文件路径都会通过 `session.validate_path()` 进行验证
3. **去重机制**: `bibtex_extract` 会自动去除重复的 cite key（保留首次出现）
4. **平均分配**: `bibtex_insert` 会将 BibTeX 条目平均分配到所有 `\cite{}` 或 `\citep{}` 命令中
5. **状态共享**: 三个工具在同一个会话中共享提取的 BibTeX 条目
