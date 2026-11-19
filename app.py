# -*- coding: utf-8 -*-
import io
import json
import re
import unicodedata
from urllib.parse import quote

import pdfplumber
import streamlit as st

# Pon aquí tus enlaces reales. Si están vacíos, los botones correspondientes no se muestran.
URL_APP = "https://liquidpaperpdf.streamlit.app/"   # ejemplo: "https://tu-app.streamlit.app"


def aplicar_estilos() -> None:
    """Inyecta CSS personalizado con paleta Persian Blue & Bright Lemon y tipografía estilo Wise."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap');

        :root {
            /* Paleta de usuario */
            --color-persian-blue: #072ac8;
            --color-dodger-blue: #1e96fc;
            --color-icy-blue: #a2d6f9;
            --color-bright-lemon: #fcf300;
            --color-school-bus: #ffc600;

            /* Superficies y contrastes seguros */
            --color-paper: #ffffff;
            --color-surface-ice: #f2f8fe;
            --color-ink-dark: #041359;
            --color-body-text: #141c3a;
            --color-muted-text: #475569;

            /* Tipografía estilo Wise */
            --font-principal: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;

            /* Geometría Wise */
            --radius-pill: 9999px;
            --radius-card: 20px;
            --radius-input: 14px;
            --shadow-pop: 0 10px 28px rgba(7, 42, 200, 0.12);
        }

        /* 1. Lienzo principal y tipografía base */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background-color: var(--color-paper) !important;
            color: var(--color-body-text) !important;
            font-family: var(--font-principal) !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1080px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 4rem !important;
        }

        /* 2. Limpieza de interfaz nativa de Streamlit */
        #MainMenu, footer {
            display: none !important;
        }
        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* 3. Tipografía jerárquica estilo Wise (Black 900 con tracking cerrado) */
        h1 {
            font-family: var(--font-principal) !important;
            font-weight: 900 !important;
            color: var(--color-ink-dark) !important;
            letter-spacing: -0.04em !important;
            line-height: 1.04 !important;
            font-size: 2.9rem !important;
            margin-bottom: 0.6rem !important;
        }

        h2, h3 {
            font-family: var(--font-principal) !important;
            font-weight: 800 !important;
            color: var(--color-persian-blue) !important;
            letter-spacing: -0.025em !important;
        }

        p, span, label, div, li {
            font-family: var(--font-principal) !important;
        }

        /* 4. Banner Hero superior / Píldora Modo Ninja */
        .ninja-badge-row {
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 0.9rem;
        }
        .ninja-pill {
            background-color: var(--color-persian-blue);
            color: var(--color-bright-lemon) !important;
            font-weight: 900;
            font-size: 12px;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            padding: 6px 14px;
            border-radius: var(--radius-pill);
            display: inline-block;
        }
        .ninja-trust-pill {
            background-color: var(--color-surface-ice);
            color: var(--color-persian-blue) !important;
            border: 1px solid var(--color-icy-blue);
            font-weight: 700;
            font-size: 12.5px;
            padding: 5px 14px;
            border-radius: var(--radius-pill);
            display: inline-block;
        }

        /* 5. Tarjeta de 3 pasos (Copy de tráfico) */
        .steps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin: 1.25rem 0 1.5rem 0;
        }
        .step-box {
            background-color: var(--color-surface-ice);
            border: 1.5px solid var(--color-icy-blue);
            border-radius: 18px;
            padding: 16px 18px;
        }
        .step-num {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 28px;
            height: 28px;
            border-radius: 9999px;
            background-color: var(--color-bright-lemon);
            color: var(--color-ink-dark) !important;
            font-weight: 900;
            font-size: 14px;
            margin-bottom: 8px;
            border: 1.5px solid var(--color-ink-dark);
        }
        .step-title {
            font-weight: 800;
            font-size: 14.5px;
            color: var(--color-ink-dark);
            margin-bottom: 3px;
        }
        .step-desc {
            font-size: 13px;
            color: var(--color-muted-text);
            line-height: 1.4;
        }

        /* 6. Sidebar (La Botonera Secreta en azul hielo suave) */
        [data-testid="stSidebar"], [data-testid="stSidebar"] > div:first-child {
            background-color: var(--color-surface-ice) !important;
            border-right: 2px solid var(--color-icy-blue) !important;
        }

        [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: var(--color-ink-dark) !important;
            font-weight: 900 !important;
        }

        /* Slider en Persian Blue / Dodger Blue */
        [data-testid="stSlider"] div[role="slider"] {
            background-color: var(--color-persian-blue) !important;
            border: 2px solid var(--color-bright-lemon) !important;
        }

        /* 7. Inputs y TextArea (Alto contraste garantizado) */
        textarea,
        [data-testid="stTextArea"] textarea,
        div[data-baseweb="textarea"],
        div[data-baseweb="base-input"] {
            background-color: var(--color-paper) !important;
            color: var(--color-ink-dark) !important;
            -webkit-text-fill-color: var(--color-ink-dark) !important;
            border-radius: var(--radius-input) !important;
        }

        [data-testid="stTextArea"] div[data-baseweb="textarea"] {
            border: 1.5px solid var(--color-dodger-blue) !important;
        }

        [data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
            border: 2px solid var(--color-persian-blue) !important;
            box-shadow: 0 0 0 3px rgba(30, 150, 252, 0.2) !important;
        }

        textarea::placeholder {
            color: var(--color-muted-text) !important;
            -webkit-text-fill-color: var(--color-muted-text) !important;
            opacity: 0.8 !important;
        }

        /* 8. File Uploader llamativo estilo Dropzone */
        [data-testid="stFileUploader"] section {
            background-color: var(--color-surface-ice) !important;
            border: 2.5px dashed var(--color-dodger-blue) !important;
            border-radius: var(--radius-card) !important;
            padding: 1.6rem !important;
            transition: all 0.2s ease !important;
        }

        [data-testid="stFileUploader"] section:hover {
            background-color: #e3f2fd !important;
            border-color: var(--color-persian-blue) !important;
        }

        [data-testid="stFileUploader"] section button {
            background-color: var(--color-bright-lemon) !important;
            color: var(--color-ink-dark) !important;
            border: 1.5px solid var(--color-ink-dark) !important;
            border-radius: var(--radius-pill) !important;
            font-weight: 800 !important;
            padding: 0.45rem 1.2rem !important;
        }

        /* 9. Botones y Download Buttons (Estilo Pill Wise con Bright Lemon & Persian Blue) */
        .stButton > button,
        .stDownloadButton > button,
        .stLinkButton > a {
            border-radius: var(--radius-pill) !important;
            background-color: var(--color-bright-lemon) !important;
            color: var(--color-ink-dark) !important;
            border: 2px solid var(--color-ink-dark) !important;
            font-family: var(--font-principal) !important;
            font-weight: 800 !important;
            font-size: 15.5px !important;
            padding: 0.65rem 1.6rem !important;
            transition: all 0.18s ease !important;
            box-shadow: 0 4px 0 var(--color-ink-dark) !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stLinkButton > a:hover {
            background-color: var(--color-school-bus) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 0 var(--color-ink-dark) !important;
        }

        .stButton > button p,
        .stDownloadButton > button p,
        .stLinkButton > a p {
            color: var(--color-ink-dark) !important;
            font-weight: 800 !important;
        }

        /* 10. Tarjetas de Métricas (Dark Card Persian Blue + acento Bright Lemon) */
        div[data-testid="stMetric"] {
            background-color: var(--color-persian-blue) !important;
            border: 2px solid var(--color-ink-dark) !important;
            border-radius: var(--radius-card) !important;
            padding: 1.2rem 1.35rem !important;
            box-shadow: var(--shadow-pop) !important;
        }

        div[data-testid="stMetricLabel"] p {
            color: var(--color-icy-blue) !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
        }

        div[data-testid="stMetricValue"] div {
            color: var(--color-bright-lemon) !important;
            font-weight: 900 !important;
            font-size: 1.9rem !important;
            letter-spacing: -0.03em !important;
        }

        /* 11. Alertas (Alto contraste garantizado) */
        div[data-testid="stAlert"],
        div[data-testid="stAlertContainer"] {
            border-radius: var(--radius-card) !important;
            padding: 1.1rem 1.35rem !important;
            border: 1.5px solid var(--color-persian-blue) !important;
            border-left: 6px solid var(--color-persian-blue) !important;
            background-color: var(--color-surface-ice) !important;
        }

        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] span,
        div[data-testid="stAlert"] strong,
        div[data-testid="stAlert"] li,
        div[data-testid="stAlert"] h3 {
            color: var(--color-ink-dark) !important;
            opacity: 1 !important;
            line-height: 1.55 !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentSuccess"]) {
            background-color: #fefce8 !important;
            border-color: var(--color-ink-dark) !important;
            border-left-color: var(--color-school-bus) !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentWarning"]) {
            background-color: #fff8db !important;
            border-color: #b45309 !important;
            border-left-color: var(--color-school-bus) !important;
        }

        div[data-testid="stAlert"]:has(div[data-testid="stAlertContentError"]) {
            background-color: #fef2f2 !important;
            border-color: #b91c1c !important;
            border-left-color: #dc2626 !important;
        }

        /* 12. Bloque de código (Prompt listo para copiar - Dark Card estilo Wise) */
        [data-testid="stCodeBlock"], pre {
            background-color: var(--color-ink-dark) !important;
            border-radius: 18px !important;
            padding: 1.25rem !important;
            border: 2px solid var(--color-dodger-blue) !important;
        }

        [data-testid="stCodeBlock"] code, pre code, pre span {
            color: var(--color-bright-lemon) !important;
            font-family: var(--font-mono) !important;
            font-size: 14px !important;
            line-height: 1.6 !important;
            background: transparent !important;
        }

        /* 13. Expanders (Preguntas frecuentes) */
        [data-testid="stExpander"] {
            background-color: var(--color-paper) !important;
            border: 1.5px solid var(--color-icy-blue) !important;
            border-radius: 16px !important;
            margin-bottom: 0.65rem !important;
            overflow: hidden !important;
        }

        [data-testid="stExpander"] summary {
            background-color: var(--color-surface-ice) !important;
            padding: 0.35rem 0.75rem !important;
        }

        [data-testid="stExpander"] summary p {
            font-weight: 800 !important;
            color: var(--color-ink-dark) !important;
            font-size: 15px !important;
        }

        /* 14. Divisores */
        hr {
            border: none !important;
            border-top: 2px solid var(--color-icy-blue) !important;
            margin: 2.2rem 0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# Configuración de página
st.set_page_config(
    page_title="Quitar CLABE y RFC del estado de cuenta | Modo Ninja",
    page_icon="🥷",
    layout="wide",
    initial_sidebar_state="expanded"
)
aplicar_estilos()

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
        "Páginas a procesar:",
        min_value=1,
        max_value=20,
        value=3,
        help="Con 2 o 3 páginas ya se ve la estructura del estado de cuenta. Más páginas tardan más."
    )

    st.subheader("🕵️‍♂️ Tu lista negra")
    st.caption("Nombres, apodos o empresas que quieres tapar. La app no sabe quién eres: si no los escribes aquí, no los tapa.")
    custom_words_input = st.text_area(
        "Nombres o palabras (una por línea):",
        placeholder="Don Chicho\nPerez\nMiEmpresa SA\nCalle Secreta",
        height=140
    )

    archivo_ocultar = st.file_uploader(
        "O sube un .txt con tu lista:",
        type=["txt"]
    )

    tokens = set()
    if custom_words_input:
        tokens.update(procesar_palabras_ocultar(custom_words_input))
    if archivo_ocultar is not None:
        contenido_archivo = archivo_ocultar.read().decode("utf-8-sig", errors="ignore")
        tokens.update(procesar_palabras_ocultar(contenido_archivo))

    if tokens:
        st.success(f"🎯 {len(tokens)} palabra(s) en la mira para tapar.")

# --- Contenido principal ---
st.markdown(
    """
    <div class="ninja-badge-row">
        <span class="ninja-pill">🥷 MODO NINJA • SIN IA</span>
        <span class="ninja-trust-pill">Gratis • Sin registro • La app no guarda tu archivo</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Tu estado de cuenta en ChatGPT, sin tu CLABE ni tu RFC")
