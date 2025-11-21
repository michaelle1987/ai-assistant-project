from langchain.text.vector.yandex_embeddings import YandexEmbeddings
from langchain.text.recursive_character_text_splitter import RecursiveCharacterTextSplitter
from langchain.text.vector.chroma import Chroma
import numpy as np

text = 'Благодаря появлению LLM возникла новая професссия будущего. \
Это промпт-инженер, который наилучшим образом направляет LLM на правильный путь . \
Этот специалист должен обладать творческим мышлением и аналитическими способностями, \
и желательно знанием методов машинного обучения и NLP и навыками программирования'

# Создаем наш сплиттер с вашими параметрами
splitter = RecursiveCharacterTextSplitter(
    chunk_size=250,
    chunk_overlap=0,
    separators=['. ']
)

# Разделяем текст
splited_data = splitter.split_text(text)
print("Результат разделения:")
for i, chunk in enumerate(splited_data):
    print(f"\nЧанк {i+1} (длина: {len(chunk)}):")
    print(f"'{chunk}'")

token='t1.9euelZqQy5eMkpeNkIrMj5OVz5mRk-3rnpWalZmajs6Mj5eSz4yez46XyY3l8_d1A0M4-e8oCnAu_t3z9zUyQDj57ygKcC7-zef1656VmovOzcaVmIyNis6Zk8uVx8uS7_zN5_XrnpWaksyNnJqcnsmKnpyXj5uKzs3v_cXrnpWai87NxpWYjI2KzpmTy5XHy5I.6OJtdVq3loNNT-7jjR5_r2t9589q3QNS7E_xEaGf6qH9P0087E0aBB3736qDdV0LBDD2Fi002D5xgDUDK8KcCA'
embedding = YandexEmbeddings(credentials=token)
vectordb_ct = Chroma.from_texts(splited_data, embedding=embedding)

question = "Кто такой промпт-инженер?"
docs = vectordb_ct.similarity_search(question,k=1)
print('')
print('docs')
print(docs)

"""similarity в выводе - это косинусное сходство между:

Эмбеддингом запроса (question = "Кто такой промпт-инженер?")

Эмбеддингом найденного чанка (. Это промпт-инженер, который наилучшим образом направляет LLM на правильный путь)"""

new_question = "Кто такие пчелы?"
# Обычный поиск - может найти очень похожие документы
# docs_simple = vectordb_ct.similarity_search(question, k=2)
# print("Обычный поиск:")
# for doc in docs_simple:
#     print(f"- {doc['page_content'][:100]}...")
#
# # MMR поиск - найдет релевантные, но разные документы
# docs_mmr = vectordb_ct.max_marginal_relevance_search(question, k=2, fetch_k=4)
# print("\nMMR поиск:")
# for doc in docs_mmr:
#     print(f"- {doc['page_content'][:100]}...")


embedding1 = embedding.embed_query(new_question)
embedding2 = embedding.embed_query(docs[0]['page_content'])  # ← исправлено
similarity = np.dot(embedding1, embedding2)
cosine_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

"""np.dot() - это скалярное произведение, которое зависит от длины векторов.
cosine_similarity - это нормированное сходство, которое учитывает только направление.
Всегда используй cosine_sim для надежности!"""

print(f"Сходство: {similarity}")
print(f"Сходство: {cosine_sim}")