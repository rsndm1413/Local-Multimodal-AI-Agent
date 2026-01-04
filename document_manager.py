import os
import fitz  # PyMuPDF
import shutil
from sentence_transformers import SentenceTransformer, models
import chromadb
from image_manager import ImageManager  # 确保能调用你之前的 ImageManager
import logging
logging.getLogger('chromadb').setLevel(logging.ERROR)

class DocumentManager:
    def __init__(self):
        # 1. 初始化文本模型 (all-MiniLM)
        model_path = os.path.abspath("./minilm")
        word_embedding_model = models.Transformer(model_path)
        pooling_model = models.Pooling(word_embedding_model.get_word_embedding_dimension())
        self.text_model = SentenceTransformer(modules=[word_embedding_model, pooling_model])

        # 2. 初始化图像管理器 (内部使用 CLIP 模型)
        self.img_manager = ImageManager()

        # 3. 初始化数据库
        db_path = os.path.abspath("./vector_db")
        self.client = chromadb.PersistentClient(path=db_path)
        self.doc_collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )

        self.topic_keywords = {
            "AI_Security": ["adversarial", "mimicry", "attack", "defense", "diffusion", "cloak", "glaze",
                            "perturbation"],
            "NLP": ["transformer", "language model", "bert", "text generation", "token", "gpt", "llm"],
            "CV": ["image classification", "object detection", "segmentation", "pixels", "vision", "gan"],
            "Medical": ["clinical", "patient", "disease", "treatment", "medical", "healthcare"]
        }
    def add_and_classify_paper(self, pdf_path, topics=None):
        """核心方法：同时处理文本和图片"""
        doc_id = os.path.basename(pdf_path)

        # --- A. 文本处理部分 ---
        print(f"正在处理文本: {doc_id}...")
        text = self.extract_text_with_pybupdf(pdf_path)  # 改用 PyMuPDF 提取速度更快
        if text:
            text_embedding = self.text_model.encode(text).tolist()
            topics_str = ",".join(topics) if topics else ""
            self.doc_collection.add(
                documents=[text],
                embeddings=[text_embedding],
                ids=[doc_id],
                metadatas=[{"path": pdf_path, "topics": topics_str}]
            )

        # --- B. 图像处理部分 ---
        print(f"正在提取 PDF 中的图片...")
        self.extract_and_index_images(pdf_path)

        # --- C. 自动分类逻辑 ---
        if topics:
            self.move_to_classified_folder(pdf_path, topics)

        print(f"完成！论文 '{doc_id}' 的文本和图片已全部索引。")

    def extract_text_with_pybupdf(self, pdf_path):
        """使用 PyMuPDF 提取文本（比 PyPDF2 更稳定）"""
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        return text[:10000]

    def extract_and_index_images(self, pdf_path):
        """提取 PDF 中的所有图片并存入 images 目录和向量库"""
        output_dir = "./images"
        os.makedirs(output_dir, exist_ok=True)

        doc_name = os.path.basename(pdf_path).replace(".pdf", "")
        with fitz.open(pdf_path) as pdf:
            for page_index in range(len(pdf)):
                page = pdf[page_index]
                image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = pdf.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]

                    # 保存图片文件
                    img_filename = f"{doc_name}_p{page_index}_{img_index}.{ext}"
                    img_path = os.path.join(output_dir, img_filename)

                    with open(img_path, "wb") as f:
                        f.write(image_bytes)

                    # 调用 ImageManager 的 add_image 将图片存入图像向量库
                    self.img_manager.add_image(img_path)

    def move_to_classified_folder(self, pdf_path, topics):
        """分类移动逻辑"""
        target_dir = os.path.join("./papers/classified", "_".join(topics))
        os.makedirs(target_dir, exist_ok=True)
        shutil.copy2(pdf_path, os.path.join(target_dir, os.path.basename(pdf_path)))

    def auto_identify_topics(self, text):
        """根据关键词自动识别主题"""
        text = text.lower()
        auto_topics = []
        for topic, keywords in self.topic_keywords.items():
            if any(kw in text for kw in keywords):
                auto_topics.append(topic)

        # 如果没匹配到，归类到 "General"
        return auto_topics if auto_topics else ["General"]

    def organize_folder(self, folder_path):
        """一键批量整理功能"""
        if not os.path.exists(folder_path):
            print(f"文件夹不存在: {folder_path}")
            return

        print(f"正在扫描并整理文件夹: {folder_path}")
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(".pdf"):
                    full_path = os.path.join(root, file)
                    print(f"--- 正在处理: {file} ---")

                    # 1. 提取文本用于识别
                    text_content = self.extract_text_with_pybupdf(full_path)
                    # 2. 自动识别主题
                    identified_topics = self.auto_identify_topics(text_content)
                    # 3. 调用入库和归档流程
                    self.add_and_classify_paper(full_path, topics=identified_topics)

        print("\n所有 PDF 已整理完毕。")

    def search_papers(self, query):
        if not query:
            return []

        # 生成查询嵌入向量
        query_embedding = self.text_model.encode(query).tolist()

        try:
            count = self.doc_collection.count()
            if count == 0:
                return []

            # 依然可以请求 top 5，我们在内存中找出最小的那一个
            results = self.doc_collection.query(
                query_embeddings=[query_embedding],
                n_results=min(5, count)
            )

            output = []
            if results['metadatas'] and len(results['metadatas'][0]) > 0:
                # 找到 distance 列表中最小值的索引
                distances = results['distances'][0]
                min_distance_index = distances.index(min(distances))

                # 获取该索引对应的元数据和 ID
                best_metadata = results['metadatas'][0][min_distance_index]
                best_id = results['ids'][0][min_distance_index]
                best_distance = distances[min_distance_index]


                # 只添加这一个最匹配的结果
                output.append({
                    "name": best_id,
                    "path": best_metadata['path'],
                    "score": best_distance
                })

            return output
        except Exception as e:
            print(f"Error searching papers: {e}")
            return []