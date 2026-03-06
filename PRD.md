# Documento de Requisitos del Producto (PRD)
## Anki MCP Server - Sistema Conversacional Inteligente

**Versión:** 1.0
**Fecha:** Febrero 2025
**Idioma:** Español
**Estado:** En Diseño

---

## 1. Visión y Objetivo

### Problema Actual

El servidor MCP para Anki es actualmente muy limitado:
- Solo 2 herramientas: `create_card` (con modelo Basic hardcodeado) y `get_decks`
- No soporta tipos de tarjetas personalizadas
- No tiene capacidad para crear decks con estilos específicos
- Sin inteligencia conversacional para guiar al usuario durante el flujo de creación

### Visión

Transformar el Anki MCP Server en un **asistente conversacional inteligente** que permita:

1. **Crear decks personalizados** con estilos ricos (Duolingo, tema oscuro, código, etc.) con HTML/CSS avanzado
2. **Soportar múltiples tipos de tarjetas** (Basic, Cloze, plantillas HTML personalizadas con medios)
3. **Actuar como inteligencia asistente** durante sesiones de estudio:
   - Hacer preguntas aclaratorias sobre el destino de las tarjetas
   - Sugerir tipos de plantilla según el contenido
   - Crear tarjetas en lotes desde el contexto de la conversación
4. **Gestión completa de ciclo de vida** de decks y tarjetas (CRUD completo)
5. **Sincronización con AnkiWeb** para acceso multiplataforma

### Objetivo Específico

Proporcionar una interfaz MCP que permita a usuarios crear, gestionar y enriquecer sus decks de Anki a través de conversación natural, sin necesidad de interactuar directamente con la interfaz de Anki.

---

## 2. Casos de Uso Principales

### Caso 1: Crear Deck Personalizado con Estilo
**Actor:** Usuario de estudiante/profesional
**Escenario:** El usuario quiere crear un deck nuevo con temática específica y estilo visual atractivo

```
Usuario: "Crea un deck para programación con estilo Duolingo,
          quiero que tenga colores verdes, fuente redondeada y animaciones"

MCP: "Perfecto. Voy a crear un nuevo deck con template Duolingo.
      ¿Cuál será el nombre del deck?"

Usuario: "Advanced Python Patterns"

MCP: "¿Quieres agregar descripción, tags por defecto, o configuración
      especial de estudio? (ej: estudiar 20 minutos diarios)"

Usuario: "Descripción: 'Patrones avanzados de Python 3.10+',
          tags: ['python', 'programación']"

MCP: "Deck creado exitosamente. Ahora puedo ayudarte a crear tarjetas.
      ¿Cuántas tarjetas quieres crear? ¿Tienes el contenido listo?"
```

### Caso 2: Captura Rápida Post-Estudio
**Actor:** Estudiante que acaba de leer/estudiar un tema
**Escenario:** El usuario quiere crear múltiples tarjetas rápidamente desde lo que estudió

```
Usuario: "Crea 8 tarjetas sobre caché en arquitectura de software.
          Usa la estructura: pregunta → respuesta corta"

MCP: "Entendido. Voy a crear 8 tarjetas sobre caché.
      ¿En qué deck las guardo? Mis decks actuales son:
      - [1] Advanced Python Patterns
      - [2] System Design
      - [3] Nuevo deck

      ¿Cuál prefieres? ¿O creo uno nuevo?"

Usuario: "System Design"

MCP: "¿Quieres que genere las 8 preguntas automáticamente sobre caché,
      o prefieres proporcionar preguntas específicas?"

Usuario: "Genera automáticamente, pero enfócate en:
          - Cache invalidation
          - Eviction policies
          - Distributed cache"

MCP: "Creando 8 tarjetas... [resultado con las tarjetas creadas]
      Las tarjetas están listas. ¿Quieres revisar alguna antes de guardar?"
```

### Caso 3: Gestión de Decks Existentes
**Actor:** Usuario gestor de contenido
**Escenario:** El usuario quiere buscar, editar o eliminar tarjetas en decks existentes

