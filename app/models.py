from typing import List, Optional

from sqlalchemy import BigInteger, CheckConstraint, Column, DECIMAL, Date, DateTime, Enum, ForeignKeyConstraint, Index, Integer, String, TIMESTAMP, Table, Text, text
from sqlalchemy.dialects.mysql import TINYINT, VARCHAR
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
import decimal

class Base(DeclarativeBase):
    pass


class Brands(Base):
    __tablename__ = 'brands'
    __table_args__ = (
        Index('brand_name', 'brand_name', unique=True),
    )

    brand_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand_name: Mapped[str] = mapped_column(String(255))
    logo_url: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    products: Mapped[List['Products']] = relationship('Products', back_populates='brand')


class Cartitems(Base):
    __tablename__ = 'cartitems'
    __table_args__ = (
        Index('fk_cart_items_variant_id', 'variant_id'),
    )

    cart_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_id: Mapped[int] = mapped_column(Integer)
    variant_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer, server_default=text("'1'"))
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    cartitemservices: Mapped[List['Cartitemservices']] = relationship('Cartitemservices', back_populates='cart_item')


class Carts(Base):
    __tablename__ = 'carts'
    __table_args__ = (
        Index('uc_session_cart', 'session_id', unique=True),
        Index('uc_user_cart', 'user_id', unique=True)
    )

    cart_id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='ID tự động tăng cho giỏ hàng')
    user_id: Mapped[Optional[int]] = mapped_column(Integer, comment='ID của người dùng nếu giỏ hàng thuộc về người dùng đã đăng nhập')
    session_id: Mapped[Optional[str]] = mapped_column(String(255), comment='ID của session nếu là giỏ hàng tạm thời cho khách chưa đăng nhập')
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))


class Categories(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        Index('category_name', 'category_name', unique=True),
    )

    category_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_name: Mapped[str] = mapped_column(String(255))
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    slogan: Mapped[Optional[str]] = mapped_column(Text)
    banner: Mapped[Optional[str]] = mapped_column(String(255))
    showable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    icon_url: Mapped[Optional[str]] = mapped_column(VARCHAR(255))

    attributegroups: Mapped[List['Attributegroups']] = relationship('Attributegroups', back_populates='category')
    options: Mapped[List['Options']] = relationship('Options', back_populates='category')
    products: Mapped[List['Products']] = relationship('Products', back_populates='category')
    services: Mapped[List['Services']] = relationship('Services', back_populates='category')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        Index('role_name', 'role_name', unique=True),
    )

    role_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    role_name: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(255))

    users: Mapped[List['Users']] = relationship('Users', back_populates='role')


class Sequelizemeta(Base):
    __tablename__ = 'sequelizemeta'
    __table_args__ = (
        Index('name', 'name', unique=True),
    )

    name: Mapped[str] = mapped_column(VARCHAR(255), primary_key=True)


class Attributegroups(Base):
    __tablename__ = 'attributegroups'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.category_id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_attributegroup_category'),
        Index('fk_attributegroup_category', 'category_id')
    )

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_name: Mapped[str] = mapped_column(String(255))
    category_id: Mapped[int] = mapped_column(Integer)
    display_order: Mapped[Optional[int]] = mapped_column(Integer)

    category: Mapped['Categories'] = relationship('Categories', back_populates='attributegroups')
    productattributes: Mapped[List['Productattributes']] = relationship('Productattributes', back_populates='group')


class Options(Base):
    __tablename__ = 'options'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.category_id'], ondelete='SET NULL', onupdate='CASCADE', name='options_ibfk_1'),
        Index('category_id', 'category_id')
    )

    option_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    option_name: Mapped[str] = mapped_column(String(255))
    is_filterable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'0'"))
    category_id: Mapped[Optional[int]] = mapped_column(Integer)

    category: Mapped[Optional['Categories']] = relationship('Categories', back_populates='options')
    optionvalues: Mapped[List['Optionvalues']] = relationship('Optionvalues', back_populates='option')


