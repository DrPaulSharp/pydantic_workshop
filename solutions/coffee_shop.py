"""Have a pydantic drink at the Sharp Coffee Residence!"""

import pint
from pydantic import BaseModel, Field, ValidationInfo, field_validator, model_validator
from pydantic.functional_validators import AfterValidator
from typing import Annotated, Literal, Union
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


class Sizes(StrEnum):
    Small = 'Plaga'
    Medium = 'Garrador'
    Large = 'El Gigante'


class Toppings(StrEnum):
    Chocolate_shavings = 'chocolate shavings'
    Flake = 'flake'
    Fudge = 'fudge'
    Marshmallows = 'marshmallows'
    Sparkler = 'sparkler'
    Whipped_cream = 'whipped cream'


class Varieties(StrEnum):
    Proper = 'proper'
    Green = 'green'
    Lapsang = 'lapsang souchong'
    Rooibos = 'rooibos'
    Burgamot = 'burgamot'


class Traditional(BaseModel, extra='forbid'):
    """Options for the traditional coffee method at the Sharp Coffee Residence."""
    name: Literal['traditional']


class Aeropress(BaseModel, extra='forbid'):
    """Options for the aeropress coffee method at the Sharp Coffee Residence."""
    name: Literal['aeropress']
    filter: Literal['metal', 'paper'] = 'metal'


class PourOver(BaseModel, extra='forbid'):
    """Options for the pour over coffee method at the Sharp Coffee Residence."""
    name: Literal['pour over']
    brewer: Literal['v60', 'wave'] = 'v60'
    brew_time: int = 120


class Chemex(BaseModel, extra='forbid'):
    """Options for the chemex coffee method at the Sharp Coffee Residence."""
    name: Literal['chemex']
    brew_time: int = 240


class HotDrink(BaseModel, validate_assignment=True, extra='forbid'):
    """Processes a hot drink order at the Sharp Coffee Residence."""
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
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
    def check_milk_and_cream(self) -> 'HotDrink':
        """Make sure we don't have milk and cream together."""
        if self.milk and self.cream:
            raise ValueError('Milk AND cream!?!?! Steady on now . . .')
        return self


def convert_volume(volume: pint.Quantity) -> pint.Quantity:
    """Convert the supplied volume to millilitres, and raise an error if a unit that is not a volume is entered."""
    volume_unit = 'milliliter'
    try:
        volume = volume.to(volume_unit)
    except pint.DimensionalityError:
        raise ValueError(f'A quantity in the unit: {volume.units} cannot be converted to a volume')
    return volume


ml_volume = Annotated[pint.Quantity, AfterValidator(convert_volume)]


class Coffee(HotDrink, arbitrary_types_allowed=True):
    """Processes a coffee order at the Sharp Coffee Residence."""
    country: Countries = Countries.Brazil
    method: Union[Traditional, Aeropress, PourOver, Chemex] = Field(discriminator='name')
    water: ml_volume = pint.Quantity(0.0, 'milliliter')

    @model_validator(mode='after')
    def check_chemex(self) -> 'Coffee':
        """Chemex is only available for the largest coffee."""
        if self.method.name == 'chemex' and self.size != Sizes.Large:
            raise ValueError(f'"Chemex" is only available for {Sizes.Large.value} size coffees.')
        return self

    @model_validator(mode='after')
    def check_fit_in_cup(self) -> 'Coffee':
        """Water needs to fit in the appropriate size cup."""
        if (self.size == Sizes.Small and self.water.magnitude > 200 or
            self.size == Sizes.Medium and self.water.magnitude > 300 or
            self.size == Sizes.Large and self.water.magnitude > 400
            ):
            raise ValueError(f'{self.water!s} is too much water for a {self.size.value} coffee - it needs to fit in '
                             f'the cup! York floods often enough thank you very much.')
        return self


class HotChocolate(BaseModel, validate_assignment=True, extra='forbid'):
    """Processes a hot chocolate order at the Sharp Coffee Residence."""
    order_id: uuid.UUID = Field(default_factory=uuid.uuid4, frozen=True)
    size: Sizes = Sizes.Small
    toppings: list[Toppings] = Field(default=[], max_length=3)

    @field_validator('toppings')
    @classmethod
    def check_unique_toppings(cls, value: list[Toppings]) -> list[Toppings]:
        """Toppings should not be repeated."""
        if list(set(value)) != value:
            raise ValueError('The list of toppings must be unique.')
        return value


class Tea(HotDrink):
    """Processes a tea order at the Sharp Coffee Residence."""
    variety: Varieties = Varieties.Proper

    @model_validator(mode='after')
    def check_sugar(self) -> 'Tea':
        """Sugar in middle class tea?"""
        if self.variety != Varieties.Proper and self.sugars != 0:
            raise ValueError('Surely you don\'t have sugar in middle class tea . . .')
        return self
