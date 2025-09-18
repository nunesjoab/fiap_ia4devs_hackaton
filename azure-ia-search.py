# 1. Instalar pacotes necessários
!pip install azure-search-documents

# 2. Importar dependências
import json
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    ComplexField,
    SearchField
)

# 3. Credenciais e configuração
SEARCH_SERVICE_NAME = "SERVICE NAME"
SEARCH_API_KEY = "API KEY"
SEARCH_INDEX_NAME = "cloud-components-index"

endpoint = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
credential = AzureKeyCredential(SEARCH_API_KEY)
index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
search_client = SearchClient(endpoint=endpoint, index_name=SEARCH_INDEX_NAME, credential=credential)

# 4. Criar índice (apaga se já existir)
def create_index():
    try:
        index_client.get_index(SEARCH_INDEX_NAME)
        index_client.delete_index(SEARCH_INDEX_NAME)
        print(f"🗑️ Índice antigo '{SEARCH_INDEX_NAME}' removido.")
    except Exception:
        print("ℹ️ Nenhum índice anterior encontrado.")

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="product", type=SearchFieldDataType.String, searchable=True, filterable=True),
        SearchableField(name="cloud", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
        SearchableField(name="categoria", type=SearchFieldDataType.String, searchable=True, filterable=True, facetable=True),
        SearchableField(name="descricao", type=SearchFieldDataType.String, searchable=True),
        SimpleField(name="link_oficial", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="recomendacoes", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True),
        SearchField(name="cis_controls", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True),
        SearchField(name="nist_controls", type=SearchFieldDataType.Collection(SearchFieldDataType.String), searchable=True),
        ComplexField(
            name="stride",
            fields=[
                SearchableField(name="S", type=SearchFieldDataType.String, searchable=True),
                SearchableField(name="T", type=SearchFieldDataType.String, searchable=True),
                SearchableField(name="R", type=SearchFieldDataType.String, searchable=True),
                SearchableField(name="I", type=SearchFieldDataType.String, searchable=True),
                SearchableField(name="D", type=SearchFieldDataType.String, searchable=True),
                SearchableField(name="E", type=SearchFieldDataType.String, searchable=True),
            ]
        )
    ]

    index = SearchIndex(name=SEARCH_INDEX_NAME, fields=fields)
    result = index_client.create_index(index)
    print(f"✅ Novo índice criado: {result.name}")

# 5. Upload de JSON a partir de arquivo local
def upload_json_file(file_path):
    print(f"📂 Lendo arquivo JSON: {file_path}")

    with open(file_path, "r", encoding="utf-8-sig") as f:
        try:
            docs = json.load(f)  # array de objetos
        except json.JSONDecodeError as e:
            print(f"❌ Erro ao ler JSON: {e}")
            return

    # Garantir tipos corretos para o Azure
    for doc in docs:
        # Campos simples → string
        for field in ["product", "categoria", "cloud", "descricao", "link_oficial"]:
            if isinstance(doc.get(field), list):
                doc[field] = ", ".join(doc[field])
            elif doc.get(field) is None:
                doc[field] = ""

        # Campos coleção → lista
        for field in ["recomendacoes", "cis_controls", "nist_controls"]:
            if field not in doc or doc[field] is None:
                doc[field] = []
            elif not isinstance(doc[field], list):
                doc[field] = [doc[field]]

        # STRIDE → dict
        if "stride" not in doc or not isinstance(doc["stride"], dict):
            doc["stride"] = {"S": "", "T": "", "R": "", "I": "", "D": "", "E": ""}
        # Garantir que todos os campos do STRIDE existam
        for key in ["S", "T", "R", "I", "D", "E"]:
            if key not in doc["stride"] or doc["stride"][key] is None:
                doc["stride"][key] = ""

    # Upload em lotes de 500 documentos
    step = 500
    for i in range(0, len(docs), step):
        batch = docs[i:i+step]
        try:
            search_client.upload_documents(documents=batch)
            print(f"📤 Upload de {len(batch)} documentos concluído (lote {i//step + 1})")
        except Exception as e:
            print(f"❌ Erro ao fazer upload do lote {i//step + 1}: {e}")

    print(f"✅ Upload finalizado. Total de documentos enviados: {len(docs)}")

# Verificar documentos processados
def verificar_documentos_processados(docs, num_exemplos=2):
    print(f"\n📄 Verificando {num_exemplos} exemplos de documentos processados:")
    for i, doc in enumerate(docs[:num_exemplos]):
        print(f"\nDocumento {i+1}:")
        print(f"  - id: {doc.get('id')}")
        print(f"  - product: {doc.get('product')}")
        print(f"  - cloud: {doc.get('cloud')}")
        print(f"  - categoria: {doc.get('categoria')}")
        print(f"  - recomendacoes: {doc.get('recomendacoes')}")
        print(f"  - stride: {doc.get('stride')}")

# 6. Função de busca de teste com diagnóstico
def search_documents():
    # Primeiro, verificamos se existem documentos no índice
    results = search_client.search(search_text="*", top=1)
    docs_count = len(list(results))

    if docs_count == 0:
        print("\n⚠️ Nenhum documento encontrado no índice. Possíveis causas:")
        print("   - Os documentos ainda estão sendo indexados (aguarde alguns segundos)")
        print("   - Houve um problema no upload (verifique erros anteriores)")
        return
    else:
        print(f"\n✅ Índice contém documentos ({docs_count} verificados)")

    # Teste 1: Busca sem filtros para verificar se existem documentos
    print("\n🔍 Teste 1: Busca sem filtros")
    results = search_client.search(search_text="*", top=5)
    print_results(results)

    # Teste 2: Busca apenas com o termo "storage"
    print("\n🔍 Teste 2: Busca por 'storage'")
    results = search_client.search(search_text="storage", top=5)
    print_results(results)

    # Teste 3: Busca apenas com filtro por cloud=azure
    print("\n🔍 Teste 3: Filtrando cloud='azure'")
    results = search_client.search(search_text="*", filter="cloud eq 'azure'", top=5)
    print_results(results)

    # Teste 4: Busca original (combinando termo e filtro)
    print("\n🔍 Teste 4: Busca original (storage + filtro azure)")
    results = search_client.search(search_text="storage", filter="cloud eq 'azure'", top=5)
    print_results(results)

def print_results(results):
    count = 0
    for r in results:
        count += 1
        print(f"- {r['product']} ({r['cloud']}) | Categoria: {r['categoria']}")
        print(f"  Recomendações: {r.get('recomendacoes',[])}")
        print(f"  STRIDE: {r.get('stride',{})}")
        print("-" * 80)

    if count == 0:
        print("Nenhum resultado encontrado para esta consulta.")
    else:
        print(f"Total: {count} resultados")

# 7. Executar
#create_index()
# Substitua pelo caminho do seu arquivo JSON local
#upload_json_file("/content/cloud_components_dataset_full_AZ_AWS.json")
search_documents()