class Products(Base):
    __tablename__ = 'products'
    __table_args__ = (
        ForeignKeyConstraint(['brand_id'], ['brands.brand_id'], ondelete='RESTRICT', onupdate='CASCADE', name='products_ibfk_1'),
        ForeignKeyConstraint(['category_id'], ['categories.category_id'], ondelete='RESTRICT', onupdate='CASCADE', name='products_ibfk_2'),
        Index('brand_id', 'brand_id'),
        Index('category_id', 'category_id')
    )

    product_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name: Mapped[str] = mapped_column(String(255))
    brand_id: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    sale_volume: Mapped[Optional[int]] = mapped_column(Integer)

    brand: Mapped['Brands'] = relationship('Brands', back_populates='products')
    category: Mapped['Categories'] = relationship('Categories', back_populates='products')
    productimages: Mapped[List['Productimages']] = relationship('Productimages', back_populates='product')
    productvariants: Mapped[List['Productvariants']] = relationship('Productvariants', back_populates='product')
    productspecifications: Mapped[List['Productspecifications']] = relationship('Productspecifications', back_populates='product')
    reviews: Mapped[List['Reviews']] = relationship('Reviews', back_populates='product')


class Services(Base):
    __tablename__ = 'services'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['categories.category_id'], name='services_ibfk_1'),
        Index('idx_service_category_id', 'category_id'),
        Index('service_name', 'service_name', unique=True)
    )

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    category_id: Mapped[Optional[int]] = mapped_column(Integer)

    category: Mapped[Optional['Categories']] = relationship('Categories', back_populates='services')
    packageserviceitems: Mapped[List['Packageserviceitems']] = relationship('Packageserviceitems', back_populates='service')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['role_id'], ['roles.role_id'], name='users_ibfk_1'),
        Index('email', 'email', unique=True),
        Index('google_sub_id', 'google_sub_id', unique=True),
        Index('role_id', 'role_id')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100))
    login_method: Mapped[str] = mapped_column(String(50), server_default=text("'traditional'"))
    is_email_verified: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    is_profile_complete: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    role_id: Mapped[Optional[int]] = mapped_column(Integer)
    google_sub_id: Mapped[Optional[str]] = mapped_column(String(255))
    avatar: Mapped[Optional[str]] = mapped_column(String(255))
    district: Mapped[Optional[str]] = mapped_column(String(255))
    province: Mapped[Optional[str]] = mapped_column(String(255))
    house_number: Mapped[Optional[str]] = mapped_column(String(255))

    role: Mapped[Optional['Roles']] = relationship('Roles', back_populates='users')
    orders: Mapped[List['Orders']] = relationship('Orders', back_populates='user')
    product_events: Mapped[List['ProductEvents']] = relationship('ProductEvents', back_populates='user')
    reviews: Mapped[List['Reviews']] = relationship('Reviews', back_populates='user')


class Optionvalues(Base):
    __tablename__ = 'optionvalues'
    __table_args__ = (
        ForeignKeyConstraint(['option_id'], ['options.option_id'], ondelete='CASCADE', onupdate='CASCADE', name='optionvalues_ibfk_1'),
        Index('option_id', 'option_id')
    )

    option_value_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    option_id: Mapped[int] = mapped_column(Integer)
    option_value_name: Mapped[str] = mapped_column(String(255))

    option: Mapped['Options'] = relationship('Options', back_populates='optionvalues')
    variant: Mapped[List['Productvariants']] = relationship('Productvariants', secondary='variantoptionselections', back_populates='option_value')


class Orders(Base):
    __tablename__ = 'orders'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='SET NULL', onupdate='CASCADE', name='orders_ibfk_1'),
        Index('user_id', 'user_id')
    )

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_status: Mapped[str] = mapped_column(String(50), server_default=text("'pending'"))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    guest_email: Mapped[Optional[str]] = mapped_column(String(255))
    guest_name: Mapped[Optional[str]] = mapped_column(String(255))
    guest_phone: Mapped[Optional[str]] = mapped_column(String(20))
    guest_province: Mapped[Optional[str]] = mapped_column(String(255))
    guest_district: Mapped[Optional[str]] = mapped_column(String(255))
    guest_house_number: Mapped[Optional[str]] = mapped_column(Text)
    order_total: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2))
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'unpaid'"))
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='orders')
    orderitems: Mapped[List['Orderitems']] = relationship('Orderitems', back_populates='order')


