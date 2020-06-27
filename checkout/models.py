# coding=utf-8

from django.db import models
from django.conf import settings
from catalog.models import Product
from pagseguro import PagSeguro

class CartItemManager(models.Manager):

    def add_item(self, cart_key, product):
        if self.filter(cart_key=cart_key, product=product).exists():
            created = False
            cart_item = self.get(cart_key=cart_key, product=product)
            cart_item.quantity = cart_item.quantity + 1
            cart_item.save()
        else:
            created = True
            cart_item = CartItem.objects.create(
                cart_key=cart_key, product=product, price=product.price
            )
        return cart_item, created

class CartItem(models.Model):

    cart_key = models.CharField(
        'Chave do Carrinho', max_length=40, db_index=True
    )
    product = models.ForeignKey('catalog.Product', verbose_name='Produto',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    price = models.DecimalField('Preço', decimal_places=2, max_digits=8)

    objects = CartItemManager()

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens dos Carrinhos'
        unique_together = (('cart_key', 'product'),)

    def __str__(self):
        return '{} [{}]'.format(self.product, self.quantity)

class OrderManager(models.Manager):

    def create_order(self, user, cart_items):

        order = self.create(user=user)
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.price,
                order=order
            )

        return order

class Order(models.Model):

    STATUS_CHOICES = (
        (0,"Aguardando Pagamento"),
        (1,"Concluida"),
        (2,"Cancelada"),
    )

    PAYMENT_OPTION_CHOICES = (
        ("deposito","Depósito"),
        ("pagueseguro","PagueSeguro"),
        ("paypal","PayPal"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="Usuário",
                             on_delete=models.CASCADE
                             )
    status = models.IntegerField(
        "Situação", choices=STATUS_CHOICES,default=0,blank=True
    )
    payment = models.CharField(
        "Opção de Pagamento", choices=PAYMENT_OPTION_CHOICES,max_length=20,
        default="deposito"
    )

    created = models.DateTimeField("Criado em", auto_now_add=True)
    modified = models.DateTimeField("Modificado em", auto_now=True)

    order = OrderManager()

    class Meta:

        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return "Pedido #{}".format(self.pk)

    def products(self):

        products_ids = self.Items.values_list("product")
        return Product.objects.filter(pk__in=products_ids)

    def total(self):

        aggregate_queryset = self.Items.aggregate(
            total=models.Sum(
                models.F("price") * models.F("quantity"),
                output_field=models.DecimalField()
            )
        )

        return aggregate_queryset["total"]

    def PagSeguro(self):

        pg = PagSeguro(
            email=settings.PAGSEGURO_EMAIL,
            token=settings.PAGSEGURO_TOKEN,
            config={
                "sandbox":settings.PAGSEGURO_SANDBOX
            }
        )

        pg.sender = {
            "email":self.user.email
        }
        pg.reference_prefix = None
        pg.shipping = None
        pg.reference = self.pk

        for item in self.Items.all():
            pg.items.append(
                {
                    "id":item.product.pk,
                    "description":item.product.name,
                    "quantity":item.quantity,
                    "amount":"%.2f" % item.price
                }
            )

        return pg


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order, verbose_name="Pedido", related_name="Items",on_delete=models.CASCADE
    )
    product = models.ForeignKey('catalog.Product', verbose_name='Produto',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    price = models.DecimalField('Preço', decimal_places=2, max_digits=8)

    class Meta:
        verbose_name = "Item do Pedido"
        verbose_name_plural = "Itens dos Pedidos"

    def __str__(self):
        return "[{}] {}".format(self.order,self.product)

def post_save_cart_item(instance, **kwargs):
        if instance.quantity < 1:
            instance.delete()

models.signals.post_save.connect(
    post_save_cart_item,sender=CartItem, dispatch_uid="post_save_cart_item"
)
