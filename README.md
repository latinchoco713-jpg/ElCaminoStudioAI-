# El Camino Studio AI

Una aplicación de música y video con IA usando Streamlit.

## Qué hace

- Genera música y letras simuladas
- Crea videos con clips de video y música
- Sincroniza video con los beats del audio
- Analiza la emoción del audio y selecciona un estilo de video automáticamente
- **Genera imágenes con IA para usar en videos**
- **Integración con OpenAI GPT-4 y DALL-E (opcional)**
- Interfaz web simple con Streamlit

## Requisitos

- Python 3.8 o superior
- `pip` instalado

## Instalación

1. Abre PowerShell en `C:\Users\latin\OneDrive\Desktop\ElCaminoStudioAI`
2. Instala dependencias:

   ```powershell
   pip install -r requirements.txt
   ```

3. Ejecuta la app:

   ```powershell
   streamlit run app.py
   ```

   O usa el script de Windows:

   ```powershell
   .\start_app.bat
   ```

4. Abre el navegador en:

   `http://localhost:8501`

## Estructura

- `app.py`: Interfaz Streamlit y flujo principal
- `backend/ai_brain.py`: Generación de música y letras
- `backend/video_engine.py`: Generación de video y sincronización con beats
- `backend/__init__.py`: Inicializador del paquete backend
- `assets/music/`: Música cargada
- `assets/clips/`: Clips de video cargados
- `output/`: Videos generados
- `requirements.txt`: Dependencias Python
- `start_app.bat`: Script rápido para iniciar la app

## Uso básico

1. Abre la app en el navegador.
2. **Configura OpenAI API (opcional)**: En la barra lateral, ingresa tu API key de OpenAI para usar GPT-4 y DALL-E.
3. Sube un archivo de música (`.wav` o `.mp3`).
4. Sube uno o más clips de video (`.mp4`).
5. Activa o desactiva la sincronización por beats.
6. Haz clic en `Crear Video`.
7. El video generado se guardará en `output/` y se mostrará en la app.

## OpenAI Integration

Para usar las funciones avanzadas de IA:

1. Obtén una API key de OpenAI en https://platform.openai.com/api-keys
2. En la app, ve a la barra lateral y pega tu API key
3. Ahora podrás:
   - Generar letras más creativas con GPT-4
   - Crear imágenes de alta calidad con DALL-E 3
   - Mejor calidad general en el contenido generado

Sin API key, la app usa generación local simulada.

## Notas

- Si ya instalaste `librosa`, `moviepy`, `numpy` y `streamlit`, todo está listo.
- `assets/` y `output/` se crean automáticamente si no existen.
- Si quieres más estilos visuales o efectos, puedo agregarlos enseguida.