"""
Servicio para extraer texto de documentos con Azure Document Intelligence
"""
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


class DocumentIntelligenceService:
    """Servicio para extraer texto de documentos con Azure Document Intelligence"""
    
    def __init__(self):
        endpoint = os.getenv("AZURE_DOC_ENDPOINT")
        key = os.getenv("AZURE_DOC_KEY")
        if not endpoint or not key:
            raise ValueError(
                f"ERROR: No se encontraron las credenciales de Document Intelligence.\n"
                f"endpoint={endpoint}\nkey={'OK' if key else None}\n"
                f"Revisa tu archivo .env"
            )
        
        self.client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    def extract_text_from_pdf(self, pdf_path):
        """
        Extrae texto de un archivo PDF
        
        Args:
            pdf_path: Ruta al archivo PDF
        
        Returns:
            dict: {
                "text": str,
                "pages": int,
                "tables": list,
                "key_value_pairs": dict
            }
        """
        try:
            with open(pdf_path, "rb") as f:
                poller = self.client.begin_analyze_document("prebuilt-read", 
                        analyze_request=f, 
                        content_type="application/pdf"
                        )

            
            result = poller.result()
            
            # Extraer texto completo
            full_text = result.content if hasattr(result, 'content') else ""
            
            # Información de páginas
            pages_count = len(result.pages) if hasattr(result, 'pages') else 0
            
            # Extraer tablas si existen
            tables = []
            if hasattr(result, 'tables') and result.tables:
                for table in result.tables:
                    table_data = {
                        "row_count": table.row_count,
                        "column_count": table.column_count,
                        "cells": []
                    }
                    for cell in table.cells:
                        table_data["cells"].append({
                            "row_index": cell.row_index,
                            "column_index": cell.column_index,
                            "content": cell.content
                        })
                    tables.append(table_data)
            
            # Extraer pares clave-valor si existen
            key_value_pairs = {}
            if hasattr(result, 'key_value_pairs') and result.key_value_pairs:
                for kv_pair in result.key_value_pairs:
                    if kv_pair.key and kv_pair.value:
                        key = kv_pair.key.content
                        value = kv_pair.value.content
                        key_value_pairs[key] = value
            
            return {
                "text": full_text,
                "pages": pages_count,
                "tables": tables,
                "key_value_pairs": key_value_pairs
            }
        
        except Exception as e:
            raise Exception(f"Error al extraer texto del PDF: {str(e)}")
    
    def extract_text_from_bytes(self, file_bytes):
        """
        Extrae texto de bytes de un archivo
        
        Args:
            file_bytes: Bytes del archivo
        
        Returns:
            dict: Mismo formato que extract_text_from_pdf
        """
        try:
            poller = self.client.begin_analyze_document(
                "prebuilt-layout",
                analyze_request=file_bytes,
                content_type="application/pdf"
            )
            
            result = poller.result()
            
            full_text = result.content if hasattr(result, 'content') else ""
            pages_count = len(result.pages) if hasattr(result, 'pages') else 0
            
            return {
                "text": full_text,
                "pages": pages_count,
                "tables": [],
                "key_value_pairs": {}
            }
        
        except Exception as e:
            raise Exception(f"Error al extraer texto: {str(e)}")
