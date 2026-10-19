# Brutal-Reviewer — Estratégia empírica (rodada 1)
Data: 2026-07-01 · Alvo: paper/sections/estrategia.tex + dados.tex + tab_principal.tex

Veredito de abertura: honestidade sobre uma falha não é conserto. O uso da taxa de notificação total como "sonda" é onde o trabalho morre.

## [FATAL] "Sonda de notificação" mecanicamente tautológica: vd_rate ⊂ notif_rate
A dependente (notificações domésticas femininas/mil) é subconjunto do regressor (todas as notificações/mil). O salto de R² 0,127→0,763 e o coef 0,368 (t≈24) NÃO são achado empírico — são identidade contábil (y aparece nos dois lados). É o controle contaminado que zera a evangélica. A conclusão-título ("reporte domina") repousa sobre bad control.
Correção exigida: usar notificações NÃO-domésticas (total − domésticas) como proxy de reporte; refazer M4 e comparar R².

## [FATAL] MQO em nível sobre taxa de contagem com 15,4% de zeros e denominador errado
(1) Processo de contagem tratado como contínuo (Poisson seria adequado). (2) Denominador = população TOTAL, mas o risco recai sobre MULHERES 15–49 → viés de medida correlacionado com região/renda. (3) log(1+y) com y de escala ~0,2 é remendo ruim (o "+1" domina) — e é justo aí que evang "aparece" (p=0,08).
Correção exigida: Poisson/NB com offset log(mulheres 15–49); reconstruir denominador; PPML em vez de log(1+y).

## [MAJOR] Viés de variável omitida nomeável e mensurável
Controles esquálidos (renda, pop, 5 macrorregiões). Faltam: infraestrutura de reporte (CNES, CRAS/CREAS, DEAM, ESF), urbanização, escolaridade/PEA feminina, presença policial. Substituir EF de 5 regiões por EF de UF (27) e mostrar a caminhada do coeficiente (Oster).

## [MAJOR] Conclusão afirma mecanismo causal ("reporte domina") sem demonstrar
R² alto é compatível com identidade, causalidade reversa e terceiro fator. Rebaixar para "fortemente confundida com" ou sustentar com proxy limpo + teste que separe reporte de incidência.

## [MAJOR] Falácia ecológica reconhecida mas interpretação continua individual
β1 é parâmetro municipal; proibir inferência sobre indivíduos evangélicos; enquadrar densidade evangélica como característica contextual/institucional.

## [MINOR] Descasamento temporal / janela 2011–13 na rampa de cobertura do SINAN
Controles 2010, desfecho 2011–13 em plena expansão do sistema. Reportar ano a ano ou controlar "anos com notificação"; reescrever a pergunta para o que os dados permitem (norma religiosa × reporte).

## [MINOR] WLS (M5) sem justificar pesos e com divergência ignorada
Documentar esquema de pesos (1/pop?) e reconciliar divergência OLS/WLS, ou remover a coluna.

Veredito: REJEIÇÃO. A coluna que sustenta a tese (M4) é tautológica. Refazer com proxy não-doméstica, migrar para Poisson com offset, enriquecer controles.
