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

- Interface Gráfica (CLI): typer
  - Escolhido por permitir a construção rápida e tipada de interfaces de linha de comando, gerando automaticamente menus de ajuda e validação de argumentos, permitindo foco total na lógica de mineração.
  
- Mineração de Histórico: pydriller
  - Framework em Python otimizado para pesquisa acadêmica. Será utilizado para iterar sobre a árvore do Git e extrair o histórico de commits, identificando facilmente os arquivos alterados e calculando as linhas adicionadas e removidas ao longo do tempo.

- Extração de Métricas de Complexidade: lizard
  - Ferramenta de análise estática leve e rápida. Sua principal vantagem é a capacidade de calcular a Complexidade Ciclomática e o tamanho de métodos em diversas linguagens de programação sem a necessidade de compilar o código ou configurar ambientes complexos.

- Análise Estrutural e de Acoplamento: tree-sitter
  - Será utilizado para a construção da Árvore de Sintaxe Abstrata do código analisado. Diferente de análises textuais simples, o parser permitirá extrair métricas de orientação a objetos mais profundas, como fan-in e fan-out e contagem estrutural de classes e métodos, independente da linguagem do repositório alvo.
