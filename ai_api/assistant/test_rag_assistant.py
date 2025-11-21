from ai_api.assistant.ai_model import AIModel, RAGModel
from ai_api.assistant.rag_assistant import RAGAssistant

def test():
    assistant = RAGAssistant(AIModel.YANDEX_GPT, system_prompt='Всегда приветствуй клиента, потом отвечай на вопрос',
                             file_paths=[
                                 r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\assistant\knowledge_base\zerocoder\main_info.md'],
                             rag_model=RAGModel.FLAT_INDEX)
    response = assistant.sendChatMessage("Меня интересует контактная информация")
    print("Ответ:")
    print(response.text)
    assistant.save_rag_index()

def test1():
    file_path = r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\assistant\knowledge_base\zerocoder\PE10.3.prompt.json'

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            system_prompt = file.read()
        print("Файл успешно прочитан")
    except FileNotFoundError:
        print(f"Файл не найден: {file_path}")
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")

    assistant = RAGAssistant(AIModel.YANDEX_GPT, system_prompt=system_prompt,
                             file_paths=[
                                 r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\assistant\knowledge_base\zerocoder\knowledgeBaseRealEstate.json'],
                             rag_model=RAGModel.FLAT_INDEX)
    print("Вопрос:")
    prompt=input()
    response = assistant.sendChatMessage(prompt)
    print("Ответ:")
    print(response.text)
    assistant.save_rag_index()

if __name__ == "__main__":
    test1()

# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ КЛАССОВ-НАСЛЕДНИКОВ
    # # Теперь ОБЯЗАТЕЛЬНО указывать rag_model
    # assistant = RAGAssistant(
    #     AIModel.YANDEX_GPT,
    #     file_paths=["doc1.txt", "doc2.txt"],
    #     rag_model=RAGModel.CHROMA_DB  # обязательно!
    # )
    #
    # # Или с FAISS
    # assistant = RAGAssistant(
    #     AIModel.YANDEX_GPT,
    #     file_paths=["doc1.txt", "doc2.txt"],
    #     rag_model=RAGModel.FLAT_INDEX  # обязательно!
    # )
    #
    # # С дополнительными параметрами
    # assistant = RAGAssistant(
    #     AIModel.YANDEX_GPT,
    #     file_paths=["doc1.txt", "doc2.txt"],
    #     rag_model=RAGModel.INVERTED_FILE_INDEX,  # обязательно!
    #     persist_directory="/custom/path",
    #     nlist=150  # специфичный параметр для IVF
    # )