   # Crée un profil automatiquement à la création d'un User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User , Profile
from .models import Cart
from django.db.models.signals import pre_save

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):  # Évite une erreur si le profil n'existe pas
        instance.profile.save()


@receiver(pre_save, sender=Cart)
def prevent_duplicate_carts(sender, instance, **kwargs):
    if Cart.objects.filter(user=instance.user).exclude(pk=instance.pk).exists():
        raise ValueError("Un panier existe déjà pour cet utilisateur")
