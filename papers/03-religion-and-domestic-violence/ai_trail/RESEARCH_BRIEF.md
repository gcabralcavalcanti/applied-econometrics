# Research Brief — Redes Tradicionalistas e Violência Doméstica Registrada no Brasil

## Pergunta de pesquisa
Municípios brasileiros com maior densidade de redes tradicionalistas — medida pela participação evangélica
na população (Censo 2010) — exibem maiores taxas de violência doméstica registrada contra mulheres? Análise
de corte transversal municipal, média 2011–2013.

## Literatura
Dialoga com Galindo-Silva & Tchuente (2026, religião × violência doméstica na Colômbia), Bhalotra et al.
(2025, violência doméstica no Brasil via notificações de saúde), Vasconcelos et al. (2024, subnotificação do
SINAN) e Bhuller et al. (2013, separação entre reporte e incidência). Contribui com evidência municipal
brasileira e um alerta sobre o viés de notificação em dados administrativos.

## Dados
- **SINAN** (Sistema de Informação de Agravos de Notificação), 2009–2019: violência doméstica definida por
  vínculo do agressor (cônjuge/ex, namorado/ex, pais, etc.), vítima feminina.
- **Censo 2010 / IBGE tabela 2094**: população total e evangélica por município.
- **PIB dos Municípios 2010 / IBGE**: PIB → renda per capita.
- Chave de merge: código IBGE de 7 dígitos. Corte transversal 2011–2013 (~5.030 municípios).

## Estratégia empírica
MQO múltiplo com efeitos fixos de UF e erros-padrão robustos (HC1). Formas funcionais: log de renda e
população, termo quadrático em densidade evangélica, log(1+y). Proxy de reporte NÃO-doméstica (exógena à
dependente). Modelo de contagem de Poisson com offset de população. Testes t e F; teste de White para
heterocedasticidade. **O trabalho é associativo, não causal.**

## Limitações (honestas)
Viés de variável omitida (infraestrutura de notificação, urbanização, capital humano feminino não
observados); subnotificação do SINAN correlacionada com os regressores; risco de falácia ecológica;
denominador de população total (não mulheres em risco); ausência de dados de internet sobrepostos à janela.

## Seções em revisão / finais (uma de cada vez)
Todas as seções (introdução, dados, estratégia, resultados, robustez, resposta ao parecerista, conclusão)
estão FINAIS após a rodada de revisão adversarial. Não reescrever sem instrução explícita.

## Arquivos de referência
- master_supporting_docs/REFERENCIAS.md — bibliografia real anotada (com DOIs).
- quality_reports/ — pareceres do brutal-reviewer e do Revisor 2 do inferno.

-- TRABALHE UMA DE CADA VEZ
