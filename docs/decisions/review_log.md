# review_log.md — Revisão crítica independente (Fase C)

> Revisão da tese "do zero", como examinador/júri imparcial: deteta fraquezas, erros, inconsistências e
> pontos de ataque. Cada achado tem severidade e estado. Os achados de reprodução de estatística e a
> auditoria página-a-página final ficam para a Fase D/E.

**Data:** 2026-06-26 · **Versão revista:** 76 pp, 50 refs.

## Achados e estado

| # | Severidade | Local | Achado | Ação | Estado |
|---|---|---|---|---|---|
| C-1 | Média (consistência) | Cap. 1 §1.5 (Document Structure) | A lista das áreas do Estado da Arte está desatualizada: omite *behavioural finance/retail*, *information retrieval*, *trust/reliance* e *existing tools* (que existem no Cap. 2). Um examinador nota a divergência entre a promessa do Cap. 1 e o conteúdo do Cap. 2. | Atualizar a lista para refletir o Cap. 2 (sem ser exaustiva). | ✅ corrigido |
| C-2 | Baixa (rigor numérico) | Cap. 5 Tab. per-sector | O *lift* da Energia é +0,377 mas as colunas arredondadas dão 0,448−0,072 = 0,376. O *lift* é correto (calculado a partir de valores não arredondados, confirmado em `evaluation_per_sector.md`), mas a aritmética mental do leitor falha por 0,001. | Nota de rodapé: *lift* calculado a partir de valores não arredondados. | ✅ corrigido |
| C-3 | Média (clareza/consistência) | Cap. 5 §CS2 "Why some sectors retrieve better" | O exemplo do Walmart descreve recuperação **sem** a restrição cross-ticker ("retrieves mostly Walmart's own items"), mas a avaliação é **cross-ticker** (exclui o próprio ticker). Pode confundir. | Clarificar que a ilustração mostra a vizinhança sem a restrição, para explicar porque, COM a restrição, o lift do consumo é baixo. | ✅ corrigido |
| C-4 | Baixa (consistência de figura) | Cap. 4 mockup Telegram vs Cap. 5 CS3 | O mockup mostra 3 precedentes e números arredondados (média −2,0%); o CS3 mostra os 5 reais (média −1,97%). Defensável (UI ilustrativa) mas pode parecer divergência. | Clarificar na legenda do mockup que é um exemplo representativo e que a saída real completa está no CS3. | ✅ corrigido |
| C-5 | Média (defesa) | Cap. 5 CS3 | O alerta do CS3 inclui precedentes do **mesmo ticker** (NVDA), enquanto a métrica do CS2 os exclui. Sem explicação, parece contradição. | Acrescentar uma frase: cross-ticker é uma escolha de **avaliação** (evitar correspondência trivial); o sistema em produção mostra os precedentes mais semelhantes, incluindo do mesmo ticker, que são legítimos para o utilizador. | ✅ corrigido |

## Pontos fortes confirmados (sem ação)
- Números consistentes entre Abstract, Cap. 5 e Cap. 6 (P@5 0,514±0,015 vs lexical 0,346 / random 0,240 /
  recency 0,126; anomalia: range 0,015 vs 0,344; F1 0,516). RQ1–RQ3 do Cap. 1 respondidas no Cap. 6.
- Limitações declaradas honestamente (corpus recente vs FNSPID; proxy de setor; sem estudo humano;
  retornos brutos vs CAR — já fundamentado; sem teste de significância — declarado).
- Citações: 50 no `.bib`, todas citadas, 0 órfãs, 0 indefinidas; cada uma verificada por DOI/ISBN.

## Deferido para Fase D/E (não corrigir agora)
- **Re-correr as estatísticas** (SBERT/torch, stack pesada) para confirmar 0,514/0,538 etc. contra a saída
  do script (`evaluation_results.md`) — Fase D (validar implementação/experimentação).
- **Auditoria página-a-página** e **re-verificação de TODAS as citações** — Fase E (porta de submissão).
- Distinção data card FNSPID (2018–2023, intended) vs dados live usados (preços 2023–2026; notícias
  recentes) — está explicada no Cap. 4/§5.1; reconfirmar clareza na Fase E.
