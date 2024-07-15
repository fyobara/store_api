from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import UUID4
from store.core.exceptions import NotFoundException
from store.core.exceptions import InsertionException
from store.schemas.product import ProductIn, ProductOut, ProductUpdate, ProductUpdateOut
from store.usecases.product import ProductUsecase

router = APIRouter(tags=["products"])


@router.post(path="/", status_code=status.HTTP_201_CREATED)
async def post(
    body: ProductIn = Body(...), usecase: ProductUsecase = Depends()
) -> ProductOut:
        try:
            return await usecase.create(body=body)
        except InsertionException as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message))

@router.get(path="/{id}", status_code=status.HTTP_200_OK)
async def get(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> ProductOut:
    try:
        return await usecase.get(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get(path="/", status_code=status.HTTP_200_OK)
async def query(usecase: ProductUsecase = Depends()) -> List[ProductOut]:
    return await usecase.query()
    

async def list_products(
    valor_minimo: float = Query(None, description="Filtro Valor Mínimo"),
    valor_maximo: float = Query(None, description="Filtro Valor Mínimo"),
    usecase: ProductUsecase = Depends()
) -> List[ProductOut]:
    products = await usecase.query()

    if valor_minimo is not None and valor_maximo is not None:
        filtro = [p for p in products if valor_minimo < p.price < valor_maximo]
    elif valor_minimo is not None:
        filtro = [p for p in products if p.price >= valor_minimo]
    elif valor_maximo is not None:
        filtro = [p for p in products if p.price <= valor_maximo]
    else:
        filtro = products
    return filtro

@router.patch(path="/{id}", status_code=status.HTTP_200_OK)
async def patch(
    id: UUID4 = Path(alias="id"),
    body: ProductUpdate = Body(...),
    usecase: ProductUsecase = Depends(),
) -> ProductUpdateOut:
    return await usecase.update(id=id, body=body)


@router.delete(path="/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    id: UUID4 = Path(alias="id"), usecase: ProductUsecase = Depends()
) -> None:
    try:
        await usecase.delete(id=id)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
