from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import smtplib
from email.mime.text import MIMEText

# Carregar configurações do config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Configuração do WebDriver
service = Service('/usr/local/bin/chromedriver')
driver = webdriver.Chrome(service=service)

# Função para enviar email
def enviar_email(data_disponivel):
    try:
        remetente = config["email_remetente"]
        senha = config["senha_remetente"]
        destinatario = config["email_destinatario"]
        assunto = "Data disponível para agendamento"
        corpo = f"Uma nova data está disponível: {data_disponivel}"

        mensagem = MIMEText(corpo)
        mensagem["Subject"] = assunto
        mensagem["From"] = remetente
        mensagem["To"] = destinatario

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remetente, senha)
            servidor.sendmail(remetente, destinatario, mensagem.as_string())
        print(f"Email enviado com sucesso para {destinatario}.")
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

# Função para verificar as datas no calendário clicando mês a mês
def verificar_calendario():
    try:
        # Abrir o calendário
        campo_data = driver.find_element(By.ID, "data.appointment_date")
        campo_data.click()
        print("Calendário aberto.")
        time.sleep(2)

        # Localizar o dropdown de meses
        select_mes = Select(driver.find_element(By.XPATH, '//select[@x-model="focusedMonth"]'))  # Selecionar o dropdown do mês
        campo_ano = driver.find_element(By.XPATH, '//input[@x-model.debounce="focusedYear"]')  # Campo do ano

        # Iterar pelos 5 primeiros meses (ajustando o ano se necessário)
        for mes_index in range(5):
            if mes_index >= len(select_mes.options):  # Se o índice exceder os meses disponíveis
                campo_ano.clear()
                campo_ano.send_keys(int(campo_ano.get_attribute("value")) + 1)  # Muda para o próximo ano
                time.sleep(2)
                select_mes = Select(driver.find_element(By.XPATH, '//select[@x-model="focusedMonth"]'))

            # Selecionar o mês pelo índice
            select_mes.select_by_index(mes_index)
            print(f"Verificando o mês: {select_mes.options[mes_index].text}")
            time.sleep(2)

            # Verificar dias habilitados no mês atual
            dias = driver.find_elements(By.XPATH, '//div[contains(@class, "day") and not(contains(@class, "disabled"))]')
            for dia in dias:
                data_disponivel = dia.text
                print(f"Data disponível encontrada: {data_disponivel}")
                enviar_email(data_disponivel)
                return True

            # Verificar os motivos das datas desabilitadas
            dias_desabilitados = driver.find_elements(By.XPATH, '//div[contains(@class, "day disabled")]')
            for dia in dias_desabilitados:
                motivo = dia.get_attribute("class")
                print(f"Data desabilitada encontrada: {dia.text} - Motivo: {motivo}")

        print("Nenhuma data disponível nos 5 primeiros meses.")
        return False

    except Exception as e:
        print(f"Erro ao verificar o calendário: {e}")
        return False

try:
    # Fluxo principal
    driver.get(config["url"])
    time.sleep(5)

    # Realizar login
    driver.find_element(By.ID, "data.email").send_keys(config["usuario"])
    driver.find_element(By.ID, "data.password").send_keys(config["senha"])
    driver.find_element(By.CLASS_NAME, "fi-btn").click()
    print("Login realizado.")
    time.sleep(5)

    # Selecionar tipo de visto e clicar em "Next"
    driver.find_element(By.CLASS_NAME, "choices__list--single").click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//div[contains(text(), "VITEM XI - Family Reunification Visa")]').click()
    driver.find_element(By.XPATH, '//span[contains(text(), "Next")]/..').click()
    print("Avançou para a tela do calendário.")
    time.sleep(5)

    # Verificar datas no calendário
    disponibilidade = verificar_calendario()

    if disponibilidade:
        print("Datas disponíveis encontradas.")
    else:
        print("Não há datas disponíveis nos 5 primeiros meses.")
finally:
    driver.quit()
