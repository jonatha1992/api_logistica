# API REST - Cotizador Inteligente de Envíos

**Versión:** 1.0.0  
**Base URL:** `http://localhost:8000` (desarrollo) / `https://tu-app.railway.app` (producción)  
**Tipo:** REST API  
**Formato:** JSON

## 📋 Descripción General

API REST para cotizar envíos en Argentina con múltiples carriers (OCA, Andreani, Correo Argentino). Diseñada para consumo desde aplicaciones de e-commerce donde el usuario final selecciona la opción de envío que prefiere.

---

## 🚀 Endpoint Principal: Cotizar Envío

### `POST /api/v1/cotizar`

Obtiene cotizaciones de envío comparando automáticamente múltiples carriers.

#### Request Headers
```http
Content-Type: application/json
```

#### Request Body
```json
{
  "origin": {
    "street": "Pareja",
    "number": "6542",
    "city": "Gonzalez Catan", 
    "state": "B",
    "postal_code": "1757",
    "country_code": "AR",
    "contact_name": "Juan Pérez",
    "contact_email": "juan@ejemplo.com",
    "contact_phone": "1122334455"
  },
  "destination": {
    "street": "Del Leon",
    "number": "504", 
    "city": "Ezeiza",
    "state": "B",
    "postal_code": "1802",
    "country_code": "AR",
    "contact_name": "María González",
    "contact_email": "maria@ejemplo.com", 
    "contact_phone": "1155667788"
  },
  "parcels": [
    {
      "weight": 1,
      "height": 10,
      "width": 20,
      "length": 20,
      "content": "Producto de ejemplo"
    }
  ],
  "carrier": "oca",
  "currency": "ARS"
}
```

#### Campos del Request

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `origin` | Object | ✅ | Dirección de origen |
| `destination` | Object | ✅ | Dirección de destino |
| `parcels` | Array | ✅ | Lista de paquetes |
| `carrier` | String | ❌ | Carrier específico: `"oca"`, `"andreani"`, `"correoargentino"` |
| `currency` | String | ❌ | Moneda (default: `"ARS"`) |

**Carriers disponibles:**
- `"oca"` - OCA Argentina
- `"andreani"` - Andreani Logística  
- `"correoargentino"` - Correo Argentino

---

## 📤 Response Structure

### Success Response (200 OK)

```json
{
  "data": [
    {
      "carrier": "oca",
      "carrierDescription": "OCA",
      "carrierId": 62,
      "serviceId": 146,
      "service": "oca_PP",
      "serviceDescription": "Oca Puerta a Puerta",
      "dropOff": 0,
      "zone": 1,
      "deliveryEstimate": "3-7 días",
      "deliveryDate": {
        "date": "2025-09-02",
        "dateDifference": 10,
        "timeUnit": "days",
        "time": "20:00"
      },
      "basePrice": 8264.33,
      "basePriceTaxes": 1735.51,
      "totalPrice": 9999.83,
      "currency": "ARS",
      "branches": [],
      "packageDetails": {
        "totalWeight": 1,
        "weightUnit": "KG"
      }
    },
    {
      "carrier": "oca", 
      "carrierDescription": "OCA",
      "carrierId": 62,
      "serviceId": 147,
      "service": "oca_PS",
      "serviceDescription": "Oca Puerta a Sucursal",
      "dropOff": 2,
      "zone": 1,
      "deliveryEstimate": "3-7 días",
      "deliveryDate": {
        "date": "2025-09-02", 
        "dateDifference": 10,
        "timeUnit": "days",
        "time": "20:00"
      },
      "basePrice": 6409.57,
      "basePriceTaxes": 1346.01,
      "totalPrice": 7755.58,
      "currency": "ARS",
      "branches": [
        {
          "branch_id": "O33",
          "branch_code": "1964", 
          "reference": "PUNTO OCA - Locutorio Pelin",
          "distance": 6.79,
          "address": {
            "street": "PASO DE LA PATRIA",
            "number": "264",
            "city": "AEROPUERTO EZEIZA",
            "state": "BA",
            "postalCode": "1802",
            "latitude": "-34.8549564",
            "longitude": "-58.5210535"
          }
        }
      ],
      "packageDetails": {
        "totalWeight": 1,
        "weightUnit": "KG"
      }
    }
  ]
}
```

---

## 📊 Campos de la Response

### Información Básica del Carrier
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `carrier` | String | Código del carrier (`"oca"`, `"andreani"`, `"correoargentino"`) |
| `carrierDescription` | String | Nombre legible (`"OCA"`, `"Andreani"`, `"Correo Argentino"`) |
| `carrierId` | Integer | ID único del carrier |

### Información del Servicio  
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `serviceId` | Integer | ID único del servicio |
| `service` | String | Código del servicio (`"oca_PP"`, `"ground"`, `"standard_dom"`) |
| `serviceDescription` | String | Descripción del servicio (`"Oca Puerta a Puerta"`) |

### Modalidades de Entrega (`dropOff`)
| Valor | Descripción |
|-------|-------------|
| `0` | **Puerta a Puerta** - Retiro y entrega a domicilio |
| `1` | **Sucursal a Puerta** - Retiro en sucursal, entrega a domicilio |
| `2` | **Puerta a Sucursal** - Retiro a domicilio, entrega en sucursal |
| `3` | **Sucursal a Sucursal** - Retiro y entrega en sucursal |