st.subheader("Sube el PDF y descarga un texto con CLABE, cuentas, RFC y correos tapados. Los importes y los movimientos quedan intactos.")

# Bloques visuales de 3 pasos (Copy de tráfico)
st.markdown(
    """
    <div class="steps-grid">
        <div class="step-box">
            <div class="step-num">1</div>
            <div class="step-title">Sube tu PDF</div>
            <div class="step-desc">El estado de cuenta descargado de tu banca en línea (con texto seleccionable).</div>
        </div>
        <div class="step-box">
            <div class="step-num">2</div>
            <div class="step-title">Activa tu lista negra</div>
            <div class="step-desc">Escribe en la barra lateral tu nombre, apodo o empresa para enmascararlos.</div>
        </div>
        <div class="step-box">
            <div class="step-num">3</div>
            <div class="step-title">Descarga y pega en tu IA</div>
            <div class="step-desc">Obtén un .txt limpio con tus importes intactos listo para analizar gastos.</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Caja de confianza: lo que hace y lo que no hace
st.info(
    """
    ### 🛡️ Qué hace y qué no hace
    * 🚫 **Sin inteligencia artificial:** reglas fijas en Python que puedes leer en el código.
    * 🔒 **Sin base de datos:** el archivo se procesa en memoria y esta app no lo guarda.
    * ✅ **Tapa:** números de 9 o más dígitos seguidos (CLABE, cuentas), RFC, correos y las palabras de tu lista negra.
    * 👀 **No tapa:** nombres que no estén en tu lista, direcciones, fechas ni importes. Revisa la vista previa antes de compartir.
    * 📄 **No devuelve un PDF tachado:** entrega texto (`.txt`) y coordenadas (`.json`).
    """
)

# File uploader con clave dinámica ligada al botón de borrado
archivo_pdf = st.file_uploader(
    "Arrastra aquí tu estado de cuenta en PDF (con texto seleccionable):",
    type=["pdf"],
    key=f"pdf_uploader_{st.session_state['uploader_key']}"
)

# Botón para borrar/expulsar el archivo
if archivo_pdf:
    col_del_1, col_del_2 = st.columns([1, 4])
    with col_del_1:
        if st.button("🗑️ Quitar PDF y limpiar", use_container_width=True):
            reiniciar_archivo()

    with st.spinner("🧙‍♂️ Pasando el marcador negro digital..."):
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
            st.error(f"💥 No se pudo leer el PDF: {e}")
            error = True

    if not error:
        if total_palabras == 0:
            st.error("📸 Este PDF parece una foto o un escaneo (no tiene texto seleccionable). Prueba con el PDF que descargas desde la banca en línea de tu banco.")
        else:
            st.balloons()
            st.success(f"🎉 Listo. Procesamos {len(paginas)} de {n_total} página(s). Revisa la vista previa antes de compartir.")

            # Tablero de datos tapados
            st.markdown("#### 🏆 Datos tapados:")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("💳 Números largos", f"{cuenta['numero_largo']} tapados")
            col2.metric("📑 RFCs", f"{cuenta['rfc']} tapados")
            col3.metric("✉️ Correos", f"{cuenta['correo']} tapados")
            col4.metric("🎭 Nombres de tu lista", f"{cuenta['nombre']} tapados")

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
                    f"👀 **Ojo:** estas palabras todavía aparecen dentro de otras frases: "
                    f"`{', '.join(sorted(sobrevivientes))}`. Revisa la vista previa."
                )

            # Botones de descarga
            st.subheader("🎁 Descarga tus archivos limpios")
            dcol1, dcol2 = st.columns(2)
            nombre_base = archivo_pdf.name.rsplit(".", 1)[0]

            dcol1.download_button(
                label="📄 Descargar texto (.txt) para pegar en tu IA",
                data=txt_salida.encode("utf-8"),
                file_name=f"{nombre_base}_anonimizado.txt",
                mime="text/plain",
                use_container_width=True
            )
            dcol2.download_button(
                label="🗺️ Descargar coordenadas (.json) para desarrolladores",
                data=json_salida.encode("utf-8"),
                file_name=f"{nombre_base}_anonimizado.json",
                mime="application/json",
                use_container_width=True
            )

            # Siguiente paso: que el usuario saque valor y vuelva
            st.subheader("🤖 Siguiente paso: pégalo en tu IA")
            st.caption("Abre el .txt, copia el contenido y pégalo en ChatGPT, Claude o Gemini con este mensaje:")
            st.code(
                "Estos son los movimientos de mi estado de cuenta, con los datos personales ya tapados. "
                "Agrúpalos por categoría, dime en qué gasto más y señala los cargos que se repiten.",
                language=None
            )

            # Previsualización en pantalla
            st.subheader("👀 Vista previa del resultado")
            st.text_area("Así quedó tu documento. Revísalo antes de compartirlo:", value=txt_salida, height=350)

            # Bucle de tráfico: compartir y reportar bancos
            st.subheader("🙌 ¿Te sirvió?")
            st.write("Mándasela a un colega que sube estados de cuenta a una IA. Y si tu banco falla, avísanos: cada reporte mejora la herramienta.")
            bcol1, bcol2 = st.columns(2)
            if URL_APP:
                texto_compartir = (
                    "Antes de subir un estado de cuenta a ChatGPT, quítale la CLABE, el RFC y el correo. "
                    f"Esta herramienta es gratis y no usa IA: {URL_APP}"
                )
                bcol1.link_button(
                    "📲 Compartir por WhatsApp",
                    f"https://wa.me/?text={quote(texto_compartir)}",
                    use_container_width=True
                )
            

# --- Preguntas frecuentes (texto visible para quien llega sin PDF) ---
st.divider()
st.subheader("❓ Preguntas frecuentes")

with st.expander("¿Puedo subir mi estado de cuenta a ChatGPT, Claude o Gemini?"):
    st.write("Puedes, pero conviene quitarle antes la CLABE, el RFC y el correo. Esta herramienta los tapa y deja los importes y las fechas para que la IA haga el análisis.")
with st.expander("¿Es seguro subir mi PDF a esta herramienta?"):
    st.write("La app procesa el archivo en memoria y no lo guarda, pero el PDF sí viaja al servidor donde está publicada. ")
with st.expander("¿Me devuelve un PDF con tachones?"):
    st.write("No. Devuelve un texto (.txt) y un archivo de coordenadas (.json) con los datos sensibles tapados. Si necesitas tachar el PDF original, esta herramienta no lo hace.")
with st.expander("¿Qué datos tapa y cuáles no?"):
    st.write("Tapa números de 9 o más dígitos seguidos (CLABE, cuentas), RFC, correos y las palabras de tu lista negra. No tapa nombres que no estén en tu lista, direcciones, fechas ni importes. Revisa siempre la vista previa.")
with st.expander("¿Usa inteligencia artificial?"):
    st.write("No. Son reglas fijas en Python y expresiones regulares, y puedes leerlas en el código.")
with st.expander("¿Funciona con mi banco?"):
    st.write("Funciona con cualquier PDF que tenga texto seleccionable. Si el PDF es un escaneo o una foto, no se puede leer. Si tu banco falla, repórtalo y lo revisamos.")
with st.expander("¿Sirve para contadores y despachos?"):
    st.write("Sí. Permite compartir la estructura de un estado de cuenta de un cliente con colegas, soporte o desarrolladores sin exponer sus datos de identificación bancaria.")

st.caption("Esta herramienta procesa tu archivo en memoria y no lo guarda. No todos los datos sensibles se detectan automáticamente: revisa el resultado antes de compartirlo.")