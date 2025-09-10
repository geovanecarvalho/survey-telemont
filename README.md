# 📋 Automação de Cadastramento de Endereços de Survey

Este projeto tem como objetivo **automatizar o cadastramento de endereços de survey** no sistema **Netwin**, utilizando **Python** e **Playwright**.  
Os dados de entrada são lidos a partir de um arquivo `survey.csv`, que contém a lista de endereços a serem cadastrados.

---

## 🚀 Tecnologias utilizadas
- [Python 3.13+](https://www.python.org/)
- [Playwright](https://playwright.dev/python/)
- [Pandas](https://pandas.pydata.org/) (para leitura do arquivo CSV)
- [Poetry](https://python-poetry.org/) (para gerenciamento de dependências)

---

## 📦 Instalação do Poetry

Para instalar o Poetry, execute:

```sh
pip install poetry
```

Ou siga as instruções oficiais: https://python-poetry.org/docs/#installation

---

## ⚙️ Como rodar o projeto

1. **Instale as dependências do projeto:**

   ```sh
   poetry install
   ```

2. **Ative o ambiente virtual do Poetry:**

   - No Windows (cmd):
     ```sh
     poetry shell
     ```
   - Ou, para ativar manualmente:
     ```sh
     .venv\Scripts\activate
     ```

3. **Instale os drivers do Playwright:**

   ```sh
   playwright install
   ```

4. **Execute o script principal:**

   ```sh
   python scriptNetwin.py
   ```

---

## 📄 Observações

- Certifique-se de ter o arquivo `survey.csv` na raiz do projeto.
- Para sair do ambiente virtual do Poetry, use o comando `exit