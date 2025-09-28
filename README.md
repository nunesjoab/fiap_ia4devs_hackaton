# Trabalho Final do Hackaton do Grupo  
## AI Architecture Analyzer  

### Descrição  
O **AI Architecture Analyzer** é uma solução desenvolvida durante o Hackaton que recebe a **URL de um desenho de arquitetura cloud** (Azure ou AWS) através de uma **API REST** e analisa os componentes de acordo com as referências:  

- **CIS (Center for Internet Security)**  
- **NIST (National Institute of Standards and Technology)**  
- **STRIDE (Threat Modeling)**  

Com base nisso, são geradas recomendações automáticas de segurança e melhores práticas.   

---

## Arquitetura da Solução  

O desenho de arquitetura utilizado é o seguinte:  

![Arquitetura da Solução](arquitetura.jpeg)  

### Componentes  

- **API Management** → Exposição da API de entrada com o link do desenho da solução no formato PNG.  
- **Logic Apps** → Responsável por orquestrar toda a execução da solução.  
- **OpenAI (GPT-4)** → Interpreta o desenho e extrai automaticamente os componentes da arquitetura.  
- **Azure AI Search** → Armazena e indexa o dataset de componentes de arquitetura carregados previamente (via Colab).  
- **Azure Storage** → Armazena os relatórios gerados e disponibiliza links autenticados com expiração de **10 minutos**.  

---

## Canais de Entrada  
O projeto foi pensado como **omnichannel**, suportando diferentes canais de interação:  

- **Frontend Web** → [Frontend.html](https://postechaigrupo16.blob.core.windows.net/componentdataset/frontend.html?sp=r&st=2025-09-25T00:47:54Z&se=2025-11-25T09:02:54Z&spr=https&sv=2024-11-04&sr=b&sig=Gfc6KMF4DzE7jHiHYX9lTut7SN%2FpHF0gUUiMq%2BzESIQ%3D)  
  A interface web (`frontend.html`) permite que o usuário insira a URL do diagrama e receba o relatório.  

- **Bot no Telegram** → [Telegram](https://t.me/iadt4g19bot)  
  Instale o aplicativo do Telegram e use nosso bot para analisar seus desenhos de arquitetura.  

> 💡 Dica: use **Ctrl+Clique** (Windows/Linux) ou **⌘ Cmd+Clique** (macOS) para abrir em nova aba.  
> 🔗 A solução é expansível para qualquer outro canal que consuma **HTTP REST API**.  




## Exemplos de Input  

- Exemplo 1:  
  https://learn.microsoft.com/pt-br/azure/architecture/icons/images/real-time-analytics.png  

- Exemplo 2:  
  https://cdn.nulab.com/learn-wp/app/uploads/2021/08/14211858/architectural-diagram-2.png  

---


### Tela do Frontend  

![Exemplo de uso do frontend](frontend.png)  


### Bot do Telegram

![Exemplo de uso do bot do Telegram](bot.png)

O bot do Telegram foi configurado para acessar um webhook ao receber mensagens com link ou imagem. O código Python desse webhook se encontra nos arquivos fontes (telegram-bot-lambda.py) e foi adaptado para hospedagem no AWS Lambda, exposto para internet através do AWS Gateway. 


### Relatório Gerado  

![Exemplo de relatório](relatorio.png) 

---

## Resultado Esperado  

1. O usuário envia a URL de um **desenho de arquitetura**.  
2. O **AI Architecture Analyzer** identifica os componentes automaticamente.  
3. São aplicadas recomendações baseadas em **CIS**, **NIST** e **STRIDE**.  
4. O relatório final é gerado e armazenado no **Azure Storage**.  
5. O usuário recebe um **link autenticado (válido por 10 minutos)** para acessar o relatório.  

---


## Futuras Expansões  

- Suporte a **Google Cloud** e **Oracle Cloud**.  
- Integração com outros canais (**Microsoft Teams**, **Slack**).  
- Geração de relatórios em **PDF** com visualização gráfica das ameaças STRIDE.  
- Dashboards em **Power BI** para consolidar recomendações de múltiplas arquiteturas.




# Documentação sobre Integração com Azure Search

## Introdução
Este projeto permite a integração com o Azure Cognitive Search, possibilitando a criação de índices e o upload de documentos em formato JSON. Este documento tem como objetivo orientar os desenvolvedores e a equipe de TI sobre como configurar e utilizar o código disponibilizado.

## Acesso ao Código
O código está hospedado no repositório e pode ser acessado através do seguinte link:

[Repositório de Integração com Azure Search](#)  *(inserir link do repositório aqui)*

## Configuração Inicial
Para utilizar o código, é necessário seguir estas etapas:

1. **Instalação dos Pacotes**:
   Antes de executar o código, instale os pacotes necessários utilizando o seguinte comando:
   ```bash
   pip install azure-search-documents
   ```

2. **Configuração das Credenciais**:
   É necessário configurar as seguintes variáveis no código:
   - `SEARCH_SERVICE_NAME`: Nome do serviço de pesquisa no Azure.
   - `SEARCH_API_KEY`: Chave API para autenticação no Azure.
   - `SEARCH_INDEX_NAME`: Nome do índice a ser utilizado.
   
   Exemplo de configuração:
   ```python
   SEARCH_SERVICE_NAME = "NOME DO SERVIÇO"
   SEARCH_API_KEY = "SUA CHAVE API"
   SEARCH_INDEX_NAME = "cloud-components-index"
   ```

## Funções Principais
O código contém as seguintes funções principais:

1. **Criar Índice**: `create_index()`
   - Esta função cria um novo índice ou remove o índice existente.

2. **Fazer Upload de JSON**: `upload_json_file(file_path)`
   - Realiza o upload de documentos a partir de um arquivo JSON.

3. **Verificar Documentos Processados**: `verificar_documentos_processados(docs, num_exemplos=2)`
   - Verifica e imprime exemplos de documentos processados.

4. **Busca de Documentos**: `search_documents()`
   - Realiza buscas no índice e imprime os resultados.

5. **Imprimir Resultados**: `print_results(results)`
   - Formata a impressão dos resultados de busca.

## Execução do Código
Para executar o código, você deve chamar as funções na seguinte ordem:

1. **Criar Índice**:
   ```python
   create_index()
   ```

2. **Fazer Upload do Arquivo JSON**:
   ```python
   upload_json_file("/caminho/para/seu/arquivo.json")
   ```

3. **Buscar Documentos**:
   ```python
   search_documents()
   ```

Substitua `"/caminho/para/seu/arquivo.json"` pelo caminho do seu arquivo JSON.

## Suporte
Em caso de dúvidas ou problemas com a integração, entre em contato com a equipe de TI.

## Conclusão
Utilize este projeto para integrar com o Azure Cognitive Search e gerenciar índices e documentos de forma eficiente. Aproveite os recursos disponíveis para melhorar a busca e a organização dos dados da sua aplicação.
