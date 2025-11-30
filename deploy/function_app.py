import azure.functions as func
import datetime
import json
import logging
import pandas as pd
import joblib
import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO
from dotenv import load_dotenv

app = func.FunctionApp()

@app.route(route="predict_pokemon", auth_level=func.AuthLevel.ANONYMOUS)
def predict_pokemon(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Obter o JSON do request
        req_body = req.get_json()

        # Verificar se o corpo da requisição é válido
        if req_body is None:
            return func.HttpResponse(
                "Por favor, envie um JSON no corpo da requisição",
                status_code=400
            )

        # Log para debug
        logging.info(f"Tipo do req_body: {type(req_body)}")

        # Se veio apenas um dict, transformamos em lista
        if isinstance(req_body, dict):
            req_body = [req_body]

        # Transformar em DataFrame
        df = pd.DataFrame(req_body)

        # Definir features necessárias
        required_features = ["base_total", "capture_rate", "is_legendary"]
        
        # Verificar se todas as features necessárias estão presentes
        missing = [col for col in required_features if col not in df.columns]
        if missing:
            return func.HttpResponse(
                f"JSON incompleto. Colunas faltantes: {missing}",
                status_code=400
            )

        # Configurações do Azure Blob Storage
        load_dotenv("../.env")
        connection_string = os.getenv("CONNECTION_STRING")
        model_container_name = "models"
        model_blob_name = "best_model.pkl"

        if not connection_string:
            return func.HttpResponse(
                "Connection string do Azure Storage não configurada",
                status_code=500
            )

        # Baixar modelo do Azure Blob Storage
        try:
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(
                container=model_container_name, 
                blob=model_blob_name
            )
            
            # Download do modelo
            model_bytes = blob_client.download_blob().readall()
            loaded_obj = joblib.load(BytesIO(model_bytes))
            
            model = loaded_obj["model"]
            label_encoder = loaded_obj.get("label_encoder")
            
            logging.info("Modelo carregado com sucesso do Azure Blob Storage")

        except Exception as blob_error:
            logging.error(f"Erro ao carregar modelo do Azure: {str(blob_error)}")
            return func.HttpResponse(
                f"Erro ao carregar modelo: {str(blob_error)}",
                status_code=500
            )

        # Preparar os dados para predição
        X = df[required_features]

        # Fazer predição
        preds = model.predict(X)

        # Mapeamento reverso para os valores de experiência
        growth_map_reverse = {
            0: 600000,    # Fast
            1: 800000,    # Medium Fast
            2: 1000000,   # Medium Slow
            3: 1059860,   # Medium Slow (outra variante)
            4: 1640000,   # Slow
            5: 6000000    # Fluctuating
        }

        # Converter predições para valores originais
        if label_encoder is not None:
            preds_numeric = label_encoder.inverse_transform(preds)
        else:
            preds_numeric = [growth_map_reverse.get(int(p), p) for p in preds]

        # Adicionar predições ao DataFrame
        df["Predicted_Experience_Growth"] = preds_numeric

        # Retornar resultado como JSON
        return func.HttpResponse(
            df.to_json(orient="records"),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        logging.error(f"Erro na função: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return func.HttpResponse(
            f"Erro interno do servidor: {str(e)}",
            status_code=500
        )