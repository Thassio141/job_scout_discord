import os
import pathlib
from fuzzywuzzy import fuzz
import csv
from web_scraping import search_gupy
from link_shortener import *
CSV_FILE = pathlib.Path('db','schedule_list.csv')

# Função para salvar um item no arquivo CSV
def save_to_csv(item):
    # Carrega os itens existentes
    existing_items = load_from_csv()

    # Verifica se o item já existe
    if item in existing_items:
        return f"Já existe um tópico com o nome '{item}'."

    # Salva o novo item no CSV
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([item])

    return f"Tópico '{item}' salvo com sucesso."


# Função para carregar todos os itens do arquivo CSV
def load_from_csv():
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return [row[0] for row in reader]  # Retorna apenas o primeiro elemento de cada linha
    except FileNotFoundError:
        return []

# Função para salvar os itens modificados de volta ao arquivo CSV
def save_all_to_csv(items):
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in items:
            writer.writerow([item])

def chunk_jobs(jobs, chunk_size=3):
    """Divide a lista de vagas em blocos de tamanho chunk_size."""
    for i in range(0, len(jobs), chunk_size):
        yield jobs[i:i + chunk_size]

async def send_jobs(ctx, termo):
    # Carrega as vagas do CSV
    job_chunks = find_similar_jobs(termo)

    # Verifica a quantidade de resultados para o termo
    if len(job_chunks) < 7:
        # Caso existam menos de 7 vagas, executa a busca no Gupy
        search_gupy(termo)
        # Atualiza as vagas do CSV após a busca
        job_chunks = find_similar_jobs(termo)

    # Envia os resultados em chunks
    for chunk in job_chunks:
        await ctx.send(chunk)



def find_similar_jobs(job_title: str, csv_file="db/search_list.csv"):
    if not os.path.exists(csv_file):
        return ["Nenhum resultado salvo ainda."]

    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        results = [row for row in reader if fuzz.partial_ratio(job_title.lower(), row[1].lower()) > 70]

    if not results:
        return [f"Nenhuma vaga encontrada para '{job_title}'."]

    # Formatar os resultados
    formatted_jobs = []
    for index, result in enumerate(results, 1):
        job = (
            f"**Vaga {index}:**\n"
            f"  **Nome:** {result[1]}\n"
            f"  **Empresa:** {result[3]}\n"
            f"  **Link:** {shorten_url_tinyurl_api(result[6])}\n"
            f"  **Publicada em:** {result[4]}\n"
            f"  **Senioridade: ** {result[2]}\n"
            f"  **Tipo de contrato:** {result[5]}\n"
            f"{'-' * 50}"
        )
        formatted_jobs.append(job)

    # Dividir os resultados em grupos de 3
    chunks = []
    for chunk in chunk_jobs(formatted_jobs, chunk_size=3):
        chunks.append("\n\n".join(chunk))  # Junta 3 vagas em uma única string

    return chunks
