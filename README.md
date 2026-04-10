# calcetines

Añade una imagen personalizada a un diseño de calcetín (archivo `.dat`). Usa un `.dat` base y tu imagen (p. ej. PNG); la herramienta compone la imagen al tamaño y posición elegidos y escribe un nuevo `.dat` llamado `<base>_with_<image>.dat`. También puedes convertir `.dat` ↔ `.bmp` para previsualizar diseños.

El formato binario compartido vive en [`sock_dat_format.py`](sock_dat_format.py); el alcance del producto está en [`docs/PRD.md`](docs/PRD.md).

**Importante (Winpds):** el programa valida la cabecera del patrón (p. ej. tipo **PDS 8F**). Los `.dat` deben ser **diseños guardados desde Winpds** (o con la misma cabecera válida). Si abres un archivo solo generado para pruebas de tamaño con cabecera inventada, verás errores del tipo *«Korea-Robot is not PDS 8F Pattern»*. Coloca tus `.dat` reales en `dat-files/` y úsalos como base con `add_image_to_dat.py`.

## Inicio rápido

1. **Opcional — Docker:** si usas contenedores, construye la imagen (una vez): `docker build -t dat2bmp .` (requiere un `Dockerfile` en el repo).

2. **Añade tu imagen** a un diseño base. El resultado se guarda como `<base>_with_<image>.dat` en el directorio de salida.

   **Local:**
   ```bash
   python add_image_to_dat.py "dat-files/02-79 y capibaras.dat" images/your_image.png -o output/ -s 64x32
   ```

3. **Previsualiza** el nuevo .dat como BMP: `python dat2bmp.py output/<base>_with_<image>.dat -o output/ -f -p`

### Interfaz web (Streamlit)

Con dependencias instaladas, ejecuta Streamlit **como módulo** (no hace falta `streamlit` en el `PATH`).

**Windows (recomendado si `python` no existe o abre la Microsoft Store):**

```bash
py -m streamlit run streamlit_app.py
```

**Si `python` apunta a tu instalación real** (p. ej. Linux, macOS, o venv con `python` en PATH):

```bash
python -m streamlit run streamlit_app.py
```

En Git Bash, `streamlit` suelto suele dar `command not found`; usa siempre `py -m` o `python -m` como arriba.

Se abre el navegador: sube un `.dat` base y una imagen, ajusta tamaño/posición y descarga el `.dat` compuesto. Las vistas usan el mismo contraste que `dat2bmp -p` para ver el diseño.

### Tamaño y posición

- **Tamaño:** `-s` acepta presets (`8x8`, `16x16`, `32x32`, `64x32`, `64x64`, `80x80`, `80x40`, `160x167`) o `WxH` personalizado. Por defecto: `64x32`.
- **Posición:** la imagen va centrada por defecto; usa `-p X,Y` para la esquina superior izquierda.
- **Redimensionado pixel-art:** usa `--nearest` para escalado en bloques.

## Convertir .dat ↔ .bmp (vista previa)

Convierte archivos `.dat` (cabecera de 48 bytes + RGB 160×167) a `.bmp` para poder verlos. Usa `-p` para generar además un `*_pattern.bmp` con más contraste y ver mejor el diseño.

## Configuración en Windows (Python y venv)

1. **Instala Python** desde [python.org/downloads](https://www.python.org/downloads/) y marca *"Add python.exe to PATH"* al instalar.

2. **Crea un entorno virtual** con el launcher **`py`** si hace falta:
   ```powershell
   py -m venv venv
   ```

3. **Activa el venv:**
   - **PowerShell:** `.\venv\Scripts\Activate.ps1`
   - **Git Bash:** `source venv/Scripts/activate`

4. **Instala dependencias:** `pip install -r requirements.txt`

5. **Tests:** `pytest` (opcional: `pip install -r requirements.txt` incluye pytest).

## Uso local

**Añadir imagen al .dat:**
```bash
pip install -r requirements.txt
python add_image_to_dat.py "dat-files/base.dat" images/your_image.png -o output/ -s 64x32
```

**Convertir .dat a .bmp (vista previa):**
```bash
python dat2bmp.py dat-files/ -o output/ -f -p
```

## Opciones (dat2bmp)

- `-o, --output-dir DIR` – escribe todos los BMP en `DIR` (por defecto: mismo directorio que cada entrada)
- `-f, --force` – sobrescribir archivos BMP existentes
- `-p, --pattern` – escribe además un `*_pattern.bmp` con contraste estirado para ver el diseño (el .bmp crudo suele ser casi todo negro)
