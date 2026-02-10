# Implementation Status - DEV-LYNXEO-DATAPLATFORM-MBS

> Comparaison entre le workspace de référence (DEV-LYNXEO-DATAPLATFORM) et le workspace MBS.
> Objectif : implémenter les pipelines pour 2 sources (API endpoint, ).

---

## Etat actuel du workspace MBS

| Type | Item | Statut |
|------|------|--------|
| Lakehouse | dataplatform_mbs | Existant |
| SQLEndpoint | dataplatform_mbs | Existant (auto-généré) |

**Total : 2 items** (vs 76 dans DEV)

---

## 1. FONDATIONS (Utils & Setup) - A recréer

Ces éléments sont nécessaires AVANT de pouvoir créer les pipelines.

| Item (DEV) | Type | Rôle | Statut MBS |
|------------|------|------|------------|
| `utils_bronze_functions` | Notebook | Fonctions réutilisables Bronze (find_files, extract_date, clean_header, process_ingestion) | A CREER |
| `utils_bronze_to_silver` | Notebook | Fonctions réutilisables Silver (get_last_run, dedup, upsert, read_source) | A CREER |
| `utils_transformation_functions` | Notebook | Fonctions de transformation | A CREER |
| `utils_logging_functions` | Notebook | Fonctions de logging/audit | A CREER |
| `utils_orchestration_functions` | Notebook | Fonctions d'orchestration (DAG, ThreadPool) | A CREER |
| `lib_environment_variables` | VariableLibrary | Variables d'environnement | A CREER |
| `ddl_create_schema_bronze` | Notebook | Création schéma bronze | A CREER |
| `ddl_create_silver_tables_v1.0` | Notebook | DDL tables Silver | A CREER |
| `ddl_create_gold_tables_v1.0` | Notebook | DDL tables Gold | A CREER |
| `ddl_create_log_tables_v1.0` | Notebook | DDL tables de logs/audit | A CREER |

---

## 2. BRONZE - Ingestion brute

| Item (DEV) | Type | Rôle | Statut MBS |
|------------|------|------|------------|
| `nb_adls_to_bronze` | Notebook | Notebook générique d'ingestion (lit YAML config) | A CREER |
| Config YAML `azure_consumption` | Fichier (Files/) | Config ingestion CSV Azure Consumption | A CREER |
| Config YAML `msentraid_account` | Fichier (Files/) | Config ingestion JSON EntraID Account | A CREER |
| Config YAML `tanium_workstation` | Fichier (Files/) | Config ingestion CSV Tanium Workstation | A CREER |

> Note : `nb_xls_to_bronze` et `pip_sharepoint_to_bronze` ne sont pas nécessaires pour nos 3 sources.

---

## 3. SILVER - Transformation & Nettoyage

Un notebook par table source. A créer pour nos 3 sources :

| Item à créer | Source Bronze | Cible Silver | Statut MBS |
|--------------|-------------|-------------|------------|
| `nb_bronze_to_silver_azure_consumption` | bronze.azure_consumption | silver.azure_consumption | A CREER |
| `nb_bronze_to_silver_msentraid_account` | bronze.msentraid_account | silver.msentraid_account | A CREER |
| `nb_bronze_to_silver_tanium_workstation` | bronze.tanium_workstation | silver.tanium_workstation | A CREER |

> Les notebooks Silver existants dans DEV (bill_*, cash_*, env_*, hr_*) ne sont PAS à recréer car ils concernent d'autres domaines.

---

## 4. GOLD - Agrégation business (star schema)

A définir selon les besoins Power BI. Potentiellement :

| Item à créer | Source Silver | Cible Gold | Statut MBS |
|--------------|-------------|-----------|------------|
| `nb_silver_to_gold_it_fact_azure_consumption` | silver.azure_consumption | gold.fact_azure_consumption | A DEFINIR |
| `nb_silver_to_gold_it_dim_subscription` | silver.azure_consumption | gold.dim_subscription | A DEFINIR |
| `nb_silver_to_gold_it_dim_meter_category` | silver.azure_consumption | gold.dim_meter_category | A DEFINIR |
| `nb_silver_to_gold_it_fact_entraid_account` | silver.msentraid_account | gold.fact_entraid_account | A DEFINIR |
| `nb_silver_to_gold_it_fact_tanium_workstation` | silver.tanium_workstation | gold.fact_tanium_workstation | A DEFINIR |
| `nb_silver_to_gold_it_dim_location` | silver.tanium_workstation | gold.dim_location | A DEFINIR |

