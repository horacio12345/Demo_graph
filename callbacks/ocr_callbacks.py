# ./callbacks/ocr_callbacks.py
# Callbacks para procesar archivos subidos/enlaces y lanzar OCR+chunking+embeddings

from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash
import base64
import os
import tempfile
from core import ocr, utils, embeddings
from openai import OpenAI

def register_ocr_callbacks(app):

    @app.callback(
        Output("progress-info", "children"),
        Input("upload-data", "contents"),
        State("upload-data", "filename"),
        State("ocr-method", "value"),
        prevent_initial_call=True
    )
    def handle_uploaded_file(contents, filename, ocr_method):
        if not contents or not filename:
            raise PreventUpdate

        # Guarda archivo temporalmente
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        tmp_path = utils.get_temp_file_path(suffix=utils.get_file_extension(filename))
        with open(tmp_path, "wb") as f:
            f.write(decoded)

        # Ejecuta OCR (elige motor)
        try:
            print("🔄 Extrayendo texto...")
            text = ocr.extract_text(tmp_path, ocr_method=ocr_method)
            
            # Chunking semántico
            print("🔄 Creando chunks...")
            from core.utils import clean_text
            from core.ocr import chunk_text_semantic
            from dotenv import load_dotenv
            load_dotenv()
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            chunks = chunk_text_semantic(clean_text(text), OPENAI_API_KEY, max_chunk_size=1000)
            
            # ⭐ NUEVA PARTE: Generar y guardar embeddings
            print(f"🔄 Generando embeddings para {len(chunks)} chunks...")
            client = OpenAI(api_key=OPENAI_API_KEY)
            document_id = utils.generate_document_id(filename)
            
            embeddings_saved = 0
            for i, chunk in enumerate(chunks):
                if not chunk.strip():  # Skip empty chunks
                    continue
                    
                try:
                    # Generar embedding usando OpenAI
                    response = client.embeddings.create(
                        input=chunk,
                        model="text-embedding-ada-002"
                    )
                    embedding_vector = response.data[0].embedding
                    
                    # Generar ID único para el chunk
                    chunk_id = utils.generate_chunk_id(chunk, document_id)
                    
                    # Guardar en Pinecone
                    embeddings.upsert_embedding(
                        vector_id=chunk_id,
                        vector_values=embedding_vector,
                        document_id=document_id,
                        metadata={
                            "filename": filename,
                            "chunk_index": i,
                            "chunk_text": chunk[:500],  # Primeros 500 chars para metadata
                            "ocr_method": ocr_method
                        }
                    )
                    embeddings_saved += 1
                    
                except Exception as e:
                    print(f"❌ Error procesando chunk {i}: {e}")
                    continue
            
            # ⭐ NUEVA PARTE: Extraer entidades y relaciones
            print("🔄 Extrayendo entidades y relaciones con LLM...")
            from core import llm
            from flask import g
            
            # Usar algunos chunks para extraer entidades (no todos para evitar costos)
            sample_chunks = chunks[:3]  # Solo primeros 3 chunks
            all_entities, all_relations = [], []
            
            for chunk in sample_chunks:
                try:
                    llm_result = llm.extract_entities_relations(chunk, llm_method="openai")  # Puedes cambiar a "claude"
                    all_entities.extend(llm_result.get("entities", []))
                    all_relations.extend(llm_result.get("relations", []))
                except Exception as e:
                    print(f"❌ Error extrayendo entidades del chunk: {e}")
                    continue
            
            # Guardar en Flask g para que lo use el callback del grafo
            g.entities = all_entities
            g.relations = all_relations
            g.chunks = chunks
            
            print(f"✅ Entidades extraídas: {len(all_entities)}")
            print(f"✅ Relaciones extraídas: {len(all_relations)}")
            
            # Limpiar archivo temporal
            try:
                os.unlink(tmp_path)
            except:
                pass
                
            return f"✅ Procesamiento completo! {len(chunks)} chunks, {embeddings_saved} embeddings, {len(all_entities)} entidades, {len(all_relations)} relaciones."
            
        except Exception as e:
            return f"Error en OCR: {e}"

    @app.callback(
        Output("progress-info", "children", allow_duplicate=True),
        Input("process-url-btn", "n_clicks"),
        State("input-url", "value"),
        State("ocr-method", "value"),
        prevent_initial_call=True
    )
    def handle_url_upload(n_clicks, url, ocr_method):
        if not n_clicks or not url:
            raise PreventUpdate
        # Descarga archivo a temporal
        try:
            print("🔄 Descargando archivo...")
            tmp_path = utils.get_temp_file_path(suffix=".pdf")
            import requests
            r = requests.get(url)
            if r.status_code == 200:
                with open(tmp_path, "wb") as f:
                    f.write(r.content)
                    
                print("🔄 Extrayendo texto...")
                text = ocr.extract_text(tmp_path, ocr_method=ocr_method)
                
                print("🔄 Creando chunks...")
                from core.utils import clean_text
                from core.ocr import chunk_text_semantic
                from dotenv import load_dotenv
                load_dotenv()
                OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
                chunks = chunk_text_semantic(clean_text(text), OPENAI_API_KEY, max_chunk_size=1000)
                
                # ⭐ NUEVA PARTE: Generar y guardar embeddings
                print(f"🔄 Generando embeddings para {len(chunks)} chunks...")
                client = OpenAI(api_key=OPENAI_API_KEY)
                document_id = utils.generate_document_id(url)
                
                embeddings_saved = 0
                for i, chunk in enumerate(chunks):
                    if not chunk.strip():
                        continue
                        
                    try:
                        # Generar embedding
                        response = client.embeddings.create(
                            input=chunk,
                            model="text-embedding-ada-002"
                        )
                        embedding_vector = response.data[0].embedding
                        
                        # Generar ID único
                        chunk_id = utils.generate_chunk_id(chunk, document_id)
                        
                        # Guardar en Pinecone
                        embeddings.upsert_embedding(
                            vector_id=chunk_id,
                            vector_values=embedding_vector,
                            document_id=document_id,
                            metadata={
                                "source_url": url,
                                "chunk_index": i,
                                "chunk_text": chunk[:500],
                                "ocr_method": ocr_method
                            }
                        )
                        embeddings_saved += 1
                        
                    except Exception as e:
                        print(f"❌ Error procesando chunk {i}: {e}")
                        continue
                
                # ⭐ NUEVA PARTE: Extraer entidades y relaciones
                print("🔄 Extrayendo entidades y relaciones con LLM...")
                from core import llm
                from flask import g
                
                # Usar algunos chunks para extraer entidades
                sample_chunks = chunks[:3]  # Solo primeros 3 chunks
                all_entities, all_relations = [], []
                
                for chunk in sample_chunks:
                    try:
                        print(f"🔄 Procesando chunk: {chunk[:100]}...")  # Primeros 100 chars
                        llm_result = llm.extract_entities_relations(chunk, llm_method="openai")
                        print(f"📊 LLM devolvió: {type(llm_result)} con keys: {llm_result.keys() if isinstance(llm_result, dict) else 'No es dict'}")
                        all_entities.extend(llm_result.get("entities", []))
                        all_relations.extend(llm_result.get("relations", []))
                    except Exception as e:
                        print(f"❌ Error completo extrayendo entidades del chunk: {str(e)}")
                        print(f"❌ Tipo de error: {type(e).__name__}")
                        continue
                
                # Guardar en Flask g para que lo use el callback del grafo
                g.entities = all_entities
                g.relations = all_relations
                g.chunks = chunks
                
                print(f"✅ Entidades extraídas: {len(all_entities)}")
                print(f"✅ Relaciones extraídas: {len(all_relations)}")
                
                # Limpiar archivo temporal
                try:
                    os.unlink(tmp_path)
                except:
                    pass
                    
                return f"✅ Procesamiento completo! {len(chunks)} chunks, {embeddings_saved} embeddings, {len(all_entities)} entidades, {len(all_relations)} relaciones."
            else:
                return f"Error al descargar archivo: status {r.status_code}"
        except Exception as e:
            return f"Error procesando enlace: {e}"