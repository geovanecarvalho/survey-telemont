# 📋 Automação de Cadastramento de Endereços de Survey

Este projeto tem como objetivo **automatizar o cadastramento de endereços de survey** no sistema **Netwin**, utilizando **Python** e **Playwright**.  
Os dados de entrada são lidos a partir de um arquivo `survey.csv`, que contém a lista de endereços a serem cadastrados.

---

## 🚀 Tecnologias utilizadas
- [Python 3.10+](https://www.python.org/)
- [Playwright](https://playwright.dev/python/)
- [Pandas](https://pandas.pydata.org/) (para leitura do arquivo CSV)

---

## 📂 Estrutura do projeto
```
git clone https://github.com/seuusuario/survey-automation.git
cd survey-automation
```

```
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```
```
pip install -r requirements.txt

```

```
playwright install
```
```
python scriptNetwin.py
```