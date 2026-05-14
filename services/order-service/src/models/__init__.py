# Import all models so SQLAlchemy metadata is fully populated
# and Alembic can discover them for autogenerate.

from src.models.reference import (  # noqa: F401
    Addresses,
    BankRequisites,
    CompanyTypes,
    DeliveryTypes,
    DocumentTemplates,
    Images,
    MeasurementUnits,
    PaymentTypes,
    Roles,
    Sellers,
    Sizes,
    Teams,
)
from src.models.user import Contracts, Users  # noqa: F401
from src.models.company import Companies  # noqa: F401
from src.models.product import Categories, Gallery, PriceMultipliers, Prices, Products  # noqa: F401
from src.models.cart import Cart, CartItemProducts, CartItems  # noqa: F401
from src.models.payment import Payments  # noqa: F401
from src.models.delivery import Deliveries  # noqa: F401
from src.models.order import Comments, OrderNumbers, OrderPaths, Orders, SuperOrders  # noqa: F401
