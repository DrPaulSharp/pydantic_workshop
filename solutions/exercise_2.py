from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
import uuid

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum


class Countries(StrEnum):
    Angola = 'Angola'
    Brazil = 'Brazil'
    Columbia = 'Columbia'
    ElSalvador = 'El Salvador'
    Ethiopia = 'Ethiopia'
    Guatemala = 'Guatemala'
    Kenya = 'Kenya'
    Tanzania = 'Tanzania'
    Uganda = 'Uganda'


class Methods(StrEnum):
    Traditional = 'traditional'
    Aeropress = 'aeropress'
    Pour_over = 'pour over'
    Chemex = 'chemex'


class Sizes(StrEnum):
    Small = 'Plaga'
    Medium = 'Garrador'
    Large = 'El Gigante'


class Coffee(BaseModel):
    """Processes a coffee order at the Sharp Coffee Residence."""
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
    country: Countries = Countries.Brazil
    method: Methods = Methods.Traditional
    size: Sizes = Sizes.Small
    milk: bool = False
    cream: bool = False
    sugars: int = Field(default=0, ge=0)

    @field_validator('sugars')
    @classmethod
    def check_odd_or_zero(cls, value: int, info: ValidationInfo) -> int:
        """We accept only an odd number of sugars, or zero."""
        if value % 2 != 0 and value != 0:
            raise ValueError(f'{info.field_name} must be odd or zero.')
        return value

    @model_validator(mode='after')
    def check_milk_and_cream(self) -> 'Coffee':
        """Make sure we don't have milk and cream together."""
        if self.milk and self.cream:
            raise ValueError('Milk AND cream!?!?! Steady on now . . .')
        return self

    @model_validator(mode='after')
    def check_chemex(self) -> 'Coffee':
        """Chemex is only available for the largest coffee."""
        if self.method.name == 'chemex' and self.size != Sizes.Large:
            raise ValueError(f'"Chemex" is only available for {Sizes.Large.value} size coffees.')
        return self
