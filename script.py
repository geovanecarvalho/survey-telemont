from playwright.sync_api import sync_playwright
from time import sleep, time
import csv
from datetime import datetime
from playwright.sync_api import TimeoutError

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

def registrar_relatorio(survey, status, tempo_execucao):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if isinstance(tempo_execucao, (int, float)):
        tempo_str = f"{tempo_execucao:.2f}s"
    else:
        tempo_str = str(tempo_execucao)
    with open("relatorio.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([survey, now, status, tempo_str])

def main():
    # Cria o cabeçalho do relatório apenas uma vez
    with open("relatorio.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["survey", "data_hora", "status", "tempo_execucao"])

    with sync_playwright() as p:
        login = False
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        for lista in read_list():
            start_time = time()
            try:
                valor = lista.split(";")
                survey = valor[0]
                complemento = valor[1][:2]
                number = valor[1][-1]
                print(survey, complemento, number)
                page.goto("http://netwin.vtal.intra/portal/netwin/login?destination=/portal/netwin/reports")
                page.wait_for_load_state("networkidle")

                if login == False:
                    login = loginNetwin(page, login)
                    page.wait_for_url("http://netwin.vtal.intra/portal/netwin/reports")
                    page.wait_for_load_state("networkidle")

                    page.click('//*[@id="breadcrumb"]/li[1]/a')
                    sleep(2)

                page.click('//*[@id="operational-module-location"]')
                sleep(2)
                page.click('//*[@id="operation-module-link-location-1-1"]')
                sleep(2)
                page.fill('//*[@id="location_locphysical_input_name"]', survey)
                sleep(2)
                page.click('//*[@id="submit_form"]')
                page.wait_for_selector('td:nth-child(8) > div > button', state="visible", timeout=90000)
                page.click('td:nth-child(8) > div > button')
                page.click('td:nth-child(8) > div > ul > li:nth-child(1) > a')
                page.click('//*[@id="location_tab_localization"]')
                page.click('td:nth-child(4) > a:nth-child(2) > i')
                page.wait_for_selector('//*[@id="modal-dialog"]/div/div/div[1]/p', state="visible", timeout=30000)
                page.eval_on_selector('//*[@id="modal-dialog"]/div/div/div[1]/p', 'el => el.scrollIntoView()')
                page.click('//*[@id="select2-location_addresses_select_complemento3-container"]')

                if complemento == "CA":
                    page.fill('//*[@id="application"]/span/span/span[1]/input', 'casa')
                if complemento == "SL":
                    page.fill('//*[@id="application"]/span/span/span[1]/input', 'sala')

                sleep(3)
                page.press('//*[@id="application"]/span/span/span[1]/input', 'Enter')
                page.fill('//*[@id="location_addresses_input_argumento3"]', number)
                
                sleep(2)
                # Confirmar
                page.click('//*[@id="modal_button_ok"]')

                sleep(5)
                # Salvar formulário
                page.click('//*[@id="forms_button_save"]')

                registrar_relatorio(survey, "Sucesso!", time() - start_time)
            except TimeoutError as e:
                registrar_relatorio(survey, "Falha crítica: Excedeu o limite de tempo", "Timeout")
            except Exception as e:
                msg = str(e)
                if "connection" in msg.lower():
                    registrar_relatorio(survey, "Falha crítica: Queda de conexão", "Conexão perdida")
                else:
                    registrar_relatorio(survey, f"Falha: {msg}", time() - start_time)

if __name__ == "__main__":
    main()