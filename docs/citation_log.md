# citation_log.md — Registo de citações verificadas

> **Protocolo de integridade de citações (§6.4):** nenhuma entrada entra no `.bib` sem identificador verificado.
> Para cada referência: identificador (DOI / arXiv id / URL), data de verificação e fonte que confirmou.
> **Se não se verifica, não entra na tese.**

## Referências verificadas (a entrar no `references.bib` na Fase D)
| Chave .bib (proposta) | Referência | Identificador | Verificado em | Fonte | Estado |
|---|---|---|---|---|---|
| `chandola2009anomaly` | Chandola, Banerjee & Kumar (2009), "Anomaly detection", ACM Computing Surveys 41(3) | DOI 10.1145/1541880.1541882 | 2026-06-21 | Crossref | ✅ verificado |
| `brown1985daily` | Brown & Warner (1985), "Using daily stock returns: The case of event studies", J. Financial Economics 14(1) | DOI 10.1016/0304-405X(85)90042-X | 2026-06-21 | Crossref | ✅ verificado |
| `reimers2019sbert` | Reimers & Gurevych (2019), "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks", EMNLP-IJCNLP | DOI 10.18653/v1/D19-1410 | 2026-06-21 | Crossref | ✅ verificado |
| `araci2019finbert` | Araci (2019), "FinBERT: Financial Sentiment Analysis with Pre-trained Language Models" | arXiv:1908.10063 | 2026-06-21 | arXiv API | ✅ verificado |
| `lundberg2017shap` | Lundberg & Lee (2017), "A Unified Approach to Interpreting Model Predictions" (SHAP), NeurIPS | arXiv:1705.07874 | 2026-06-21 | arXiv API | ✅ verificado |
| `arrieta2020xai` | Arrieta et al. (2020), "Explainable Artificial Intelligence (XAI): Concepts, taxonomies…", Information Fusion 58 | DOI 10.1016/j.inffus.2019.12.012 | 2026-06-21 | Crossref | ✅ verificado |
| `adadi2018peeking` | Adadi & Berrada (2018), "Peeking Inside the Black-Box: A Survey on XAI", IEEE Access 6 | DOI 10.1109/ACCESS.2018.2870052 | 2026-06-21 | Crossref | ✅ verificado |
| `dong2024fnspid` | Dong, Fan & Peng (2024), "FNSPID: A Comprehensive Financial News Dataset in Time Series" | arXiv:2402.06698 | 2026-06-21 | arXiv API | ✅ verificado |

## Contextualização — fontes atuais 2025–2026 (§6.1; verificadas em fonte primária)
| Chave .bib | Referência | Identificador | Verificado em | Fonte | Estado |
|---|---|---|---|---|---|
| `sifma2025factbook` | SIFMA (2025), *2025 Capital Markets Fact Book* | PDF oficial SIFMA (cap. ações US = 49,1% global / $62,2T, 2024) | 2026-06-21 | PDF SIFMA (extraído) | ✅ verificado |
| `gallup2025stock` | Gallup (2025), *What Percentage of Americans Own Stock?* | news.gallup.com/poll/266807 (62% em 2025) | 2026-06-21 | Página Gallup | ✅ verificado |
| `ccaf2026aifs` | CCAF/Cambridge (2026), *Global AI in Financial Services Report* | jbs.cam.ac.uk (81% adoção; 40% avançada; 71% GenAI) | 2026-06-21 | Página CCAF | ✅ verificado |

## Rejeitadas / não verificáveis (NÃO usar)
| Referência | Motivo | Data |
|---|---|---|
| MacKinlay (1997), "Event Studies in Economics and Finance", JEL 35(1) | Sem DOI resolúvel (JSTOR 2729691 → 404 no Crossref; ausente no OpenAlex search). Substituída por `brown1985daily`. | 2026-06-21 |

> Nota: ainda **não** existe `references.bib` (criado na Fase D). Estas entradas verificadas são a base inicial;
> cada uma será transcrita para BibTeX e citada apenas onde fizer sentido. Mais referências (contextualização
> 2025–2026, revisão de literatura) serão verificadas e adicionadas nas fases de escrita.
