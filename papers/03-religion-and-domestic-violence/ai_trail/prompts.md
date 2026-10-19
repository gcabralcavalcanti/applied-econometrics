# prompts.md — Questão 4 (Grupo 02)

Todos os prompts que usamos, na ordem. O trabalho rodou no fluxo **clo-author** (agente no terminal, que lê
o `CLAUDE.md`, o `RESEARCH_BRIEF.md` e o `MEMORY.md` a cada sessão). Os marcados **[SUBAGENTE]** foram dados
aos agentes de busca e aos críticos da revisão adversarial. A escrita é informal de propósito: é como a
gente conversou com a IA mesmo.

## Começo do projeto
**1.** quero começar um projeto de econometria aplicada sobre normas tradicionalistas e violência doméstica
no Brasil, no nível dos municípios. lê o `CLAUDE.md` e o `RESEARCH_BRIEF.md`, depois os PDFs em
`master_supporting_docs/`, e roda `/discover interview` pra gente afinar a pergunta.

**2.** monta o `RESEARCH_BRIEF.md` com o que a gente combinou. a pergunta, no caso, é se município com mais
evangélico (Censo 2010) e mais internet registra mais violência doméstica contra a mulher. bota literatura,
os dados candidatos, a estratégia e as limitações.

## Literatura e dados (`/discover`)
**3.** roda o `/discover` na parte de literatura. o que a economia já falou sobre religião/normas de gênero e
violência doméstica? e sobre internet e denúncia? e sobre subnotificação no SINAN? me diz também se o sinal
esperado é ambíguo, porque eu acho que é.

**4.** [SUBAGENTE] preciso de 8 a 12 referências REAIS, com DOI, sobre internet × violência, religião ×
violência doméstica, subnotificação do SINAN e determinantes socioeconômicos da VD. não inventa nada — se
não achar o DOI, tira. me devolve um `references.bib` e um `REFERENCIAS.md` anotado.

**5.** explora os dados que dá pra usar de verdade: SINAN, Censo 2010 (tabela 2094, evangélicos) e PIB
municipal. me fala a cobertura no tempo, a chave de merge (código IBGE de 7 dígitos) e onde tá furado, antes
de rodar qualquer regressão.

**6.** [SUBAGENTE] procura uma série de internet por município que dê pra cruzar com o SINAN (SIDRA,
basedosdados, ANATEL, Censo 2010). se não bater no tempo, ou não der pra baixar aqui, fala na lata e deixa
um script pronto (`baixar_internet_2010.py`). não inventa dado.

**7.** a internet não vai dar, no caso: a ANATEL só começa em 2021 e o SINAN vai até 2019, e a de 2010 só tá
nos microdados do Censo. então reenquadra pra corte transversal municipal (média 2011–2013), associativo, sem
causalidade. mantém o tema (tradicionalismo × violência) e deixa a internet como motivação/limitação, com o
script no pacote. anota isso no `MEMORY.md` com `[LEARN]`.

## Estratégia (`/strategize`)
**8.** roda o `/strategize`. justifica o MQO direitinho: a dependente é a taxa de VD feminina notificada por
mil habitantes (definida pelo vínculo do agressor), o regressor de interesse é a densidade evangélica, os
controles são log-renda e log-população, com efeito fixo de UF, e as formas funcionais são log e quadrático.
e explica bem por que isso NÃO é causal. lista as ameaças à validade e um plano de robustez.

**9.** presta atenção numa coisa do SINAN: o `sexo_paciente` vem como 0/1, não como 'F'. valida na mão se o
filtro tá contando vítima de verdade antes de agregar — não quero contar zero por causa de bug.

## Análise (`/analyze`)
**10.** roda o `/analyze` na parte de dados: monta o corte 2011–2013 (SINAN doméstico feminino + evangélicos
e população do Censo + PIB pra renda per capita), faz o merge pelo código IBGE e me diz a taxa de match.
salva a base em `tmp/`.

**11.** agora estima tudo: (1) MQO base com EF de UF e erro robusto HC1; (2) quadrático na evangélica; (3)
log(1+y); (4) a proxy de reporte; (5) MQO ponderado por população. roda o teste de White e os testes t e F,
e gera as tabelas `.tex`. não inventa número nenhum — tudo sai do output.

