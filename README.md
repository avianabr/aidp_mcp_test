# AIDP Lakehouse: desenvolvimento local e teste remoto

## Teste de Object Storage

`notebooks/Access_Object_Storage_Data_dev.ipynb` adapta o exemplo Oracle `getting-started/Access_Object_Storage_Data.ipynb`.

- Informe `OCI_BUCKET=oci://bucket@namespace` como parâmetro da tarefa. O bucket deve ser destinado ao teste e acessível pela identidade usada no compute AIDP.
- `CATALOG_NAME=default` e `SCHEMA_NAME=default` definem o destino dos metadados. Use um catálogo interno, não o catálogo externo do Autonomous Lakehouse.
- `BASE_PREFIX=aidp_codex_tests/object_storage` é o prefixo base. Cada execução acrescenta um identificador aleatório.
- O teste valida CSV por URI OCI, por volume externo e por tabela externa. Compara todos os valores, testa append nos arquivos da tabela externa e consulta novamente.
- Permanecem três diretórios de dados sintéticos, um volume externo e uma tabela externa por execução. Nenhum recurso anterior é sobrescrito ou apagado.
- O marcador de sucesso é `AIDP_OBJECT_STORAGE_TEST_RESULT=`. Validação local: `python3 scripts/validate_notebook.py notebooks/Access_Object_Storage_Data_dev.ipynb`.
- Runtime recomendado neste projeto: workspace `Medallion_arch`, compute `Medallion_Compute`. A criação de um workflow e o teste remoto dependem da escolha do bucket.

Notebook: `notebooks/Access_ALH_Data_dev.ipynb`, adaptado do exemplo Oracle:
https://github.com/oracle-samples/oracle-aidp-samples/blob/main/getting-started/Access_ALH_Data.ipynb

## Ambiente de teste

- Workspace: `Medallion_arch` (`c3131b56-0b74-4869-92aa-984a4d0123e8`).
- Compute: `Medallion_Compute` (`7196b48e-0f40-43d7-bd30-4fcce9f85d8e`).
- Catálogo: `oracle_26ai_lakehouse`.
- Autenticação do Ask-AIDP: perfil `DEFAULT`, `api_key`, região `us-ashburn-1`.

## Ciclo de desenvolvimento

1. Abra esta pasta no VS Code. Use o editor Jupyter para editar o notebook e o Codex para revisar as células.
2. Execute `python3 scripts/validate_notebook.py` para conferir JSON, células e sintaxe Python. Isso não executa Spark nem valida a conectividade remota.
3. Faça commit/push dos arquivos do projeto para uma branch de desenvolvimento. `.env`, wallets e evidências de execução ficam fora do Git.
4. Crie uma Git folder no workspace com URL do repositório, branch e chave da credencial Git cadastrada no AIDP. Sugestão de destino: `/Workspace/repos/alh-dev` (o caminho efetivo deve ser confirmado após a criação).
5. A cada mudança, faça pull da branch na Git folder e confirme a revisão recebida antes de iniciar o job. Não altere a pasta enquanto um job a estiver usando.
6. Crie um workflow exclusivo de teste apontando para o caminho remoto do notebook dentro da Git folder e para o compute acima. Não reutilize o workflow Bronze existente.
7. Execute e acompanhe o job com Ask-AIDP. Salve a revisão Git, job key, run key, status das tarefas e outputs em `qa-runs/`.
8. Procure no output `AIDP_ALH_TEST_RESULT=` e valide o conteúdo antes de considerar o teste aprovado.

O notebook exige o runtime AIDP (`spark` e `oidlUtils`). A execução pelo kernel Python local falha com uma mensagem explicativa. A extensão AIDP para VS Code pode acompanhar o workflow; a edição `.ipynb` usa o editor Jupyter.

## Parâmetros do workflow

| Nome | Padrão | Uso |
|---|---|---|
| CATALOG | oracle_26ai_lakehouse | Catálogo externo já provisionado |
| SCHEMA | vazio | Schema da tabela de teste |
| TABLE | vazio | Tabela de teste existente |
| WRITE_ENABLED | false | `true` habilita três inserts de dados sintéticos |

Com SCHEMA/TABLE vazios, apenas a descoberta de schemas é testada. Para validar leitura, informe ambos; o teste força a leitura de até cinco linhas sem imprimi-las.

Para escrita, prepare uma tabela exclusiva de teste com as seis colunas descritas no notebook. Cada execução gera IDs únicos e insere três linhas (duas via DataFrame, uma via SQL). As linhas permanecem na origem; uma nova execução adiciona outro conjunto. O parâmetro opcional `CREATE_TEST_TABLE=true` prepara uma tabela `admin.aidp_notebook_write_test*` via conector `aidataplatform`, sem sobrescrever uma tabela existente. O notebook não apaga os registros de teste.

Credenciais do banco são gerenciadas pelo catálogo AIDP. O notebook não precisa do wallet ou da senha ADMIN. Mantenha outputs de dados e credenciais fora dos commits.

## Ferramentas Ask-AIDP

- `aidp_create_git_folder`: criar a pasta vinculada ao repositório.
- `aidp_git_pull`: receber alterações.
- `aidp_git_get_repository`: conferir a conexão Git.
- `aidp_cli`: criar e executar o workflow.
- `aidp_track_runs`: acompanhar tarefas e coletar outputs.

As ferramentas Git nativas exigem `oci-common` e `aidp-typescript-client` disponíveis para o plugin. A disponibilidade dessas dependências e do recurso Git Preview deve ser validada antes da primeira criação.

Ainda não foram criados repositório Git, Git folder ou workflow de teste por este projeto.

Para o teste de escrita, configure SCHEMA=admin, TABLE=aidp_notebook_write_test e WRITE_ENABLED=true. Na primeira execução, use CREATE_TEST_TABLE=true para preparar a tabela. A validação confere três linhas e os valores de todas as colunas.
