import os
import sys
import xmltodict
import shutil
from datetime import datetime, date, timedelta


def sanitizar_nome(nome):
    """
    Remove caracteres inválidos para nomes de pasta e arquivos no Windows
    Mantém espaços, hífens, underlines e pontos
    Converte para ASCII (remove acentos) e limita o tamanho do nome
    """
    # Caracteres permitidos (Unicode code points)
    permitidos = (
        " -_."  # Espaço, hífen, underline, ponto
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
    )

    # Converter para ASCII removendo acentos
    try:
        nome_ascii = nome.encode("ascii", errors="ignore").decode("ascii")
    except:
        nome_ascii = nome

    # Filtrar caracteres permitidos
    nome_sanitizado = "".join(c for c in nome_ascii if c in permitidos).strip()

    # Remover múltiplos espaços consecutivos
    nome_sanitizado = " ".join(nome_sanitizado.split())

    # Limitar tamanho máximo para 200 caracteres
    max_length = 200
    if len(nome_sanitizado) > max_length:
        nome_sanitizado = nome_sanitizado[:max_length]

    # Garantir que o nome não termine com ponto ou espaço
    while nome_sanitizado and nome_sanitizado[-1] in (".", " "):
        nome_sanitizado = nome_sanitizado[:-1]

    # Se o nome ficar vazio, usar fallback
    return nome_sanitizado or "nome_invalido"


def extrair_dados_xml(caminho, tipo_documento):
    """Extrai xNome e dhEmi com tratamento de diferentes estruturas XML"""
    try:
        with open(caminho, "rb") as arquivo:
            dados = xmltodict.parse(arquivo)

            # Verificar diferentes estruturas de XML
            estruturas = list()

            if tipo_documento in ["NFE", "ALL"]:
                estruturas.append(
                    dados.get("nfeProc", {}).get("NFe", {}).get("infNFe", {})
                )
                estruturas.append(dados.get("NFe", {}).get("infNFe", {}))
                estruturas.append(dados.get("nfeProc", {}).get("NFe", {}))
                estruturas.append(dados.get("NFe", {}))
                estruturas.append(
                    dados.get("envEvento", {}).get("evento", {}).get("infEvento", {})
                )
                estruturas.append(dados.get("EventoNFe", {}))
                estruturas.append(
                    dados.get("procEventoNFe", {})
                    .get("evento", {})
                    .get("infEvento", {})
                )
                estruturas.append(dados.get("procEventoNFe", {}).get("evento", {}))
                estruturas.append(dados.get("procEventoNFe", {}))

            if tipo_documento in ["MDFE", "ALL"]:
                estruturas.append(
                    dados.get("procEventoMDFe", {})
                    .get("eventoMDFe", {})
                    .get("infEvento", {})
                )
                estruturas.append(
                    dados.get("mdfeProc", {}).get("MDFe", {}).get("infMDFe", {})
                )
                estruturas.append(
                    dados.get("MDFe", {}).get("mdfeProc", {}).get("infMDFe", {})
                )
                estruturas.append(dados.get("mdfeProc", {}).get("infMDFe", {}))
                estruturas.append(dados.get("MDFe", {}).get("infMDFe", {}))
                estruturas.append(dados.get("MDFe", {}))
                estruturas.append(dados.get("procEventoMDFe", {}))
                estruturas.append(dados.get("procEventoMDFe", {}).get("eventoMDFe", {}))

            estruturas_formatada = [x for x in estruturas if x]

            for estrutura in estruturas_formatada:
                if "emit" in estrutura and "CNPJ" in estrutura["emit"]:
                    emitente = estrutura["emit"]["CNPJ"]
                    data_str = estrutura.get("ide", {}).get("dhEmi", "sem_data")
                    return emitente, data_str
                elif "CNPJ" in estrutura and estrutura.get("tpEvento") in ["110111"]:
                    emitente = estrutura.get("CNPJ")
                    data_str = estrutura.get("dhEvento", "sem_data")
                    return emitente, data_str

            return None, None

    except Exception as e:
        print(f"Erro na leitura de {os.path.basename(caminho)}: {str(e)}")
        return None, None


