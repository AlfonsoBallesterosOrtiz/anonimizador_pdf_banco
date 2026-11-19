# 🥷 Modo Ninja: estado de cuenta sin CLABE ni RFC

Convierte un estado de cuenta bancario en PDF en un texto con la CLABE, las cuentas, el RFC y los correos tapados. Los importes y los movimientos quedan intactos, listos para pegarlos en ChatGPT, Claude o Gemini, mandárselos a tu contador o usarlos para construir parsers. Hecho con Python, Streamlit y pdfplumber. Sin IA, sin base de datos.

**Probar la app:** [pon aquí el enlace a tu app]

## ¿Para qué sirve?

- Pedirle a una IA que analice tus gastos sin darle tu CLABE ni tu RFC.
- Compartir la estructura de un estado de cuenta con tu contador, con soporte o con un colega sin exponer los datos de identificación bancaria.
- Construir parsers de PDFs bancarios con la estructura y las coordenadas, sin datos reales.

## ¿Qué tapa?

- Números de 9 o más dígitos seguidos (CLABE, cuentas).
- RFC de personas físicas y morales.
- Correos electrónicos.
- Los nombres, apodos o empresas de tu lista negra personal.

## ¿Qué no hace?

- No devuelve un PDF tachado: devuelve un `.txt` (columnas, para leer) y un `.json` (palabras y coordenadas por página).
- No tapa nombres que no estén en tu lista, ni direcciones, fechas o importes.
- No lee PDFs escaneados o fotos: el PDF necesita texto seleccionable.

Revisa siempre la vista previa antes de compartir el resultado.

## Ejecutar en tu computadora (el archivo no sale de tu equipo)

```bash
git clone https://github.com/TU_USUARIO/anonimizador-pdf-banco.git
cd anonimizador-pdf-banco
pip install streamlit pdfplumber
streamlit run app.py
```

## ¿Tu banco falla?

Abre un *issue* con el nombre del banco y qué dato quedó sin tapar (sin subir tu PDF real). Cada reporte mejora la herramienta.

## Temas del repositorio

`streamlit` `pdf` `privacidad` `anonimizacion` `estado-de-cuenta` `mexico` `clabe` `rfc` `python` `pdfplumber`
