from django.db import models
from django.utils import timezone
from accounts.models import Profile
from django.contrib.sites.models import Site

CATEGORY_CHOICES = [('Action','Action'),
                    ('Adventure','Adventure'),
                    ('Arcade','Arcade'),
                    ('FPS','FPS'),
                    ('Racing','Racing'),
                    ('Simulation','Simulation'),
                    ('Sport','Sport'),
                    ('Strategy','Strategy')]

TRANSACTION_STATUS = [('start', 'start'),
                      ('succes', 'succes'),
                      ('cancel', 'cancel'),
                      ('error', 'error')]


class Game(models.Model):
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=20,
        choices=CATEGORY_CHOICES,
        default="Action",
    )
    price = models.DecimalField(max_digits=20, decimal_places=2)
    url = models.URLField(max_length=200)
    description = models.TextField()
    global_highscore = models.FloatField(default=0)
    developer = models.ForeignKey(Profile, related_name="games", default=1, on_delete=models.CASCADE)

    @property
    def get_description_url(self):
        current_site = Site.objects.all()[0]
        return "http://" + current_site.domain + "/description/%d/" % self.id

class GamePurchase(models.Model):
    player = models.ForeignKey(Profile, related_name="purchased_games", null=True, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name="sold_games", null=True, on_delete=models.CASCADE)


class Transaction(models.Model):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    dateTime = models.DateTimeField(default=timezone.now)
    game = models.ForeignKey(Game, related_name="transactions", default=1, on_delete=models.CASCADE)
    status = models.CharField(max_length=20,
        choices = TRANSACTION_STATUS,
        default = 'start',
    )

    def __str__(self):
        return 'T of amount %f' % (self.amount)


class GameSession(models.Model):
    score = models.FloatField(default=0)
    state = models.TextField()
    status = models.CharField(max_length=10, default='start')
    game = models.ForeignKey(Game, related_name="sessions", on_delete=models.CASCADE)
    player = models.ForeignKey(Profile, related_name="sessions", on_delete=models.CASCADE)
