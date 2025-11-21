import os

from unstructured_ingest.pipeline.pipeline import Pipeline
from unstructured_ingest.interfaces import ProcessorConfig
from unstructured_ingest.processes.connectors.local import (
    LocalIndexerConfig,
    LocalDownloaderConfig,
    LocalConnectionConfig,
    LocalUploaderConfig
)
from unstructured_ingest.processes.partitioner import PartitionerConfig
from unstructured_ingest.processes.chunker import ChunkerConfig

if __name__ == "__main__":
    os.environ["UNSTRUCTURED_API_KEY"] = ""
    os.environ["UNSTRUCTURED_URL"] = ""

    directory_with_pdfs=r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\assistant\knowledge_base\zerocoder\input' # откуда брать данные
    directory_with_results=r'C:\Users\mnigh\PycharmProjects\PythonProject\ai_api\assistant\knowledge_base\zerocoder\output' # куда отправлять данные

    Pipeline.from_configs( # настройки
        context=ProcessorConfig(),
        indexer_config=LocalIndexerConfig(input_path=directory_with_pdfs),
        downloader_config=LocalDownloaderConfig(),
        source_connection_config=LocalConnectionConfig(),
        partitioner_config=PartitionerConfig(
            partition_by_api=True,
            api_key=os.getenv("UNSTRUCTURED_API_KEY"),
            partition_endpoint=os.getenv("UNSTRUCTURED_API_URL"),
            strategy="hi_res",
            additional_partition_args={
                "language": "rus",
                "split_pdf_page": True, # разделять текст на "кусочки"
                "split_pdf_concurrency_level": 15, # параллельно будут обрабатываться 15 "кусочков"
                },
            ),
        uploader_config=LocalUploaderConfig(output_dir=directory_with_results)
    ).run()

    # pip install "protobuf<6.0" --force-reinstallpip uninstall grpcio-status grpcio-tools