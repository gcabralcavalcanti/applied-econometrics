# Brutal-Reviewer — Rascunho completo (rodada 1)
Data: 2026-07-01 · Alvo: main.tex + todas as seções + 3 tabelas · Nota clo-author: 54/100

## [FATAL] main.tex inclui sections/resposta_parecerista e sections/apendice_reflexao
Confirmar que existem, compilam e são coerentes; se forem resquício, remover os \input. Não aceito veredito sem compilar de ponta a ponta.

## [FATAL] Inconsistência numérica e robustez que se autodesmente
tab_robustez: "Janela 2013–15" tem N=5304 > universo declarado (5.033) e coef evang = −0,0039*** (significante a 1%), contradizendo "não distinguível de zero em todas as variações" (robustez.tex/abstract). Reconciliar N (amostra muda de composição entre janelas); tratar honestamente o coef significativo.

## [FATAL] Título e resumo prometem "Internet"; o artigo não tem uma única observação de internet
Overclaiming estrutural (a palavra do título não tem contrapartida empírica). Remover "Internet" do título OU rebaixar inequivocamente no abstract, na mesma frase, deixando claro que não foi medida.

## [MAJOR] notif_rate mecanicamente contaminada (vd ⊂ total) — mesmo ponto do revisor de estratégia
Reconstruir a taxa total EXCLUINDO a VD feminina do numerador; reestimar col. (4); reportar novo R².

## [MAJOR] R² não comparável entre dependentes transformadas
0,127 (nível) vs 0,171 (log) vs 0,102 (WLS) não estão na mesma escala; não comparar R² cross-transformação em prosa.

## [MAJOR] Proxy "densidade evangélica ≈ tradicionalismo" mono-citada
Evangélicos são heterogêneos (histórico vs. neopentecostal vs. renovado); parte da literatura aponta AUMENTO de autonomia feminina na conversão (sinal oposto). Citar >1 referência e afirmar que o sinal é teoricamente AMBÍGUO (o que fortalece o resultado nulo).

## [MAJOR] "painel municipal inédito" — erro conceitual + overclaiming
É corte transversal, não painel; "inédito" sem suporte. Trocar por "base de corte transversal a partir de fontes públicas".

## [MAJOR] Renda per capita mín R$3,29 e máx R$311.882 — outliers/erro de unidade
Com log(renda), a cauda inferior vira alavanca. Winsorizar/expurgar valores implausíveis e mostrar que β2 sobrevive.

## [MINOR] Números soltos sem fonte na tabela (15,4% zeros; 1.660→5.273); White/F sem g.l.; cluster com 27 UFs (poucos); \caption+\caption* duplicado; evang² ilegível (0,0000).

## Consistência numérica texto↔tabelas
Coef/EP batem com as tabelas; DUAS contradições graves: (1) N=5304 na janela 2013–15 > universo; (2) coef −0,0039*** dessa janela contradiz "nulo em todas as variações".

Veredito: reprovar-e-revisar (54/100). Núcleo honesto e defensável; falham execução e calibragem de reivindicações. Ações: (a) compilar e mostrar os 2 arquivos; (b) reconciliar N e tratar o −0,0039***; (c) tirar Internet do título; (d) proxy de reporte sem a VD; (e) sanear outliers de renda.
