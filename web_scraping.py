import csv
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


# Função auxiliar para determinar senioridade
def determinar_senioridade(titulo):
    senioridades = {
        "Pleno": "Pleno",
        "Senior": "Sênior",
        "Junior": "Júnior",
        "Sr": "Sênior",
        "PL": "Pleno",
        "Jr": "Júnior",
    }
    for key, value in senioridades.items():
        if key.lower() in titulo.lower():
            return value
    return "Não especificada"

# Função auxiliar para determinar o tipo de contrato
def determinar_contrato(tipo):
    if "Pessoa Jurídica" in tipo:
        return "PJ"
    elif "Efetivo" in tipo:
        return "CLT"
    elif "Associado" in tipo:
        return "Associado"
    return "Não especificado"

from selenium.webdriver.chrome.options import Options

def search_gupy(termo: str):
    # Configurando o WebDriver em modo headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ativar modo headless
    chrome_options.add_argument("--disable-gpu")  # Necessário para alguns sistemas
    chrome_options.add_argument("--no-sandbox")  # Segurança adicional
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memória em ambientes com poucos recursos

    driver = webdriver.Chrome(options=chrome_options)

    # URL formatada com o termo de busca
    gupy_url = f"https://portal.gupy.io/job-search/term={termo}&workplaceTypes[]=remote"
    driver.get(gupy_url)

    # Esperando a página carregar completamente
    time.sleep(3)

    # XPaths para os atributos
    titulo_vaga_xpath = "/html/body/div[1]/div[3]/div/div/main/ul/li/div/a/div/h3"
    data_lancamento_xpath = "/html/body/div[1]/div[3]/div/div/main/ul/li/div/a/div/span/div/p"
    nome_empresa_xpath = "/html/body/div[1]/div[3]/div/div/main/ul/li/div/a/div/div[1]/div/p"
    pj_ou_clt_xpath = "/html/body/div[1]/div[3]/div/div/main/ul/li/div/a/div/div[2]/div/div[3]/span"
    link_da_vaga_xpath = "/html/body/div[1]/div[3]/div/div/main/ul/li/div/a"

    # Capturar os elementos
    titulos = driver.find_elements(By.XPATH, titulo_vaga_xpath)
    datas = driver.find_elements(By.XPATH, data_lancamento_xpath)
    empresas = driver.find_elements(By.XPATH, nome_empresa_xpath)
    contratos = driver.find_elements(By.XPATH, pj_ou_clt_xpath)
    links = driver.find_elements(By.XPATH, link_da_vaga_xpath)

    # Criar diretório se não existir
    os.makedirs("db", exist_ok=True)
    csv_file = "db/search_list.csv"

    # Carregar vagas existentes no CSV
    vagas_existentes = set()
    if os.path.exists(csv_file):
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                vagas_existentes.add(tuple(row))

    # Abrir o arquivo CSV no modo de escrita (append)
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Processar cada vaga
        for i in range(len(titulos)):
            titulo = titulos[i].text if i < len(titulos) else "Não encontrado"
            data = datas[i].text if i < len(datas) else "Não especificada"
            empresa = empresas[i].text if i < len(empresas) else "Não especificada"
            contrato = contratos[i].text if i < len(contratos) else "Não especificado"
            link = links[i].get_attribute("href") if i < len(links) else "Sem link"

            # Determinar senioridade e tipo de contrato
            senioridade = determinar_senioridade(titulo)
            tipo_contrato = determinar_contrato(contrato)

            vaga = (termo, titulo, senioridade, empresa, data, tipo_contrato, link)

            # Escrever no CSV apenas se a vaga não existir
            if vaga not in vagas_existentes:
                writer.writerow(vaga)

    # Fechar o WebDriver
    driver.quit()
