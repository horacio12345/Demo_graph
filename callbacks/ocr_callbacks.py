# ./callbacks/ocr_callbacks.py
# Callbacks corregidos para guardar datos del grafo correctamente

from dash import Input, Output, State, ctx, no_update
from dash.exceptions import PreventUpdate
import dash
import base64
import os
import tempfile
from core import ocr, utils, embeddings
from openai import OpenAI

# Variable local para guardar datos del grafo
GRAPH_DATA = {
    'entities': [],
    'relations': [],
    'last_update': None
}

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

        try:
            text = ocr.extract_text(tmp_path, ocr_method=ocr_method)
            
            # Chunking semántico
            from core.utils import clean_text
            from core.ocr import chunk_text_semantic
            from dotenv import load_dotenv
            load_dotenv()
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            chunks = chunk_text_semantic(clean_text(text), OPENAI_API_KEY, max_chunk_size=1000)
            
            # Generar y guardar embeddings
            client = OpenAI(api_key=OPENAI_API_KEY)
            document_id = utils.generate_document_id(filename)
            
            embeddings_saved = 0
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                    
                try:
                    response = client.embeddings.create(
                        input=chunk,
                        model="text-embedding-3-small"
                    )
                    embedding_vector = response.data[0].embedding
                    
                    chunk_id = utils.generate_chunk_id(chunk, document_id)
                    
                    embeddings.upsert_embedding(
                        vector_id=chunk_id,
                        vector_values=embedding_vector,
                        document_id=document_id,
                        metadata={
                            "filename": filename,
                            "chunk_index": i,
                            "chunk_text": chunk[:500],
                            "ocr_method": ocr_method
                        }
                    )
                    embeddings_saved += 1
                    
                except Exception as e:
                    print(f"❌ Error procesando chunk {i}: {e}")
                    continue
            
            # ⭐ EXTRAER ENTIDADES Y RELACIONES ⭐
            from core import llm
            
            # Procesar chunks para extraer entidades
            sample_chunks = chunks[:3]  # Usar más chunks
            all_entities, all_relations = [], []
            
            for i, chunk in enumerate(sample_chunks):
                try:
                    llm_result = llm.extract_entities_relations(chunk, llm_method="openai")
                    
                    # Verificar resultado
                    if isinstance(llm_result, dict):
                        chunk_entities = llm_result.get("entities", [])
                        chunk_relations = llm_result.get("relations", [])
                        
                        # Asegurar IDs únicos agregando prefijo de chunk
                        for entity in chunk_entities:
                            if "id" in entity:
                                entity["id"] = f"c{i}_{entity['id']}"
                        
                        for relation in chunk_relations:
                            if "source_id" in relation:
                                relation["source_id"] = f"c{i}_{relation['source_id']}"
                            if "target_id" in relation:
                                relation["target_id"] = f"c{i}_{relation['target_id']}"
                        
                        all_entities.extend(chunk_entities)
                        all_relations.extend(chunk_relations)
                    else:
                        print(f"⚠️ LLM devolvió formato inesperado: {type(llm_result)}")
                        
                except Exception as e:
                    print(f"❌ Error completo extrayendo entidades del chunk {i}: {str(e)}")
                    continue
            
            # ⭐ GUARDAR EN VARIABLE LOCAL ⭐
            
            # Guardar en variable local de este módulo
            global GRAPH_DATA
            GRAPH_DATA['entities'] = all_entities
            GRAPH_DATA['relations'] = all_relations
            GRAPH_DATA['last_update'] = filename
            
            # También intentar guardar en Flask g (backup)
            try:
                from flask import g
                g.entities = all_entities
                g.relations = all_relations
                g.chunks = chunks
            except:
                pass
            
            # Limpiar archivo temporal
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            # Mensaje de éxito que activará el callback del grafo
            success_message = f"✅ Procesamiento completo! {len(chunks)} chunks, {embeddings_saved} embeddings, {len(all_entities)} entidades, {len(all_relations)} relaciones extraídas."
            
            return success_message
            
        except Exception as e:
            error_msg = f"❌ Error en procesamiento: {e}"
            print(error_msg)
            return error_msg

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
        
        try:
            
            # Hacer request para obtener headers
            import requests
            response = requests.head(url, allow_redirects=True, timeout=10)
            content_type = response.headers.get('content-type', '').lower()
            
            
            # Determinar tipo de contenido
            if 'application/pdf' in content_type:
                # Es un PDF - usar método original
                return process_pdf_url(url, ocr_method)
                
            elif 'text/html' in content_type or 'wikipedia.org' in url:
                # Es HTML - extraer texto web
                return process_html_url(url, ocr_method)
                
            else:
                # Intentar como PDF de todos modos (algunos servidores no envían headers correctos)
                return process_pdf_url(url, ocr_method)
                
        except Exception as e:
            error_msg = f"❌ Error procesando enlace: {e}"
            print(error_msg)
            return error_msg

