from discord.ext import commands
import db.load_read_csv as db
from web_scraping import *

# Comando: add_list
@commands.command()
async def add(ctx, *, items: str):
    """Comando para adicionar múltiplos itens à lista, separados por vírgula."""
    if not items:
        await ctx.send("Por favor, informe o que deseja adicionar à lista.")
    else:
        # Verifica se há vírgula
        if ',' in items:
            # Se houver vírgula, separa os itens
            item_list = [item.strip() for item in items.split(',')]
            for item in item_list:
                db.save_to_csv(item)
            await ctx.send(f"Item(s) adicionado(s): {', '.join(item_list)}")
        else:
            # Se não houver vírgula, adiciona o texto todo como um único item
            db.save_to_csv(items.strip())
            await ctx.send(f"Item adicionado: {items.strip()}")

# Comando: see_list
@commands.command()
async def list(ctx):
    """Comando para visualizar a lista no arquivo CSV."""
    items = db.load_from_csv()
    if not items:
        await ctx.send("A lista está vazia.")
    else:
        # Formatar a lista de forma amigável
        formatted_list = "\n".join([f"- {item}" for item in items])
        await ctx.send(f"**Itens na lista:**\n{formatted_list}")

# Comando: delete_list
@commands.command()
async def delete(ctx, *, items: str):
    """Comando para deletar itens da lista, separados por vírgula."""
    if not items:
        await ctx.send("Por favor, informe o que deseja remover da lista.")
    else:
        # Separar os itens pela vírgula, remover espaços extras
        item_list = [item.strip() for item in items.split(',')]
        current_items = db.load_from_csv()

        # Remover os itens fornecidos da lista
        updated_items = [item for item in current_items if item not in item_list]

        # Verificar se algum item foi removido
        if len(updated_items) == len(current_items):
            await ctx.send(f"Nenhum item encontrado para remover: {', '.join(item_list)}")
        else:
            # Salvar a lista modificada no CSV
            db.save_all_to_csv(updated_items)
            await ctx.send(f"Item(s) removido(s): {', '.join(item_list)}")


@commands.command()
async def search(ctx, termo: str):

    await db.send_jobs(ctx, termo)


# Função para adicionar os comandos ao bot
def setup_commands(bot):
    bot.add_command(search)
    bot.add_command(add)
    bot.add_command(list)
    bot.add_command(delete)
