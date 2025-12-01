#!/usr/bin/env python3
# python3 analisar_e_fatiar.py prova_enem.pdf ENEM/2019/pdfs

import pdfplumber
import fitz  # PyMuPDF
import re
import argparse
import sys
import os

def analisar_e_cortar(pdf_entrada, pasta_saida):
    doc_fitz = fitz.open(pdf_entrada)

    with pdfplumber.open(pdf_entrada) as pdf_plumber:
        total_fatias = 0

        for i, page_plumber in enumerate(pdf_plumber.pages):
            width = page_plumber.width
            height = page_plumber.height
            mid_x = width / 2

            # --- PASSO 1: MAPEAR QUESTÕES ---
            words = page_plumber.extract_words()
            marcadores = []

            for index, w in enumerate(words):
                if re.match(r'^Questão$', w['text'], re.IGNORECASE):
                    if index + 1 < len(words) and re.match(r'^\d+$', words[index+1]['text']):
                        numero = words[index+1]['text']
                        marcadores.append({
                            'num': numero,
                            'y': w['top'],
                            'coluna': 'ESQ' if w['x0'] < mid_x else 'DIR'
                        })

            cortes_finais = []

            # --- PASSO 2: ESTRATÉGIA DE CORTE ---

            # CASO A: PÁGINA SEM QUESTÕES (Capa, etc) -> Full Page
            if not marcadores:
                cortes_finais.append({
                    'rect': fitz.Rect(0, 0, width, height),
                    'suffix': 'conteudo_full',
                    'coluna': 'FULL'
                })

            # CASO B: PÁGINA DE PROVA
            else:
                # 1. Definir Header (Topo até a 1ª questão)
                primeira_questao_y = min(m['y'] for m in marcadores)
                y_fim_header = max(0, primeira_questao_y - 10)

                if y_fim_header > 50:
                    cortes_finais.append({
                        'rect': fitz.Rect(0, 0, width, y_fim_header),
                        'suffix': 'header',
                        'coluna': 'FULL'
                    })

                y_inicio_corpo = y_fim_header

                # Separar marcadores
                m_esq = sorted([m for m in marcadores if m['coluna'] == 'ESQ'], key=lambda k: k['y'])
                m_dir = sorted([m for m in marcadores if m['coluna'] == 'DIR'], key=lambda k: k['y'])

                # Se NÃO existem questões na coluna da direita, assume layout linear (Pág 7)
                eh_layout_linear = (len(m_dir) == 0)

                if eh_layout_linear:
                    # --- MODO COLUNA ÚNICA (LARGURA TOTAL) ---
                    for k, m in enumerate(m_esq):
                        y_topo = m['y'] - 5

                        # Texto de apoio antes da primeira questão?
                        if k == 0 and y_topo > y_inicio_corpo + 20:
                             cortes_finais.append({
                                'rect': fitz.Rect(0, y_inicio_corpo, width, y_topo),
                                'suffix': 'apoio_linear',
                                'coluna': 'FULL'
                            })

                        if k + 1 < len(m_esq):
                            y_base = m_esq[k+1]['y'] - 5
                        else:
                            y_base = height - 30

                        # CORTA COM LARGURA TOTAL
                        cortes_finais.append({
                            'rect': fitz.Rect(0, y_topo, width, y_base),
                            'suffix': f"q{m['num']}",
                            'coluna': 'FULL'
                        })

                else:
                    # --- MODO DUAS COLUNAS ---
                    # Processa Esquerda
                    if not m_esq:
                        cortes_finais.append({
                            'rect': fitz.Rect(0, y_inicio_corpo, mid_x, height),
                            'suffix': 'col_esq_txt',
                            'coluna': 'ESQ', 'eh_q': False
                        })
                    else:
                        for k, m in enumerate(m_esq):
                            y_topo = m['y'] - 5
                            if k == 0 and y_topo > y_inicio_corpo + 20:
                                 cortes_finais.append({
                                     'rect': fitz.Rect(0, y_inicio_corpo, mid_x, y_topo),
                                     'suffix': 'col_esq_apoio',
                                     'coluna': 'ESQ', 'eh_q': False
                                 })

                            y_base = m_esq[k+1]['y'] - 5 if k + 1 < len(m_esq) else height - 30
                            cortes_finais.append({
                                'rect': fitz.Rect(0, y_topo, mid_x, y_base),
                                'suffix': f"q{m['num']}",
                                'coluna': 'ESQ', 'eh_q': True, 'num': m['num']
                            })

                    # Processa Direita
                    if not m_dir:
                        cortes_finais.append({
                            'rect': fitz.Rect(mid_x, y_inicio_corpo, width, height),
                            'suffix': 'col_dir_txt',
                            'coluna': 'DIR', 'eh_q': False
                        })
                    else:
                        for k, m in enumerate(m_dir):
                            y_topo = m['y'] - 5
                            if k == 0 and y_topo > y_inicio_corpo + 20:
                                 # Pode ser continuação ou apoio novo
                                 cortes_finais.append({
                                     'rect': fitz.Rect(mid_x, y_inicio_corpo, width, y_topo),
                                     'suffix': 'col_dir_apoio',
                                     'coluna': 'DIR', 'eh_q': False
                                 })

                            y_base = m_dir[k+1]['y'] - 5 if k + 1 < len(m_dir) else height - 30
                            cortes_finais.append({
                                'rect': fitz.Rect(mid_x, y_topo, width, y_base),
                                'suffix': f"q{m['num']}",
                                'coluna': 'DIR', 'eh_q': True, 'num': m['num']
                            })

                    # --- CORREÇÃO LÓGICA (A PONTE) ---
                    # Verifica se a Questão da esquerda continua na direita
                    if m_esq:
                        last_num = m_esq[-1]['num']
                        suffix_esq = f"q{last_num}"

                        # 1. Localiza o índice do corte da última questão da esquerda
                        idx_esq = next((i for i, c in enumerate(cortes_finais) if c['suffix'] == suffix_esq), -1)

                        # 2. Verifica se existe um bloco de texto (não questão) no topo da direita
                        idx_dir_apoio = next((i for i, c in enumerate(cortes_finais) if c['suffix'] in ['col_dir_txt', 'col_dir_apoio']), -1)

                        # Se achou a questão na esquerda E um texto solto na direita:
                        if idx_esq != -1 and idx_dir_apoio != -1:
                            # Garante ordem (Direita vem depois da Esquerda)
                            if idx_dir_apoio > idx_esq:
                                # Renomeia para criar a continuidade
                                cortes_finais[idx_esq]['suffix'] = f"q{last_num}_ini" # Parte 1
                                cortes_finais[idx_dir_apoio]['suffix'] = f"q{last_num}" # Parte 2 (Fim)

            # --- PASSO 3: EXECUTAR OS CORTES ---
            for corte in cortes_finais:
                total_fatias += 1
                r = corte['rect']
                if r.height < 5 or r.width < 5: continue

                novo_doc = fitz.open()
                novo_doc.insert_pdf(doc_fitz, from_page=i, to_page=i)

                # --- SEM MEDIABOX AQUI (Visual correto garantido) ---
                novo_pg = novo_doc[0]
                novo_pg.set_cropbox(r)

                nome_arq = f"{total_fatias:03d}_p{i+1}_{corte['suffix']}.pdf"
                caminho_completo = os.path.join(pasta_saida, nome_arq)

                novo_doc.save(caminho_completo)
                novo_doc.close()
                print(caminho_completo)

    doc_fitz.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("entrada")
    parser.add_argument("saida")
    args = parser.parse_args()

    if not os.path.exists(args.saida):
        os.makedirs(args.saida)

    analisar_e_cortar(args.entrada, args.saida)
