# Local Multimodal AI Agent: 智能论文与图像管理助手



这是一个基于本地 AI 模型驱动的多模态知识管理工具。它可以自动解析 PDF 论文，提取文本与图片，并利用向量数据库实现“语义化”搜索。

---

## 🛠 技术选型

* **文本嵌入**: `all-MiniLM-L6-v2` (本地化部署)
* **多模态检索**: `OpenAI CLIP (ViT-B-32)` (支持文字搜图片)
* **向量数据库**: `ChromaDB` (支持 HNSW 索引)
* **PDF 解析**: `PyMuPDF` (高性能文本/图片提取)

---

## 📦 环境配置

1.  **安装依赖库**:
    ```bash
    pip install pymupdf sentence-transformers chromadb pillow torch torchvision tqdm
    ```
2.  **模型放置**:
    * 将 MiniLM 模型放置在 `./minilm` 文件夹。
    * 将 CLIP 模型放置在 `./clip` 文件夹。

---

## 🚀 详细使用说明

本工具通过命令行（CLI）驱动，支持以下四大核心指令：

### 1. `add_paper` —— 单篇论文入库
手动将指定论文加入索引库，并进行分类。
* **指令格式**: `python main.py add_paper <文件路径> --topics <标签>`
* **参数说明**:
    * `path`: PDF 文件的绝对或相对路径。
    * `--topics`: (可选) 逗号分隔的标签，如 "NLP,Transformer"。
* **示例**:
    ```bash
    python main.py add_paper "./downloads/attention_is_all_you_need.pdf" --topics "NLP,Deep_Learning"
    ```

### 2. `search_paper` —— 论文语义搜索
基于语义理解搜索库中最匹配的论文。**注意：** 它不是关键词匹配，而是寻找含义最接近的内容。
* **指令格式**: `python main.py search_paper "<搜索词>"`
* **示例**:
    ```bash
    # 即使论文标题没写“机器翻译”，也能根据语义搜到相关论文
    python main.py search_paper "关于神经机器翻译的研究"
    ```
* **输出示例**:
    > Found papers:
    > - ./papers/classified/NLP/attention.pdf

### 3. `search_image` —— 图像跨模态搜索
使用文字描述来寻找所有已入库论文中的**插图、图表或架构图**。
* **指令格式**: `python main.py search_image "<描述内容>"`
* **示例**:
    ```bash
    # 搜索论文中出现的架构图
    python main.py search_image "system architecture diagram"
    
    # 搜索论文中的实验对比柱状图
    python main.py search_image "bar chart showing experimental results"
    ```
* **输出示例**:
    > Found images:
    > - ./images/attention_p3_1.png (第3页的第1张图)

### 4. `organize` —— 一键批量整理
扫描指定文件夹中所有的 PDF，自动识别主题，完成索引，并移动到分类文件夹中。
* **指令格式**: `python main.py organize <文件夹路径>`
* **自动识别逻辑**: 系统会扫描全文前 10000 字，匹配 `AI_Security`, `NLP`, `CV`, `Medical` 等关键词。
* **示例**:
    ```bash
    python main.py organize "C:/Users/Admin/Downloads/Messy_PDFs"
    ```

---

## 📂 自动生成的目录结构

处理完成后，项目会自动构建以下结构：
* `/papers/classified/`: 按主题存放的 PDF（如 `./NLP/`, `./CV/`）。
* `/images/`: 从所有 PDF 中提取出的原始图片库。
* `/vector_db/`: 存储文本和图片特征向量的数据库。

---

**提示**: 第一次运行 `organize` 或 `add_paper` 时，提取图片和生成向量可能需要一定时间，具体取决于 PDF 的大小和页数。
