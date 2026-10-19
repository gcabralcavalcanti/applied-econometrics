# Reflexão crítica sobre o uso de IA — Questão 4

A gente tocou esse mini-artigo com um agente de IA (o fluxo *clo-author*), mas com a gente no comando das
decisões. Vale ser honesto sobre onde a IA ajudou e, principalmente, onde ela errou e como consertamos.

## Onde a IA errou
Foram quatro coisas que doeram.

Primeiro, referência inventada. Uma versão inicial da estratégia citava trabalho que simplesmente não existe
("Silva & Pereira 2024"). Trocamos tudo por bibliografia real, conferida por DOI.

Segundo, um bug de dados silencioso. O *pipeline* filtrava as vítimas por `sexo == 'F'`, só que o SINAN
codifica sexo como 0/1. Ou seja, o filtro contava zero vítima e ninguém percebia. A gente só pegou isso
olhando os dados brutos na mão.

Terceiro, o desenho original não fechava. A ideia era internet × violência, mas a cobertura de banda larga
(ANATEL) começa em 2021 e o SINAN vai até 2019 — não tem como cruzar. A IA tinha montado um *pipeline* que
ia gerar um painel vazio.

Quarto, *overclaiming*. A primeira redação vendia como "achado" um R² de 0,76 que era, na real, tautológico:
a gente estava regredindo a violência doméstica sobre uma notificação total que já contém essa mesma
violência.

## O que os agentes-críticos pegaram
Rodamos três revisões adversariais (dois *brutal-reviewer* e um "Revisor 2 do inferno"). As três, sem
combinar, apontaram a mesma coisa: a tautologia do regressor, a tabela de robustez que se contradizia (tinha
um coeficiente significativo escondido numa janela) e o exagero do título ("Internet" sem um único dado de
internet). Também reclamaram do denominador, da falta de controles e dos *outliers* de renda.

## O que corrigimos na mão
Trocamos o regressor pela proxy não-doméstica, que não contém a dependente; botamos efeito fixo de UF;
tiramos três municípios com renda impossível e winsorizamos; comparamos as janelas na mesma amostra; e
acrescentamos a figura dos coeficientes e um modelo de Poisson. Quando os críticos pediam um dado que a gente
não tinha (o denominador de mulheres em risco, a internet do Censo 2010), a decisão foi não inventar:
preferimos assumir a limitação e deixar o script de coleta no pacote. A interpretação econômica e as escolhas
de método são nossas; a IA escreveu e depurou código e organizou o material.

## Declaração de uso de IA
Usamos IA (via fluxo *clo-author*) para depurar o *pipeline*, escrever e organizar código, rascunhar as
seções sob nossa direção e conduzir a revisão adversarial. Todos os prompts estão no `prompts.md` e a trilha
de decisões no `MEMORY.md`. As decisões de método e a interpretação são de responsabilidade nossa.