```
Usuario: "Busca todas mis tarjetas que contengan 'SQL'
          en los decks de programación"

MCP: "Encontré 12 tarjetas con 'SQL':
      - Database Transactions [SQL Fundamentals]
      - Query Optimization [SQL Advanced]
      - Indexes Explained [Database Design]
      ... (mostrando preview de 5, listando todas)"

Usuario: "Edita la tarjeta 'Query Optimization':
          agrega un ejemplo de ejecución de plan"

MCP: "Tarjeta actualizada. Cambios guardados en 'SQL Advanced'."

Usuario: "Elimina todas las tarjetas del deck 'old-learn-stuff'"

MCP: "Advertencia: vas a eliminar 34 tarjetas del deck 'old-learn-stuff'.
      ¿Estás seguro? [Sí / No / Respaldar y eliminar]"
```

### Caso 4: Crear Deck Completamente Custom (Máximo Control)
**Actor:** Usuario avanzado que quiere control total sobre la estructura y aspecto visual de su deck
**Escenario:** El usuario quiere definir exactamente la estructura y aspecto visual de su deck, sin limitarse a templates predefinidos.

```
Usuario: "Quiero crear un deck con máximo control. Necesito 6 campos: front, back, image, sound, example, tips.
          Quiero un tema oscuro calmante con animaciones suaves.
          Será para un flujo de aprendizaje específico: memorización tipo rellena-el-espacio."

MCP: "Perfecto. Voy a crear un deck con modelo completamente personalizado con 6 campos.
      ¿Cuál es el nombre del deck?"

Usuario: "Advanced Learning Deck"

MCP: "Creando el modelo personalizado con campos: Front, Back, Image, Sound, Example, Tips.
      Para memorización tipo 'rellena el espacio', usaré tarjetas Cloze.

      ¿Cuál es tu preferencia de estilo? Puedo:
      - Usar uno de los templates predefinidos (Default, Duolingo, Dark Mode, Code)
      - Crear un estilo completamente personalizado (especifica colores, animaciones, layout)

      Por ejemplo, si dices 'dark profundo, fondo azul, verde menta, animaciones fade',
      yo creo el CSS exacto que necesitas."

Usuario: "Crea un estilo personalizado: fondo azul profundo (#0d1117), acento verde menta (#7ee8a2),
          texto claro, animaciones fade suave. Tipo Cloze para el modelo."

MCP: "Perfecto. Generando CSS personalizado...

      Deck y modelo creados exitosamente.
      Configuración:
      - Nombre: Advanced Learning Deck
      - Campos: Front, Back, Image, Sound, Example, Tips
      - Tipo: Cloze (rellena espacios)
      - Estilo: Custom CSS (fondo #0d1117, acento #7ee8a2, animaciones fade)

      ¿Empezamos a agregar tarjetas?"

Usuario: "Sí, crea 10 tarjetas"

MCP: "¿Quieres que genere las tarjetas automáticamente con contenido de ejemplo,
      o prefieres proporcionar el contenido específico?"

Usuario: "Genera automáticamente con contenido de ejemplo."

MCP: "Creando 10 tarjetas Cloze... [proceso] Listo. Las 10 tarjetas están en el deck.
      Cada tarjeta usa tu CSS personalizado y muestra animaciones fade al revelar contenido.
      ¿Quieres ajustar el CSS, agregar más tarjetas, o cambiar la estructura?"
```

**Nota Técnica sobre Máximo Control:** Con el modo Custom, defines exactamente:
- **Cantidad y nombre de campos:** Front, Back, Image, Sound, Example, Tips, o cualquier combinación
- **CSS completo:** Colores, animaciones, layout, tipografía, sin limitaciones de template predefinido
- **Tipo de tarjeta:** Basic, Cloze, o ambos como templates distintos
- **HTML de templates:** Referencias dinámicas a campos con `{{Campo}}`

El MCP interpreta tu descripción en lenguaje natural y construye el CSS/HTML automáticamente.

---

## 3. Flujos de Usuario (Conversational Flows)

### Flujo A: Crear Deck + Tarjetas Personalizadas

```mermaid
Entrada: "Crea 10 tarjetas sobre caché con estilo oscuro"
    ↓
¿Deck existe? → No → Crear nuevo
    ↓
¿Cuál es el nombre del deck?
    ↓
[Recibe: "Advanced Caching"]
    ↓
¿Template de estilo?
  - Default
  - Duolingo
  - Dark Mode ← Selecciona
  - Code Style
  - Custom
    ↓
¿Tipo de tarjeta?
  - Basic (Pregunta/Respuesta)
  - Cloze (Rellena espacios)
  - Custom HTML
    ↓
Generar/Recibir contenido de 10 tarjetas
    ↓
Crear tarjetas en batch
    ↓
Sincronizar
    ↓
Éxito: "10 tarjetas creadas en 'Advanced Caching' con tema Dark Mode"
```

