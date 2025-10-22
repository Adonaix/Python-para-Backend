from fastapi import FastAPI, Query, status, Response, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="CRUD de producto")


class Product(BaseModel):
    id: int
    nombre: str
    categoria: str
    precio: float
    en_stock: bool


class ProductOut(BaseModel):
    nombre: str
    categoria: str
    precio: float
    en_stock: bool

PRODUCT_DB : List[Product] = []

@app.post(
    "/producto", 
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar un producto",
    response_description="Producto agregado exitosamente"
)
# -> ProductOut signica que definimos la funcion en espera de retorno de una clase de ProductOut
def add_product(product : Product)->ProductOut:
    #función integrada de python para el manejo de colecciones donde devuelve True si es verdadero cualquier elemento del iterable
    if any(producto.id == product.id for producto in PRODUCT_DB):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error":"Producto ya existente"}
            )
    PRODUCT_DB.append(product)
    #convierte de diccionario a llenarlo el objeto ProductOut
    return ProductOut(**product.model_dump())
   

@app.get(
    "/producto/{id}", 
    response_model=ProductOut,
    status_code=status.HTTP_200_OK,
    summary="Consultando un producto por ID",
    response_description="Datos del producto solicitado"
)
def get_product(producto_id: int)->ProductOut:
    for producto in PRODUCT_DB:
        if producto.id == producto_id:
            return ProductOut(**producto.model_dump())

    raise HTTPException(
         status_code=status.HTTP_404_NOT_FOUND,
         detail={"error": "Producto no encontrado"}
    )      
    
@app.put(
    "/producto/{id}", 
    status_code=status.HTTP_200_OK,
    summary="Modificando un producto por ID",
    response_description="Producto actualizado correctamente"
)    
def put_product(product_id: int, product: Product)-> dict:
    for i, producto in enumerate(PRODUCT_DB):
        if producto.id == product_id :
            PRODUCT_DB[i] = product
            return {"mensaje":"Producto actualizado correctamente"}
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Producto no encontrado"
    )

@app.delete(
    "/producto/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un producto de la BD",
    response_description="Producto eliminado"
)
def delete_product(product_id: int)-> Response:
    for i, producto in enumerate(PRODUCT_DB):
        if producto.id == product_id:
            PRODUCT_DB.pop(i)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Producto no encontrado"
    )

@app.get(
    "/producto/filter", 
    response_model=List[ProductOut],
    summary="Filtrar productos por categoría y/o precio máximo",
    response_description="Lista (posiblemente vacía) de productos filtrados"
)
def get_product(
    categoria: Optional[str] = Query(default=None, description="Categoría exacta (case-insensitive)"),
    precio_max: Optional[float] = Query(default=None, ge=0,  description="Precio de preferencia máximo (>= 0)")
)->List[ProductOut]:
    filtrados = PRODUCT_DB

    if categoria is not None:
        filtrados = [p for p in filtrados if p.categoria.lower() == categoria.lower()]
   
    if precio_max is not None:
        filtrados = [p for p in filtrados if p.precio <= precio_max]
    
    return [ProductOut(**p.model_dump()) for p in filtrados]