class Productattributes(Base):
    __tablename__ = 'productattributes'
    __table_args__ = (
        ForeignKeyConstraint(['group_id'], ['attributegroups.group_id'], ondelete='SET NULL', onupdate='CASCADE', name='productattributes_ibfk_1'),
        Index('group_id', 'group_id')
    )

    attribute_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attribute_name: Mapped[str] = mapped_column(String(255))
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    is_filterable: Mapped[Optional[int]] = mapped_column(TINYINT(1), server_default=text("'0'"))
    group_id: Mapped[Optional[int]] = mapped_column(Integer)
    unit: Mapped[Optional[str]] = mapped_column(String(50))

    group: Mapped[Optional['Attributegroups']] = relationship('Attributegroups', back_populates='productattributes')
    productspecifications: Mapped[List['Productspecifications']] = relationship('Productspecifications', back_populates='attribute')


class Productimages(Base):
    __tablename__ = 'productimages'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE', onupdate='CASCADE', name='productimages_ibfk_1'),
        Index('product_id', 'product_id')
    )

    img_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer)
    image_url: Mapped[str] = mapped_column(String(2048))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    display_order: Mapped[Optional[int]] = mapped_column(Integer)

    product: Mapped['Products'] = relationship('Products', back_populates='productimages')


class Productvariants(Base):
    __tablename__ = 'productvariants'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE', onupdate='CASCADE', name='productvariants_ibfk_1'),
        Index('product_id', 'product_id'),
        Index('variant_sku', 'variant_sku', unique=True)
    )

    variant_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer)
    variant_name: Mapped[str] = mapped_column(String(255), server_default=text("'Unknow'"))
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    stock_quantity: Mapped[int] = mapped_column(Integer, server_default=text("'0'"))
    variant_sku: Mapped[str] = mapped_column(String(255))
    image_url: Mapped[Optional[str]] = mapped_column(String(255))
    item_status: Mapped[Optional[str]] = mapped_column(String(50), server_default=text("'in_stock'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    option_value: Mapped[List['Optionvalues']] = relationship('Optionvalues', secondary='variantoptionselections', back_populates='variant')
    product: Mapped['Products'] = relationship('Products', back_populates='productvariants')
    inventory_snapshots: Mapped[List['InventorySnapshots']] = relationship('InventorySnapshots', back_populates='variant')
    orderitems: Mapped[List['Orderitems']] = relationship('Orderitems', back_populates='variant')
    price_history: Mapped[List['PriceHistory']] = relationship('PriceHistory', back_populates='variant')
    product_events: Mapped[List['ProductEvents']] = relationship('ProductEvents', back_populates='variant')
    servicepackages: Mapped[List['Servicepackages']] = relationship('Servicepackages', back_populates='variant')


class InventorySnapshots(Base):
    __tablename__ = 'inventory_snapshots'
    __table_args__ = (
        ForeignKeyConstraint(['variant_id'], ['productvariants.variant_id'], name='inventory_snapshots_ibfk_1'),
        Index('variant_id', 'variant_id')
    )

    snapshot_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    snapshot_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    stock_qty: Mapped[int] = mapped_column(Integer, server_default=text("'0'"))
    stock_status: Mapped[str] = mapped_column(Enum('in_stock', 'out_of_stock', 'preorder', 'backorder'), server_default=text("'in_stock'"))
    variant_id: Mapped[Optional[int]] = mapped_column(Integer)

    variant: Mapped[Optional['Productvariants']] = relationship('Productvariants', back_populates='inventory_snapshots')


class Orderitems(Base):
    __tablename__ = 'orderitems'
    __table_args__ = (
        ForeignKeyConstraint(['order_id'], ['orders.order_id'], ondelete='CASCADE', onupdate='CASCADE', name='orderitems_ibfk_1'),
        ForeignKeyConstraint(['variant_id'], ['productvariants.variant_id'], ondelete='RESTRICT', onupdate='CASCADE', name='orderitems_ibfk_2'),
        Index('order_id', 'order_id'),
        Index('variant_id', 'variant_id')
    )

    order_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(Integer)
    variant_id: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    total_price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))

    order: Mapped['Orders'] = relationship('Orders', back_populates='orderitems')
    variant: Mapped['Productvariants'] = relationship('Productvariants', back_populates='orderitems')
    orderitemservices: Mapped[List['Orderitemservices']] = relationship('Orderitemservices', back_populates='order_item')
    reviews: Mapped[List['Reviews']] = relationship('Reviews', back_populates='order_item')


