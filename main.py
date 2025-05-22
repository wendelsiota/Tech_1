from fastapi import FastAPI, Query, HTTPException
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from web_scraper import scrape_table
from urllib.parse import urlencode
from typing import Optional
from pydantic import BaseModel, Field

app = FastAPI(
    title="Vitibrasil Scraper API",
    description="""
    API para scraping de dados do site Vitibrasil, com opções de ano, categoria e subcategoria.

    ### Opções e Subopções Disponíveis

    | Opção   | Subopção       | Descrição                       | Aceita Subopção? |
    |---------|----------------|---------------------------------|------------------|
    | opt_02  | -              | Produção                       | Não              |
    | opt_03  | subopt_01      | Processamento - Viníferas      | Sim              |
    |         | subopt_02      | Processamento - Americanas e Híbridas | Sim       |
    |         | subopt_03      | Processamento - Uvas de Mesa   | Sim              |
    |         | subopt_04      | Processamento - Sem Classificação | Sim           |
    | opt_04  | -              | Comercialização                | Não              |
    | opt_05  | subopt_01      | Importação - Vinhos de Mesa    | Sim              |
    |         | subopt_02      | Importação - Espumantes        | Sim              |
    |         | subopt_03      | Importação - Uvas Frescas      | Sim              |
    |         | subopt_04      | Importação - Uvas Passas       | Sim              |
    |         | subopt_05      | Importação - Suco de Uva       | Sim              |
    | opt_06  | subopt_01      | Exportação - Vinhos de Mesa    | Sim              |
    |         | subopt_02      | Exportação - Espumantes        | Sim              |
    |         | subopt_03      | Exportação - Uvas Frescas      | Sim              |
    |         | subopt_04      | Exportação - Suco de Uva       | Sim              |
    """,
    version="1.0.0"
)

# Configuração das opções válidas
VALID_OPTIONS = {
    "opt_02": {"subopcao": None, "descricao": "Produção"},
    "opt_03": {
        "subopt_01": "Processamento - Viníferas",
        "subopt_02": "Processamento - Americanas e Híbridas",
        "subopt_03": "Processamento - Uvas de Mesa",
        "subopt_04": "Processamento - Sem Classificação"
    },
    "opt_04": {"subopcao": None, "descricao": "Comercialização"},
    "opt_05": {
        "subopt_01": "Importação - Vinhos de Mesa",
        "subopt_02": "Importação - Espumantes",
        "subopt_03": "Importação - Uvas Frescas",
        "subopt_04": "Importação - Uvas Passas",
        "subopt_05": "Importação - Suco de Uva"
    },
    "opt_06": {
        "subopt_01": "Exportação - Vinhos de Mesa",
        "subopt_02": "Exportação - Espumantes",
        "subopt_03": "Exportação - Uvas Frescas",
        "subopt_04": "Exportação - Suco de Uva"
    }
}

# Anos válidos
VALID_YEARS = range(1970, 2025)

class TableResponse(BaseModel):
    status: str
    data: list[list[str]]
    url: str

class ErrorResponse(BaseModel):
    status: str
    message: str

def build_url(ano: int, opcao: str, subopcao: Optional[str] = None) -> str:

    base_url = "http://vitibrasil.cnpuv.embrapa.br/index.php"
    params = {"ano": ano, "opcao": opcao}
    if subopcao:
        params["subopcao"] = subopcao
    return f"{base_url}?{urlencode(params)}"

@app.get(
    "/scrape",
    response_model=TableResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Extrair dados da tabela do Vitibrasil",
    description="Endpoint para extrair dados de tabelas do site Vitibrasil com base em ano, opção e subopção."
)
async def get_table_data(
    ano: int = Query(..., description="Ano da consulta (ex.: 2020). Deve estar entre 1970 e 2024.", ge=1970, le=2024),
    opcao: str = Query(..., description="Opção da consulta. Veja a tabela de opções na descrição geral da API."),
    subopcao: Optional[str] = Query(None, description="Subopção da consulta (obrigatória para algumas opções como opt_03, opt_05, opt_06).")
):

    if opcao not in VALID_OPTIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Opção inválida. Opções válidas: {list(VALID_OPTIONS.keys())}"
        )

    # Verifica se subopcao é necessária ou válida
    option_details = VALID_OPTIONS[opcao]
    if isinstance(option_details, dict) and "subopcao" in option_details and option_details["subopcao"] is None:
        if subopcao:
            raise HTTPException(
                status_code=400,
                detail=f"A opção '{opcao}' não aceita subopcao"
            )
    elif isinstance(option_details, dict) and subopcao and subopcao not in option_details:
        raise HTTPException(
            status_code=400,
            detail=f"Subopção inválida para '{opcao}'. Subopções válidas: {list(option_details.keys())}"
        )

    try:
        # Constrói a URL
        url = build_url(ano, opcao, subopcao)

        # Chama a função de scraping
        data = scrape_table(url)
        return {"status": "success", "data": data, "url": url}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar a URL: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)