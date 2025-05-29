from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings 
from typing import List, Dict, Optional
import os

class FAISSVectorDB:
    def __init__(self, collection_name: str = "software_concepts", persist_dir: str = "faiss_db"):
        # 初始化嵌入模型
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="./all-MiniLM-L6-v2", 
            model_kwargs={'device': 'cpu'}
        )
                
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.db_path = os.path.join(persist_dir, collection_name)
        
        # 确保存储目录存在
        os.makedirs(self.persist_dir, exist_ok=True)
        
        # 加载或新建FAISS索引
        if os.path.exists(self.db_path):
            self.vector_db = FAISS.load_local(self.db_path, self.embedding_model,
            allow_dangerous_deserialization=True)
        else:
            # 创建一个空的FAISS索引
            from langchain.schema import Document
            self.vector_db = FAISS.from_documents(
                documents=[Document(page_content="init")], 
                embedding=self.embedding_model
            )
            self.vector_db.delete([self.vector_db.index_to_docstore_id[0]])  # 删除初始化文档

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """语义搜索"""
        try:
            docs = self.vector_db.similarity_search(query, k=top_k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": 1.0  # FAISS不直接返回分数，可以后续计算
                }
                for doc in docs
            ]
        except Exception as e:
            print(f"搜索失败: {str(e)}")
            return []

    def insert(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """插入单条数据"""
        from langchain.schema import Document
        
        if metadata is None:
            metadata = {}
            
        try:
            doc = Document(page_content=content, metadata=metadata)
            self.vector_db.add_documents([doc])
            self._persist()
            return True
        except Exception as e:
            print(f"插入失败: {str(e)}")
            return False

    def batch_insert(self, documents: List[Dict[str, str]]) -> bool:
        """批量插入数据"""
        from langchain.schema import Document
        
        try:
            docs = [
                Document(page_content=doc["text"], metadata=doc.get("metadata", {}))
                for doc in documents
            ]
            self.vector_db.add_documents(docs)
            self._persist()
            return True
        except Exception as e:
            print(f"批量插入失败: {str(e)}")
            return False

    def delete(self, ids: List[str]) -> bool:
        """删除数据（FAISS删除功能有限）"""
        try:
            # FAISS的删除功能有限，这里简单实现
            # 更完整的实现需要维护自己的文档存储
            print("警告: FAISS原生不支持精确删除，此操作可能不生效")
            self.vector_db.delete(ids)
            self._persist()
            return True
        except Exception as e:
            print(f"删除失败: {str(e)}")
            return False

    def _persist(self):
        """持久化存储"""
        self.vector_db.save_local(self.db_path)

    def get_collection_stats(self) -> Dict:
        """获取集合统计信息"""
        return {
            "collection_name": self.collection_name,
            "doc_count": len(self.vector_db.index_to_docstore_id),
            "dimension": self.vector_db.index.d,
            "is_trained": self.vector_db.index.is_trained
        }