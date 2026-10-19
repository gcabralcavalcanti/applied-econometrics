# Brutal-Reviewer — Verificação pós-revisão (rodada 2)
Data: 2026-07-01 · Natureza: confirmar que os FATAL sumiram (reexecução independente da análise)

## Status de cada FATAL/MAJOR
- [FATAL] Sonda tautológica (vd ⊂ notif total) → RESOLVIDO: proxy agora é NÃO-doméstica; R² 0,17→0,44 (não mais 0,76).
- [FATAL] MQO/contagem/denominador → PARCIAL: Poisson com offset adicionado (evang NS); offset ainda é pop. total (limitação assumida).
- [FATAL] Robustez auto-contraditória (N=5304; evang −0,0039***) → RESOLVIDO: amostra comum (4.956) + EF UF + winsorização → janela 2013–15 = +0,0016 (p=0,15), NS. Reexecutado e confirmado: TODAS as 9 janelas móveis dão evang ~0, p∈[0,14; 0,44].
- [FATAL] Título "Internet" sem dado → RESOLVIDO: fora do título, rebaixada a limitação.
- [trecho removido]
- [MAJOR] VVO / EF de UF → RESOLVIDO (Oster não feito); [MAJOR] mecanismo causal → rebaixado a associativo; [MAJOR] R² não comparável → nota; [MAJOR] proxy mono-citada/sinal ambíguo → resolvido; [MAJOR] painel inédito → corte transversal; [MAJOR] outliers renda → 3 expurgados+winsor; [MAJOR] forma funcional → Poisson; [MAJOR] endogeneidade → PARCIAL (EF UF + linguagem rebaixada; CNES/DEAM indisponíveis).
- [MINOR] falácia ecológica / clusters / g.l. → todos tratados.

Placar FATAL: 6 resolvidos, 2 parciais (mesmo tema: denominador de pop. em risco — mitigado por Poisson, rotulado como limitação).

## Consistência numérica texto↔tabelas↔_stats
Todos os números reconciliam (R² 0,17→0,44; proxy 0,4244***; evang base +0,0009 p=0,32; janela +0,0016 p≈0,15; Poisson −0,0077 NS; White LM=160,1 gl=28 p=0,001; F=44,4; VD=36,3% do total; 3 municípios <R$500; 15,4% de zeros; comum=4.956). Nenhuma contradição sobrevive.

## Veredito
ACEITÁVEL PARA ENTREGA DE CURSO. Nota clo-author: **82/100** (era 54). Desconto: denominador ainda em pop. total no Poisson (−6); endogeneidade estrutural só rebaixada na linguagem (−7); sem Oster/wild-bootstrap (−5).

## Melhorias opcionais de baixo esforço (aplicadas)
1. [trecho removido] 2. Ancorar "15,4%" exato. 3. Nota na tabela de robustez explicando a mudança do coeficiente 2013–15.
