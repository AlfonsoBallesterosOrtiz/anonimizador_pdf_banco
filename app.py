# -*- coding: utf-8 -*-
import io
import json
import re
import unicodedata
import pdfplumber
import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="Anonimizador de Estados de Cuenta",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constantes y expresiones regulares
RE_RFC = re.compile(r"^[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}$", re.IGNORECASE)
RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")
RE_NUM_LARGO = re.compile(r"^\d{9,}$")
PALABRAS_NEUTRAS = {"DE", "DEL", "LA", "LAS", "LOS", "EL", "Y", "SA", "CV", "SAPI", "SC", "AC", "RL", "EN", "POR", "CON"}

def norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t)
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Za-z0-9&@.+_-]", "", t).upper()

def procesar_palabras_ocultar(texto_entradas: str) -> set:
    tokens = set()
    if not texto_entradas:
        return tokens
    for linea in texto_entradas.splitlines():
        for pal in linea.split():
            n = norm(pal)
            if len(n) >= 3 and n not in PALABRAS_NEUTRAS:
                tokens.add(n)
    return tokens

def enmascarar(texto: str, tokens: set, cuenta: dict) -> str:
    limpio = texto.strip()
    n = norm(limpio)
    solo_digitos = re.sub(r"[\s\-]", "", limpio)
    
    if RE_NUM_LARGO.match(solo_digitos):
        cuenta["numero_largo"] += 1
        return re.sub(r"\d", "X", texto)
    if RE_RFC.match(n):
        cuenta["rfc"] += 1
        return re.sub(r"[A-Za-zÑñ&0-9]", "X", texto)
    if RE_EMAIL.match(limpio):
        cuenta["correo"] += 1
        return "xxxx@xxxx.xxx"
    if n in tokens:
        cuenta["nombre"] += 1
        return re.sub(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]", "X", texto)
    return texto

def agrupar_lineas(palabras: list, tol: float = 3.0) -> list:
    lineas = []
    for p in sorted(palabras, key=lambda w: (round(w["top"], 1), w["x0"])):
        if lineas and abs(lineas[-1]["y"] - p["top"]) <= tol:
            lineas[-1]["palabras"].append(p)
        else:
            lineas.append({"y": p["top"], "palabras": [p]})
    for l in lineas:
        l["palabras"].sort(key=lambda w: w["x0"])
    return lineas

def linea_texto(palabras: list, ancho_car: float = 4.5) -> str:
    s = ""
    for p in palabras:
        col = int(p["x0"] / ancho_car)
        if len(s) < col:
            s += " " * (col - len(s))
        elif s:
            s += " "
        s += p["texto"]
    return s

# --- Barra lateral ---
with st.sidebar:
    st.header("⚙️ Configuración")
    max_paginas = st.slider(
        "Máximo de páginas a procesar:",
        min_value=1,
        max_value=20,
        value=3,
        help="Suficiente para perfilar la estructura del banco y optimizar tiempo de procesamiento."
    )
    
    st.subheader("Palabras o Nombres a Ocultar")
    custom_words_input = st.text_area(
        "Ingresa palabras personalizadas (una por línea):",
        placeholder="Juan\nPerez\nEmpresa SA\nMiCalle",
        height=140
    )
    
    archivo_ocultar = st.file_uploader(
        "O sube un archivo .txt con nombres/palabras:",
        type=["txt"]
    )
    
    tokens = set()
    if custom_words_input:
        tokens.update(procesar_palabras_ocultar(custom_words_input))
    if archivo_ocultar is not None:
        contenido_archivo = archivo_ocultar.read().decode("utf-8-sig", errors="ignore")
        tokens.update(procesar_palabras_ocultar(contenido_archivo))
        
    if tokens:
        st.info(f"🔍 {len(tokens)} token(s) activo(s) para ocultar.")

# --- Contenido principal ---
st.title("🔒 Anonimizador de Estados de Cuenta Bancarios")
st.markdown(
    """
    Convierte tu estado de cuenta PDF digital en coordenadas y texto plano completamente anonimizado.
    
    * **Seguridad:** Enmascara automáticamente números largos (cuentas, CLABE, tarjetas), RFCs, correos y palabras personalizadas.
    * **Conserva:** Encabezados, fechas, importes, saldos y conceptos genéricos para análisis o creación de perfiles.
    """
)

