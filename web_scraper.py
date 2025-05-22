import requests
from bs4 import BeautifulSoup



def scrape_table(url):
    """
    Função que realiza o scraping de uma tabela em uma página web e retorna os dados extraídos.

    Args:
        url (str): URL da página web contendo a tabela a ser extraída.

    Returns:
        list: Lista de listas contendo os dados da tabela (incluindo cabeçalho).

    Raises:
        requests.HTTPError: Se a requisição HTTP falhar.
        AttributeError: Se a tabela com a classe especificada não for encontrada.
    """
    # Faz a requisição HTTP
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida
    response.raise_for_status()

    # Parseia o HTML da página usando BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontra a tabela específica pela classe
    table = soup.find('table', {'class': 'tb_base tb_dados'})

    # Verifica se a tabela foi encontrada
    if not table:
        raise AttributeError("Tabela com a classe 'tb_base tb_dados' não encontrada.")

    # Extrai as linhas da tabela
    rows = table.find_all('tr')

    # Lista para armazenar os dados
    data = []

    # Itera sobre as linhas e extrai o texto das células
    for row in rows:
        cells = row.find_all(['th', 'td'])  # Inclui cabeçalhos (th) e dados (td)
        cell_text = [cell.get_text(strip=True) for cell in cells]
        if cell_text:  # Ignora linhas vazias
            data.append(cell_text)

    return data