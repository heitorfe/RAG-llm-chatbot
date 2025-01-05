from dotenv import load_dotenv
import os
from datetime import timedelta
from azure.identity import get_bearer_token_provider
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection
)
from azure.search.documents.indexes.models import (
    SplitSkill,
    InputFieldMappingEntry,
    OutputFieldMappingEntry,
    AzureOpenAIEmbeddingSkill,
    SearchIndexerIndexProjection,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    IndexProjectionMode,
    SearchIndexerSkillset,
    IndexingParametersConfiguration
)
from datetime import datetime
load_dotenv()

# Set endpoints and API keys for Azure services
AZURE_SEARCH_SERVICE = os.getenv("AZURE_SEARCH_SERVICE")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_OPENAI_ACCOUNT = os.getenv("AZURE_OPENAI_ACCOUNT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_AI_MULTISERVICE_ACCOUNT = os.getenv("AZURE_AI_MULTISERVICE_ACCOUNT")
AZURE_AI_MULTISERVICE_KEY = os.getenv("AZURE_AI_MULTISERVICE_KEY")
AZURE_STORAGE_CONNECTION = os.getenv("AZURE_STORAGE_CONNECTION")
CONTAINERS = ['public']
CONTENT = 'az-docs'
credential = AzureKeyCredential(AZURE_SEARCH_KEY)
index_client = SearchIndexClient(endpoint=AZURE_SEARCH_SERVICE, credential=credential)  

fields = [
    SearchField(
        name="chunk_id",
        type=SearchFieldDataType.String,
        key=True,
        stored=True,
        searchable=True,
        filterable=True,
        sortable=True,
        facetable=False,
        analyzer_name="keyword"
    ),
    SearchField(
        name="parent_id",
        type=SearchFieldDataType.String,
        key=False,
        stored=True,
        searchable=True,
        filterable=True,
        sortable=True,
        facetable=False
    ),
    SearchField(
        name="title",
        type=SearchFieldDataType.String,
        key=False,
        stored=True,
        searchable=True,
        filterable=False,
        sortable=False,
        facetable=False
    ),
    SearchField(
        name="chunk",
        type=SearchFieldDataType.String,
        key=False,
        stored=True,
        searchable=True,
        filterable=False,
        sortable=False,
        facetable=False
    ),
    SearchField(
        name="text_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        key=False,
        stored=True,
        searchable=True,
        filterable=False,
        sortable=False,
        facetable=False,
        vector_search_dimensions=3072,
        vector_search_profile_name="vp"
    )
]


vector_search=VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="algo", parameters=HnswParameters(metric=VectorSearchAlgorithmMetric.COSINE))
            ],
            compressions=[
                BinaryQuantizationCompression(
                    compression_name="bq",
                    default_oversampling=10,
                    rerank_with_original_vectors=True)
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                    vectorizer_name="openaivect",
                    parameters=AzureOpenAIVectorizerParameters(
                        resource_url=AZURE_OPENAI_ACCOUNT,
                        deployment_name="text-embedding-3-large",
                        model_name="text-embedding-3-large"
                    )
                )
            ],
            profiles=[
                VectorSearchProfile(name="vp", algorithm_configuration_name="algo", compression_name="bq", vectorizer_name="openaivect")
            ]
        )

semantic_search=SemanticSearch(
            configurations=[
                SemanticConfiguration(
                    name="semsearch",
                    prioritized_fields=SemanticPrioritizedFields(title_field=SemanticField(field_name="title"), content_fields=[SemanticField(field_name="chunk")])
                )
            ],
            default_configuration_name="semsearch"
        )


for container in CONTAINERS:
    index = SearchIndex(
        name=f"ix-{CONTENT}",
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    result = index_client.create_or_update_index(index)  
    print(f"{result.name} created")  

# DATA SOURCE
indexer_client = SearchIndexerClient(endpoint = AZURE_SEARCH_SERVICE, credential = credential)
for container in CONTAINERS:
    indexer_client.create_or_update_data_source_connection(
        data_source_connection=SearchIndexerDataSourceConnection(
            name=f"ds-{CONTENT}", 
            type=SearchIndexerDataSourceType.AZURE_BLOB,
            connection_string=AZURE_STORAGE_CONNECTION,
            container=SearchIndexerDataContainer(name=container)
           ))
    print(f" Criado data source ds-{CONTENT}")

# SKILLSET
for container in CONTAINERS:
    skillset_name = f'{CONTENT}-skillset-doc-to-vec'
    
    skills = [
                SplitSkill(
                    text_split_mode="pages",
                    context="/document",
                    maximum_page_length=2000,
                    page_overlap_length=500,
                    inputs=[InputFieldMappingEntry(name="text", source="/document/content")],
                    outputs=[OutputFieldMappingEntry(name="textItems", target_name="pages")]),
                AzureOpenAIEmbeddingSkill(
                    context="/document/pages/*",
                    resource_url=AZURE_OPENAI_ACCOUNT,
                    api_key=None,
                    deployment_name="text-embedding-3-large",
                    model_name="text-embedding-3-large",
                    dimensions=3072,
                    inputs=[InputFieldMappingEntry(name="text", source="/document/pages/*")],
                    outputs=[OutputFieldMappingEntry(name="embedding", target_name="text_vector")])
            ]
    
    index_projection = SearchIndexerIndexProjection(
                selectors=[
                    SearchIndexerIndexProjectionSelector(
                        target_index_name=f"ix-{CONTENT}",
                        parent_key_field_name="parent_id",
                        source_context="/document/pages/*",
                        mappings=[
                            InputFieldMappingEntry(name="chunk", source="/document/pages/*"),
                            InputFieldMappingEntry(name="text_vector", source="/document/pages/*/text_vector"),
                            InputFieldMappingEntry(name="title", source="/document/metadata_storage_name"),
                        ]
                    )
                ],
                parameters=SearchIndexerIndexProjectionsParameters(
                    projection_mode=IndexProjectionMode.SKIP_INDEXING_PARENT_DOCUMENTS
                )
    )
    
        
    indexer_client.create_or_update_skillset(
        skillset=SearchIndexerSkillset(
            name=skillset_name,
            skills=skills,
            index_projection=index_projection
            )
    )
    
    print(f"SKILLSET {skillset_name} created")  

# INDEXER
    count = 0
for container in CONTAINERS:

    data_source_name = f'ds-{CONTENT}'
    target_index_name = f'ix-{CONTENT}'
    skillset_name = f'{CONTENT}-skillset-doc-to-vec'
    indexer_name = f'indexer-{CONTENT}'
    indexer_client.create_or_update_indexer(
    indexer=SearchIndexer(
        name=indexer_name,
        data_source_name=data_source_name,
        skillset_name=skillset_name,
        target_index_name= target_index_name,        
        field_mappings=[FieldMapping(source_field_name="metadata_storage_name", target_field_name="title")]
        ,schedule=IndexingSchedule(
                interval=timedelta(hours=1),
                start_time= datetime.now() + timedelta(minutes=count)
            )
        ,parameters= IndexingParameters(configuration=IndexingParametersConfiguration(data_to_extract='contentAndMetadata', query_timeout=None))
    )
)
    count+=10

    print(f' {indexer_name} is created and running. Give the indexer a few minutes before running a query.')  



