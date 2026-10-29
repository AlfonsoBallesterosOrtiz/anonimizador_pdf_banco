# -*- coding: utf-8 -*-
import io
import json
import re
import unicodedata
import pdfplumber
import streamlit as st

# Configuración de página con onda
st.set_page_config(
    page_title="Modo Ninja: Anonimizador de Estados de Cuenta",
    page_icon="🥷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar clave de sesión para poder resetear el uploader fácilmente
if "uploader_key" not in st.session_state:
    st.session_state["uploader_key"] = 0

def reiniciar_archivo():
    st.session_state["uploader_key"] += 1
    st.rerun()

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
    st.header("🎛️ La Botonera Secreta")
    max_paginas = st.slider(
        "¿Cuántas páginas quieres pasar por la trituradora?:",
        min_value=1,
        max_value=20,
        value=3,
        help="Con 2 o 3 páginas es más que suficiente para analizar la estructura sin saturar el sistema."
    )
    
    st.subheader("🕵️‍♂️ Lista negra personal")
    st.caption("Escribe aquí nombres, apodos o empresas que no quieras que nadie vea jamás.")
    custom_words_input = st.text_area(
        "Nombres o palabras (una por línea):",
        placeholder="Don Chicho\nPerez\nMiEmpresa SA\nCalle Secreta",
        height=140
    )
    
    archivo_ocultar = st.file_uploader(
        "O suelta un archivo .txt con tu lista secreta:",
        type=["txt"]
    )
    
    tokens = set()
    if custom_words_input:
        tokens.update(procesar_palabras_ocultar(custom_words_input))
    if archivo_ocultar is not None:
        contenido_archivo = archivo_ocultar.read().decode("utf-8-sig", errors="ignore")
        tokens.update(procesar_palabras_ocultar(contenido_archivo))
        
    if tokens:
        st.success(f"🎯 ¡{len(tokens)} objetivo(s) en la mira para censurar!")

# --- Contenido principal ---
st.title("🥷 Modo Ninja: Anonimizador de PDFs Bancarios")
st.subheader("Tus secretos están a salvo: ni los hackers, ni el SAT, ni tu ex.")

# Caja destacada de privacidad
st.info(
    """
    ### 🛡️ Declaración de Paz Mental (¡100% Libre de IA!):
    * 🚫 **CERO Inteligencia Artificial:** Aquí no hay ningún ChatGPT, Skynet ni robots entrenándose con tus gastos secretos en tacos. Es puro código Python matemático y expresiones regulares directas.
    * 🔒 **CERO Bases de Datos:** Nada se guarda, nada se envía a la nube, nada queda registrado. Cuando cierras o recargas esta pestaña, todo desaparece de la memoria RAM.
    * ✨ **Tus números se vuelven misterio:** Enmascara CLABEs, números de cuenta, plásticos, RFCs y correos, dejando intactos los importes y la estructura.
    """
)

# File uploader con clave dinámica ligada al botón de borrado
archivo_pdf = st.file_uploader(
    "Arroja tu estado de cuenta PDF aquí (¡sin miedo al éxito!):",
    type=["pdf"],
    key=f"pdf_uploader_{st.session_state['uploader_key']}"
)

# Botón para borrar/expulsar el archivo
if archivo_pdf:
    col_del_1, col_del_2 = st.columns([1, 4])
    with col_del_1:
        if st.button("🗑️ Desechar PDF y limpiar", use_container_width=True):
            reiniciar_archivo()

    with st.spinner("🧙‍♂️ Pasando el marcador negro digital... ¡Abracadabra!..."):
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
            st.error(f"💥 ¡Rayos! Algo salió mal al leer el PDF: {e}")
            error = True

    if not error:
        if total_palabras == 0:
            st.error("📸 ¡Momento! Este PDF parece una foto o escaneo plano (sin capa de texto seleccionable). Necesitas un archivo con texto digital seleccionable.")
        else:
            st.balloons()
            st.success(f"🎉 ¡Misión cumplida! Procesamos {len(paginas)} de {n_total} página(s) sin dejar rastro.")

            # Tablero de trofeos / censuras
            st.markdown("#### 🏆 Marcador de datos neutralizados:")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💳 Números largos", f"{cuenta['numero_largo']} tachados")
            col2.metric("📑 RFCs", f"{cuenta['rfc']} borrados")
            col3.metric("✉️ Correos", f"{cuenta['correo']} camuflados")
            col4.metric("🎭 Nombres", f"{cuenta['nombre']} enmascarados")

            # Construir salidas
            json_salida = json.dumps(
                {"paginas_totales": n_total, "paginas_incluidas": len(paginas), "paginas": paginas},
                ensure_ascii=False,
                separators=(",", ":")
            )

            txt_buffer = io.StringIO()
            for pg in paginas:
                txt_buffer.write(f"===== 📄 PÁGINA {pg['n']} ANÓNIMA =====\n")
                for l in pg["lineas"]:
                    txt_buffer.write(linea_texto([{"texto": w[0], "x0": w[1]} for w in l["p"]]).rstrip() + "\n")
            txt_salida = txt_buffer.getvalue()

            # Verificación de palabras sospechosas que hayan sobrevivido
            contenido_norm = norm(txt_salida.replace("\n", " "))
            sobrevivientes = [t for t in tokens if t in contenido_norm]
            if sobrevivientes:
                st.warning(
                    f"👀 **Ojo de halcón:** Estas palabras todavía aparecen pegaditas dentro de otras frases: "
                    f"`{', '.join(sorted(sobrevivientes))}`. Échale un ojo a la vista previa."
                )

            # Botones de descarga
            st.subheader("🎁 Llévate tus archivos limpiecitos")
            dcol1, dcol2 = st.columns(2)
            nombre_base = archivo_pdf.name.rsplit(".", 1)[0]
            
            dcol1.download_button(
                label="📄 Descargar Texto Estructurado (.txt)",
                data=txt_salida.encode("utf-8"),
                file_name=f"{nombre_base}_anonimizado.txt",
                mime="text/plain",
                use_container_width=True
            )
            dcol2.download_button(
                label="🗺️ Descargar Coordenadas JSON (.json)",
                data=json_salida.encode("utf-8"),
                file_name=f"{nombre_base}_anonimizado.json",
                mime="application/json",
                use_container_width=True
            )

            # Previsualización en pantalla
            st.subheader("👀 Espía el resultado final")
            st.text_area("Así de irreconocible quedó tu documento:", value=txt_salida, height=350)