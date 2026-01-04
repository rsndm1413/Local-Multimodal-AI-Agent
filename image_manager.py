import os
from PIL import Image
import chromadb
import torchvision.transforms as transforms
from sentence_transformers import SentenceTransformer, models
from tqdm import tqdm

class ImageManager:
    def __init__(self):
        # 使用 README 推荐的 CLIP ViT-B-32 模型
        model_path = os.path.abspath("./clip")
        clip_model = models.CLIPModel(model_path)
        self.model = SentenceTransformer(modules=[clip_model])
        self.client = chromadb.PersistentClient(path="./vector_db")
        self.collection = self.client.get_or_create_collection("images")
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

    def add_image(self, image_path):
        """添加图像到向量数据库，移除普通 print 以便配合进度条"""
        try:
            # 加载并预处理图像
            image = Image.open(image_path).convert('RGB')

            # 生成图像嵌入向量
            image_embedding = self.model.encode(image).tolist()

            # 存储到向量数据库 (改用 upsert 避免重复 ID 报错)
            image_id = os.path.basename(image_path)
            self.collection.upsert(
                embeddings=[image_embedding],
                ids=[image_id],
                metadatas=[{"path": image_path}]
            )
        except Exception as e:
            # 使用 tqdm.write 打印错误，确保不破坏终端中的进度条显示
            tqdm.write(f"Error adding image {image_path}: {e}")

    def search_images(self, query):
        """根据文本描述搜索相关图像"""
        if not query:
            return []

        try:
            # 生成文本查询嵌入向量
            text_embedding = self.model.encode(query).tolist()

            # 在向量数据库中搜索
            results = self.collection.query(
                query_embeddings=[text_embedding],
                n_results=5
            )
            return results['metadatas'][0] if results['metadatas'] else []
        except Exception as e:
            print(f"Error searching images: {e}")
            return []