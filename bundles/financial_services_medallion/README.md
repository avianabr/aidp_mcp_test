# Financial Services Medallion — bundle AIDP

Versão modular do [notebook financeiro original](../../notebooks/Financial_Services_Medallion_dev.ipynb), adaptado do [exemplo Oracle](https://github.com/oracle-samples/oracle-aidp-samples/blob/main/data-engineering/transformation/medallion-lake/financial_services_medallion_architecture_demo.ipynb).

## Artefatos

```text
financial_services_medallion/
├── aidp_workbench.yaml
├── jobs/finance_medallion_pipeline.job.json
├── artifacts/notebooks/
│   ├── bronze.ipynb
│   ├── silver.ipynb
│   ├── gold.ipynb
│   └── train.ipynb
└── overrides.example.yaml
```

O workflow executa `bronze → silver → gold → train`, com `ALL_SUCCESS`, uma execução concorrente e sem retries automáticos. Cada tarefa tem sessão independente e lê suas entradas persistidas no catálogo. O bundle referencia um compute existente; não provisiona compute adicional.

| Tarefa | Entrada | Saída / validação |
|---|---|---|
| Bronze | Gerador sintético com seed | `finance_bronze_<DATASET_ID>.account_transactions_bronze`; contagem gerada versus persistida |
| Silver | Tabela Bronze | `finance_silver_<DATASET_ID>.account_transactions_silver`; qualidade, datas e contagens |
| Gold | Tabela Silver | `finance_gold_<DATASET_ID>.transaction_analytics_gold` e `fraud_detection_model_gold`; reconciliação de valores, contagens e features |
| Train | Features Gold | Random Forest, AUC, matriz de confusão e importância das features no output |

As quatro tabelas são Delta gerenciadas no catálogo escolhido. O último nome é mantido por compatibilidade com o demo: `fraud_detection_model_gold` contém features, não um modelo serializado. O treinamento continua demonstrativo e não publica/persiste um novo modelo ou registra automaticamente um Experiment. A persistência e o Experiment anteriores são testes separados. Os rótulos derivam de risco aleatório; `risk_score` não entra nas features do modelo.

## Configuração e execução

1. Abra esta pasta no VS Code. Edite os notebooks em `artifacts/notebooks/` e o workflow em `jobs/`.
2. Valide cada notebook: `python3 scripts/validate_notebook.py bundles/financial_services_medallion/artifacts/notebooks/bronze.ipynb`, a partir da raiz do repositório; repita para Silver, Gold e Train.
3. Faça commit/push e pull da revisão na Git folder do AIDP.
4. Dentro do bundle no workspace, crie `.aidp/overrides.yaml` baseado em `overrides.example.yaml`. Informe `compute_key`, `dataset_id` e, se necessário, `catalog_name`. O placeholder `CONFIGURE_COMPUTE_KEY` do manifesto deve ser substituído por override antes de publicar.
5. Publique pela aba Deployment ou por `POST .../workspaces/{workspaceKey}/actions/publishBundle`, body `{"path":"/Workspace/repos/finance-bundle-dev/bundles/financial_services_medallion"}`. Acompanhe a operação assíncrona e consulte `actions/getBundlePublishStatus`.
6. Confira o job publicado `finance_medallion_pipeline` e execute. Ele usa os artefatos em `/Workspace/Shared/financial_services_medallion_modular/artifacts/notebooks/`.
7. Confira as quatro tarefas e os marcadores `AIDP_FINANCE_BUNDLE_STAGE_RESULT=`. Guarde outputs e evidências em `qa-runs/finance-bundle/`, fora do Git.

`DATASET_ID` deve começar com letra e conter até 48 letras, números ou underscores. Todas as tarefas recebem o mesmo valor pela variável `dataset_id` do bundle. As escritas usam `errorifexists`: uma nova carga completa exige **novo dataset_id e nova publicação**, preservando dados anteriores. Para retomar uma falha, execute/repare somente a tarefa que falhou e suas dependentes, mantendo o dataset. Não reinicie Bronze com destinos já criados.

Defaults mantêm 5.000 contas, seed 42, 100 árvores e profundidade 10. Liquid clustering permanece desligado. A execução exige runtime AIDP com `spark` e `oidlUtils`, compute acessível e permissões para criar schemas/tabelas no catálogo Standard. Não usa wallet ou senha do Autonomous Lakehouse.

## Manutenção e promoção

Este diretório é a fonte de verdade. Para mudanças locais, edite os artefatos/descritores, revise o diff, faça commit/push, pull no destino e publique novamente. Para atualizar artefatos já publicados pelo mesmo bundle, configure `overwrite_publish_artifacts: true` após revisar as mudanças. Evite editar as cópias de runtime em `/Workspace/Shared/`: a próxima publicação pode substituí-las.

O bundle foi inicialmente gerado pelo AIDP e seus descritores foram ajustados para caminhos curtos e variáveis de ambiente. `Sync` a partir do job de bootstrap recria o snapshot desse job e pode desfazer essas edições; para este fluxo de manutenção local, publique os arquivos versionados diretamente. `.aidp/` contém overrides e estado do ambiente e fica fora do Git.

Para outro workspace, mantenha a pasta completa, configure o compute e o catálogo de destino, escolha um dataset novo e um publish path exclusivo se necessário. O bundle cria os recursos do workflow; dados e credenciais do ambiente precisam existir ou ser criados pelas tarefas conforme descrito acima.

Referência: [Bundles and CI/CD (Preview)](https://docs.oracle.com/en/cloud/paas/ai-data-platform/aidug/git-bundles-oracle-ai-data-platform.html).
