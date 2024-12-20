import csv
import os
from discord import Intents
from discord.ext import commands, tasks
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Carregar as variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Inicializar o bot do Discord com intents
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Função para verificar se a vaga já foi registrada
def vaga_ja_registrada(link):
    try:
        with open('vagas.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[4] == link:  # Verifica se o link já existe
                    return True
    except FileNotFoundError:
        print("Arquivo vagas.csv não encontrado.")
    return False

# Função para salvar a vaga no arquivo vagas.csv
def salvar_vaga(vaga):
    try:
        with open('vagas.csv', mode='a', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(vaga)
    except FileNotFoundError:
        print("Arquivo vagas.csv não encontrado.")

# Função para enviar mensagem no Discord
async def enviar_no_discord(mensagem):
    channel = bot.get_channel(1274549604834218066)  # Substitua pelo ID do canal
    if channel:
        await channel.send(mensagem)

# Função para configurar o Selenium WebDriver
def configurar_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Não abrir a interface gráfica do navegador
    chrome_options.add_argument("--disable-gpu")  # Desabilitar aceleração de GPU
    chrome_options.add_argument("--no-sandbox")  # Necessário em alguns ambientes Linux
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas em memória compartilhada
    chrome_options.add_argument("--window-size=1920x1080")  # Define um tamanho padrão para a janela

    # Verifica o sistema operacional para localizar o chromedriver
    driver_path = "/usr/bin/chromedriver" if os.name == "posix" else "chromedriver.exe"
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Função para buscar vagas
def buscar_vagas(term):
    url = f"https://portal.gupy.io/job-search/term={term.replace(' ', '%20')}&workplaceTypes[]=remote"
    driver = configurar_selenium()
    driver.get(url)

    # Espera a página carregar completamente (ajuste o tempo de espera conforme necessário)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[3]/div/div/main/ul/li'))
    )

    vagas = []
    vagas_elements = driver.find_elements(By.XPATH, '/html/body/div[1]/div[3]/div/div/main/ul/li')

    for vaga in vagas_elements:
        try:
            nome_da_empresa = vaga.find_element(By.XPATH, './/div/a/div/div[1]/div/p').text
            titulo_da_vaga = vaga.find_element(By.XPATH, './/div/a/div/h3').text
            link_da_vaga = vaga.find_element(By.XPATH, './/div/a').get_attribute('href')

            senioridade = tipo_de_contratacao = data_de_publicacao = "N/A"
            try:
                senioridade = vaga.find_element(By.XPATH, './/div/a/div/div[2]/div/div[3]/span').text
            except:
                pass
            try:
                tipo_de_contratacao = vaga.find_element(By.XPATH, './/div/a/div/div[2]/div/div[3]/span').text
            except:
                pass
            try:
                data_de_publicacao = vaga.find_element(By.XPATH, './/div/a/div/span/div/p').text
            except:
                pass

            if nome_da_empresa and titulo_da_vaga and link_da_vaga:
                vaga_info = [
                    nome_da_empresa,
                    senioridade,
                    tipo_de_contratacao,
                    titulo_da_vaga,
                    link_da_vaga,
                    data_de_publicacao
                ]
                if not vaga_ja_registrada(link_da_vaga):
                    salvar_vaga(vaga_info)
                    vagas.append(vaga_info)

        except Exception as e:
            print(f"Erro ao extrair dados de uma vaga: {e}")
            continue

    driver.quit()  # Fecha o driver do Selenium
    return vagas

# Restante do código permanece o mesmo...


# Tarefa periódica para buscar vagas a cada 30 minutos
@tasks.loop(minutes=30)  # 30 minutos para a execução periódica
async def busca_vagas_periodica():
    termos = carregar_termos()
    novas_vagas = []
    for termo in termos:
        vagas = buscar_vagas(termo)
        for vaga in vagas:
            mensagem = f"Nova vaga encontrada!\n\n" \
                       f"**Empresa**: {vaga[0]}\n" \
                       f"**Senioridade**: {vaga[1]}\n" \
                       f"**Tipo de Contratação**: {vaga[2]}\n" \
                       f"**Título**: {vaga[3]}\n" \
                       f"**Link**: {vaga[4]}\n" \
                       f"**Data de Publicação**: {vaga[5]}"
            await enviar_no_discord(mensagem)
            novas_vagas.append(vaga)

    if novas_vagas:
        print(f"{len(novas_vagas)} novas vagas encontradas.")
    else:
        print("Nenhuma nova vaga encontrada.")

# Função para carregar os termos do arquivo termos.csv
def carregar_termos():
    termos = []
    try:
        with open('termos.csv', mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                termos.append(row[0])  # Adiciona o termo na lista
    except FileNotFoundError:
        print("Arquivo termos.csv não encontrado.")
    return termos

# Função para salvar os termos no arquivo termos.csv
def salvar_termos(termos):
    try:
        with open('termos.csv', mode='w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            for termo in termos:
                writer.writerow([termo])  # Escreve cada termo no arquivo
    except FileNotFoundError:
        print("Arquivo termos.csv não encontrado.")

# Comando para adicionar um termo ao arquivo
@bot.command(name="add")
async def add_termo(ctx, *, termo: str):
    termos = carregar_termos()
    if termo not in termos:
        termos.append(termo)
        salvar_termos(termos)
        await ctx.send(f"Termo '{termo}' adicionado com sucesso!")
    else:
        await ctx.send(f"O termo '{termo}' já está na lista.")

# Comando para deletar um termo do arquivo
@bot.command(name="delete")
async def delete_termo(ctx, *, termo: str):
    termos = carregar_termos()
    if termo in termos:
        termos.remove(termo)
        salvar_termos(termos)
        await ctx.send(f"Termo '{termo}' removido com sucesso!")
    else:
        await ctx.send(f"O termo '{termo}' não está na lista.")

# Comando para listar todos os termos no arquivo
@bot.command(name="list")
async def list_termos(ctx):
    termos = carregar_termos()
    if termos:
        await ctx.send("Termos armazenados:\n" + "\n".join(termos))
    else:
        await ctx.send("Não há termos armazenados.")

# Evento: Bot pronto
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    busca_vagas_periodica.start()

# Inicia o bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("Erro: Token não encontrado. Verifique seu arquivo .env.")