def process_html_url(url, ocr_method):
    """
    Procesa una URL HTML extrayendo el texto.
    """
    try:
        import requests
        from bs4 import BeautifulSoup
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remover scripts, estilos, etc.
        for script in soup(["script", "style", "nav", "footer", "aside"]):
            script.decompose()
        
        # Extraer texto principal
        text = soup.get_text()
        
        # Limpiar texto
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Truncar si es muy largo
        if len(text) > 50000:  # Límite para evitar costos excesivos
            text = text[:50000] + "..."
        
        # Continuar con el procesamiento normal
        return process_extracted_text(text, url, "web_extraction")
        
    except Exception as e:
        raise Exception(f"Error procesando HTML: {e}")

def process_pdf_url(url, ocr_method):
    """
    Procesa una URL PDF usando el método original.
    """
    try:
        tmp_path = utils.get_temp_file_path(suffix=".pdf")
        import requests
        r = requests.get(url, timeout=30)
        
        if r.status_code == 200:
            with open(tmp_path, "wb") as f:
                f.write(r.content)
                
            text = ocr.extract_text(tmp_path, ocr_method=ocr_method)
            
            # Limpiar archivo temporal
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            return process_extracted_text(text, url, ocr_method)
        else:
            raise Exception(f"Error descargando PDF: status {r.status_code}")
            
    except Exception as e:
        raise Exception(f"Error procesando PDF: {e}")

def process_extracted_text(text, source, method):
    """
    Procesa texto extraído (común para HTML y PDF).
    """
    try:
        from core.utils import clean_text
        from core.ocr import chunk_text_semantic
        from dotenv import load_dotenv
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        
        cleaned_text = clean_text(text)
        chunks = chunk_text_semantic(cleaned_text, OPENAI_API_KEY, max_chunk_size=1000)
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        document_id = utils.generate_document_id(source)
        
        embeddings_saved = 0
        for i, chunk in enumerate(chunks):
            if not chunk.strip():
                continue
                
            try:
                response = client.embeddings.create(
                    input=chunk,
                    model="text-embedding-3-small"
                )
                embedding_vector = response.data[0].embedding
                
                chunk_id = utils.generate_chunk_id(chunk, document_id)
                
                embeddings.upsert_embedding(
                    vector_id=chunk_id,
                    vector_values=embedding_vector,
                    document_id=document_id,
                    metadata={
                        "source_url": source,
                        "chunk_index": i,
                        "chunk_text": chunk[:500],
                        "extraction_method": method
                    }
                )
                embeddings_saved += 1
                
            except Exception as e:
                print(f"❌ Error procesando chunk {i}: {e}")
                continue
        
        # Extraer entidades y relaciones
        from core import llm
        
        sample_chunks = chunks[:5]
        all_entities, all_relations = [], []
        
        for i, chunk in enumerate(sample_chunks):
            try:
                llm_result = llm.extract_entities_relations(chunk, llm_method="openai")
                
                if isinstance(llm_result, dict):
                    chunk_entities = llm_result.get("entities", [])
                    chunk_relations = llm_result.get("relations", [])
                    
                    # Asegurar IDs únicos
                    for entity in chunk_entities:
                        if "id" in entity:
                            entity["id"] = f"c{i}_{entity['id']}"
                    
                    for relation in chunk_relations:
                        if "source_id" in relation:
                            relation["source_id"] = f"c{i}_{relation['source_id']}"
                        if "target_id" in relation:
                            relation["target_id"] = f"c{i}_{relation['target_id']}"
                    
                    all_entities.extend(chunk_entities)
                    all_relations.extend(chunk_relations)
                    
            except Exception as e:
                print(f"❌ Error extrayendo entidades del chunk {i}: {e}")
                continue
        
        # Guardar datos en variable local
        global GRAPH_DATA
        GRAPH_DATA['entities'] = all_entities
        GRAPH_DATA['relations'] = all_relations
        GRAPH_DATA['last_update'] = source
        
        try:
            from flask import g
            g.entities = all_entities
            g.relations = all_relations
            g.chunks = chunks
        except:
            pass
        
        success_message = f"✅ URL procesada! {len(chunks)} chunks, {embeddings_saved} embeddings, {len(all_entities)} entidades, {len(all_relations)} relaciones extraídas."
        return success_message
        
    except Exception as e:
        raise Exception(f"Error en procesamiento de texto: {e}")