### Precios
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `basePrice` | Float | Precio base sin impuestos |
| `basePriceTaxes` | Float | Impuestos aplicados |
| `totalPrice` | Float | **PRECIO FINAL** a mostrar al usuario |
| `currency` | String | Moneda (`"ARS"`) |

### Tiempos de Entrega
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `deliveryEstimate` | String | Estimación en texto (`"2-5 días"`, `"3-7 días"`) |
| `deliveryDate.date` | String | Fecha específica (`"2025-09-02"`) |
| `deliveryDate.dateDifference` | Integer | Días desde hoy |
| `deliveryDate.time` | String | Hora de entrega (`"20:00"`) |

### Sucursales (solo si `dropOff` es 1, 2 o 3)
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `branches` | Array | Lista de sucursales disponibles |
| `branches[].reference` | String | Nombre de la sucursal |
| `branches[].distance` | Float | Distancia en km |
| `branches[].address` | Object | Dirección completa con coordenadas GPS |

---

## 🎯 Cómo Consumir en tu E-commerce

### 1. Request Básico (JavaScript ejemplo)
```javascript
const cotizacion = await fetch('/api/v1/cotizar', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    origin: { /* datos origen */ },
    destination: { /* datos destino */ }, 
    parcels: [{ /* datos paquete */ }],
    carrier: "oca" // o "andreani" o "correoargentino"
  })
});

const opciones = await cotizacion.json();
```

### 2. Mostrar Opciones al Usuario
```javascript
opciones.data.forEach(opcion => {
  console.log(`${opcion.carrierDescription}: $${opcion.totalPrice} - ${opcion.deliveryEstimate}`);
  
  // Determinar modalidad
  const modalidad = {
    0: "Puerta a Puerta",
    1: "Sucursal a Puerta", 
    2: "Puerta a Sucursal",
    3: "Sucursal a Sucursal"
  }[opcion.dropOff];
  
  console.log(`Modalidad: ${modalidad}`);
  
  // Si tiene sucursales, mostrarlas
  if (opcion.branches?.length > 0) {
    opcion.branches.forEach(sucursal => {
      console.log(`Sucursal: ${sucursal.reference} - ${sucursal.distance}km`);
    });
  }
});
```

### 3. Comparar Automáticamente (Opcional)
```javascript
// Más barato
const masBarato = opciones.data.reduce((min, actual) => 
  actual.totalPrice < min.totalPrice ? actual : min
);

// Más rápido (menor dateDifference)  
const masRapido = opciones.data.reduce((min, actual) =>
  actual.deliveryDate.dateDifference < min.deliveryDate.dateDifference ? actual : min
);
```

---

## 🔧 Otros Endpoints Disponibles

### `GET /api/v1/carriers`
Lista todos los carriers disponibles en Argentina.

**Response:**
```json
{
  "meta": "carriers",
  "total": 8,
  "data": [
    {
      "id": 62,
      "name": "oca", 
      "category": "local"
    },
    {
      "id": 114,
      "name": "andreani",
      "category": "local" 
    },
    {
      "id": 127,
      "name": "correoArgentino",
      "category": "postal"
    }
  ]
}
```

### `GET /api/v1/status`
Health check de la API.

**Response:**
```json
{
  "status": "operativo",
  "environment": "PRO", 
  "timestamp": "2025-08-23T14:30:00.000Z"
}
```

---

## ❌ Error Responses

### 400 Bad Request
```json
{
  "detail": "Datos de entrada inválidos"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "origin", "postal_code"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error  
```json
{
  "detail": "Error al comunicarse con la API de Envia.com: mensaje del error"
}
```

---

## 💡 Casos de Uso para E-commerce

### Checkout con Múltiples Opciones
1. Usuario llega al checkout
2. Tu app consulta `/api/v1/cotizar` con datos del pedido
3. Muestras las opciones: precio, tiempo, modalidad
4. Usuario selecciona su preferida
5. Guardas la selección para el fulfillment

### Calculadora de Envío en Producto
1. Usuario ingresa CP de destino en página de producto
2. Consultas con datos aproximados del producto
3. Muestras estimaciones de costo y tiempo
4. Usuario puede decidir antes de agregar al carrito

### Comparador Automático
1. Consultas los 3 carriers principales
2. Destacas automáticamente "Más económico" y "Más rápido"
3. Usuario ve claramente las ventajas de cada opción

---

## 🌐 URLs de la API

- **Desarrollo:** `http://localhost:8000`
- **Producción:** `https://tu-app.railway.app` (configurar después del deploy)
- **Documentación interactiva:** `/docs` (Swagger UI)
- **Documentación alternativa:** `/redoc`

---

## 📈 Próximas Funciones (Roadmap)

🔜 **En desarrollo futuro:**
- ✅ Cotizaciones (ACTUAL)  
- 🔄 Creación de envíos reales
- 🔄 Números de tracking  
- 🔄 Generación de etiquetas
- 🔄 Seguimiento en tiempo real
- 🔄 Webhooks de estado
- 🔄 Integración con más carriers

**Status actual:** ✅ Cotizador completo y funcional para e-commerce