# Top 5 Ocupaciones - Componente UI

Componente profesional para mostrar las 5 ocupaciones/carreras que mejor se ajustan al perfil del usuario. Incluye dos implementaciones: **React + CSS Modules** y **HTML + CSS puro**.

## 📋 Características

✅ **Diseño responsivo**: Desktop (5 col) → Tablet (2 col) → Mobile (1 col)  
✅ **Paleta pastel arcoíris suave**: Colores variados por card (lila, celeste, menta, durazno, rosado)  
✅ **Cards cuadradas**: Aspect ratio 1:1 con información organizada  
✅ **Barra de progreso gradiente**: Muestra compatibilidad visualmente  
✅ **Badge de porcentaje**: Visible en la esquina superior derecha  
✅ **Hover elegante**: Elevación y sombra mejorada  
✅ **Ellipsis automático**: Títulos con máximo 2 líneas

---

## 🚀 Opción 1: React + CSS Modules (Recomendado)

### Archivos:
- `TopOccupations.jsx` - Componente principal
- `OccupationCard.jsx` - Componente de card individual
- `TopOccupations.module.css`
- `OccupationCard.module.css`

### Uso:

```jsx
import TopOccupations from './TopOccupations';

// Con datos custom
const occupations = [
  { id: 1, name: 'Ingeniería en Sistemas', percentage: 98.7, colorScheme: 'lila' },
  { id: 2, name: 'Administración', percentage: 92.3, colorScheme: 'celeste' },
  { id: 3, name: 'Psicología', percentage: 87.5, colorScheme: 'menta' },
  { id: 4, name: 'Diseño Gráfico', percentage: 85.1, colorScheme: 'durazno' },
  { id: 5, name: 'Contabilidad', percentage: 78.9, colorScheme: 'rosado' }
];

<TopOccupations occupations={occupations} />;

// O sin props para usar datos por defecto
<TopOccupations />;
```

### Props:
- `occupations` (array): Array de objetos con `id`, `name`, `percentage`, `colorScheme`
- Si no se pasa, usa datos de ejemplo

---

## 🎨 Opción 2: HTML + CSS Puro

### Archivos:
- `top-occupations-example.html` - HTML completo
- `top-occupations-styles.css` - Estilos CSS

### Uso:
Simplemente incluir el CSS en tu `<head>`:

```html
<link rel="stylesheet" href="top-occupations-styles.css">
```

Y copiar la estructura HTML de `top-occupations-example.html` en tu sección.

---

## 🎯 Esquemas de color

| Esquema  | Gradiente Pastel                    |
|----------|-------------------------------------|
| Lila     | #E8D5F2 → #D8B4FE                 |
| Celeste  | #D4E8F7 → #B3E5FC                 |
| Menta    | #D4F0E8 → #A7F3D0                 |
| Durazno  | #F5D4C8 → #FBBF7E                 |
| Rosado   | #F0D4E8 → #F3B3D9                 |

---

## 📱 Breakpoints Responsivos

```css
Desktop:  5 columnas (≥1400px)
         3 + 2 centrado (1000px-1399px)
Tablet:   2 columnas (481px-767px)
Mobile:   1 columna (≤480px)
```

---

## 🎨 Personalizaciones

### Cambiar colores:
En `OccupationCard.module.css` o `top-occupations-styles.css`, editar las clases `.lila`, `.celeste`, etc.

### Cambiar el gradiente de la barra de progreso:
```css
.progress-bar {
  background: linear-gradient(90deg, 
    #TU_COLOR_1 0%, 
    #TU_COLOR_2 25%, 
    #TU_COLOR_3 50%, 
    #TU_COLOR_4 75%, 
    #TU_COLOR_5 100%);
}
```

### Ajustar sombra y hover:
En `.card:hover` (CSS Modules) o `.occupation-card:hover` (CSS puro)

---

## 📐 Especificaciones Técnicas

- **Bordes**: 8px de border-radius
- **Sombra reposo**: 0 2px 8px rgba(0,0,0,0.06)
- **Sombra hover**: 0 8px 16px rgba(0,0,0,0.12)
- **Elevación hover**: translateY(-3px)
- **Tipografía**: Poppins (700 títulos, 600 subtítulos)
- **Animaciones**: cubic-bezier(0.4, 0, 0.2, 1)

---

## ✨ Detalles de diseño

✓ Badges con fondo blanco translúcido (0.95 opacity)  
✓ Títulos con ellipsis automático (max 2 líneas)  
✓ Barras de progreso con border sutil  
✓ Compatibilidad total con navegadores modernos  
✓ Sin dependencias externas (CSS puro)

---

**Listo para usar en producción** ✅
