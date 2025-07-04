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

            if "NFE" == tipo_documento or "ALL" == tipo_documento:
                estruturas.append(
                    dados.get("nfeProc", {}).get("NFe", {}).get("infNFe", {})
                )
                estruturas.append(dados.get("NFe", {}).get("infNFe", {}))
                estruturas.append(dados.get("nfeProc", {}).get("NFe", {}))
                estruturas.append(dados.get("NFe", {}))
                estruturas.append(dados.get("envEvento", {}).get("evento", {}).get("infEvento", {}))
                estruturas.append(dados.get("EventoNFe", {}))
                estruturas.append(
                    dados.get("procEventoNFe", {})
                    .get("evento", {})
                    .get("infEvento", {})
                )
                estruturas.append(dados.get("procEventoNFe", {}).get("evento", {}))
                estruturas.append(dados.get("procEventoNFe", {}))
            elif "MDFE" == tipo_documento or "ALL" == tipo_documento:
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
                estruturas.append(
                    dados.get("procEventoMDFe", {})
                    .get("eventoMDFe", {})
                    .get("infEvento", {})
                )

            for estrutura in estruturas:
                if "emit" in estrutura and "CNPJ" in estrutura["emit"]:
                    # dados_emitente = list()
                    # dados_emitente.append(estrutura["emit"]["CNPJ"])
                    # dados_emitente.append(estrutura["emit"]["xNome"])
                    # emitente = "-".join(dados_emitente)
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


def processar_xml(pasta_origem, pasta_destino, funcao_copy, tipo_documento):
    """Processa todos os XMLs recursivamente com relatório detalhado"""
    contador = 0
    erros = 0

    if tipo_documento == None or tipo_documento == "":
        tipo_documento = "ALL"

    print(f"\nIniciando processamento em: {pasta_origem}")

    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if not arquivo.lower().endswith(".xml"):
                continue

            caminho_completo = os.path.join(raiz, arquivo)
            emitente, data_str = extrair_dados_xml(caminho_completo, tipo_documento)

            if data_str:
                data_minima = date.today() - timedelta(days=5)
                try:
                    data_emissao_nf = date.fromisoformat(data_str.split("T")[0])
                except:
                    print(f"Erro: Falha na conversao de data de emissao.")
                    continue

            if data_str is None:
                print(f"Erro: Data de emissao vazia. {data_str}.")
                continue

            if data_emissao_nf < data_minima:
                print(
                    f"Erro: Data de emissao menor que data minima, {data_emissao_nf}."
                )
                continue

            if not emitente:
                erros += 1
                print(f"Erro: Não foi possível extrair dados de {arquivo}.")
                continue

            destino = criar_estrutura_pastas(pasta_destino, emitente, data_str)

            if not destino:
                erros += 1
                print(f"Erro: Não foi possível criar estrutura para {emitente}")
                continue

            try:
                if funcao_copy.lower() == "copiar":
                    shutil.copy2(caminho_completo, os.path.join(destino, arquivo))
                else:
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
    opcao = sys.argv[1].strip()
    origem = sys.argv[2].strip()
    destino = sys.argv[3].strip()
    documento = sys.argv[4].strip()

    if not os.path.exists(origem):
        print("\nErro: A pasta de origem não existe!")
    else:
        processar_xml(origem, destino, opcao, documento)