### Flujo B: Búsqueda y Edición

```mermaid
Entrada: "Busca 'HTTP' en mis decks"
    ↓
Ejecutar búsqueda con AnkiConnect
    ↓
Retornar resultados agrupados por deck
    ↓
Usuario selecciona tarjeta
    ↓
Mostrar contenido actual
    ↓
¿Editar?
  - Sí → Recibir cambios → Actualizar → Confirmar
  - No → Listo
```

### Flujo C: Operación Destructiva (Eliminación)

```mermaid
Entrada: "Elimina el deck 'temporal'"
    ↓
Contar tarjetas en deck (N tarjetas)
    ↓
Advertencia: "¿Seguro eliminar 'temporal' (N tarjetas)?"
    ↓
Usuario confirma
    ↓
¿Deseas respaldar primero?
  - Sí → Exportar estado → Eliminar → Confirmar
  - No → Eliminar directo → Confirmar
    ↓
Éxito
```

---

## 4. Requisitos Funcionales

### 4.1 Gestión de Decks

| Funcionalidad | Descripción | Prioridad |
|---|---|---|
| **Listar Decks** | Obtener lista de todos los decks disponibles con estadísticas (total tarjetas, tarjetas nuevas, pendientes de revisar) | P0 |
| **Crear Deck** | Crear nuevo deck con nombre, descripción, tags por defecto y configuración de estudio | P0 |
| **Eliminar Deck** | Eliminar deck con confirmación y opción de respaldar primero | P1 |
| **Renombrar Deck** | Cambiar nombre de deck existente | P2 |
| **Obtener Estadísticas** | Retornar estadísticas del deck (total, nuevas, en revisión, tasa de aprobación) | P1 |

### 4.2 Tipos de Tarjetas Soportadas

| Tipo | Estructura | Casos de Uso | Prioridad |
|---|---|---|---|
| **Basic** | Front / Back | Preguntas simples, definiciones, traducciones | P0 |
| **Cloze** | Texto con [espacios] | Rellena espacios en blanco, completaciones | P1 |
| **Custom HTML** | HTML personalizado, CSS, campos dinámicos | Contenido complejo, tabla de datos, código | P2 |
| **Con Medios** | Front/Back + imagen/audio | Pronunciación, identificación visual | P2 |

### 4.3 Plantillas de Estilo

