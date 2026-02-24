# calcetines

Añade una imagen personalizada a un diseño de calcetín (archivo `.dat`). Usa un `.dat` base y tu imagen (p. ej. PNG); la herramienta compone la imagen al tamaño y posición elegidos y escribe un nuevo `.dat` llamado `<base>_with_<image>.dat`. También puedes convertir `.dat` ↔ `.bmp` para previsualizar diseños.

## Inicio rápido

1. **Construye** la imagen Docker (una vez):
   ```bash
   docker build -t dat2bmp .
   ```

2. **Añade tu imagen** a un diseño base. El resultado se guarda como `<base>_with_<image>.dat` en el directorio de salida.

   **Docker:**
   ```bash
   docker run --rm \
     -v "$(pwd)/dat-files:/data:ro" \
     -v "$(pwd)/images:/images:ro" \
     -v "$(pwd)/output:/output" \
     dat2bmp add_image_to_dat.py \
     "/data/02-79 y capibaras.dat" \
     /images/your_image.png \
     -o /output \
     -s 64x32
   ```

   **Local:**
   ```bash
   python add_image_to_dat.py "dat-files/02-79 y capibaras.dat" images/your_image.png -o output/ -s 64x32
   ```

3. **Previsualiza** el nuevo .dat como BMP: `python dat2bmp.py output/<base>_with_<image>.dat -o output/ -f -p` (o usa Docker con `dat2bmp.py`).

### Tamaño y posición

- **Tamaño:** `-s` acepta presets (`8x8`, `16x16`, `32x32`, `64x32`, `64x64`, `80x80`, `80x40`, `160x167`) o `WxH` personalizado. Por defecto: `64x32`.
- **Posición:** la imagen va centrada por defecto; usa `-p X,Y` para la esquina superior izquierda.
- **Redimensionado pixel-art:** usa `--nearest` para escalado en bloques.

## Convertir .dat ↔ .bmp (vista previa)

Convierte archivos `.dat` (cabecera de 48 bytes + RGB 160×167) a `.bmp` para poder verlos. Usa `-p` para generar además un `*_pattern.bmp` con más contraste y ver mejor el diseño.

## Build (Docker)

Construye la imagen antes del primer `docker run`:

```bash
docker build -t dat2bmp .
```

## Ejecutar (Docker)

Convertir .dat a .bmp:

```bash
docker run --rm -v "$(pwd)/dat-files:/data:ro" -v "$(pwd)/output:/output" dat2bmp dat2bmp.py /data -o /output
```

Para crear también los BMP de patrón visible, añade `-p`:

```bash
docker run --rm -v "$(pwd)/dat-files:/data:ro" -v "$(pwd)/output:/output" dat2bmp dat2bmp.py /data -o /output -p
```

Archivos concretos (la salida va junto a cada archivo si no usas `-o`):

```bash
docker run --rm -v "$(pwd)/dat-files:/data:ro" -v "$(pwd)/dat-files:/data" dat2bmp dat2bmp.py /data/file1.dat /data/file2.dat
```

## Uso local

**Añadir imagen al .dat:**
```bash
pip install -r requirements.txt
python add_image_to_dat.py "dat-files/base.dat" images/your_image.png -o output/ -s 64x32
```

**Convertir .dat a .bmp (vista previa):**

Para crear también los BMP de patrón visible, añade `-p`:

```bash
python dat2bmp.py dat-files/ -o output/ -p
```

Para sobrescribir archivos existentes, añade `-f`:

```bash
python dat2bmp.py dat-files/ -o output/ -f -p
```

## Opciones (dat2bmp)

- `-o, --output-dir DIR` – escribe todos los BMP en `DIR` (por defecto: mismo directorio que cada entrada)
- `-f, --force` – sobrescribir archivos BMP existentes
- `-p, --pattern` – escribe además un `*_pattern.bmp` con contraste estirado para ver el diseño (el .bmp crudo suele ser casi todo negro)
