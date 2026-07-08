# Cómo publicar la app de Precios Ganaderos (una sola vez, ~15 minutos)

La app queda en internet gratis y se actualiza sola todas las semanas.
No hace falta saber programar: son 5 pasos desde el navegador.

## Paso 1 – Crear la cuenta de GitHub

1. Entrá a **https://github.com/signup**
2. Poné tu email, una contraseña y un nombre de usuario (por ejemplo `diegofperez`).
   **Anotá el nombre de usuario**: va a ser parte del link de la app.
3. Confirmá el código que te llega por email.

## Paso 2 – Crear el repositorio (la carpeta del proyecto)

1. Arriba a la derecha tocá el **+** → **New repository**.
2. En "Repository name" escribí: `precios-ganaderos`
3. Dejá marcado **Public**.
4. Tocá el botón verde **Create repository**.

## Paso 3 – Subir los archivos

1. En la página que aparece, tocá el link **"uploading an existing file"**.
2. Abrí en tu PC la carpeta `precios-ganaderos` (la que extrajiste del ZIP)
   y arrastrá **todo su contenido** (todos los archivos Y la carpeta `.github`)
   al recuadro del navegador.
3. Tocá el botón verde **Commit changes** y esperá que termine.

> Si la carpeta `.github` no se subió (verificá que aparezca en la lista de
> archivos del repositorio): tocá **Add file → Create new file**, en el nombre
> escribí exactamente `.github/workflows/actualizar.yml`, pegá adentro el
> contenido del archivo `actualizar.yml` (lo podés abrir con el Bloc de notas)
> y tocá **Commit changes**.

## Paso 4 – Encender la página web

1. En el repositorio, andá a **Settings** (pestaña de arriba) → **Pages** (menú izquierdo).
2. En "Branch" elegí **main**, dejá **/ (root)** y tocá **Save**.
3. Esperá 2 minutos y recargá: arriba va a aparecer el link de tu app:
   **https://TU-USUARIO.github.io/precios-ganaderos/**
4. Abrilo y verificá que se vean los dos gráficos.

## Paso 5 – Encender el robot semanal

1. Andá a la pestaña **Actions** del repositorio.
2. Si aparece un botón verde para habilitar los workflows, tocalo.
3. A la izquierda tocá **Actualizar precios** → botón **Run workflow** → **Run workflow**.
   Eso lo prueba ahora mismo; después corre solo todos los viernes a la tarde.

## Para tu jefe (en el celular)

1. Pasale el link por WhatsApp: `https://TU-USUARIO.github.io/precios-ganaderos/`
2. Que lo abra en Chrome (Android) o Safari (iPhone).
3. Menú del navegador → **"Agregar a pantalla de inicio"**.
   Le queda el ícono verde como una app: la abre y ve los precios al día.

## ¿Cómo funciona?

- `index.html` = la app (gráficos con selector de categoría).
- `data.json` = los precios guardados (ya viene cargado con 6 meses).
- `scraper.py` + `.github/workflows/actualizar.yml` = el robot que todos los
  viernes visita elrural.com (y el sitio del MAG como respaldo) y agrega la
  semana nueva.
- Podés ver si el robot corrió bien en la pestaña **Actions**.
