# tp-mineracao-es2

## 1. Membros do Grupo
1. Thales Augusto Rocha Fernandes
2. Brendo Getico Eugenio


## 2. Explicação do Sistema

Problema:
A manutenção de software fica cada vez mais cara à medida que os sistemas evoluem e se tornam mais complexos. Quanto maior for um sistema, mais difícil é saber onde priorizar refatorações e testes. Código complexo que raramente é alterado apresenta baixo risco, mas arquivos altamente complexos e acoplados que sofrem modificações constantes são os que causam mais problemas.

Proposta do Sistema:
Este projeto visa desenvolver uma ferramenta de linha de comando (CLI) focada na mineração de repositórios. O objetivo principal é identificar e classificar os gargalos de manutenção de um projeto cruzando:
1. Histórico Temporal (Git): Frequência de modificações para identificar os arquivos mais instáveis.
2. Qualidade Estática (Código-fonte): Métricas estruturais e de complexidade para identificar códigos de difícil compreensão e alto acoplamento.

Ao final da execução, a CLI entregará um relatório apontando quais arquivos são críticos, fornecendo dados para guiar decisões arquiteturais e de refatoração da equipe.

## 3. Possíveis Tecnologias Utilizadas

O sistema será construído em Python, usando as seguintes tools:

- Interface de Linha de Comando (CLI): typer
  - Escolhido por permitir a construção rápida e tipada de interfaces de linha de comando, gerando automaticamente menus de ajuda e validação de argumentos, permitindo foco total na lógica de mineração.
  
- Mineração de Histórico: pydriller
  - Framework em Python otimizado para pesquisa acadêmica. Será utilizado para iterar sobre a árvore do Git e extrair o histórico de commits, identificando facilmente os arquivos alterados e calculando as linhas adicionadas e removidas ao longo do tempo.

- Extração de Métricas de Complexidade: lizard
  - Ferramenta de análise estática leve e rápida. Sua principal vantagem é a capacidade de calcular a Complexidade Ciclomática e o tamanho de métodos em diversas linguagens de programação sem a necessidade de compilar o código ou configurar ambientes complexos.

- Visualização no terminal: rich
  - Utilizado para tornar a experiência no terminal mais clara e apresentável, com painéis, tabelas, destaques de prioridade e barras de risco.

## 4. Ferramenta Implementada

A ferramenta implementada é uma CLI em Python que cruza três grupos de métricas:

1. Histórico de alterações via Git, usando `pydriller`
   - quantidade de commits que alteraram cada arquivo;
   - linhas adicionadas;
   - linhas removidas;
   - churn total, calculado como linhas adicionadas + removidas.

2. Complexidade estática, usando `lizard`
   - linhas de código;
   - quantidade de funções/métodos;
   - complexidade ciclomática total;
   - maior complexidade ciclomática encontrada no arquivo;
   - complexidade média por função.

3. Dependências por arquivo
   - em Python, a ferramenta usa `ast` para contar imports;
   - em outras linguagens comuns, usa padrões simples para `import`, `require`, `use`, `using` e `#include`.

Com esses dados, a CLI calcula um score de prioridade de refatoração:

- 40% frequência de alterações;
- 30% complexidade total;
- 20% quantidade de dependências;
- 10% churn.

Arquivos com score mais alto são candidatos mais urgentes para refatoração, porque combinam instabilidade histórica com dificuldade de manutenção.

A CLI foi pensada para apresentação em terminal: ela mostra um resumo executivo, destaca os principais hotspots, exibe o ranking em tabela e ainda permite exportar o resultado para JSON ou CSV.

## 5. Como Executar

Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale o projeto:

```bash
pip install -e .
```

Analise o repositório atual:

```bash
repo-miner analyze .
```

Ou use o modo guiado, mais fácil para demonstração:

```bash
repo-miner wizard
```

Analise outro repositório Git:

```bash
repo-miner analyze /caminho/para/repositorio
```

Limite a quantidade de resultados exibidos:

```bash
repo-miner analyze . --limit 10
```

Mostre somente arquivos acima de um score mínimo:

```bash
repo-miner analyze . --min-score 40
```

Controle quantos hotspots aparecem no painel de destaque:

```bash
repo-miner analyze . --hotspots 3
```

Gere um relatório em JSON ou CSV:

```bash
repo-miner analyze . --output relatorio.json
repo-miner analyze . --output relatorio.csv
```

## 6. Interpretação do Relatório

A saída no terminal é dividida em três partes:

1. `Resumo executivo`
   - total de arquivos analisados;
   - quantidade de arquivos em prioridade alta e média;
   - churn total;
   - complexidade total;
   - dependências detectadas.

2. `Hotspots principais`
   - arquivos mais críticos;
   - barra visual de score;
   - recomendação objetiva de refatoração.

3. `Ranking de prioridade`
   - tabela completa dos arquivos mais relevantes.

O ranking mostra:

- `Score`: prioridade geral de refatoração, de 0 a 100;
- `Prioridade`: classificação `alta`, `media` ou `baixa`;
- `Commits`: número de commits que alteraram o arquivo;
- `Churn`: soma de linhas adicionadas e removidas;
- `CC total`: complexidade ciclomática total do arquivo;
- `CC max`: maior complexidade ciclomática em uma função/método;
- `Deps`: quantidade de dependências detectadas.
- `Recomendacao`: explicação curta do motivo pelo qual o arquivo merece atenção.

Um arquivo com muitos commits, alta complexidade e muitas dependências deve aparecer no topo da lista, indicando maior risco de manutenção.

## 7. Exemplo de Uso para Apresentação

Um fluxo simples para demonstrar a ferramenta:

```bash
source .venv/bin/activate
repo-miner wizard
```

Para uma execução direta:

```bash
repo-miner analyze /caminho/para/repositorio --limit 15 --hotspots 5
```

Para salvar evidências do resultado:

```bash
repo-miner analyze /caminho/para/repositorio --output relatorio.csv
```
