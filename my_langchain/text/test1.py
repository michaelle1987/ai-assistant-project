from langchain.text.vector.yandex_embeddings import YandexEmbeddings
from langchain.text.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from langchain.text.vector.chroma import Chroma
from ai_api.assistant.ai_assistant import AIAssistant
from ai_api.assistant.ai_model import AIModel


def normalize_query(query: str) -> str:
    """Нормализация запроса для стабильного поиска"""
    return query.lower().strip()

def simple_rag_chain(vectordb,assistant,question: str):
    # 1. Поиск релевантных документов
    docs = vectordb.similarity_search(question, k=1)

    # 2. Форматирование контекста
    context = "\n\nФрагмент текста\n\n".join([doc['page_content'] for doc in docs])

    # 3. Создание промпта
    prompt_template = f"""Используй следующий контекст чтобы ответить на вопрос:
    
{context}

Вопрос: {question}
"""

    print(prompt_template)
    # 4. Отправка в модель
    response = assistant.sendChatMessage(prompt_template)
    return response.text

with open(r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\assistant\knowledge_base\zerocoder\main_info.md', 'r', encoding='utf-8') as file:
    doc_text = file.read()

# print(doc_text)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", "(?<=\. )"]
)
splited_data = splitter.split_text(doc_text)

token='t1.9euelZqQy5eMkpeNkIrMj5OVz5mRk-3rnpWalZmajs6Mj5eSz4yez46XyY3l8_d1A0M4-e8oCnAu_t3z9zUyQDj57ygKcC7-zef1656VmovOzcaVmIyNis6Zk8uVx8uS7_zN5_XrnpWaksyNnJqcnsmKnpyXj5uKzs3v_cXrnpWai87NxpWYjI2KzpmTy5XHy5I.6OJtdVq3loNNT-7jjR5_r2t9589q3QNS7E_xEaGf6qH9P0087E0aBB3736qDdV0LBDD2Fi002D5xgDUDK8KcCA'
embedding = YandexEmbeddings(credentials=token)
vectordb_ct = Chroma.from_texts(splited_data, embedding=embedding)

# Использование
answer = simple_rag_chain(vectordb_ct,AIAssistant(AIModel.YANDEX_GPT),"Подскажите ваши контакты")
print('answer')
print(answer)