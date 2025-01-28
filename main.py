import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

# Carregar configurações do config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Configuração do WebDriver
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

def realizar_login():
    try:
        # Acessar o site
        driver.get(config["url"])
        time.sleep(5)  # Esperar a página carregar

        # Preencher o campo de email/usuário
        campo_email = driver.find_element(By.ID, "data.email")
        campo_email.send_keys(config["usuario"])
        print("Campo de email/usuário preenchido.")

        # Preencher o campo de senha
        campo_senha = driver.find_element(By.ID, "data.password")
        campo_senha.send_keys(config["senha"])
        print("Campo de senha preenchido.")

        # Localizar e clicar no botão de login
        botao_login = driver.find_element(By.CLASS_NAME, "fi-btn")
        botao_login.click()
        print("Botão de login clicado.")

        # Esperar o site processar o login
        time.sleep(5)
        print("Login realizado com sucesso!")

    except Exception as e:
        print(f"Erro ao realizar login: {e}")
        driver.quit()

def selecionar_tipo_visto():
    try:
        # Clicar no dropdown para abrir a lista de tipos de visto
        dropdown = driver.find_element(By.CLASS_NAME, "choices__list--single")
        dropdown.click()
        time.sleep(2)

        # Selecionar o tipo de visto pelo texto
        tipo_visto = driver.find_element(By.XPATH, '//div[contains(text(), "VITEM XI - Family Reunification Visa")]')
        tipo_visto.click()
        print("Tipo de visto selecionado.")

        # Clicar no botão "Next" para avançar
        botao_next = driver.find_element(By.XPATH, '//span[contains(text(), "Next")]/..')
        botao_next.click()
        print("Botão 'Next' clicado.")
        time.sleep(5)

    except Exception as e:
        print(f"Erro ao selecionar tipo de visto: {e}")
        driver.quit()

def verificar_disponibilidade():
    try:
        # Verificar se o calendário ou o próximo botão está presente
        time.sleep(5)  # Aguarda o calendário carregar completamente

        # Localizar possíveis datas no calendário
        datas = driver.find_elements(By.CSS_SELECTOR, ".date-class")  # Ajuste conforme necessário
        for dia in datas:
            if "disabled" not in dia.get_attribute("class"):  # Verifica se o dia está habilitado
                data_disponivel = dia.text
                print(f"Data disponível encontrada: {data_disponivel}")
                return True

        print("Nenhuma data disponível no momento.")
        return False

    except Exception as e:
        print(f"Erro ao verificar disponibilidade: {e}")
        return False

try:
    # Fluxo principal
    realizar_login()  # Realiza o login no site
    selecionar_tipo_visto()  # Seleciona o tipo de visto e avança
    disponibilidade = verificar_disponibilidade()  # Verifica disponibilidade no calendário

    if disponibilidade:
        print("Horários disponíveis encontrados.")
    else:
        print("Não há horários disponíveis.")
finally:
    driver.quit()
