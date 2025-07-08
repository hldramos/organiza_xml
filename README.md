Perfeito, Helder! Aqui está uma documentação em **formato Markdown** para o seu script de organização de XMLs fiscais. Ela pode ser usada como arquivo `README.md` no GitHub, incluída em uma Wiki de time ou mesmo convertida em PDF para distribuição.

---

# 🗂️ Organizador de XMLs Fiscais

Script em Python para organizar arquivos XML de documentos fiscais eletrônicos (NFe e MDFe) em uma estrutura hierárquica de pastas baseada no **CNPJ do emitente** e na **data de emissão**.

---

## 📌 Funcionalidades

- Leitura e extração de dados (CNPJ e data de emissão) de XMLs fiscais
- Suporte a múltiplas estruturas XML (NFe, MDFe e eventos)
- Criação de estrutura de pastas: `CNPJ/ano/mês/dia-mês-ano`
- Sanitização de nomes para evitar erros em sistemas de arquivos
- Validação por data de corte mínima
- Opção para copiar ou mover os arquivos para a nova estrutura
- Relatório completo de processamento com erros e sucesso

---

## 🚀 Como executar

Execute o script diretamente pelo terminal:

```bash
python main.py [COPIAR|MOVER] [PASTA_ORIGEM] [PASTA_DESTINO] [TIPO_DOC] [DATA_MINIMA]
```

### 🧾 Parâmetros obrigatórios

| Parâmetro      | Tipo     | Descrição                                                                 |
|----------------|----------|---------------------------------------------------------------------------|
| `COPIAR/MOVER` | `str`    | Define se os arquivos serão copiados ou movidos                           |
| `PASTA_ORIGEM` | `str`    | Caminho da pasta raiz onde estão os XMLs                                  |
| `PASTA_DESTINO`| `str`    | Caminho para onde os XMLs serão organizados                               |
| `TIPO_DOC`     | `str`    | Tipo de documento: `NFE`, `MDFE` ou `ALL`                                 |
| `DATA_MINIMA`  | `str`    | Data mínima de emissão no formato `AAAA-MM-DD`                            |

---

## 🧠 Exemplo de uso

```bash
python main.py COPIAR ./xmls ./organizados NFE 2024-01-01
```

Esse comando:
- Copia todos os XMLs de NFe encontrados em `./xmls`
- Que tenham **data de emissão a partir de 01/01/2024**
- Para a pasta `./organizados/[CNPJ]/[Ano]/[Mês]/[Dia-Mês-Ano]/`

---

## 🛡️ Regras de negócio

- Se o nome do emitente possuir caracteres inválidos para pastas, eles serão removidos
- Arquivos com datas abaixo da data mínima são ignorados
- XMLs com falha na leitura, sem data ou emitente válido são reportados como erro
- É criada uma pasta `sem_data/` se o XML não contiver data
- Data inválida gera pasta `data_invalida/`

---

## 📦 Dependências

- `xmltodict`
- `shutil`
- `datetime`
- `os`
- `sys`

Para instalar a dependência externa:

```bash
pip install xmltodict
```

---

## 📄 Licença

Este script é livre para uso, modificação e distribuição. Se for útil para seu projeto, fique à vontade para dar os créditos. 😉

---

Se quiser, posso exportar esse conteúdo como um arquivo `.md`, gerar uma versão em PDF ou até criar um template de repositório GitHub completo com essa estrutura. Só dizer! 💡📘