class PriceHistory(Base):
    __tablename__ = 'price_history'
    __table_args__ = (
        ForeignKeyConstraint(['variant_id'], ['productvariants.variant_id'], ondelete='RESTRICT', onupdate='CASCADE', name='price_history_ibfk_1'),
        Index('variant_id', 'variant_id')
    )

    price_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    starts_at: Mapped[datetime.datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    variant_id: Mapped[Optional[int]] = mapped_column(Integer)
    ends_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    variant: Mapped[Optional['Productvariants']] = relationship('Productvariants', back_populates='price_history')


class ProductEvents(Base):
    __tablename__ = 'product_events'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.user_id'], name='product_events_ibfk_2'),
        ForeignKeyConstraint(['variant_id'], ['productvariants.variant_id'], name='product_events_ibfk_1'),
        Index('idx_session_event_variant_on_product_events', 'session_id', 'event_type', 'variant_id'),
        Index('idx_user_event_variant_on_product_events', 'user_id', 'event_type', 'variant_id'),
        Index('variant_id', 'variant_id')
    )

    event_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    event_time: Mapped[datetime.date] = mapped_column(Date)
    event_type: Mapped[str] = mapped_column(Enum('view', 'add_to_cart', 'purchase'))
    quantity: Mapped[int] = mapped_column(Integer, server_default=text("'1'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    click_counting: Mapped[int] = mapped_column(Integer, server_default=text("'1'"))
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    session_id: Mapped[Optional[str]] = mapped_column(String(255))
    variant_id: Mapped[Optional[int]] = mapped_column(Integer)
    price_at_event: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(12, 2))
    referrer: Mapped[Optional[str]] = mapped_column(String(255))
    utm_source: Mapped[Optional[str]] = mapped_column(String(100))
    utm_medium: Mapped[Optional[str]] = mapped_column(String(100))

    user: Mapped[Optional['Users']] = relationship('Users', back_populates='product_events')
    variant: Mapped[Optional['Productvariants']] = relationship('Productvariants', back_populates='product_events')


class Productspecifications(Base):
    __tablename__ = 'productspecifications'
    __table_args__ = (
        ForeignKeyConstraint(['attribute_id'], ['productattributes.attribute_id'], ondelete='RESTRICT', onupdate='CASCADE', name='fk_product_spec_attribute'),
        ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='RESTRICT', onupdate='CASCADE', name='fk_product_spec_product'),
        Index('idx_attribute_id', 'attribute_id'),
        Index('idx_product_id', 'product_id')
    )

    specification_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer)
    attribute_id: Mapped[int] = mapped_column(Integer)
    attribute_value: Mapped[Optional[str]] = mapped_column(VARCHAR(255))

    attribute: Mapped['Productattributes'] = relationship('Productattributes', back_populates='productspecifications')
    product: Mapped['Products'] = relationship('Products', back_populates='productspecifications')