archivo_pdf = st.file_uploader("Sube el estado de cuenta bancario en PDF", type=["pdf"])

if archivo_pdf:
    with st.spinner("Procesando y enmascarando documento..."):
        cuenta = {"numero_largo": 0, "rfc": 0, "correo": 0, "nombre": 0}
        paginas = []
        total_palabras = 0
        error = False

        try:
            with pdfplumber.open(archivo_pdf) as pdf:
                n_total = len(pdf.pages)
                paginas_a_procesar = pdf.pages[:max_paginas]
                
                for i, pg in enumerate(paginas_a_procesar, start=1):
                    crudas = pg.extract_words(keep_blank_chars=False, use_text_flow=False)
                    total_palabras += len(crudas)
                    pals = [
                        {
                            "texto": enmascarar(w["text"], tokens, cuenta),
                            "x0": round(w["x0"], 1),
                            "x1": round(w["x1"], 1),
                            "top": w["top"]
                        }
                        for w in crudas
                    ]
                    lineas = agrupar_lineas(pals)
                    paginas.append({
                        "n": i,
                        "ancho": round(float(pg.width), 1),
                        "alto": round(float(pg.height), 1),
                        "lineas": [
                            {
                                "y": round(l["y"], 1),
                                "p": [[w["texto"], w["x0"], w["x1"]] for w in l["palabras"]]
                            }
                            for l in lineas
                        ]
                    })
        except Exception as e:
            st.error(f"Error al abrir o leer el PDF: {e}")
            error = True

    if not error:
        if total_palabras == 0:
            st.error("⚠️ El PDF no tiene capa de texto (parece un documento escaneado/imagen). Se requiere OCR para procesarlo.")
        else:
            st.success(f"Procesadas {len(paginas)} de {n_total} página(s) con éxito.")

            # Métricas
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Números largos", cuenta["numero_largo"])
            col2.metric("RFCs", cuenta["rfc"])
            col3.metric("Correos", cuenta["correo"])
            col4.metric("Nombres/Tokens", cuenta["nombre"])

            # Construir salidas
            json_salida = json.dumps(
                {"paginas_totales": n_total, "paginas_incluidas": len(paginas), "paginas": paginas},
                ensure_ascii=False,
                separators=(",", ":")
            )

            txt_buffer = io.StringIO()
            for pg in paginas:
                txt_buffer.write(f"===== PÁGINA {pg['n']} =====\n")
                for l in pg["lineas"]:
                    txt_buffer.write(linea_texto([{"texto": w[0], "x0": w[1]} for w in l["p"]]).rstrip() + "\n")
            txt_salida = txt_buffer.getvalue()

            # Verificación de palabras residuales
            contenido_norm = norm(txt_salida.replace("\n", " "))
            sobrevivientes = [t for t in tokens if t in contenido_norm]
            if sobrevivientes:
                st.warning(
                    f"⚠️ **Aviso:** Las siguientes palabras aún aparecen dentro de cadenas o palabras compuestas: "
                    f"`{', '.join(sorted(sobrevivientes))}`. Revisa el texto antes de compartirlo."
                )

            # Botones de descarga
            st.subheader("📥 Descargar Archivos Anonimizados")
            dcol1, dcol2 = st.columns(2)
            nombre_base = archivo_pdf.name.rsplit(".", 1)[0]
            
            dcol1.download_button(
                label="Descargar TXT alineado (.txt)",
                data=txt_salida.encode("utf-8"),
                file_name=f"{nombre_base}_anonimizado.txt",
                mime="text/plain",
                use_container_width=True
            )
            dcol2.download_button(
                label="Descargar Coordenadas JSON (.json)",
                data=json_salida.encode("utf-8"),
                file_name=f"{nombre_base}_anonimizado.json",
                mime="application/json",
                use_container_width=True
            )

            # Previsualización
            st.subheader("👁️ Vista previa del texto")
            st.text_area("Resultado estructurado:", value=txt_salida, height=350)