from ai_api.assistant.rag_db.abs_db import AbsRAG_DB
from my_langchain.text.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from my_langchain.text.vector.base_embeddings import BaseEmbeddings
from ai_api.assistant.rag_db.chroma import Chroma


class SimpleChroma(AbsRAG_DB):
    def __init__(self, file_paths):
        super().__init__(file_paths)

    def init_rag_instance(self, embeddings: BaseEmbeddings = None):
        """Инициализация ChromaDB - сразу разделяем на чанки"""
        if not self._initialized:
            print("Инициализация ChromaDB...")
            self.split_into_chunks()  # ChromaDB требует предварительного разделения
            self._initialized = True

    def split_into_chunks(self):
        for file_path in self._file_paths:
            with open(file_path, 'r',
                      encoding='utf-8') as file:
                doc_text = file.read()

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                separators=["\n\n", "\n", "(?<=\. )"]
            )
            self._splited_data+= splitter.split_text(doc_text)

    def get_relevant_text(self, question: str, embedding: BaseEmbeddings) -> str:
        vectordb_ct = Chroma.from_texts(self._splited_data, embedding=embedding)
        docs = vectordb_ct.similarity_search(question, k=3)
        return "\n\nФрагмент текста\n\n".join([doc['page_content'] for doc in docs])