class Servicepackages(Base):
    __tablename__ = 'servicepackages'
    __table_args__ = (
        ForeignKeyConstraint(['variant_id'], ['productvariants.variant_id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_servicepackage_variant'),
        Index('variant_id', 'variant_id', 'package_name', unique=True)
    )

    package_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[int] = mapped_column(Integer)
    package_name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    display_order: Mapped[Optional[int]] = mapped_column(Integer)
    description: Mapped[Optional[str]] = mapped_column(Text)

    variant: Mapped['Productvariants'] = relationship('Productvariants', back_populates='servicepackages')
    packageserviceitems: Mapped[List['Packageserviceitems']] = relationship('Packageserviceitems', back_populates='package')


t_variantoptionselections = Table(
    'variantoptionselections', Base.metadata,
    Column('variant_id', Integer, primary_key=True, nullable=False),
    Column('option_value_id', Integer, primary_key=True, nullable=False),
    ForeignKeyConstraint(['option_value_id'], ['optionvalues.option_value_id'], ondelete='CASCADE', onupdate='CASCADE', name='variantoptionselections_ibfk_2'),
    ForeignKeyConstraint(['variant_id'], ['productvariants.variant_id'], ondelete='CASCADE', onupdate='CASCADE', name='variantoptionselections_ibfk_1'),
    Index('option_value_id', 'option_value_id')
)


class Orderitemservices(Base):
    __tablename__ = 'orderitemservices'
    __table_args__ = (
        ForeignKeyConstraint(['order_item_id'], ['orderitems.order_item_id'], ondelete='CASCADE', onupdate='CASCADE', name='FK_orderserviceitem_orderitem'),
        Index('FK_orderserviceitem_orderitem', 'order_item_id')
    )

    order_item_service_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_item_id: Mapped[int] = mapped_column(Integer)
    package_service_item_id: Mapped[int] = mapped_column(Integer)
    price: Mapped[Optional[decimal.Decimal]] = mapped_column(DECIMAL(10, 2), server_default=text("'0.00'"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    order_item: Mapped['Orderitems'] = relationship('Orderitems', back_populates='orderitemservices')


class Packageserviceitems(Base):
    __tablename__ = 'packageserviceitems'
    __table_args__ = (
        ForeignKeyConstraint(['package_id'], ['servicepackages.package_id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_packageitem_package'),
        ForeignKeyConstraint(['service_id'], ['services.service_id'], ondelete='CASCADE', onupdate='CASCADE', name='fk_packageitem_service'),
        Index('fk_packageitem_service', 'service_id'),
        Index('package_id', 'package_id', 'service_id', unique=True)
    )

    package_service_item_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    package_id: Mapped[int] = mapped_column(Integer)
    service_id: Mapped[int] = mapped_column(Integer)
    item_price_impact: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    at_least_one: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'0'"))
    selectable: Mapped[int] = mapped_column(TINYINT(1), server_default=text("'1'"))
    created_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[datetime.datetime] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    package: Mapped['Servicepackages'] = relationship('Servicepackages', back_populates='packageserviceitems')
    service: Mapped['Services'] = relationship('Services', back_populates='packageserviceitems')
    cartitemservices: Mapped[List['Cartitemservices']] = relationship('Cartitemservices', back_populates='package_service_item')


class Reviews(Base):
    __tablename__ = 'reviews'
    __table_args__ = (
        CheckConstraint('((`rating` >= 1) and (`rating` <= 5))', name='reviews_chk_1'),
        ForeignKeyConstraint(['order_item_id'], ['orderitems.order_item_id'], ondelete='SET NULL', onupdate='CASCADE', name='reviews_ibfk_1'),
        ForeignKeyConstraint(['product_id'], ['products.product_id'], ondelete='CASCADE', onupdate='CASCADE', name='reviews_ibfk_3'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE', onupdate='CASCADE', name='reviews_ibfk_2'),
        Index('order_item_id', 'order_item_id'),
        Index('product_id', 'product_id'),
        Index('user_id', 'user_id')
    )

    review_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer)
    rating: Mapped[int] = mapped_column(Integer)
    order_item_id: Mapped[Optional[int]] = mapped_column(Integer)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    session_id: Mapped[Optional[str]] = mapped_column(String(128))
    comment_text: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    order_item: Mapped[Optional['Orderitems']] = relationship('Orderitems', back_populates='reviews')
    product: Mapped['Products'] = relationship('Products', back_populates='reviews')
    user: Mapped[Optional['Users']] = relationship('Users', back_populates='reviews')


class Cartitemservices(Base):
    __tablename__ = 'cartitemservices'
    __table_args__ = (
        ForeignKeyConstraint(['cart_item_id'], ['cartitems.cart_item_id'], ondelete='CASCADE', name='fk_cart_item_services_cart_item_id'),
        ForeignKeyConstraint(['package_service_item_id'], ['packageserviceitems.package_service_item_id'], name='fk_cart_item_services_package_service_item_id'),
        Index('fk_cart_item_services_package_service_item_id', 'package_service_item_id'),
        Index('uc_cart_item_package_service_item', 'cart_item_id', 'package_service_item_id', unique=True)
    )

    cart_item_service_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_item_id: Mapped[int] = mapped_column(Integer)
    package_service_item_id: Mapped[int] = mapped_column(Integer)
    price: Mapped[decimal.Decimal] = mapped_column(DECIMAL(10, 2))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    cart_item: Mapped['Cartitems'] = relationship('Cartitems', back_populates='cartitemservices')
    package_service_item: Mapped['Packageserviceitems'] = relationship('Packageserviceitems', back_populates='cartitemservices')
