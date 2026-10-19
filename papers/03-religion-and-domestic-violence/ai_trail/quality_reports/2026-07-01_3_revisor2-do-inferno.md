# Revisor 2 do Inferno — Parecer (rodada 1)
Data: 2026-07-01 · Recomendação: REJEITAR (resubmissão condicionada às 3 exigências)

Abertura: um artigo que se autoelogia por "honestidade" enquanto comete o erro de identificação mais grosseiro do manual — regredir uma variável contra uma soma que a contém — e chama de "robusta a janela" uma tabela cuja 2ª coluna vira significativa a 1% ao mudar a janela.

## [FATAL 1] O "achado central" (col. 4) é identidade contábil
VD média 0,30 e notificação total 0,81 → a dependente é ~37% do próprio regressor. Regredir vd sobre (vd+resto) força coef 0,368/t=24/R²0,76. Não é evidência de "reporte domina"; é a≈b+c. Correção: notif_total − VD feminina (complemento), ou proxy independente (CNES/DEAM/ESF).

## [FATAL 2] A alegação de robustez é falseada pela própria tabela
Janela 2013–15: evang −0,0039*** (≈3× o base, significante a 1%). A única janela insignificante é a base (2011–13) — padrão de window-shopping. N muda 5.033→5.304 (amostra diferente, não perturbação). Correção: reescrever robustez reconhecendo sensibilidade à janela; gráfico de coeficientes em TODAS as janelas móveis 2009–2019 na mesma amostra balanceada.

## [FATAL 3] Denominador errado: população total, não população em risco
Taxa por mil habitantes (inclui homens/crianças/idosos), mas o desfecho é violência contra mulheres. Estrutura etária e razão de sexo variam com renda/urbanização/religião → viés de medida correlacionado com X. Correção: por mil MULHERES (15+ ou 15–49); Poisson/NB com offset.

## [MAJOR 4] Título/motivação (internet, tradicionalismo) não testados
Internet nunca entra em regressão; "tradicionalismo" = uma proxy (% evangélica) sem validação. Rodar o script de internet do Censo 2010 OU remover Internet do título; validar/rebaixar a proxy.

## [MAJOR 5] Endogeneidade da notificação reconhecida no texto e ignorada na estimação
Sem proxy de infraestrutura de saúde/urbanização. β1 é viesado de forma admitida-mas-não-tratada. Incluir CNES/DEAM/ESF/urbanização; senão, rebaixar linguagem para correlação parcial bruta.

## [MAJOR 6] Inconsistência amostral (N muda) + outliers (renda R$3,29)
Fixar universo único; auditar/remover renda e população implausíveis; impor população mínima ou winsorizar; explicar por que 2013–15 tem mais municípios.

## [MAJOR 7] Forma funcional: MQO-nível como principal sem justificar (vs. contagem)
Poisson/NB com offset = log(pop em risco) como principal, ou justificar. Discutir por que evang vira marginal em log.

## [MINOR] Poucos clusters (27 UF; wild bootstrap); EF de 5 regiões grosseiros (usar UF); White sem g.l.; falácia ecológica violada na redação.

## Recomendação: REJEITAR. 3 exigências inegociáveis:
1. Eliminar a tautologia do regressor (proxy sem a VD).
2. Corrigir denominador + forma funcional (Poisson/offset) e refazer robustez honesta (evang é significativo em 2013–15).
3. Alinhar título/alegações ao conteúdo e tratar (não só admitir) a endogeneidade; expurgar renda R$3,29.
