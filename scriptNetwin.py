from playwright.sync_api import sync_playwright
from time import sleep, time
import csv
from datetime import datetime
from playwright.sync_api import TimeoutError
from tqdm import tqdm

NOMECLATURA_ED = {
    "CA": "Casa",
    "SL": "Sala",
    "LJ": "Loja",
    "DV": "Divisão",
    "AP": "Apartamento",
    "SB": "Sobrado",
    "LT": "Lote",
    "BL": "Bloco",
    "GP": "Galpão",
    "ED": "Edifício",
    "ST": "Setor",
    "SQ": "Super quadra"
}


def read_list():
    lista_de_surveys= []
    with open("survey.csv", "r") as file:
        for line in file:
            lista_de_surveys.append(line.strip())
    return lista_de_surveys

def loginNetwin(page, login):
    page.fill('//*[@id="inputLogin"]', "tt633973")
    page.fill('//*[@id="inputPassword"]', "anth243nYsouz")
    login = True
    return login

def registrar_relatorio(survey, endereco, status, tempo_execucao):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(tempo_execucao, (int, float)):
        tempo_str = f"{tempo_execucao:.2f}s"
    else:
        tempo_str = str(tempo_execucao)
    with open("relatorio.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([survey, endereco, now, status, tempo_str])

def main():
    # Cria o cabeçalho do relatório apenas uma vez
    with open("relatorio.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["survey", "endereco", "data_hora", "status", "tempo_execucao"])

    with sync_playwright() as p:
        login = False
        # Inicia o navegador visível para login
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for idx, lista in enumerate(tqdm(read_list(), desc="Processando surveys")):
            start_time = time()
            try:
                valor = lista.split(";")
                survey = valor[0]
                complemento = valor[1][:2]
                number = valor[1][-1]
                endereco = f"{complemento}{number}"
                print(f"Editando Survey: {survey}, Endereço: {endereco}")

                page.goto("http://netwin.vtal.intra/portal/netwin/login?destination=/portal/netwin/reports")
                page.wait_for_load_state("networkidle")

                if login == False:
                    login = loginNetwin(page, login)
                    page.wait_for_url("http://netwin.vtal.intra/portal/netwin/reports")
                    page.wait_for_load_state("networkidle")
                    page.click('//*[@id="breadcrumb"]/li[1]/a')
                    sleep(2)

                    # Após login, fecha o navegador visível e abre headless
                    page.context.storage_state(path="auth.json")
                    browser.close()
                    # ocultar navegador
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(storage_state="auth.json")
                    page = context.new_page()
                    # Vai direto para a página de reports já autenticado (cookies/session podem ser necessários)
                    page.goto("http://netwin.vtal.intra/portal/netwin")
                    page.wait_for_load_state("networkidle")
                    login = True
                    sleep(5)
                    # Após login bem-sucedido, salve o estado
                print(f"Processando pesquisa survey {survey}")
                page.click('//*[@id="operational-module-location"]')
                sleep(2)
                page.click('//*[@id="operation-module-link-location-1-1"]')
                sleep(2)
                page.fill('//*[@id="location_locphysical_input_name"]', survey)
                sleep(2)
                page.click('//*[@id="submit_form"]')
                page.wait_for_selector('td:nth-child(8) > div > button', state="visible", timeout=200000)
                page.click('td:nth-child(8) > div > button')
                page.click('td:nth-child(8) > div > ul > li:nth-child(1) > a')
                page.click('//*[@id="location_tab_localization"]')
                page.click('td:nth-child(4) > a:nth-child(2) > i')
                page.wait_for_selector('//*[@id="modal-dialog"]/div/div/div[1]/p', state="visible", timeout=30000)
                page.eval_on_selector('//*[@id="modal-dialog"]/div/div/div[1]/p', 'el => el.scrollIntoView()')
                page.click('//*[@id="select2-location_addresses_select_complemento3-container"]')

                nome_completo = NOMECLATURA_ED.get(complemento)
                
                #if complemento == "CA":
                    #page.fill('//*[@id="application"]/span/span/span[1]/input', 'casa')
                #if complemento == "SL":
                    #page.fill('//*[@id="application"]/span/span/span[1]/input', 'sala')

                # Verifica se o select está desabilitado pela classe
                select_locator = page.locator('//*[@id="select2-location_addresses_select_complemento3-container"]/ancestor::span[contains(@class, "select2-container")]')
                classes = select_locator.get_attribute("class")

                if "select2-container--disabled" in classes:
                    print("Input complemento 3 está desabilitado")
                    sleep(3)
                    page.click('//*[@id="location_section_caracterizacao"]/div/div/div[3]/div[2]/div[6]/div[1]/div/div/div/span')
                    sleep(1)
                    page.fill('//*[@id="application"]/span/span/span[1]/input', str(nome_completo).lower())
                    page.press('//*[@id="application"]/span/span/span[1]/input', 'Enter')
                
                    sleep(2)
                    page.fill('//*[@id="location_addresses_input_argumento2"]', number)
                else:
                    print("Input complemento 3 está habilitado")
                    sleep(3)
                    page.fill('//*[@id="application"]/span/span/span[1]/input', str(nome_completo).lower())
                    page.press('//*[@id="application"]/span/span/span[1]/input', 'Enter')

                    sleep(2)
                    page.fill('//*[@id="location_addresses_input_argumento3"]', number)
                
                sleep(2)
                # Confirmar
                page.click('//*[@id="modal_button_ok"]')

                sleep(5)
                # Salvar formulário
                page.click('//*[@id="forms_button_save"]')
                print(f"Survey {survey} salvo com sucesso!, {time() - start_time}")

                sleep(15)

                registrar_relatorio(survey, endereco, "Sucesso!", time() - start_time)
            except TimeoutError as e:
                registrar_relatorio(survey, endereco, "Falha crítica: Excedeu o limite de tempo", "Timeout")
                print(f"Survey {survey} falhou: Excedeu o limite de tempo")
            except Exception as e:
                msg = str(e)
                if "connection" in msg.lower():
                    registrar_relatorio(survey, endereco, "Falha crítica: Queda de conexão", "Conexão perdida")
                    print(f"Survey {survey} falhou: Queda de conexão")
                else:
                    registrar_relatorio(survey, endereco, f"Falha: {msg}", time() - start_time)
                    print(f"Survey {survey} falhou: {msg}")

if __name__ == "__main__":
    main()