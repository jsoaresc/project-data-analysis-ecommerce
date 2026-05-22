import os
import pandas as pd
import kagglehub
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("A variável DATABASE_URL não foi encontrada no arquivo .env")

engine = create_engine(db_url)

def run_etl():
    print("Baixando dataset da Olist via Kagglehub")
    dataset_path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    print(f"Download concluído. Arquivos salvos em: {dataset_path}")

    csv_files = [f for f in os.listdir(dataset_path) if f.endswith('.csv')]

    for file_name in csv_files:
        table_name = file_name.replace('.csv', '') # Ex: olist_orders_dataset vira nome da tabela
        file_path = os.path.join(dataset_path, file_name)
        
        print(f"Processando {file_name}")
        
        try:
            df = pd.read_csv(file_path)
            
            # Envia para o Supabase
            df.to_sql(
                name=table_name, 
                con=engine, 
                if_exists='replace', 
                index=False,
                chunksize=10000 
            )
            print(f"Tabela '{table_name}' carregada com {len(df)} linhas.")
            
        except Exception as e:
            print(f"Erro ao processar {file_name}: {e}")

    print("\nPipeline ETL finalizado. Os dados estão no Supabase.")

if __name__ == "__main__":
    run_etl()