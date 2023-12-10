from pydantic import BaseModel


class Coffee(BaseModel):
    """Processes a coffee order at the Sharp Coffee Residence."""
    country: str = 'Brazil'
    method: str = 'traditional'
    size: str = 'small'
    milk: bool = False
    cream: bool = False
    sugars: int = 0