| Template | Características | Caso de Uso | Prioridad |
|---|---|---|---|
| **Default** | Anki estándar, limpio y minimalista | General | P0 |
| **Duolingo-style** | Colores verdes (#1f8722), fuente redondeada (Poppins), animaciones suaves | Aprendizaje de idiomas, gamificación | P1 |
| **Dark Mode** | Fondo oscuro (#1a1a1a), texto claro, contraste alto | Estudio nocturno, reducir fatiga visual | P1 |
| **Code Style** | Monoespaciado, syntax highlighting (Prism.js), tema dracula | Programación, algoritmos | P2 |
| **Custom Completo** | Usuario define: cantidad de campos, nombres, CSS completo, HTML de templates, tipo de tarjeta, animaciones | Cualquier caso de uso específico | P1 |

### 4.4 Inteligencia Conversacional

| Capacidad | Descripción | Prioridad |
|---|---|---|
| **Preguntas Aclaratorias** | MCP pregunta deck destino, template, tipo de tarjeta antes de crear | P0 |
| **Sugerencias Inteligentes** | Sugerir template según contenido (ej: si tiene código → Code Style) | P1 |
| **Confirmación de Operaciones Destructivas** | Confirmar antes de eliminar, mostrar advertencias | P0 |
| **Creación de Tarjetas en Batch** | Crear múltiples tarjetas en una sola llamada desde contexto conversacional | P0 |
| **Extracción de Contenido** | Parsear contenido del usuario para extraer preguntas/respuestas automáticamente | P2 |

### 4.5 Operaciones CRUD Completas

| Operación | Descripción | Prioridad |
|---|---|---|
| **Crear (Create)** | Crear tarjeta(s) con validación de campos | P0 |
| **Buscar (Read)** | Buscar tarjetas por texto, deck, tags, fecha de creación | P1 |
| **Editar (Update)** | Modificar campos de tarjeta existente, cambiar deck | P1 |
| **Eliminar (Delete)** | Eliminar una o múltiples tarjetas con confirmación | P1 |
| **Sincronizar (Sync)** | Sincronizar con AnkiWeb para acceso multiplataforma | P2 |

### 4.6 Capacidades de Customización

En modo **Custom Completo**, el usuario puede personalizar:

| Dimensión | Lo que el usuario puede definir |
|---|---|
| **Campos** | Número y nombre de campos (ej: Front, Back, Image, Sound, Example, Tips, o cualquier otro) |
| **CSS** | Cualquier CSS válido: colores, tipografía, layout, `@keyframes`, transiciones, background-images |
| **HTML** | Template de frente y dorso con referencias `{{Campo}}`, condicionales, bucles |
| **Tipo de Tarjeta** | Basic, Cloze, o ambos como templates distintos en el mismo modelo |
| **Medios** | Soporta `<img>`, `[sound:]`, renderizado condicional `{{#Campo}}...{{/Campo}}` |
| **Animaciones** | Transiciones CSS suaves, `@keyframes` personalizadas, reveal animations |

---

## 5. Arquitectura Técnica

### 5.1 Nuevas Herramientas MCP a Implementar

| Herramienta | Descripción | Parámetros | Retorno |
|---|---|---|---|
| **`create_deck`** | Crear nuevo deck con configuración | `name`: str, `description?`: str, `tags?`: list, `config?`: dict | `{success: bool, deck_id: str, message: str}` |
| **`delete_deck`** | Eliminar deck existente | `deck_id`: str, `confirm`: bool, `backup?`: bool | `{success: bool, message: str}` |
| **`list_decks`** | Listar todos los decks con estadísticas | Ninguno | `[{name: str, id: str, total: int, new: int, due: int}]` |
| **`create_note_type`** | Crear modelo/template personalizado con CSS/HTML | `name`: str, `fields`: list, `template`: str, `css`: str, `style`: str | `{success: bool, model_id: str}` |
| **`get_note_types`** | Listar modelos disponibles (built-in + custom) | Ninguno | `[{name: str, id: str, fields: list}]` |
| **`create_card`** | Crear una tarjeta (compatibilidad hacia atrás) | `deck_name`: str, `front`: str, `back`: str, `tags?`: list | `{success: bool, card_id: str}` |
| **`create_card_batch`** | Crear múltiples tarjetas en una llamada | `deck_name`: str, `cards`: list, `model_name?`: str | `{success: bool, created: int, ids: list}` |
| **`create_card_custom`** | Crear tarjeta con modelo personalizado y campos dinámicos | `deck_name`: str, `model_name`: str, `fields`: dict, `tags?`: list | `{success: bool, card_id: str}` |
| **`search_cards`** | Buscar tarjetas con query de Anki | `query`: str, `deck?`: str | `[{id: str, front: str, back: str, deck: str, tags: list}]` |
| **`update_card`** | Editar campos de tarjeta existente | `card_id`: str, `fields`: dict | `{success: bool, message: str}` |
| **`delete_cards`** | Eliminar una o múltiples tarjetas | `card_ids`: list, `confirm`: bool | `{success: bool, deleted: int, message: str}` |
| **`add_media`** | Subir/agregar imagen o audio para usar en tarjetas | `filename`: str, `data`: str (base64), `media_type`: str | `{success: bool, media_path: str}` |
| **`sync_anki`** | Sincronizar con AnkiWeb | Ninguno | `{success: bool, last_sync: str, message: str}` |
| **`get_deck_stats`** | Obtener estadísticas detalladas de un deck | `deck_name`: str | `{total: int, new: int, due: int, learning: int, suspended: int, buried: int}` |
| **`update_note_type_style`** | Actualizar CSS de modelo existente | `model_name`: str, `css`: str | `{success: bool, message: str}` |
| **`update_note_type_template`** | Actualizar HTML de templates de un modelo | `model_name`: str, `templates`: dict | `{success: bool, message: str}` |

### 5.2 Plantillas CSS/HTML Predefinidas

#### Template 1: Default (Anki Estándar)
```css
/* Minimal, clean Anki default style */
.card {
  font-family: Arial, sans-serif;
  font-size: 20px;
  text-align: center;
  color: #000;
  background-color: #fff;
}
```

#### Template 2: Duolingo-Style
```css
/* Vibrant, modern Duolingo-inspired design */
.card {
  font-family: 'Poppins', sans-serif;
  font-size: 18px;
  background: linear-gradient(135deg, #1f8722 0%, #28a745 100%);
  color: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  animation: slideIn 0.3s ease-in-out;
}

.question {
  font-weight: bold;
  margin-bottom: 16px;
  font-size: 22px;
}

.answer {
  margin-top: 12px;
  font-size: 18px;
  animation: fadeIn 0.5s ease-in;
}

@keyframes slideIn {
  from { transform: translateY(10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

#### Template 3: Dark Mode
```css
/* High contrast dark theme for night studying */
.card {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  font-size: 18px;
  background-color: #1a1a1a;
  color: #e0e0e0;
  padding: 20px;
  border-left: 4px solid #00bcd4;
}

.question {
  color: #00bcd4;
  font-weight: 600;
  font-size: 20px;
  margin-bottom: 16px;
}

.answer {
  color: #e0e0e0;
  margin-top: 12px;
  line-height: 1.6;
}

code {
  background-color: #2a2a2a;
  color: #76ff03;
  padding: 2px 6px;
  border-radius: 3px;
}
```

#### Template 4: Code-Style (Programación)
```css
/* Syntax highlighting for code-related content */
.card {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 16px;
  background-color: #282c34;
  color: #abb2bf;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
}

.question {
  color: #61dafb;
  font-weight: bold;
  margin-bottom: 12px;
}

.answer {
  color: #98c379;
  margin-top: 12px;
  white-space: pre-wrap;
}

code {
  color: #e06c75;
}

/* Dracula-inspired syntax highlighting */
.keyword { color: #f92672; }
.string { color: #a6e22e; }
.function { color: #66d9ef; }
.comment { color: #75715e; }
```

#### Custom Template — Cómo Funciona

En modo **Custom**, el usuario describe el estilo deseado en **lenguaje natural**, y el MCP genera el CSS/HTML exacto.

**Ejemplo: Usuario describe un estilo**
```
"Dark mode, fondo azul profundo, acento verde menta, animaciones fade suave"
```

**Lo que el MCP genera (CSS automático):**
```css
/* CSS generado dinámicamente por el MCP */
.card {
  font-family: 'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 18px;
  background-color: #0d1117;  /* Azul oscuro profundo */
  color: #c9d1d9;            /* Gris claro confortable */
  padding: 24px;
  border-radius: 12px;
  max-width: 600px;
  margin: 0 auto;
  animation: fadeIn 0.4s ease-in-out;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.question {
  color: #7ee8a2;            /* Verde menta */
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.answer {
  color: #c9d1d9;
  margin-top: 16px;
  line-height: 1.6;
  animation: fadeIn 0.5s ease-in-out 0.2s backwards;
}

/* Animaciones suaves */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**Capacidades CSS Soportadas:**
- Colores: `color`, `background-color`, `background-image`, `border-color`
- Tipografía: `font-family`, `font-size`, `font-weight`, `line-height`
- Layout: `padding`, `margin`, `max-width`, `border-radius`
- Animaciones: `@keyframes`, `animation`, `transition`
- Variables CSS: `--variable-name` para reutilización
- Media queries: `@media (prefers-color-scheme: dark)` para respuesta a preferencias del sistema
- Efectos: `box-shadow`, `filter`, `transform`, `opacity`

**Limitaciones de Seguridad:**
- No se permite `javascript:` en ningún contexto
- No se permite `<script>` tags en HTML
- No se permite `eval()` o código ejecutable
- Sólo CSS y HTML estáticos/declarativos

**HTML Custom:**
El usuario puede definir templates con campos dinámicos:
```html
<div class="card">
  <h2 class="question">{{Front}}</h2>
  <div class="answer">
    {{Back}}
    {{#Example}}<p class="example">{{Example}}</p>{{/Example}}
  </div>
</div>
```

### 5.3 Configuración y Dependencias

**Dependencias existentes:**
- `mcp`: Motor MCP FastMCP
- `httpx`: Cliente HTTP para AnkiConnect

**Nuevas dependencias sugeridas:**
- `pydantic`: Validación de esquemas
- `jinja2`: Renderización de templates (opcional para templates dinámicos)
- `aiofiles`: I/O asincrónico para medios

**Configuración:**
```python
# config.py
ANKI_CONNECT_URL = "http://localhost:8765"
ANKI_CONNECT_VERSION = 6

# Configuración de medios
MEDIA_UPLOAD_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MEDIA_TYPES = ["image/jpeg", "image/png", "audio/mpeg", "audio/wav"]

# Templates built-in
BUILTIN_TEMPLATES = {
    "default": {...},
    "duolingo": {...},
    "dark": {...},
    "code": {...}
}
```

### 5.4 Validación y Manejo de Errores

**Validaciones clave:**
1. Validar conexión a AnkiConnect antes de operaciones
2. Validar que deck existe antes de crear tarjetas
3. Validar que campos requeridos están presentes en tarjetas
4. Validar CSS personalizado (no ejecutar JavaScript)
5. Validar tamaño de media antes de subida

**Errores esperados:**
- `AnkiConnectError`: AnkiConnect no disponible
- `DeckNotFoundError`: Deck no existe
- `ModelNotFoundError`: Modelo de tarjeta no existe
- `ValidationError`: Validación de campos falló
- `MediaError`: Error en procesamiento de media

---

## 6. Fases de Implementación

### Fase 1: Fundación - CRUD Completo (2 semanas)

**Objetivo:** Proporcionar operaciones CRUD básicas robustas

**Herramientas a implementar:**
- ✅ `create_deck` — Crear decks
- ✅ `list_decks` — Listar decks con stats
- ✅ `delete_deck` — Eliminar decks (con confirmación)
- ✅ `create_card_batch` — Crear múltiples tarjetas
- ✅ `search_cards` — Buscar tarjetas
- ✅ `update_card` — Editar tarjetas
- ✅ `delete_cards` — Eliminar tarjetas
- ✅ `sync_anki` — Sincronizar

**Entregables:**
- 8 nuevas herramientas MCP funcionales
- Tests unitarios para cada herramienta
- Documentación de API en formato OpenAPI/JSON Schema

**Criterios de aceptación:**
- Todas las herramientas se comunican correctamente con AnkiConnect
- Manejo robusto de errores con mensajes claros
- Validación de entrada de datos

---

### Fase 2: Templates y Estilos (2 semanas)

**Objetivo:** Soportar múltiples tipos de tarjetas y estilos visuales, incluyendo máximo control custom

**Herramientas a implementar:**
- ✅ `create_note_type` — Crear modelos personalizados
- ✅ `get_note_types` — Listar modelos disponibles
- ✅ `create_card_custom` — Crear tarjetas con modelos personalizados
- ✅ `update_note_type_style` — Actualizar CSS de modelos existentes
- ✅ `update_note_type_template` — Actualizar HTML de templates

**Entregables:**
- 4 templates CSS/HTML predefinidos (Default, Duolingo, Dark, Code)
- Sistema de Custom Template: usuario describe en lenguaje natural, MCP genera CSS/HTML automático
- Sistema de validación de CSS personalizado (sin JS)
- Documentación de capacidades CSS soportadas
- Tests visuales mostrando los templates en diferentes temas

**Criterios de aceptación:**
- Templates predefinidos se ven correctamente en Anki
- Modelos personalizados se pueden crear sin errores
- Sistema Custom interpreta descripciones en lenguaje natural y genera CSS válido
- CSS no contiene código JavaScript
- Usuarios pueden actualizar estilos de modelos existentes

---

### Fase 3: Media y Enriquecimiento (2 semanas)

**Objetivo:** Soporte para medios y contenido enriquecido HTML

**Herramientas a implementar:**
- ✅ `add_media` — Subir imágenes y audio
- ✅ Mejora de `create_card_custom` para soportar HTML enriquecido

**Entregables:**
- Funcionalidad de upload de media con validación
- Soporte para referencias de media en tarjetas (img, audio tags)
- Ejemplos de tarjetas con imágenes y audio

**Criterios de aceptación:**
- Media se sube correctamente a la carpeta de Anki
- Referencias de media funcionan en tarjetas
- Validación de tipo y tamaño de archivo

---

### Fase 4: Inteligencia Conversacional (2 semanas)

**Objetivo:** Mejorar UX con preguntas inteligentes y sugerencias

**Cambios a implementar:**
- Instrucciones en `system prompt` del servidor para guiar flujos
- Lógica de sugerencias basada en contenido
- Mejora de retornos de herramientas para ser más conversacionales

**Entregables:**
- Sistema prompt mejorado
- Ejemplos de flujos conversacionales completos
- Documentación de patrones de uso

**Criterios de aceptación:**
- MCP hace preguntas aclaratorias automáticas
- Sugerencias son relevantes al contexto
- Flujos conversacionales se sienten naturales

---

## 7. Restricciones y Consideraciones

### 7.1 Dependencias Técnicas

- **AnkiConnect debe estar activo** en `localhost:8765` (requiere Anki running con AnkiConnect plugin)
- **Python 3.9+** para soportar type hints modernos
- **Sistema operativo:** Compatible con Linux, macOS, Windows (donde Anki está soportado)

### 7.2 Limitaciones del Renderer de Anki

- CSS personalizado corre dentro del renderer WebView de Anki
- No se permite JavaScript/código ejecutable en templates
- Algunas propiedades CSS pueden tener soporte limitado según versión de Anki
- Medios deben estar en formato soportado por Anki (JPEG, PNG, MP3, WAV, OGG)

### 7.3 Generación de Contenido

- El MCP **no genera automáticamente** imágenes, audio o contenido de tarjetas
- Usa URLs proporcionadas por usuario o imágenes/audio en base64
- La generación de contenido dependerá de modelos LLM externos (integración futura posible)

### 7.4 Sincronización y Respaldo

- `sync_anki` requiere credenciales de AnkiWeb configuradas en Anki
- Se recomienda respaldar antes de operaciones destructivas masivas
- Sincronización es una operación lenta (puede tomar minutos)

### 7.5 Seguridad

- Validar y sanitizar CSS personalizado (no permitir `javascript:` URLs)
- No ejecutar código Python desde templates
- Limitar tamaño de media para evitar abuso de almacenamiento
- Validar queries de búsqueda para evitar inyección

---

## 8. Criterios de Éxito

### Para Fase 1 (CRUD)
- [ ] Todas las 8 herramientas CRUD funcionan sin errores
- [ ] Manejo de errores es robusto y mensajes son útiles
- [ ] Tests automatizados cubren 80%+ del código

### Para Fase 2 (Templates)
- [ ] Los 4 templates predefinidos se renderizan correctamente
- [ ] Usuarios pueden crear modelos personalizados sin tocar código
- [ ] CSS personalizado se valida correctamente

### Para Fase 3 (Media)
- [ ] Imágenes y audio se cargan correctamente en tarjetas
- [ ] Validación de tipo y tamaño funciona
- [ ] Ejemplos demuestran tarjetas multimedia funcionales

### Para Fase 4 (Inteligencia)
- [ ] MCP hace preguntas contextuales automáticas
- [ ] Sugerencias de template basadas en contenido funcionan
- [ ] Flujos conversacionales son intuitivos

---

## 9. Referencias y Recursos

### Documentación Oficial
- [AnkiConnect API](https://github.com/FooSoft/anki-connect)
- [Anki Card Templates Docs](https://docs.ankiweb.net/templates/index.html)
- [Anki CSS Guide](https://docs.ankiweb.net/styling.html)

### Ejemplos de Uso

**Crear deck personalizado:**
```
Usuario: "Crea un deck 'Machine Learning 101' con tema Duolingo"
MCP: [crea deck] → [crea modelo personalizado] → "¿Listo para agregar tarjetas?"
```

**Búsqueda y edición:**
```
Usuario: "Busca 'backpropagation' en mis decks"
MCP: [retorna tarjetas] → Usuario selecciona → "¿Editar?"
```

---

## 10. Próximas Acciones

1. **Revisión PRD** — Validar que el documento cubre todos los requisitos
2. **Definir métricas** — ¿Cómo mediremos éxito en cada fase?
3. **Planificar sprint 1** — Asignar tareas para Fase 1 (CRUD)
4. **Configurar ambiente** — Testing local con AnkiConnect
5. **Iniciar desarrollo** — Comenzar con herramientas de Fase 1

---

**Documento preparado por:** Claude Code
**Última actualización:** Febrero 2025
**Próxima revisión:** Post-Fase 1 (validar contra requisitos reales)
