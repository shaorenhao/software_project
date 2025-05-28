import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

class VectorKnowledgeBase:
    def __init__(self, db_path: str = "./vector_db"):
        # 初始化嵌入模型（小型本地模型）
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(allow_reset=True)
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="software_engineering_knowledge",
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
    
    def add_documents(self, documents: List[Dict]):
        """
        添加文档到向量数据库
        :param documents: [{"term": "...", "definition": "...", "examples": "...", "category": "..."}]
        """
        if not documents:
            return
        
        # 准备数据
        ids = []
        texts = []
        embeddings = []
        metadatas = []
        
        for idx, doc in enumerate(documents):
            # 组合文本用于嵌入
            text = f"{doc['term']}: {doc['definition']}"
            if doc.get('examples'):
                text += f" Examples: {doc['examples']}"
            
            # 生成嵌入
            embedding = self.embedding_model.encode(text)
            
            ids.append(f"id_{idx}")
            texts.append(text)
            embeddings.append(embedding.tolist())
            metadatas.append({
                "term": doc["term"],
                "category": doc.get("category", "general")
            })
        
        # 批量添加
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )
    
    def semantic_search(self, query: str, top_k: int = 3, threshold: float = 0.7) -> List[Dict]:
        """
        语义搜索
        :param query: 查询文本
        :param top_k: 返回最相似的k个结果
        :param threshold: 相似度阈值
        :return: 搜索结果列表
        """
        # 生成查询嵌入
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # 执行查询
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["metadatas", "documents", "distances"]
        )
        
        # 格式化结果
        formatted_results = []
        for i in range(len(results["ids"][0])):
            if results["distances"][0][i] < threshold:
                continue
                
            formatted_results.append({
                "term": results["metadatas"][0][i]["term"],
                "content": results["documents"][0][i],
                "similarity": 1 - results["distances"][0][i],  # 转换为相似度分数
                "category": results["metadatas"][0][i].get("category", "general")
            })
        
        return formatted_results
    
    def reset(self):
        """重置数据库"""
        self.client.reset()