> Le modèle Gold dépend des besoins analytiques. A affiner après validation Silver.

---

## 5. ORCHESTRATION

| Item (DEV) | Type | Rôle | Statut MBS |
|------------|------|------|------------|
| `orchestrator_bronze_to_silver` | Notebook | Exécution parallèle Silver notebooks | A CREER |
| `orchestrator_silver_to_gold` | Notebook | Exécution parallèle Gold notebooks | A CREER |
| `refresh_semantic_model` | Notebook | Refresh du Semantic Model | A CREER |
| `refresh_SQL_endpoint` | Notebook | Refresh du SQL Endpoint | A CREER |
| `00_orchestrator_data_platform_daily` | DataPipeline | Pipeline principal quotidien | A CREER |
| `pipeline_alerting_global` | DataPipeline | Alerting Teams/Email | A CREER |

---

## 6. TEMPLATES (optionnel mais utile)

| Item (DEV) | Statut MBS |
|------------|------------|
| `template_nb_bronze_to_silver_[stream]_[entity_name]` | A CREER |
| `template_nb_silver_to_gold_[stream]_[entity]` | A CREER |

---

## Ordre d'implémentation recommandé

```
Phase 1 - Fondations
  1.1  lib_environment_variables
  1.2  utils_bronze_functions
  1.3  utils_logging_functions
  1.4  utils_bronze_to_silver
  1.5  utils_transformation_functions
  1.6  utils_orchestration_functions
  1.7  ddl_create_schema_bronze
  1.8  ddl_create_log_tables_v1.0
  1.9  ddl_create_silver_tables_v1.0
  1.10 ddl_create_gold_tables_v1.0

Phase 2 - Bronze (ingestion)
  2.1  nb_adls_to_bronze (notebook générique)
  2.2  YAML config azure_consumption
  2.3  YAML config msentraid_account
  2.4  YAML config tanium_workstation
  2.5  Test : exécution Bronze pour les 3 sources

Phase 3 - Silver (transformation)
  3.1  nb_bronze_to_silver_azure_consumption
  3.2  nb_bronze_to_silver_msentraid_account
  3.3  nb_bronze_to_silver_tanium_workstation
  3.4  Test : exécution Silver pour les 3 sources

Phase 4 - Gold (à définir)
  4.1  Définir le modèle de données Gold (star schema IT)
  4.2  Créer les notebooks Gold
  4.3  Test : exécution Gold

Phase 5 - Orchestration
  5.1  orchestrator_bronze_to_silver
  5.2  orchestrator_silver_to_gold
  5.3  00_orchestrator_data_platform_daily (pipeline)
  5.4  Test end-to-end
```

---

## Données sources disponibles (ADLS landingdata)

| Source | Chemin | Format | Fichiers | Fréquence |
|--------|--------|--------|----------|-----------|
| Azure Consumption | `AZURE/CONSUMPTION/` | CSV (7 cols) | 1 | Mensuel |
| EntraID Account | `MSENTRAID/ACCOUNT/` | JSON (nested) | 2 | Ponctuel |
| Tanium Workstation | `TANIUM/WORKSTATION/` | CSV (6 cols) | 2 | Ponctuel |

### Colonnes détaillées

**Azure Consumption** : `subscriptionId, subscriptionName, PreTaxCost, UsageQuantity, BillingMonth, MeterCategory, Currency`

**EntraID Account** : `{date_time, data[{id, userPrincipalName, displayName, accountEnabled, employeeType, officeLocation, assignedLicenses[{skuPartNumber, name}]}]}`

**Tanium Workstation** : `date_time, name, manufacturer, model, location, is_laptop`
