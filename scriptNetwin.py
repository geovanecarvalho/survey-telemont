from playwright.sync_api import sync_playwright
from time import sleep, time
import csv, os
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
        tempo_str = tempo_execucao
    else:
        tempo_str = str(tempo_execucao)
    with open("relatorio.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([survey, endereco, now, status, tempo_str])

def formatar_tempo(segundos):
    # Separar parte inteira (segundos) da parte decimal (milissegundos)
    segundos_int = int(segundos)
    milissegundos = int((segundos - segundos_int) * 1000)

    # Calcular horas, minutos e segundos
    horas = segundos_int // 3600
    minutos = (segundos_int % 3600) // 60
    segundos_restantes = segundos_int % 60

    # Retornar no formato desejado
    # horas, minutos, segundos e milissegundos
    # return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}:{milissegundos:03d}"
    # horas, minutos e segundos
    return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"


def main():
    # Cria o cabeçalho do relatório apenas se o arquivo não existir ou estiver vazio
    if not os.path.exists("relatorio.csv") or os.path.getsize("relatorio.csv") == 0:
        with open("relatorio.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["survey", "endereco", "data_hora", "status", "tempo_execucao"])

    with sync_playwright() as p:
        login = False
        # Inicia o navegador visível para login
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        erros_consecutivos_conexao = 0  # Contador de erros consecutivos de conexão
        
        for idx, lista in enumerate(tqdm(read_list(), desc="Barra de progresso de surveys:")):
            start_time = time()
            try:
                valor = lista.split(";")
                survey = valor[0]
                complemento = valor[1][:2]
                number = valor[1][-1]
                endereco = f"{complemento}{number}"
                print(f"Digitando nº de Survey: {survey}, Endereço: {endereco}")

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
                    browser = p.chromium.launch(headless=False)
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
                print("Clicou em location manager")
                sleep(2)
                page.click('//*[@id="operation-module-link-location-1-1"]')
                print("Clicou em localização manager aba lateral esquerda")
                sleep(2)
                page.fill('//*[@id="location_locphysical_input_name"]', survey)
                print(f"Preencheu o nome da localização: {survey}")
                sleep(2)
                page.click('//*[@id="submit_form"]')
                print("Clicou em buscar e aguarda resultados........")
                page.wait_for_selector('td:nth-child(8) > div > button', state="visible", timeout=90000)
                print("Resultados carregados")
                page.click('td:nth-child(8) > div > button')
                print("Clicou em editar")
                page.click('td:nth-child(8) > div > ul > li:nth-child(1) > a')
                print("Clicou no segunda opção para editar")
                page.click('//*[@id="location_tab_localization"]')
                print("Clicou na aba localização")
                page.click('td:nth-child(4) > a:nth-child(2) > i')
                print("Clicou em editar endereço")
                page.wait_for_selector('//*[@id="modal-dialog"]/div/div/div[1]/p', state="visible", timeout=30000)
                print("Modal de edição de endereço carregado")
                page.eval_on_selector('//*[@id="modal-dialog"]/div/div/div[1]/p', 'el => el.scrollIntoView()')
                print("Scroll para o útimo topo do modal")
                page.click('//*[@id="select2-location_addresses_select_complemento3-container"]')
                print("Clicou no select complemento 3")
                sleep(2)

                nome_completo = NOMECLATURA_ED.get(complemento)
                
                #if complemento == "CA":
                    #page.fill('//*[@id="application"]/span/span/span[1]/input', 'casa')
                #if complemento == "SL":
                    #page.fill('//*[@id="application"]/span/span/span[1]/input', 'sala')

                # Verifica se o select está desabilitado pela classe
                select_locator = page.locator('//*[@id="select2-location_addresses_select_complemento3-container"]/ancestor::span[contains(@class, "select2-container")]')
                classes = select_locator.get_attribute("class")

                print("Verificando se o select do complemento 3 está desabilitado...")
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
                print("Confirmou o endereço")

                sleep(5)
                # Salvar formulário
                page.click('//*[@id="forms_button_save"]')
                print("Salvou o formulário")
                tempo_execucao = time() - start_time
                # tempo_str = f"{tempo_execucao:.2f}s"
                print(f"Survey {survey} salvo com sucesso!, tempo: {formatar_tempo(tempo_execucao)}\n")

                sleep(15)
                
                registrar_relatorio(survey, endereco, "Sucesso!", formatar_tempo(tempo_execucao))
                erros_consecutivos_conexao = 0  # Zera contador em caso de sucesso
            
            except TimeoutError as e:
                registrar_relatorio(survey, endereco, "Falha crítica: Excedeu o limite de tempo", formatar_tempo(time() - start_time))
                print(f"Survey {survey} falhou: Excedeu o limite de tempo\n")
                erros_consecutivos_conexao = 0  # Não conta timeout como erro de conexão
            
            except Exception as e:
                msg = str(e)
                if "connection" in msg.lower():
                    registrar_relatorio(survey, endereco, "Falha crítica: Queda de conexão", "Conexão perdida")
                    print(f"Survey {survey} falhou: Queda de conexão\n")
                    erros_consecutivos_conexao += 1
                
                if erros_consecutivos_conexao >= 3:
                    print("3 erros consecutivos de conexão detectados. Encerrando execução.")
                    registrar_relatorio(survey, endereco, "Falha crítica: Queda de conexão", "3 erros consecutivos de conexão detectados. Execução finalizada.")
                    break
                else:
                    registrar_relatorio(survey, endereco, f"Falha: {msg}", formatar_tempo(time() - start_time))
                    print(f"Survey {survey} falhou: {msg} tempo: {formatar_tempo(time() - start_time)}\n")
                    erros_consecutivos_conexao = 0  # Zera para outros tipos de erro
               

if __name__ == "__main__":
    main()

