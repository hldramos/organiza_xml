import os
import sys
import xmltodict
import shutil
from datetime import datetime


def sanitizar_nome(nome):
    """
    Remove caracteres inválidos para nomes de pasta e arquivos no Windows
    Mantém espaços, hífens, underlines e pontos
    Converte para ASCII (remove acentos) e limita o tamanho do nome
    """
    # Caracteres permitidos (Unicode code points)
    permitidos = (
        ' -_.'  # Espaço, hífen, underline, ponto
        'abcdefghijklmnopqrstuvwxyz'
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        '0123456789'
    )

    # Converter para ASCII removendo acentos
    try:
        nome_ascii = nome.encode('ascii', errors='ignore').decode('ascii')
    except:
        nome_ascii = nome

    # Filtrar caracteres permitidos
    nome_sanitizado = ''.join(
        c for c in nome_ascii
        if c in permitidos
    ).strip()

    # Remover múltiplos espaços consecutivos
    nome_sanitizado = ' '.join(nome_sanitizado.split())

    # Limitar tamanho máximo para 200 caracteres
    max_length = 200
    if len(nome_sanitizado) > max_length:
        nome_sanitizado = nome_sanitizado[:max_length]

    # Garantir que o nome não termine com ponto ou espaço
    while nome_sanitizado and nome_sanitizado[-1] in ('.', ' '):
        nome_sanitizado = nome_sanitizado[:-1]

    # Se o nome ficar vazio, usar fallback
    return nome_sanitizado or 'nome_invalido'


def extrair_dados_xml(caminho):
    """Extrai xNome e dhEmi com tratamento de diferentes estruturas XML"""
    try:
        with open(caminho, 'rb') as arquivo:
            dados = xmltodict.parse(arquivo)

            # Verificar diferentes estruturas de XML
            estruturas = [
                dados.get('NFe', {}).get('infNFe', {}),
                dados.get('nfeProc', {}).get('NFe', {}).get('infNFe', {}),
                dados.get('NFe', {}),
                dados.get('nfeProc', {}).get('NFe', {})
            ]


            for estrutura in estruturas:
                if 'emit' in estrutura and 'xNome' in estrutura['emit']:
                    dados_emitente = list()
                    dados_emitente.append(estrutura['emit']['CNPJ'])
                    dados_emitente.append(estrutura['emit']['xNome'])
                    emitente = "-".join(dados_emitente)
                    data_str = estrutura.get('ide', {}).get('dhEmi', 'sem_data')
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
        if data_str.lower() == 'sem_data':
            caminho_final = os.path.join(caminho_emissor, 'sem_data')
        else:
            try:
                # Remover timezone e converter para objeto datetime
                data_limpa = data_str.split('T')[0]
                dt = datetime.strptime(data_limpa, '%Y-%m-%d')

                # Criar estrutura ano/mês/dia-mes-ano
                ano = str(dt.year)
                mes = f"{dt.month:02d}"
                dia_formatado = f"{dt.day:02d}-{dt.month:02d}-{dt.year}"

                caminho_final = os.path.join(caminho_emissor, ano, mes, dia_formatado)

            except ValueError:
                caminho_final = os.path.join(caminho_emissor, 'data_invalida')

        # Criar toda a hierarquia de pastas
        os.makedirs(caminho_final, exist_ok=True)
        return caminho_final

    except Exception as e:
        print(f"Erro crítico ao criar pastas: {str(e)}")
        return None


def processar_xml(pasta_origem, pasta_destino, funcao_copy):
    """Processa todos os XMLs recursivamente com relatório detalhado"""
    contador = 0
    erros = 0

    print(f"\nIniciando processamento em: {pasta_origem}")

    for raiz, _, arquivos in os.walk(pasta_origem):
        for arquivo in arquivos:
            if not arquivo.lower().endswith('.xml'):
                continue

            caminho_completo = os.path.join(raiz, arquivo)
            emitente, data_str = extrair_dados_xml(caminho_completo)


            if not emitente:
                erros += 1
                print(f"Erro: Não foi possível extrair dados de {arquivo}")
                continue

            destino = criar_estrutura_pastas(pasta_destino, emitente, data_str)

            if not destino:
                erros += 1
                print(f"Erro: Não foi possível criar estrutura para {emitente}")
                continue

            try:
                if funcao_copy=="copiar":
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

    if not os.path.exists(origem):
        print("\nErro: A pasta de origem não existe!")
    else:
        processar_xml(origem, destino, opcao)


"C:\\Users\\helde\\Downloads\\teste"