# Project Memory — Q4 (Grupo 02)

Trilha de decisões (marcações [LEARN]). Mais recentes ao fim.

## Desenho e dados
[LEARN:design] Os dados baixados NÃO sustentam o DiD internet×violência: a cobertura de banda larga (ANATEL
"Meu Município") começa em 2021 e não se sobrepõe ao SINAN (≤2019). Reenquadrado como CORTE TRANSVERSAL
municipal ~2011–2013 (associativo, não causal).
[LEARN:dados] SINAN codifica `sexo_paciente` como 0/1 (não 'F'). Validado que **0 = feminino** (via
predominância feminina entre vítimas de agressor conjugal). O pipeline herdado filtrava por 'F' → contava
ZERO vítimas. Bug corrigido.
[LEARN:dados] Violência doméstica definida por vínculo do agressor (autor_conjugue/ex, namorado/ex, pai, mãe,
padrasto, madrasta, filho, irmão), vítima feminina. Doméstica = 36,3% das notificações totais.
[LEARN:dados] Janela 2011–2013: equilibra proximidade ao Censo 2010 e cobertura do SINAN (que cresce por
expansão: 1.660 municípios em 2009 → 5.273 em 2019).
[LEARN:dados] Merge IBGE 2094 (só nomes) → código via arquivo de PIB (nome+UF), 99,7% de match.

## Especificação (pós-revisão adversarial)
[LEARN:método] Proxy de reporte deve ser NÃO-doméstica (n_total − n_dom). Usar a notificação TOTAL é
tautológico (a VD é subconjunto dela). Com a proxy limpa, R² 0,17→0,44 (antes 0,76, artefato).
[LEARN:método] Efeitos fixos de UF (27), não de 5 macrorregiões — absorvem cobertura estadual do SINAN.
[LEARN:método] Renda: expurgar municípios com renda per capita < R$500 (3 casos, erro de dados) e winsorizar
nos percentis 1/99.
[LEARN:método] Denominador ideal = mulheres em risco (indisponível no ambiente); usar pop total + modelo de
Poisson com offset; declarar como limitação. NÃO fabricar denominador.
[LEARN:método] "Internet" fora do título — sem dados que sobreponham a janela. Manter como motivação/limitação
+ script de coleta no pacote.

## Resultado e integridade
[LEARN:resultado] Achado honesto: densidade evangélica SEM associação robusta com violência doméstica
registrada (nula em todas as janelas móveis 2009–2019; Poisson concorda). Reporte domina.
[LEARN:integridade] NÃO usar citações fabricadas. Bibliografia real verificada por Crossref/DOI.
[LEARN:processo] Revisão adversarial (2× brutal-reviewer + 1× Revisor 2 do inferno) subiu a nota interna de
54 para 82/100; todos os FATAL resolvidos.
