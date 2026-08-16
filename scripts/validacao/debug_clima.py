from app.services.api_clima import buscar_coordenadas, buscar_clima_historico_intervalo

def testar():
    print("--- Teste de Conectividade Open-Meteo ---")
    
    print("\n1. Testando Geocoding (Sao Paulo)...")
    coords = buscar_coordenadas("São Paulo")
    
    if coords:
        print(f"Coordenadas obtidas: {coords}")
        
        print("\n2. Testando Archive API (Historico)...")
        clima = buscar_clima_historico_intervalo(coords["latitude"], coords["longitude"])
        
        if clima:
            print(f"Historico obtido! Total de dias: {len(clima)}")
            print(f"Exemplo do ultimo dia: {clima[-1]}")
        else:
            print("Falha ao obter historico.")
    else:
        print("Falha ao obter coordenadas.")

if __name__ == "__main__":
    testar()