def criar_estrutura_pastas(base, emitente, data_str):
    """Cria a estrutura hierárquica de pastas com tratamento de erros"""
    try:
        # Sanitizar nome do emitente
        pasta_emissor = sanitizar_nome(emitente)
        caminho_emissor = os.path.join(base, pasta_emissor)

        # Processar data de emissão
        if data_str.lower() == "sem_data":
            caminho_final = os.path.join(caminho_emissor, "sem_data")
        else:
            try:
                # Remover timezone e converter para objeto datetime
                data_limpa = data_str.split("T")[0]
                dt = datetime.strptime(data_limpa, "%Y-%m-%d")

                # Criar estrutura ano/mês/dia-mes-ano
                ano = str(dt.year)
                mes = f"{dt.month:02d}"
                dia_formatado = f"{dt.day:02d}-{dt.month:02d}-{dt.year}"

                caminho_final = os.path.join(caminho_emissor, ano, mes, dia_formatado)

            except ValueError:
                caminho_final = os.path.join(caminho_emissor, "data_invalida")

        # Criar toda a hierarquia de pastas
        os.makedirs(caminho_final, exist_ok=True)
        return caminho_final

    except Exception as e:
        print(f"Erro crítico ao criar pastas: {str(e)}")
        return None


def processar_xml(
    pasta_origem, pasta_destino, funcao_copy, tipo_documento, data_inicial
):
    """Processa todos os XMLs recursivamente com relatório detalhado"""
    contador = 0
    erros = 0

    if not tipo_documento.split():
        tipo_documento = "ALL"

    try:
        data_minima = date.fromisoformat(data_inicial)
    except:
        data_minima = date.today() - timedelta(days=30)

    print("-" * 55)
    print(f"Iniciando processamento em: {pasta_origem}")
    print(f"Tipo de documento definido: {tipo_documento}")
    print(f"Data ininial definida: {data_minima} ")
    print("-" * 55)

    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if not arquivo.lower().endswith(".xml"):
                continue

            caminho_completo = os.path.join(raiz, arquivo)
            emitente, data_str = extrair_dados_xml(caminho_completo, tipo_documento)

            if data_str is None:
                print(f"Erro: Data de emissao vazia. {data_str}. {arquivo}")
                continue

            data_emissao_nf = date.fromisoformat(data_str.split("T")[0])

            if data_emissao_nf < data_minima:
                print(
                    f"Erro: Data de emissao menor que data minima, {data_emissao_nf}. {arquivo}"
                )
                continue

            if not emitente:
                erros += 1
                print(f"Erro: Não foi possível extrair dados de {arquivo}.")
                continue

            destino = criar_estrutura_pastas(pasta_destino, emitente, data_str)

            if not destino:
                erros += 1
                print(
                    f"Erro: Não foi possível criar estrutura para {emitente}. {arquivo}"
                )
                continue

            try:
                if funcao_copy.lower() == "copiar":
                    if not os.path.exists(os.path.join(destino, arquivo)):
                        shutil.copy2(caminho_completo, os.path.join(destino, arquivo))
                else:
                    if not os.path.exists(os.path.join(destino, arquivo)):
                        shutil.move(caminho_completo, os.path.join(destino, arquivo))
                contador += 1
            except Exception as e:
                erros += 1
                print(f"Erro ao copiar {arquivo}: {str(e)}")

    print(f"\nProcesso concluído!")
    print(f"Arquivos processados com sucesso: {contador}")
    print(f"Erros encontrados: {erros}")
    print(f"Pasta destino: {pasta_destino}")


if __name__ == "__main__":
    print("=== Organizador de XMLs ===")
    opcao = sys.argv[1].strip()  # --- COPIAR ou MOVER
    origem = sys.argv[2].strip()  # --- Pasta Raiz de Origem
    destino = sys.argv[3].strip()  # --- Pasta Raiz de Destino
    documento = sys.argv[4].strip()  # --- Tipo de Documento ["NFE","MDFE","ALL"]
    data = sys.argv[5].strip()  # --- Data de inicio da emissao

    if not os.path.exists(origem):
        print("\nErro: A pasta de origem não existe!")
    else:
        processar_xml(origem, destino, opcao, documento, data)
