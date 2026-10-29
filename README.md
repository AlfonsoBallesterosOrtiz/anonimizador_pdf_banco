# 🔒 Anonimizador de Estados de Cuenta Bancarios

Aplicación web desarrollada con [Streamlit](https://streamlit.io/) que permite convertir un estado de cuenta bancario en PDF digital a texto estructurado y coordenadas JSON, enmascarando cualquier dato sensible o confidencial.

## ✨ Funcionalidades
- **Enmascaramiento automático:** Reemplaza números de cuenta, CLABE, tarjetas (9+ dígitos), RFCs y correos.
- **Ocultamiento personalizado:** Permite indicar nombres de personas, razones sociales o palabras clave a censurar.
- **Formato para perfiles bancarios:** Genera archivos `.txt` (visión humana en columnas) y `.json` (coordenadas para parsing y machine learning).

## 🚀 Ejecución en local

1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/anonimizador-pdf-banco.git](https://github.com/TU_USUARIO/anonimizador-pdf-banco.git)
   cd anonimizador-pdf-banco