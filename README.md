# TED 03 — Gerenciador de Persistência de Dados (CSV e JSON)

Aplicação de linha de comando em Python que **lê, converte e atualiza arquivos CSV e JSON**, com uso obrigatório de `with open(...)`, tratamento de exceções e **backup automático antes de toda alteração em arquivo existente**.

## Identificação

- **Instituição:** UniBalsas
- **Curso:** Análise e Desenvolvimento de Sistemas (ADS)
- **Disciplina:** Algoritmos e Programação Avançada
- **Integrante 1:** Katson Kawan Cardoso de Carvalho
- **Integrante 2:** Bonifácio Pinto Costa Neto
- **Integrante 3:** Phelype Rocha Marques
- **Atividade:** TED 03 — Gerenciador de Persistência de Dados em Arquivos Estruturados
- **Data de entrega:** 31/10/2026

## Funcionalidades

1. Leitura de arquivos CSV com `csv.reader` e JSON com `json.load`.
2. Conversão de CSV para JSON e de JSON para CSV, preservando campos e valores de texto.
3. Atualização de registro por identificador `id`, nos dois formatos.
4. Geração de backup com data/hora em `backups/` **antes** da atualização ou sobrescrita de arquivos existentes.
5. Gravação em arquivo temporário no mesmo diretório e substituição por `os.replace` para reduzir riscos de gravação parcial.
6. Mensagens de erro claras para arquivo ausente, acesso negado, codificação UTF-8, JSON inválido, CSV inconsistente e falhas de E/S.
7. Testes automatizados usando apenas a biblioteca padrão do Python.

## Requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa para a aplicação nem para os testes.
- Windows, macOS ou Linux.

## Executar

Abra o terminal na pasta do projeto:

```bash
python main.py --help

# Leitura CSV
python main.py ler dados/clientes.csv

# CSV -> JSON
python main.py converter dados/clientes.csv resultados/clientes_convertidos.json

# JSON -> CSV
python main.py converter dados/clientes.json resultados/clientes_convertidos.csv

# Atualizar um registro; cria backup antes de alterar
python main.py atualizar resultados/clientes_convertidos.csv --id 002 --campo cidade --valor "Imperatriz - MA"

# Ler resultado atualizado
python main.py ler resultados/clientes_convertidos.csv

# Testar erro controlado
python main.py ler dados/nao_existe.csv
```

**Nota:** a pasta `resultados/` já está incluída no projeto. Para arquivos em outro diretório, crie esse diretório antes de executar a conversão.

Se sua instalação usa `python3`, substitua `python` por `python3`.

## Executar os testes

```bash
python -m unittest discover -s testes -v
```

Os testes usam diretórios temporários e não alteram `dados/`.

## Organização

```text
TED03_Gerenciador_CSV_JSON/
├── main.py                   # Interface e mensagens de erro
├── configuracao_relatorio.json # Dados da capa e identificação
├── gerar_relatorio.py        # Regeneração opcional do PDF
├── gerenciador/
│   ├── __init__.py
│   ├── backup.py             # Cópia original antes de alterações
│   ├── conversao.py          # Conversões CSV/JSON
│   ├── excecoes.py           # Exceção para dados inválidos
│   ├── io_csv.py             # Leitura/escrita CSV com with open
│   ├── io_json.py            # Leitura/escrita JSON com with open
│   ├── persistencia.py       # Gravação segura e atualização
│   └── validacao.py          # Integridade da estrutura dos dados
├── dados/
│   ├── clientes.csv
│   └── clientes.json
├── resultados/               # Arquivos gerados nas demonstrações
│   └── backups/              # Backups gerados de arquivos existentes
├── testes/
│   └── test_gerenciador.py
├── evidencias/               # Capturas reais da execução no terminal
└── TED03_Relatorio_Katson_Bonifacio_Phelype.pdf
```

## Como o backup funciona

Ao atualizar ou converter para um **destino já existente**, o sistema salva previamente uma cópia binária de seu conteúdo anterior, com extensão `.bak`. Exemplo:

```text
resultados/backups/clientes_convertidos.csv.20261031_180000_123456_abcd1234.bak
```

A cópia é concluída antes de qualquer substituição. Se o backup falhar, a atualização é cancelada. A escrita acontece em arquivo temporário; só depois de concluir a gravação é executada a troca pelo arquivo final. Ao criar um arquivo novo, o sistema informa que não existe versão anterior para copiar. Operações de leitura não modificam arquivos e, portanto, não geram backup.

## Garantias e limites documentados

- CSV é um formato **textual**. Para não perder o tipo de dados na conversão, JSON deve ser uma **lista não vazia de objetos com as mesmas chaves e valores de texto**. Números JSON, booleanos, `null`, listas e objetos aninhados são recusados **com mensagem explícita**, em vez de convertidos silenciosamente com perda de tipos.
- O CSV deve conter cabeçalho único e pelo menos um registro. Registros incompletos são rejeitados em vez de perder campos.
- São preservados acentos, vírgulas, aspas, quebras de linha em valores e zeros à esquerda.
- A ordem dos campos é a do primeiro registro. A atualização requer a coluna `id` com valor único para o registro selecionado.
- O backup é local e não substitui uma estratégia completa de cópias externas ou controle de acesso concorrente.

## Evidências e relatório

As imagens em `evidencias/` representam a saída real de quatro execuções de terminal e uma execução de testes: conversão nos dois sentidos, atualização com backup, erro controlado e testes automatizados. O relatório técnico PDF contém descrição, trechos relevantes de código, legendas, explicação dos resultados e referências.

## Personalizar e regenerar o relatório PDF

Os três integrantes, a instituição, o curso e a disciplina estão registrados no arquivo `configuracao_relatorio.json` e já aparecem na seção **Identificação** deste README. Caso seja necessário corrigir algum desses dados, atualize o JSON e regenere o relatório técnico.

Para regenerar o PDF, execute:

```bash
python -m pip install reportlab pillow
python gerar_relatorio.py
```

**Importante:** `reportlab` e `pillow` são necessários apenas para gerar o PDF; a aplicação e os 18 testes funcionam sem instalações adicionais.

## Publicar no GitHub

1. Crie um repositório novo, por exemplo, `ted03-gerenciador-csv-json`.
2. Na pasta do projeto, execute:

```bash
git init
git add .
git commit -m "Entrega TED03: gerenciador CSV e JSON"
git branch -M main
git remote add origin https://github.com/katsonkawan/TED03-Gerenciador-CSV-JSON.git
git push -u origin main
```

3. Confirme que o PDF, `main.py`, `gerenciador/`, `dados/`, `testes/`, `evidencias/` e `README.md` estão visíveis no repositório.
4. Entregue o **link do repositório** no Portal do Aluno, não o ZIP nem apenas o PDF.

## Referências técnicas

- Python Software Foundation. [Documentação do módulo csv](https://docs.python.org/3/library/csv.html).
- Python Software Foundation. [Documentação do módulo json](https://docs.python.org/3/library/json.html).
- Python Software Foundation. [Entrada e saída de arquivos](https://docs.python.org/3/tutorial/inputoutput.html).
- Python Software Foundation. [Exceções embutidas](https://docs.python.org/3/library/exceptions.html).
