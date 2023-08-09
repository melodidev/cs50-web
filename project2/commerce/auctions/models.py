from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    avatar_url = models.URLField(default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwoc-wOHrC7EoqCbHPbhQdpNOR2uDZB8tzmA&usqp=CAU')

    def __str__(self):
        return f"{self.username}"

class Category(models.Model):
    category_name = models.CharField(max_length=24, default="Other")
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.category_name}"

class Product(models.Model):
    title = models.CharField(max_length=24)
    description = models.CharField(max_length=140)
    image_url = models.URLField(default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQwoc-wOHrC7EoqCbHPbhQdpNOR2uDZB8tzmA&usqp=CAU')
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category_id")
    is_open = models.BooleanField(default=True)
    current_bid = models.IntegerField()
    current_bid_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_bid_user", blank=True, null=True)
    bid_count = models.IntegerField(default=0)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer", blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class Watchlist(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="watchlist_product_id")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist_user_id")

    def __str__(self):
        return f"{self.user_id.username} added {self.product_id.title}"


class Comment(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comment_product_id")
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment_user_id")
    content = models.CharField(max_length=140)
    time = models.DateTimeField()

    def __str__(self):
        return f"{self.user_id.username} at {self.time}"


