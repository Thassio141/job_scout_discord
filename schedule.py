import csv
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta


# Função que simula a execução da busca
async def search_gupy(termo):
    # Aqui você colocaria a lógica de busca real
    print(f"Buscando por: {termo}")


# Função para ler as palavras-chave do arquivo CSV
def load_keywords():
    keywords = []
    with open('schedule_list.csv', mode='r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row:  # Ignora linhas vazias
                keywords.append(row[0])  # Considera apenas a primeira coluna
    return keywords


# Função que calcula o tempo até as 11h de amanhã
def get_next_run_time():
    now = datetime.now()
    next_run = now.replace(hour=15, minute=12, second=0, microsecond=0)
    print("passei por aqui")
    if now > next_run:
        next_run += timedelta(days=1)
    return next_run


# Função que configura o agendamento
def scheduled_search():
    scheduler = AsyncIOScheduler()
    keywords = load_keywords()

    # Função que executa a busca para cada termo
    def perform_search():
        for keyword in keywords:
            asyncio.create_task(search_gupy(keyword))  # Chama a função de busca para cada termo

    # Calculando o tempo até a próxima execução às 11h
    next_run_time = get_next_run_time()

    # Agendando a execução diária com o intervalo calculado
    scheduler.add_job(perform_search, IntervalTrigger(start_date=next_run_time, days=1))

    # Inicia o agendador
    scheduler.start()


# validar toda vez que a vaga já tiver 2 dias de publicada remover da lista de search_list.csv