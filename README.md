# Local Multimodal AI Agent: 智能论文与图像管理助手



这是一个基于本地 AI 模型驱动的多模态知识管理工具。它可以自动解析 PDF 论文，提取文本与图片，并利用向量数据库实现“语义化”搜索。不仅能找论文，还能通过文字描述直接搜索论文内部的插图、架构图或图表。

---

## 🚀 核心功能

* **智能论文入库 (`add_paper`)**：解析 PDF，自动提取文本摘要与图片特征，支持手动或自动打标签。
* **语义文本搜索 (`search_paper`)**：基于 MiniLM 语义嵌入，即使关键词不完全匹配也能通过含义找到相关论文。
* **跨模态图像搜索 (`search_image`)**：使用自然语言搜索 PDF 中的图片（例如：搜索“模型架构图”或“实验结果散点图”）。
* **一键批量整理 (`organize`)**：扫描杂乱的文件夹，自动识别论文领域（NLP/CV/安全等）并归档。

---

## 🛠 技术选型

该项目坚持 **100% 本地化** 运行，保护学术隐私：

| 维度 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **文本 Embedding** | `all-MiniLM-L6-v2` | 轻量级 Transformer 模型，用于高效文本向量化。 |
| **多模态 Embedding** | `OpenAI CLIP` | 实现“文字找图”的核心，将图片和文字映射到同一向量空间。 |
| **向量数据库** | `ChromaDB` | 本地持久化存储向量，支持高速相似度检索（Cosine Similarity）。 |
| **PDF 解析引擎** | `PyMuPDF (fitz)` | 极速提取 PDF 文本及无损导出嵌入式图片。 |

---

## 📦 环境配置

### 1. 安装依赖
确保已安装 Python 3.8+，执行以下命令安装必要库：

```bash
pip install pymupdf sentence-transformers chromadb pillow torch torchvision tqdm
