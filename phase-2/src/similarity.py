"""
Semantic Similarity Computation
================================
این ماژول محاسبه شباهت معنایی بین کلمات/عبارات را انجام می‌دهد.
از embeddings یا LLM برای محاسبه شباهت استفاده می‌کند.
"""

from typing import List, Dict, Optional, Tuple
import numpy as np
from abc import ABC, abstractmethod


class SimilarityComputer(ABC):
    """کلاس پایه برای محاسبه شباهت معنایی"""
    
    @abstractmethod
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        محاسبه شباهت بین دو متن
        
        Args:
            text1: متن اول
            text2: متن دوم
            
        Returns:
            شباهت معنایی (0 تا 1)
        """
        pass
    
    @abstractmethod
    def compute_batch_similarity(self, texts1: List[str], texts2: List[str]) -> List[float]:
        """محاسبه شباهت برای چندین جفت متن"""
        pass


class LMStudioSimilarity(SimilarityComputer):
    """
    محاسبه شباهت با استفاده از API محلی LM Studio
    این روش نیاز به نصب کتابخانه‌های سنگین ندارد و از سرور LM Studio استفاده می‌کند
    """
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        """
        Args:
            base_url: آدرس سرور محلی LM Studio
        """
        self.base_url = base_url

    def _get_embedding(self, text: str) -> np.ndarray:
        """دریافت امبدینگ از طریق API"""
        import requests
        
        response = requests.post(
            f"{self.base_url}/embeddings",
            json={
                "input": text,
                "model": "local-model"  # در LM Studio مدل لود شده به طور پیش‌فرض پاسخ می‌دهد
            }
        )
        
        if response.status_code != 200:
            raise ConnectionError(
                f"خطا در اتصال به LM Studio. مطمئن شوید سرور در {self.base_url} در حال اجرا است.\n"
                f"Error: {response.text}"
            )
            
        data = response.json()
        return np.array(data['data'][0]['embedding'])

    def compute_similarity(self, text1: str, text2: str) -> float:
        """محاسبه شباهت کسینوسی"""
        emb1 = self._get_embedding(text1)
        emb2 = self._get_embedding(text2)
        
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        return float((similarity + 1) / 2)

    def compute_batch_similarity(self, texts1: List[str], texts2: List[str]) -> List[float]:
        return [self.compute_similarity(t1, t2) for t1, t2 in zip(texts1, texts2)]


class GGUFEmbeddingSimilarity(SimilarityComputer):
    """
    محاسبه شباهت با استفاده از مدل‌های GGUF محلی
    """
    
    def __init__(self, model_path: str):
        """
        Args:
            model_path: آدرس کامل فایل .gguf
        """
        self.model_path = model_path
        self._llm = None

    def _load_model(self):
        """بارگذاری مدل (lazy loading)"""
        if self._llm is None:
            try:
                from llama_cpp import Llama
                self._llm = Llama(model_path=self.model_path, embedding=True, verbose=False)
            except ImportError:
                raise ImportError(
                    "برای استفاده از GGUFEmbeddingSimilarity، llama-cpp-python را نصب کنید:\n"
                    "pip install llama-cpp-python"
                )

    def _get_embedding(self, text: str) -> np.ndarray:
        """دریافت embedding از مدل GGUF"""
        self._load_model()
        # تولید امبدینگ
        output = self._llm.create_embedding(text)
        # در llama-cpp-python خروجی معمولاً در ['data'][0]['embedding'] است
        embedding = np.array(output['data'][0]['embedding'])
        return embedding

    def compute_similarity(self, text1: str, text2: str) -> float:
        """محاسبه cosine similarity"""
        emb1 = self._get_embedding(text1)
        emb2 = self._get_embedding(text2)
        
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        similarity = np.dot(emb1, emb2) / (norm1 * norm2)
        # نرمال‌سازی به بازه [0, 1]
        return float((similarity + 1) / 2)

    def compute_batch_similarity(self, texts1: List[str], texts2: List[str]) -> List[float]:
        """محاسبه دسته‌ای برای بهره‌وری (فعلاً ساده پیاده شده)"""
        return [self.compute_similarity(t1, t2) for t1, t2 in zip(texts1, texts2)]


class EmbeddingSimilarity(SimilarityComputer):
    """
    محاسبه شباهت با استفاده از embeddings
    از cosine similarity بین بردارهای embedding استفاده می‌کند
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Args:
            model_name: نام مدل embedding (پیش‌فرض: all-MiniLM-L6-v2)
        """
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """بارگذاری مدل (lazy loading)"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "برای استفاده از EmbeddingSimilarity، sentence-transformers را نصب کنید:\n"
                    "pip install sentence-transformers"
                )
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """دریافت embedding برای یک متن"""
        self._load_model()
        embedding = self._model.encode(text, convert_to_numpy=True)
        return embedding
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """محاسبه cosine similarity بین دو embedding"""
        emb1 = self._get_embedding(text1)
        emb2 = self._get_embedding(text2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        # نرمال‌سازی به بازه [0, 1]
        return float((similarity + 1) / 2)
    
    def compute_batch_similarity(self, texts1: List[str], texts2: List[str]) -> List[float]:
        """محاسبه شباهت برای چندین جفت متن"""
        if len(texts1) != len(texts2):
            raise ValueError("تعداد متون در هر لیست باید برابر باشد")
        
        self._load_model()
        embeddings1 = self._model.encode(texts1, convert_to_numpy=True)
        embeddings2 = self._model.encode(texts2, convert_to_numpy=True)
        
        similarities = []
        for emb1, emb2 in zip(embeddings1, embeddings2):
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            similarities.append(float((similarity + 1) / 2))
        
        return similarities


class SimpleWordSimilarity(SimilarityComputer):
    """
    محاسبه شباهت ساده بر اساس کلمات مشترک
    برای استفاده در تست‌ها و مثال‌ها (بدون نیاز به مدل)
    """
    
    def __init__(self, similarity_matrix: Optional[Dict[Tuple[str, str], float]] = None):
        """
        Args:
            similarity_matrix: ماتریس شباهت از پیش تعریف شده
        """
        self.similarity_matrix = similarity_matrix or {}
    
    def _word_overlap_similarity(self, text1: str, text2: str) -> float:
        """محاسبه شباهت بر اساس همپوشانی کلمات"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """محاسبه شباهت"""
        # بررسی ماتریس از پیش تعریف شده
        key1 = (text1.lower(), text2.lower())
        key2 = (text2.lower(), text1.lower())
        
        if key1 in self.similarity_matrix:
            return self.similarity_matrix[key1]
        if key2 in self.similarity_matrix:
            return self.similarity_matrix[key2]
        
        # استفاده از همپوشانی کلمات
        return self._word_overlap_similarity(text1, text2)
    
    def compute_batch_similarity(self, texts1: List[str], texts2: List[str]) -> List[float]:
        """محاسبه شباهت برای چندین جفت متن"""
        return [self.compute_similarity(t1, t2) for t1, t2 in zip(texts1, texts2)]


class LLMSimilarity(SimilarityComputer):
    """
    محاسبه شباهت با استفاده از LLM
    می‌تواند از یک LLM کوچک برای محاسبه دقیق‌تر شباهت استفاده کند
    """
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", use_api: bool = False):
        """
        Args:
            model_name: نام مدل LLM
            use_api: استفاده از API (برای مدل‌های بزرگ) یا مدل محلی
        """
        self.model_name = model_name
        self.use_api = use_api
        self._model = None
    
    def _load_model(self):
        """بارگذاری مدل LLM"""
        if self._model is None:
            if self.use_api:
                # برای استفاده از API (نیاز به کلید API)
                pass
            else:
                # استفاده از مدل محلی کوچک
                try:
                    from transformers import pipeline
                    self._model = pipeline("text-classification", model="distilbert-base-uncased")
                except ImportError:
                    raise ImportError(
                        "برای استفاده از LLMSimilarity، transformers را نصب کنید:\n"
                        "pip install transformers torch"
                    )
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        محاسبه شباهت با LLM
        در این پیاده‌سازی ساده، از embedding استفاده می‌کنیم
        برای استفاده واقعی از LLM، می‌توان prompt طراحی کرد
        """
        # برای سادگی، از embedding استفاده می‌کنیم
        # در پیاده‌سازی کامل، می‌توان از LLM برای محاسبه مستقیم استفاده کرد
        embedding_sim = EmbeddingSimilarity()
        return embedding_sim.compute_similarity(text1, text2)
    
    def compute_batch_similarity(self, texts1: List[str], texts2: List[str]) -> List[float]:
        """محاسبه شباهت برای چندین جفت متن"""
        embedding_sim = EmbeddingSimilarity()
        return embedding_sim.compute_batch_similarity(texts1, texts2)


def build_semantic_graph_from_texts(
    texts: List[str],
    similarity_computer: SimilarityComputer,
    similarity_threshold: float = 0.3,
    connect_all: bool = False
):
    """
    ساخت گراف معنایی از لیست متون
    
    Args:
        texts: لیست متون
        similarity_computer: محاسبه‌گر شباهت
        similarity_threshold: حداقل شباهت برای ایجاد یال
        connect_all: آیا تمام گره‌ها را به هم متصل کنیم؟
    
    Returns:
        گراف معنایی ساخته شده
    """
    from semantic_graph import SemanticGraph
    
    graph = SemanticGraph(similarity_threshold=similarity_threshold)
    
    # افزودن تمام گره‌ها
    for text in texts:
        graph.add_node(text)
    
    # محاسبه شباهت و افزودن یال‌ها
    if connect_all:
        # محاسبه شباهت بین تمام جفت‌ها
        for i, text1 in enumerate(texts):
            for j, text2 in enumerate(texts[i+1:], start=i+1):
                similarity = similarity_computer.compute_similarity(text1, text2)
                if similarity >= similarity_threshold:
                    graph.add_bidirectional_edge(text1, text2, similarity)
    else:
        # فقط یال‌های با شباهت بالا
        for i, text1 in enumerate(texts):
            for j, text2 in enumerate(texts[i+1:], start=i+1):
                similarity = similarity_computer.compute_similarity(text1, text2)
                if similarity >= similarity_threshold:
                    graph.add_bidirectional_edge(text1, text2, similarity)
    
    return graph

