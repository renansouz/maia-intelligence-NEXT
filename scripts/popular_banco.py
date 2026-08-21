import random
import time
from app.core.database import db
from app.services.api_clima import buscar_coordenadas, buscar_clima_historico_intervalo
from app.services.processamento_service import calcular_indicadores, gerar_risco_probabilistico

def gerar_e_salvar():
    cidades = ["São Paulo", "Campinas", "Ribeirão Preto", "Sorocaba", "Piracicaba"]
    maquinas_por_cidade = {cid: [f"EQP-{cid[:3].upper()}-{i:02d}" for i in range(1, 11)] for cid in cidades}
    
    buffer_insercao = []
    
    print("Iniciando coleta de dados climaticos...")
    
    for cidade in cidades:
        try:
            print(f"Processando: {cidade}")
            coords = buscar_coordenadas(cidade)
            if not coords: continue
            
            time.sleep(2)
            
            historico = buscar_clima_historico_intervalo(coords["latitude"], coords["longitude"])
            if not historico: continue

            for registro in historico:
                for eq_id in maquinas_por_cidade[cidade]:
                    umid_base = random.randint(20, 100)
                    umidade_solo = random.randint(70, 100) if registro['chuva_mm'] > 20 else umid_base
                    incl_base = round(random.uniform(0, 25), 1)
                    vel_base = round(random.uniform(5, 12), 1) if incl_base > 15 else round(random.uniform(12, 25), 1)

                    telemetria = {
                        "equipamento_id": eq_id, "temperatura": registro['temperatura'], 
                        "chuva_mm": registro['chuva_mm'], "umidade_solo": umidade_solo, 
                        "velocidade_kmh": vel_base, "proximidade_agua_m": random.randint(10, 1000), 
                        "inclinacao_graus": incl_base, "tempo_uso_horas": random.randint(1, 20), 
                        "manutencao_dias": random.randint(0, 150), "cidade": cidade,
                        "data_medicao": registro['data']
                    }

                    inds = calcular_indicadores(telemetria)
                    risco = gerar_risco_probabilistico(inds)
                    buffer_insercao.append({**telemetria, **inds, "risco": risco})
            
            print(f"Sucesso: {cidade} preparada.")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"Erro ao processar {cidade}: {e}")

    if not buffer_insercao:
        print("Erro: Nenhum dado gerado. Verifique a conexao ou limite da API.")
        return

    print(f"\nPersistindo {len(buffer_insercao)} registros no Oracle...")
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM TB_RISCO_AGRICOLA_TRATADO")
        
        sql = """
        INSERT INTO TB_RISCO_AGRICOLA_TRATADO (
            EQUIPAMENTO_ID, CIDADE, DATA_MEDICAO, TEMPERATURA, CHUVA_MM, 
            UMIDADE_SOLO, VELOCIDADE_KMH, PROXIMIDADE_AGUA_M, INCLINACAO_GRAUS, 
            TEMPO_USO_HORAS, MANUTENCAO_DIAS, INDICADOR_CHUVA_ALTA, 
            INDICADOR_SOLO_UMIDO, INDICADOR_VELOCIDADE_ALTA, INDICADOR_PERTO_AGUA, 
            INDICADOR_INCLINACAO_ALTA, INDICADOR_MANUTENCAO_ATRASADA, RISCO_OPERACIONAL
        ) VALUES (
            :eq_id, :cid, TO_DATE(:dt_med, 'YYYY-MM-DD'), :temp, :chuva, 
            :umid, :vel, :prox, :incl, :t_uso, :manut, :i_chuva, :i_solo, 
            :i_vel, :i_agua, :i_incl, :i_manut, :risco
        )
        """
        
        params = [
            {
                "eq_id": d['equipamento_id'], "cid": d['cidade'], "dt_med": d['data_medicao'],
                "temp": d['temperatura'], "chuva": d['chuva_mm'], "umid": d['umidade_solo'],
                "vel": d['velocidade_kmh'], "prox": d['proximidade_agua_m'], "incl": d['inclinacao_graus'],
                "t_uso": d['tempo_uso_horas'], "manut": d['manutencao_dias'],
                "i_chuva": d['indicador_chuva_alta'], "i_solo": d['indicador_solo_umido'],
                "i_vel": d['indicador_velocidade_alta'], "i_agua": d['indicador_perto_agua'],
                "i_incl": d['indicador_inclinacao_alta'], "i_manut": d['indicador_manutencao_atrasada'],
                "risco": d['risco']
            } for d in buffer_insercao
        ]
        
        cursor.executemany(sql, params)
        conn.commit()
        print(f"Banco populado com {cursor.rowcount} registros.")

    except Exception as e:
        conn.rollback()
        print(f"Erro na persistencia: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)

if __name__ == "__main__":
    gerar_e_salvar()