**12.** saneia a base: tira os municípios com renda per capita absurda (< R$500/ano, que é erro de escala) e
winsoriza a renda no 1 e no 99. como a dependente é contagem com muito zero, roda também um Poisson com
offset de log(população). reestima e atualiza as tabelas.

**13.** faz as figuras: binscatter da VD contra a densidade evangélica; VD contra a taxa de notificação
não-doméstica; e o coeficiente da evangélica nas janelas móveis de 3 anos (2009–2019), com IC de 95%.

## Redação (`/write`, uma seção por vez)
**14.** roda `/write introducao`. motiva a pergunta, encaixa na literatura (com o tal sinal ambíguo), já
adianta o resultado nulo e o achado da notificação, e delimita o escopo (associativo, não causal; internet
como limitação). só cita o que estiver no `references.bib`.

**15.** agora `/write` pra dados, estrategia e resultados, uma de cada vez. puxa os números das tabelas em
`output/tables`. na estratégia, deixa MUITO claro por que a proxy de reporte tem que ser a NÃO-doméstica,
senão vira tautologia.

**16.** `/write` robustez e conclusao. na robustez cobre a janela alternativa na mesma amostra, tirar as
capitais, cluster por UF, população mínima e o Poisson. na conclusão, sê honesto nas limitações: viés de
variável omitida, o denominador, a falácia ecológica e a internet que ficou de fora.

## Revisão adversarial
**17.** [SUBAGENTE] lê a `estrategia.tex` e a `dados.tex` e roda `/brutal-reviewer` SÓ na estratégia. ataca
viés de variável omitida, mau controle (será que a notificação total contém a dependente?), forma
funcional/zeros/denominador e falácia ecológica. classifica cada falha em FATAL/MAJOR/MINOR e diz a correção.

**18.** [SUBAGENTE] agora `/brutal-reviewer` no rascunho inteiro (main + todas as seções + tabelas). confere
se o texto bate com as tabelas, classifica FATAL/MAJOR/MINOR e dá uma nota de 0 a 100. e não me dá veredito
sem compilar de ponta a ponta.

**19.** [SUBAGENTE] age como o parecerista mais implacável de uma revista boa de economia. sem elogio nenhum.
ataca especificação e forma funcional, viés de variável omitida, qualidade dos dados, interpretação dos
coeficientes, inferência (heterocedasticidade, autocorrelação, erro-padrão), p-hacking, generalização e
robustez. classifica cada falha em FATAL/MAJOR/MINOR, explica por que compromete o artigo e diz exatamente o
que fazer pra corrigir.

## Correções (`/revise`)
**20.** os três pareceres bateram na mesma tecla: regredir a VD na notificação TOTAL é tautologia (a VD é uns
36% do total). troca pela total MENOS a VD feminina (a não-doméstica), reestima a coluna do canal de reporte
e me diz o R² novo.

**21.** a tabela de robustez tava se contradizendo — tinha uma janela com coeficiente significativo e a
amostra mudando de tamanho. compara as janelas na MESMA amostra, bota efeito fixo de UF (não de 5 regiões),
tira os outliers de renda e winsoriza. e gera a figura do coeficiente em todas as janelas móveis.

**22.** tira "Internet" do título (a gente não tem um dado de internet sequer na janela) e rebaixa pra
motivação/limitação. adiciona o Poisson. e maneira na linguagem: nada de "reporte domina", é associação
condicional. lista os confundidores que ficaram de fora (infra de saúde, delegacia da mulher, urbanização).

**23.** escreve a seção "Resposta ao parecerista" mapeando cada crítica FATAL/MAJOR → o que a gente mudou (ou
por que não mudou). e escreve o `REFLEXAO.md` (e o apêndice): onde a IA errou (referência inventada, o bug do
sexo, o desenho inviável, o R² tautológico), o que os críticos pegaram e o que a gente decidiu na mão.

## Fechamento
**24.** [SUBAGENTE] confirma item por item se cada FATAL/MAJOR sumiu na versão revisada. roda a análise de
novo, confere se o texto bate com as tabelas e com o `_stats`, e me dá o veredito com a nota.

**25.** roda o `/deep-audit`: vê se código, tabela e texto batem, se o `main.tex` compila do começo ao fim sem
erro e se as referências e citações fecham.

**26.** por último, fecha o pacote: confere a formatação do artigo (capa, seções, tabelas), atualiza o
`MEMORY.md` com as decisões da sessão e garante que o `_master.py` roda de ponta a ponta.
